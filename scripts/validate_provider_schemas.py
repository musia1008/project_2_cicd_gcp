import json
import sys
from pathlib import Path


def validate_fields(fields: object, schema_file: Path, location: str = "") -> bool:
    if not isinstance(fields, list) or not fields:
        print(f"Expected a non-empty field list in {schema_file}{location}", file=sys.stderr)
        return False

    valid = True
    for index, field in enumerate(fields):
        field_location = f"{location}[{index}]"
        if (
            not isinstance(field, dict)
            or not isinstance(field.get("name"), str)
            or not isinstance(field.get("type"), str)
        ):
            print(f"Invalid BigQuery field in {schema_file}{field_location}", file=sys.stderr)
            valid = False
            continue

        if "fields" in field and not validate_fields(
            field["fields"], schema_file, f"{field_location}.fields"
        ):
            valid = False

    return valid


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

        if not validate_fields(document, schema_file):
            invalid = True

    if invalid:
        return 1

    print(f"Validated {len(files)} provider BigQuery schema files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
