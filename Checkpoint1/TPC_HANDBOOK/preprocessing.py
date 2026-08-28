# -*- coding: utf-8 -*-
"""
Checkpoint 1 - Text Preprocessing Script
Balik-Turo: Filipino Folk Remedy & Herbal Medicine Assistant

What this does:
  1. Loads every raw .txt document in data/raw/
  2. Cleans and normalizes the text (line endings, whitespace, casing,
     stray markup, tabs)
  3. Tokenizes the cleaned text (simple whitespace/regex tokenizer -
     no external model download required, works fully offline)
  4. Saves the cleaned versions to data/processed/
  5. Writes a before/after report to docs/preprocessing_report.md so the
     cleaning work is easy to grade and demonstrate

Run:
    python3 src/preprocessing.py
"""

import os
import re
import json

RAW_DIR = os.path.join(os.path.dirname(__file__), "data")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "data", "processed")
REPORT_PATH = os.path.join(os.path.dirname(__file__), "docs", "preprocessing_report.md")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)


def clean_text(raw_text: str) -> str:
    """Normalize a raw document into clean, model-ready text."""
    text = raw_text

    # 1. Normalize line endings (files have mixed \r\n and \n)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 2. Strip HTML-style comment artifacts, e.g. <!-- source: ... -->
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    # 3. Replace tabs with a single space
    text = text.replace("\t", " ")

    # 4. Collapse runs of whitespace (double spaces, extra blank lines) but
    #    keep paragraph breaks as a single blank line
    text = re.sub(r"[ ]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 5. Trim trailing whitespace on each line
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines).strip()

    return text


def simple_tokenize(text: str):
    """
    Lightweight regex tokenizer (word-level), lower-cased, punctuation
    stripped. Kept dependency-free and offline so it runs anywhere.
    In the full pipeline this is swapped for the tokenizer that ships
    with the chosen embedding model (Checkpoint 1, Embedding Demo).
    """
    text = text.lower()
    tokens = re.findall(r"[a-zA-Z]+(?:-[a-zA-Z]+)*|\d+", text)
    return tokens


def main():
    files = sorted(f for f in os.listdir(RAW_DIR) if f.endswith(".txt"))
    report_rows = []

    for fname in files:
        raw_path = os.path.join(RAW_DIR, fname)
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        cleaned = clean_text(raw_text)
        tokens = simple_tokenize(cleaned)

        out_path = os.path.join(PROCESSED_DIR, fname.replace(".txt", ".json"))
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "source_file": fname,
                    "clean_text": cleaned,
                    "num_tokens": len(tokens),
                    "tokens_preview": tokens[:25],
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        report_rows.append(
            {
                "file": fname,
                "raw_chars": len(raw_text),
                "clean_chars": len(cleaned),
                "num_tokens": len(tokens),
                "raw_preview": raw_text[:180].replace("\n", "\\n"),
                "clean_preview": cleaned[:180].replace("\n", "\\n"),
            }
        )

    write_report(report_rows)
    print(f"Processed {len(files)} documents.")
    print(f"Cleaned JSON written to: {PROCESSED_DIR}")
    print(f"Before/after report written to: {REPORT_PATH}")


def write_report(rows):
    lines = [
        "# Preprocessing Before/After Report",
        "",
        "Checkpoint 1 evidence: text cleaning, normalization, and tokenization",
        "applied to the TPC Student Handbook raw dataset (41 documents, extracted",
        "from the instructor-provided handbook PDF).",
        "",
        "## Sample before/after (first 3 documents)",
        "",
    ]
    for row in rows[:3]:
        lines += [
            f"### {row['file']}",
            "",
            f"**Raw ({row['raw_chars']} chars):**",
            f"```\n{row['raw_preview']}...\n```",
            "",
            f"**Cleaned ({row['clean_chars']} chars):**",
            f"```\n{row['clean_preview']}...\n```",
            "",
            f"Tokens produced: {row['num_tokens']}",
            "",
        ]

    lines += ["## Summary across all documents", "", "| File | Raw chars | Clean chars | Tokens |", "|---|---|---|---|"]
    for row in rows:
        lines.append(f"| {row['file']} | {row['raw_chars']} | {row['clean_chars']} | {row['num_tokens']} |")

    total_raw = sum(r["raw_chars"] for r in rows)
    total_clean = sum(r["clean_chars"] for r in rows)
    total_tokens = sum(r["num_tokens"] for r in rows)
    lines += [
        "",
        f"**Totals:** {len(rows)} documents, {total_raw} raw chars -> {total_clean} clean chars "
        f"({total_raw - total_clean} chars removed by cleaning), {total_tokens} tokens generated.",
    ]

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
