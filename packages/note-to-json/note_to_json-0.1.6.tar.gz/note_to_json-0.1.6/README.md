# 📝 Note-to-json-demo 📁

[![CI](https://img.shields.io/github/actions/workflow/status/Mugiwara555343/note-to-json-demo/python-ci.yml?branch=main)](#)
[![Release](https://img.shields.io/github/v/tag/Mugiwara555343/note-to-json-demo)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
> Convert markdown notes to structured JSON offline in seconds.

This is a standalone demo of the **Markdown-to-JSON memory parser** and **file change watcher** used in the AI Memory Architecture project. It converts `.md` logs into clean `.parsed.json` objects with metadata, summaries, and core reflections.

You can:
- 📝 Write or edit markdown memory entries
- ⚙️ Parse them into structured `.parsed.json` snapshots
- 👁️ Enable live file watching (auto-parse on edit)

---

## 🚀 Quickstart

```bash
pip install "git+https://github.com/Mugiwara555343/note-to-json-demo@v0.1.6"

# macOS/Linux:
printf "# Demo note\nFelt heavy this morning..." > demo.md

# Windows (PowerShell):
Set-Content -Encoding UTF8 demo.md "# Demo note`nFelt heavy this morning..."

# Basic parsing
note2json demo.md -o out.json

# Print JSON to STDOUT
note2json demo.md --stdout

# Pretty-print JSON to STDOUT
note2json demo.md --stdout --pretty

# Pipe to jq for filtering
note2json demo.md --stdout | jq '.title'
```

---

## 📦 What's Inside

| File/Directory      | Role                                         |
|---------------------|----------------------------------------------|
| `note_to_json/`     | Main package directory                       |
| `note_to_json/parser.py` | Core parsing logic                        |
| `note_to_json/cli.py` | Command-line interface                    |
| `memory_watcher.py` | Watches folder for `.md` edits, auto-parses  |
| `demo_entries/`     | Folder with 5 sample logs for testing        |
| `watch_config.json` | Declares which folders the watcher monitors  |
| `pyproject.toml`    | Package configuration and dependencies       |
| `tests/`           | Test suite with automated CI                 |

### 🧪 Demo Entries

The `demo_entries/` folder contains 5 sample markdown files showcasing different emotional tones:
- `demo_entry.md` - Reflective morning entry
- `creative_breakthrough.md` - Enthusiastic breakthrough moment
- `frustration_moment.md` - Frustrated debugging session
- `peaceful_morning.md` - Calm gratitude practice
- `team_collaboration.md` - Energized team meeting

---

## 🚀 How to Use

### 1. Clone the Repository

```bash
git clone https://github.com/Mugiwara555343/note-to-json-demo.git
cd note-to-json-demo
```

### 2. Install the Package

**Option A: Install in Development Mode**
```bash
pip install -e .
```

**Option B: Install with Development Dependencies**
```bash
pip install -e ".[dev]"
```

### 3. Use the CLI

**Parse a single file:**
```bash
note2json input.md
```

**Parse with custom output:**
```bash
note2json input.md -o output.json
```

**Print JSON to STDOUT:**
```bash
note2json input.md --stdout
```

**Pretty-print JSON to STDOUT:**
```bash
note2json input.md --stdout --pretty
```

**Pipe to jq for filtering:**
```bash
note2json input.md --stdout | jq '.title'
```

**Parse multiple files with glob patterns:**
```bash
note2json *.md
note2json notes\**\*.md --stdout | jq
```

**Note:** PowerShell often passes wildcards literally. This tool now expands glob patterns like `*.md` and `**/*.md` automatically.

### 4. Use as a Python Package

```python
from note_to_json import parse_file
from pathlib import Path

# Parse a markdown file
data = parse_file(Path("input.md"))
print(data["title"])
print(data["summary"])
```

### 5. Enable Live Watching (Auto Mode)

```bash
python memory_watcher.py
```

Now edit any `.md` file in the current folder (or add new ones).

✅ On save, the watcher re-runs the parser and updates/creates the corresponding `.parsed.json`.

---

## 🧪 Output Example

After parsing, you’ll get:

{
  "title": "Morning Reflection",
  "timestamp": "2025-07-17T20:18:21Z",
  "summary": "Today I spent time refining the AI memory watcher...",
  "tags": ["focus", "emotion", "ai"],
  "reflections": [
    "Resilience is built through iteration.",
    "System design is emotional memory made technical."
  ]
}

---

## 📝 Markdown Format

Your `.md` files should follow this structure:

```markdown
# Title
**Date:** YYYY-MM-DD  
**Tags:** #tag1 #tag2 #tag3  
**Tone:** Emotional tone

**Summary:**
Brief summary of the entry.

**Core Reflections:**
- First reflection point
- Second reflection point
- Third reflection point
```

## 🧪 Testing & CI

The project includes automated testing and continuous integration:

### Running Tests Locally
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest -q
```

### CI/CD Pipeline
- **GitHub Actions** automatically runs tests on every push and pull request
- **CI Badge** shows current build status at the top of this README
- **Test Coverage** includes parser validation, metadata extraction, and schema compliance

### Test Structure
- `tests/test_parser.py` - Core parser functionality tests
- `tests/fixtures/sample.md` - Test markdown fixture
- Validates JSON schema, required fields, metadata extraction, and content parsing

---

## 📌 Notes

- `.parsed.json` is stored in the same folder as the `.md` file
- Files that fail schema validation will be skipped with a warning
- Watching behavior is debounced to avoid duplicate triggering
- The parser extracts: title, date, tags, tone, summary, and reflections
- All fields are optional except title, timestamp, raw_text, and plain_text

### Exit Codes
- **0**: Success - all files parsed successfully
- **2**: Missing files - one or more input files don't exist or glob patterns matched zero files
- **3**: Parsing errors - one or more files failed to parse

---

## 📜 License

MIT — free to use, modify, and extend.

---
### 🔄 Related Work
* **Legacy-AMA (v1, archived)** – full pipeline prototype  
* **AMA v2 (private, in progress)** – orchestration, GPU router, RAG

