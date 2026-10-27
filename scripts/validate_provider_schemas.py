import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_provider_schemas.py <schema-directory>", file=sys.stderr)
        return 2

    schema_dir = Path(sys.argv[1])
    if not schema_dir.is_dir():
        print(f"Schema directory does not exist: {schema_dir}", file=sys.stderr)
        return 2

    files = sorted(schema_dir.glob("*.json"))
    if not files:
        print(f"No JSON schemas found in: {schema_dir}", file=sys.stderr)
        return 1

    invalid = False
    for schema_file in files:
        try:
            with schema_file.open(encoding="utf-8") as file:
                document = json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            print(f"Invalid JSON in {schema_file}: {error}", file=sys.stderr)
            invalid = True
            continue

        if not isinstance(document, dict):
            print(f"Schema must have a JSON object at its root: {schema_file}", file=sys.stderr)
            invalid = True

    if invalid:
        return 1

    print(f"Validated {len(files)} provider BigQuery schema files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
