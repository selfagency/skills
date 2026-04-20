#!/usr/bin/env python3
"""
Validate environment variables against a schema file.

Usage:
  validate-env-vars.py <schema-file> [--env-file .env] [--strict]

Schema format (JSON):
  {
    "required": ["API_KEY", "DATABASE_URL"],
    "optional": ["LOG_LEVEL"],
    "rules": {
      "API_KEY": {"type": "string", "min_length": 10, "pattern": "^[a-zA-Z0-9_]+$"},
      "PORT": {"type": "integer", "min": 1024, "max": 65535},
      "LOG_LEVEL": {"type": "choice", "values": ["debug", "info", "warn", "error"]}
    }
  }

Examples:
  validate-env-vars.py config/env-schema.json
  validate-env-vars.py config/env-schema.json --env-file .env.production --strict
  validate-env-vars.py config/env-schema.json --strict > validation-report.json

Exit codes:
  0  All environment variables valid
  1  Missing required variables or validation failed
  2  Schema file error
"""

# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "jsonschema>=4.0.0",
# ]
# ///

import sys
import json
import os
import re
import argparse
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path


def load_schema(schema_file: str) -> Dict[str, Any]:
    """Load and validate schema file."""
    try:
        with open(schema_file, 'r') as f:
            schema = json.load(f)
        return schema
    except FileNotFoundError:
        print(f"ERROR: Schema file not found: {schema_file}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in schema: {e}", file=sys.stderr)
        sys.exit(2)


def load_env_file(env_file: str) -> Dict[str, str]:
    """Load environment variables from .env file."""
    env_vars = {}

    if not os.path.exists(env_file):
        return env_vars

    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    env_vars[key] = value
    except Exception as e:
        print(f"WARNING: Error reading .env file: {e}", file=sys.stderr)

    return env_vars


def validate_string_rule(value: str, rule: Dict[str, Any]) -> Optional[str]:
    """Validate string value against rule."""
    if "min_length" in rule:
        if len(value) < rule["min_length"]:
            return f"String too short (min: {rule['min_length']}, got: {len(value)})"

    if "max_length" in rule:
        if len(value) > rule["max_length"]:
            return f"String too long (max: {rule['max_length']}, got: {len(value)})"

    if "pattern" in rule:
        if not re.match(rule["pattern"], value):
            return f"Value does not match pattern: {rule['pattern']}"

    return None


def validate_integer_rule(value: str, rule: Dict[str, Any]) -> Optional[str]:
    """Validate integer value against rule."""
    try:
        int_val = int(value)
    except ValueError:
        return "Not a valid integer"

    if "min" in rule:
        if int_val < rule["min"]:
            return f"Value too small (min: {rule['min']}, got: {int_val})"

    if "max" in rule:
        if int_val > rule["max"]:
            return f"Value too large (max: {rule['max']}, got: {int_val})"

    return None


def validate_choice_rule(value: str, rule: Dict[str, Any]) -> Optional[str]:
    """Validate choice value against rule."""
    choices = rule.get("values", [])

    if value not in choices:
        return f"Invalid choice. Allowed: {', '.join(choices)}"

    return None


def validate_value(var_name: str, value: str, schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate a single environment variable value."""
    rules = schema.get("rules", {})

    if var_name not in rules:
        # No specific rules, assume valid
        return True, None

    rule = rules[var_name]
    var_type = rule.get("type", "string")

    # Validate based on type
    if var_type == "string":
        error = validate_string_rule(value, rule)
    elif var_type == "integer":
        error = validate_integer_rule(value, rule)
    elif var_type == "choice":
        error = validate_choice_rule(value, rule)
    else:
        error = f"Unknown type: {var_type}"

    if error:
        return False, error

    return True, None


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate environment variables")
    parser.add_argument("schema", help="Schema file (JSON)")
    parser.add_argument("--env-file", default=".env", help="Environment file to validate (default: .env)")
    parser.add_argument("--strict", action="store_true", help="Fail on first error")
    parser.add_argument("--json", action="store_true", help="Output JSON report")

    args = parser.parse_args()

    # Load schema
    schema = load_schema(args.schema)

    # Load environment variables (from file or environment)
    if args.env_file:
        env_vars = load_env_file(args.env_file)
    else:
        env_vars = os.environ.copy()

    # Validate
    errors: List[Dict[str, str]] = []
    warnings: List[Dict[str, str]] = []
    valid_count = 0

    required_vars = schema.get("required", [])
    optional_vars = schema.get("optional", [])

    # Check required variables
    for var_name in required_vars:
        if var_name not in env_vars:
            errors.append({
                "variable": var_name,
                "error": "MISSING (required)",
            })
            if args.strict:
                break
        else:
            # Validate value
            is_valid, error = validate_value(var_name, env_vars[var_name], schema)
            if not is_valid:
                errors.append({
                    "variable": var_name,
                    "error": error or "Invalid value",
                })
                if args.strict:
                    break
            else:
                valid_count += 1

    # Check optional variables if present
    for var_name in optional_vars:
        if var_name in env_vars:
            is_valid, error = validate_value(var_name, env_vars[var_name], schema)
            if not is_valid:
                warnings.append({
                    "variable": var_name,
                    "warning": error or "Invalid value",
                })
            else:
                valid_count += 1

    # Output
    if args.json:
        report = {
            "valid": len(errors) == 0,
            "valid_count": valid_count,
            "errors": errors,
            "warnings": warnings,
        }
        print(json.dumps(report, indent=2))
    else:
        if errors:
            print(f"❌ Validation failed ({len(errors)} errors):")
            for err in errors:
                print(f"  - {err['variable']}: {err['error']}")

        if warnings:
            print(f"⚠️  Warnings ({len(warnings)}):")
            for warn in warnings:
                print(f"  - {warn['variable']}: {warn['warning']}")

        if not errors and not warnings:
            print(f"✅ All environment variables valid ({valid_count} checked)")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
