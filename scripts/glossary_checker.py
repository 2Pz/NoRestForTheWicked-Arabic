import csv
import re
import sys
import os
import glob


def load_glossaries(glossaries_dir):
    glossary = {}
    csv_files = glob.glob(os.path.join(glossaries_dir, "*.csv"))
    for f in csv_files:
        with open(f, "r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                term = row.get("Term", "").strip()
                arabic = row.get("Arabic", "").strip()
                if term and arabic:
                    # Sort by length descending to match longest terms first
                    glossary[term.lower()] = arabic
    return glossary


def check_translations(translations_dir, glossary):
    csv_files = glob.glob(os.path.join(translations_dir, "*.csv"))

    # Sort keys by length so "The Pestilence" matches before "Pestilence"
    sorted_terms = sorted(glossary.keys(), key=len, reverse=True)

    all_errors = []

    for f in csv_files:
        filename = os.path.basename(f)
        with open(f, "r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for i, row in enumerate(reader, start=2):
                source = row.get("source", "")
                target = row.get("target", "")

                if not target.strip():
                    continue  # Skip untranslated

                source_lower = source.lower()

                for term in sorted_terms:
                    # Use regex with word boundaries if it's a word,
                    # but since terms might have spaces, \b is good enough
                    # escape the term for regex
                    escaped_term = re.escape(term)
                    if re.search(r"\b" + escaped_term + r"\b", source_lower):
                        expected_arabic_options = [
                            opt.strip() for opt in glossary[term].split("/")
                        ]

                        match_found = False
                        for opt in expected_arabic_options:
                            # Also check the option without leading 'ال'
                            opt_no_al = opt[2:] if opt.startswith("ال") else opt
                            if opt in target or opt_no_al in target:
                                match_found = True
                                break

                        if not match_found:
                            all_errors.append(
                                f"Line {i} in {filename}: Missing glossary term.\n  Source: {source}\n  Expected Arabic term: '{glossary[term]}' for English '{term}'\n  Target: {target}\n"
                            )

    return all_errors


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    glossaries_dir = os.path.join(base_dir, "glossaries")
    translations_dir = os.path.join(base_dir, "translations")

    glossary = load_glossaries(glossaries_dir)
    errors = check_translations(translations_dir, glossary)

    if errors:
        print(f"Found {len(errors)} glossary consistency errors:")
        for err in errors[:50]:  # limit output
            print(err)
        if len(errors) > 50:
            print(f"... and {len(errors) - 50} more errors.")
        sys.exit(1)
    else:
        print("All translated text adheres to the glossary perfectly!")
        sys.exit(0)


if __name__ == "__main__":
    main()
