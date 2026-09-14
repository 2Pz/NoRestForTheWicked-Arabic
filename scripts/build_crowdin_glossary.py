import os
import csv
import glob


def build_glossary():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    glossary_dir = os.path.join(base_dir, "glossaries")

    # We want to merge files 00 through 10
    files_to_merge = glob.glob(os.path.join(glossary_dir, "0[0-9]_*.csv")) + glob.glob(
        os.path.join(glossary_dir, "10_*.csv")
    )

    master_glossary = {}

    for file_path in files_to_merge:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                continue

            for row in reader:
                if len(row) >= 2:
                    en_term = row[0].strip()
                    ar_term = row[1].strip()
                    desc = row[2].strip() if len(row) > 2 else ""

                    if en_term and ar_term:
                        # Store in dict to prevent duplicates (latest overrides)
                        if en_term not in master_glossary:
                            master_glossary[en_term] = {"ar": ar_term, "desc": desc}

    # Write to a Crowdin compatible CSV format
    output_path = os.path.join(glossary_dir, "crowdin_glossary.csv")
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Term", "Arabic", "Description"])
        for en_term, data in sorted(master_glossary.items()):
            writer.writerow([en_term, data["ar"], data["desc"]])

    print(
        f"Compiled {len(master_glossary)} unique terms into {output_path} for Crowdin!"
    )


if __name__ == "__main__":
    build_glossary()
