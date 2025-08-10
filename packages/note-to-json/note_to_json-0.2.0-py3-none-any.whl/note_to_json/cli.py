#!/usr/bin/env python3
"""
note_to_json.cli

Command-line interface for the note-to-json parser.
"""

import argparse
import glob
import json
import sys
from pathlib import Path
from .parser import parse_file, read_input


def expand_glob_patterns(patterns):
    """Expand glob patterns and return sorted, deduplicated list of files"""
    expanded_files = []
    
    for pattern in patterns:
        # Check if pattern contains glob characters
        if any(char in pattern for char in ['*', '?', '[']):
            # Use recursive=True if pattern contains '**'
            recursive = '**' in pattern
            matched_files = glob.glob(pattern, recursive=recursive)
            if not matched_files:
                # If glob pattern matches nothing, treat as missing file
                expanded_files.append(pattern)
            else:
                expanded_files.extend(matched_files)
        else:
            # No glob characters, treat as literal path
            expanded_files.append(pattern)
    
    # Deduplicate and sort for deterministic order
    return sorted(set(expanded_files))


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Convert markdown/text or JSON inputs to structured JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  note2json input.md                    # Parse to input.parsed.json
  note2json input.md -o output.json     # Parse to custom output file
  note2json input.md --stdout           # Print JSON to STDOUT
  note2json input.md --stdout --pretty  # Pretty-print JSON to STDOUT
  note2json *.md                        # Parse multiple files

  # Read from STDIN (Windows):
  type data.json | note2json --stdin --input-format json --stdout

  # Read from STDIN (macOS/Linux):
  cat data.json | note2json --stdin --input-format json --stdout
        """
    )
    
    parser.add_argument(
        "input_file",
        nargs="*",
        help="Input file(s) to parse (supports glob patterns like *.md, **/*.md)"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: input.parsed.json)"
    )
    
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print JSON to STDOUT instead of writing to file"
    )
    
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON with 2-space indentation"
    )

    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read input from STDIN instead of files"
    )

    parser.add_argument(
        "--input-format",
        choices=["auto", "md", "txt", "json"],
        default="auto",
        help="Input format: auto-detect (default), md, txt, or json"
    )
    
    args = parser.parse_args()
    
    # Handle conflict between --stdout and -o/--output
    if args.stdout and args.output:
        print("Warning: --stdout overrides -o/--output", file=sys.stderr)
    
    # If --stdin is provided, prefer it over file paths
    if args.stdin:
        if args.input_file:
            print("Warning: --stdin provided; ignoring file paths", file=sys.stderr)
        try:
            # Read from STDIN (binary safe), BOM-safe decoding
            raw_bytes = sys.stdin.buffer.read()
            text = raw_bytes.decode("utf-8-sig", errors="replace")
            parsed_data = read_input(text, args.input_format, filename_hint="stdin")
        except Exception as e:
            print(f"Error: Failed to parse STDIN", file=sys.stderr)
            sys.exit(3)

        indent = 2 if args.pretty else None
        if args.stdout or not args.output:
            json.dump(parsed_data, sys.stdout, indent=indent, ensure_ascii=False)
            if not args.pretty:
                print()
        else:
            output_path = Path(args.output)
            output_path.write_text(
                json.dumps(parsed_data, indent=indent, ensure_ascii=False),
                encoding="utf-8"
            )
            print(f"✅ Parsed: STDIN → {output_path.name}")
        sys.exit(0)

    # No --stdin: need at least one file
    if not args.input_file:
        print("Error: No input provided. Use files or --stdin.", file=sys.stderr)
        sys.exit(2)

    # Expand glob patterns
    input_files = expand_glob_patterns(args.input_file)
    
    # Track missing files and parsing errors
    missing_files = []
    parsing_errors = []
    successful_parses = []
    
    # Process each input file
    for input_path_str in input_files:
        input_path = Path(input_path_str)
        
        if not input_path.exists():
            missing_files.append(input_path)
            continue
        
        try:
            # Read file and parse according to input format
            text = input_path.read_text(encoding="utf-8-sig", errors="replace")
            filename_hint = input_path.stem
            parsed_data = read_input(text, args.input_format, filename_hint=filename_hint)
            successful_parses.append((input_path, parsed_data))
            
        except Exception as e:
            parsing_errors.append((input_path, str(e)))
    
    # Handle missing files
    for missing_file in missing_files:
        print(f"Error: File not found: {missing_file}", file=sys.stderr)
    
    # Handle parsing errors
    for failed_file, error_msg in parsing_errors:
        print(f"Error: Failed to parse: {failed_file}", file=sys.stderr)
    
    # Determine exit code
    if missing_files:
        sys.exit(2)  # Missing files
    elif parsing_errors:
        sys.exit(3)  # Parsing errors
    
    # Determine JSON formatting
    indent = 2 if args.pretty else None
    
    # Handle output
    if args.stdout:
        # Print to STDOUT (NDJSON format for multiple files)
        for i, (input_path, parsed_data) in enumerate(successful_parses):
            if i > 0 and args.pretty:
                print()  # Add blank line between pretty-printed objects
            json.dump(parsed_data, sys.stdout, indent=indent, ensure_ascii=False)
            if not args.pretty:
                print()  # Add newline for compact format
    else:
        # Handle file output
        if args.output:
            if len(successful_parses) > 1:
                print(f"Error: --output can only be used with a single input file", file=sys.stderr)
                sys.exit(1)
            elif len(successful_parses) == 1:
                output_path = Path(args.output)
                input_path, parsed_data = successful_parses[0]
                output_path.write_text(
                    json.dumps(parsed_data, indent=indent, ensure_ascii=False),
                    encoding="utf-8"
                )
                print(f"✅ Parsed: {input_path.name} → {output_path.name}")
        else:
            # Write individual output files
            for input_path, parsed_data in successful_parses:
                output_path = input_path.with_suffix(".parsed.json")
                output_path.write_text(
                    json.dumps(parsed_data, indent=indent, ensure_ascii=False),
                    encoding="utf-8"
                )
                print(f"✅ Parsed: {input_path.name} → {output_path.name}")


if __name__ == "__main__":
    main()
