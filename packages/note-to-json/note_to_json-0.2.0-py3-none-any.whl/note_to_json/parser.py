#!/usr/bin/env python3
"""
note_to_json.parser

Parses markdown/text or JSON into a structured JSON schema. Supports:
- Markdown/text parsing with inline metadata
- JSON passthrough/normalization
"""

import io
import json
from pathlib import Path
from datetime import datetime
from typing import IO, Union, Optional
from jsonschema import validate, ValidationError

# === SCHEMA ===
SCHEMA = {
    "type": "object",
    "required": ["title", "timestamp", "raw_text", "plain_text"],
    "properties": {
        "title":       {"type": "string"},
        "timestamp":   {"type": "string", "format": "date-time"},
        "raw_text":    {"type": "string"},
        "plain_text":  {"type": "string"},
        "tags":        {"type": "array", "items": {"type": "string"}},
        "headers":     {"type": "array", "items": {"type": "string"}},
        "date":        {"type": "string"},
        "tone":        {"type": "string"},
        "summary":     {"type": "string"},
        "reflections": {"type": "array", "items": {"type": "string"}},
    },
    "additionalProperties": False
}


def validate_parsed(data: dict):
    validate(instance=data, schema=SCHEMA)


def _parse_text(text: str, *, filename_hint: Optional[str] = None) -> dict:
    """
    Parse markdown/plain text into structured JSON.
    
    Args:
        text: Full file content
        filename_hint: Used to derive a reasonable title when headers are absent
        
    Returns:
        dict: Parsed data with metadata, content, and reflections
    """
    lines = text.splitlines()

    raw_text   = text.strip()
    plain_text = raw_text.replace("\n", " ")
    title      = (filename_hint or "stdin")
    tags, headers, reflections = [], [], []
    date_str, tone_str, summary_text = None, None, None
    in_summary = in_reflect = False

    for line in lines:
        if line.startswith("# "):
            h = line.lstrip("# ").strip()
            headers.append(h)
            # Use the first H1 as title
            if title == (filename_hint or "stdin"):
                title = h

        if line.startswith("**Date:**"):
            date_str = line.split("**Date:**", 1)[1].strip()
        if line.startswith("**Tags:**"):
            vals = line.split("**Tags:**", 1)[1].strip()
            tags = [t.strip().lstrip("#") for t in vals.split() if t.startswith("#")]
        if line.startswith("**Tone:**"):
            tone_str = line.split("**Tone:**", 1)[1].strip()

        if line.lower().startswith("**summary:**"):
            in_summary = True
            summary_text = ""
            continue
        if in_summary:
            if line.strip() == "" or line.strip().startswith("---"):
                in_summary = False
            else:
                summary_text += line.strip() + " "

        if line.lower().startswith("**core reflections:**"):
            in_reflect = True
            continue
        if in_reflect:
            if not line.startswith("-"):
                in_reflect = False
            else:
                reflections.append(line.lstrip("- ").strip())

    # If no headers were found and we still have the default title,
    # use the first non-empty line as a fallback title
    if headers == [] and title == (filename_hint or "stdin"):
        for line in lines:
            if line.strip():
                title = line.strip()
                break

    if date_str:
        try:
            dt = datetime.fromisoformat(date_str)
            timestamp = dt.isoformat() + "Z"
        except:
            timestamp = datetime.utcnow().isoformat() + "Z"
    else:
        timestamp = datetime.utcnow().isoformat() + "Z"

    parsed = {
        "title":       title,
        "timestamp":   timestamp,
        "raw_text":    raw_text,
        "plain_text":  plain_text,
        "tags":        tags,
        "headers":     headers,
        "date":        date_str,
        "tone":        tone_str,
        "summary":     summary_text.strip() if summary_text else None,
        "reflections": reflections,
    }

    parsed = {k: v for k, v in parsed.items() if v is not None}
    validate_parsed(parsed)
    return parsed


def read_input(source: Union[str, IO[bytes], IO[str]], input_format: str, *, filename_hint: Optional[str] = None) -> dict:
    """
    Read and parse input from a text string or stream according to input_format.

    - If input_format == 'auto': decide JSON vs text by peeking first non-whitespace char.
      '{' or '[' -> JSON, else text.
    - If JSON:
        * If object matches our schema keys, validate and return as-is
        * Else, normalize arbitrary JSON to our schema
    - If text: parse as markdown/plain using the existing flow

    The function is BOM-safe when reading from byte streams.
    """
    # Extract text from source
    if isinstance(source, str):
        text_content = source
    else:
        # Stream case: prefer bytes then decode; if str stream, read directly
        raw = source.read()
        if isinstance(raw, bytes):
            text_content = raw.decode("utf-8-sig", errors="replace")
        else:
            text_content = raw

    # Determine effective input format
    effective_format = input_format
    if input_format == "auto":
        first_non_ws = next((ch for ch in text_content.lstrip()[:1]), "")
        if first_non_ws in ("{", "["):
            effective_format = "json"
        else:
            effective_format = "txt"

    if effective_format in ("md", "txt"):
        return _parse_text(text_content, filename_hint=filename_hint)

    if effective_format == "json":
        try:
            data = json.loads(text_content)
        except json.JSONDecodeError as exc:
            raise exc

        allowed_keys = set(SCHEMA["properties"].keys())
        required_keys = set(["title", "timestamp", "raw_text", "plain_text"])

        if isinstance(data, dict):
            data_keys = set(data.keys())
            # If object already matches schema keys and has required fields, validate and return
            if data_keys.issubset(allowed_keys) and required_keys.issubset(data_keys):
                validate_parsed(data)
                return data

            # Normalize arbitrary JSON object
            title = str(data.get("title")) if "title" in data else (filename_hint or "stdin")
            # Keep tags if present and is list of strings
            tags_val = data.get("tags")
            if isinstance(tags_val, list):
                tags_norm = [str(t) for t in tags_val if isinstance(t, (str, int, float, bool))]
                tags_norm = [t for t in tags_norm if isinstance(t, str)]
            else:
                tags_norm = []
        else:
            # Array or primitive: treat as arbitrary JSON
            title = (filename_hint or "stdin")
            tags_norm = []

        # Minified raw/plain text representation of the original JSON
        minified = json.dumps(json.loads(text_content), ensure_ascii=False, separators=(",", ":"))
        parsed = {
            "title": title,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "raw_text": minified,
            "plain_text": minified,
            "tags": tags_norm,
            "headers": [],
            "reflections": [],
        }
        validate_parsed(parsed)
        return parsed

    raise ValueError(f"Unsupported input_format: {input_format}")


def parse_file(md_path: Path) -> dict:
    """
    Parse a markdown file into structured JSON.
    """
    text = md_path.read_text(encoding="utf-8-sig", errors="replace")
    return _parse_text(text, filename_hint=md_path.stem)


# Backward compatibility
def parse_md_file(md_path: Path) -> dict:
    """Alias for parse_file for backward compatibility"""
    return parse_file(md_path)
