#!/usr/bin/env python3
"""
Validate jc JSON output for correctness and schema conformance.

Usage:
  validate-jc-output.py <parser> [--input FILE] [--pretty]

Examples:
  ps aux | jc --ps | validate-jc-output.py ps
  validate-jc-output.py df --input df-output.json --pretty

Options:
  --input FILE    Read JSON from file instead of stdin (default: stdin)
  --pretty        Pretty-print valid JSON (default: compact)
  --help          Show this help message
"""

# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "jsonschema>=4.0.0",
# ]
# ///

import sys
import json
import argparse
from typing import Any, Dict, List

SCHEMAS: Dict[str, Dict[str, Any]] = {
    "ps": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "user": {"type": "string"},
                "pid": {"type": ["integer", "string"]},
                "cpu_percent": {"type": ["number", "string"]},
                "mem_percent": {"type": ["number", "string"]},
                "command": {"type": "string"},
            },
            "required": ["pid"],
        },
    },
    "df": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "filesystem": {"type": "string"},
                "size": {"type": ["string", "integer"]},
                "used": {"type": ["string", "integer"]},
                "available": {"type": ["string", "integer"]},
                "use_percent": {"type": ["number", "integer"]},
                "mounted_on": {"type": "string"},
            },
            "required": ["filesystem"],
        },
    },
    "netstat": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "protocol": {"type": "string"},
                "local_address": {"type": "string"},
                "local_port": {"type": ["integer", "string"]},
                "remote_address": {"type": "string"},
                "remote_port": {"type": ["integer", "string"]},
                "state": {"type": "string"},
            },
        },
    },
    "ls": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "filename": {"type": "string"},
                "size": {"type": ["integer", "string"]},
                "permissions": {"type": "string"},
                "owner": {"type": "string"},
                "group": {"type": "string"},
            },
            "required": ["filename"],
        },
    },
}


def validate_json(data: Any, parser: str, pretty: bool = False) -> bool:
    """Validate JSON against jc parser schema."""

    # Check if data is list (most jc outputs are arrays)
    if not isinstance(data, list):
        print(f"ERROR: Expected array, got {type(data).__name__}", file=sys.stderr)
        return False

    # Check if empty (valid but unusual)
    if len(data) == 0:
        print("WARNING: Empty array (no results)", file=sys.stderr)

    # Basic field validation for known parsers
    if parser in SCHEMAS:
        schema = SCHEMAS[parser]
        required_fields = schema["items"].get("required", [])

        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                print(f"ERROR: Item {idx} is not object (got {type(item).__name__})", file=sys.stderr)
                return False

            # Check required fields present
            for field in required_fields:
                if field not in item:
                    print(f"ERROR: Item {idx} missing required field '{field}'", file=sys.stderr)
                    return False

    # Print results
    if pretty:
        print(json.dumps(data, indent=2))
    else:
        print(json.dumps(data, separators=(',', ':')))

    return True


def main() -> int:
    """Main entry point."""
    parser_arg = argparse.ArgumentParser(
        description="Validate jc JSON output for correctness",
        add_help=False
    )
    parser_arg.add_argument("parser", help="jc parser name (ps, df, netstat, ls, etc)")
    parser_arg.add_argument("--input", help="Read JSON from file (default: stdin)")
    parser_arg.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    parser_arg.add_argument("--help", action="store_true", help="Show help message")

    args = parser_arg.parse_args()

    if args.help:
        print(__doc__)
        return 0

    # Read JSON input
    try:
        if args.input:
            with open(args.input, 'r') as f:
                data = json.load(f)
        else:
            data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # Validate
    success = validate_json(data, args.parser, args.pretty)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
