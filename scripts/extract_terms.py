import csv
import re
import os
import glob
from collections import Counter


def load_existing_glossary_terms(glossaries_dir):
    terms = set()
    for f in glob.glob(os.path.join(glossaries_dir, "*.csv")):
        with open(f, "r", encoding="utf-8-sig") as file:
            for row in csv.DictReader(file):
                term = row.get("Term", "").strip()
                if term:
                    terms.add(term.lower())
    return terms


def extract_frequent_terms(translations_dir, existing_terms):
    words_counter = Counter()

    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "as",
        "is",
        "are",
        "was",
        "were",
        "it",
        "this",
        "that",
    }

    for f in glob.glob(os.path.join(translations_dir, "*.csv")):
        with open(f, "r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                source = row.get("source", "")
                if not source:
                    continue

                # Remove tags and placeholders before extracting terms
                clean_source = re.sub(r"\{[^}]+\}", "", source)
                clean_source = re.sub(r"\[[^\]]+\]", "", clean_source)
                clean_source = re.sub(r"<[^>]+>", "", clean_source)

                # Find capitalized words or phrases (Title Case)
                # Regex matches sequences of Title Case words
                matches = re.findall(
                    r"\b[A-Z][a-z]*(?:\s+[A-Z][a-z]*)*\b", clean_source
                )

                for match in matches:
                    term = match.strip()
                    term_lower = term.lower()

                    if len(term) < 3:
                        continue

                    if term_lower in stop_words:
                        continue

                    if term_lower in existing_terms:
                        continue

                    words_counter[term] += 1

    return words_counter.most_common(200)


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    glossaries_dir = os.path.join(base_dir, "glossaries")
    translations_dir = os.path.join(base_dir, "translations")

    existing_terms = load_existing_glossary_terms(glossaries_dir)
    frequent_terms = extract_frequent_terms(translations_dir, existing_terms)

    output_file = os.path.join(glossaries_dir, "09_extracted_potential_terms.csv")
    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Term", "Arabic", "Description", "Frequency"])
        for term, count in frequent_terms:
            # We don't have the translation yet, leave it empty
            writer.writerow([term, "", "", count])

    print(f"Extracted {len(frequent_terms)} frequent terms and saved to {output_file}")


if __name__ == "__main__":
    main()
