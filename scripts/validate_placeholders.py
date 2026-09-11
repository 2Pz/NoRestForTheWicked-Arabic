import csv
import re
import sys
import os


def get_placeholders(text):
    # Find all placeholders like {0}, {1}, {amount}
    curly_braces = re.findall(r"\{[^}]+\}", text)
    # Find all input bindings like [interact]
    square_braces = re.findall(r"\[[^\]]+\]", text)
    # Find HTML-like tags like <color=#F2E6BD> and </color>
    tags = re.findall(r"<[^>]+>", text)
    # Find explicit newlines
    newlines = re.findall(r"\\n", text)
    return sorted(curly_braces + square_braces + tags + newlines)


def validate_file(filepath):
    errors = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # 1-based index + header
            source = row.get("source", "")
            target = row.get("target", "")

            if not target.strip():
                continue  # Skip untranslated

            source_pl = get_placeholders(source)
            target_pl = get_placeholders(target)

            if source_pl != target_pl:
                errors.append(
                    f"Line {i} in {os.path.basename(filepath)}:\n  Source Placeholders: {source_pl}\n  Target Placeholders: {target_pl}\n  Source: {source}\n  Target: {target}\n"
                )
    return errors


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    translations_dir = os.path.join(base_dir, "translations")

    translation_files = []
    for root, dirs, files in os.walk(translations_dir):
        for file in files:
            if file.endswith(".csv") and "needsReview" not in file:
                translation_files.append(os.path.join(root, file))

    all_errors = []
    for file_path in translation_files:
        errors = validate_file(file_path)
        all_errors.extend(errors)

    if all_errors:
        print(f"Found {len(all_errors)} placeholder mismatch errors:")
        for err in all_errors:
            print(err)
        sys.exit(1)
    else:
        print("All placeholders match perfectly!")
        sys.exit(0)


if __name__ == "__main__":
    main()
