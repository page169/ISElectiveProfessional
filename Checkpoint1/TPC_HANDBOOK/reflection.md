# Checkpoint 1 Reflection

**Project:** TPC Handbook Assistant — a RAG Q&A assistant over the Talibon
Polytechnic College Student Handbook

## What was messy about the data

The raw dataset came from a real, instructor-provided 202-page PDF (`TPC
Student Handbook v.04`), extracted with `pdftotext -layout`. Unlike a
hand-written or synthetic dataset, this text carried real-world PDF export
artifacts:

- **Running headers and page numbers** ("TPC STUDENT HANDBOOK v.04" and a
  bare page number) repeated on every single page and had to be stripped
  out programmatically, or they would have polluted every chunk and biased
  retrieval toward matching the header text instead of the actual content.
- **Form-feed characters** (`\f`) marking page breaks, which show up as
  stray control characters in the raw text and needed to be removed before
  any further cleaning.
- **Broken word hyphenation from layout wrapping** — for example "mandates"
  extracted as "man dates" because of how the PDF's text layer wrapped a
  justified paragraph. This kind of artifact is much harder to catch with
  a generic regex than the deliberate spacing issues from a synthetic
  dataset, since it looks like a legitimate two-word phrase.
- **Mixed document structure** — most of the handbook is narrative policy
  text organized into Articles and Chapters with numbered Sections, but a
  few pages (e.g. the Grading System table, and the multi-year course
  curriculum "Prospectus" tables) are dense tabular data. Tables extracted
  by `pdftotext -layout` come out as loosely-aligned columns of numbers and
  text rather than a clean table structure.
- **A genuinely huge document** — 202 pages is far larger than a toy
  dataset, so a real decision had to be made about *chunk granularity*
  rather than just "clean the whole thing." Splitting arbitrarily by
  character count would have cut sentences and even numbered sub-clauses
  (e.g., disciplinary sanction lists) in half.

## How it was handled

- Used the handbook's own structure (Article → Chapter → Section) as the
  chunk boundary instead of a fixed character/token window. I located every
  `ARTICLE`/`Chapter` heading in the extracted text and grep'd their line
  numbers, then split the document into 41 sections along those natural
  boundaries — this keeps every chunk topically coherent (e.g. "Grading
  System" is its own chunk, "Norms of Conduct" is its own chunk) which
  should make retrieval far more precise than arbitrary chunking would.
- Wrote a regex-based cleaning pass that strips the repeated header line
  and bare page numbers, removes form-feed characters, and collapses
  excess blank lines left behind after that removal.
- Deliberately **excluded** the multi-hundred-page course "Prospectus"
  curriculum tables from the knowledge base for this checkpoint. Table
  data extracted via `pdftotext -layout` is not reliable prose for a
  chatbot to quote from, and a wrongly-reconstructed row (e.g. matching a
  course code to the wrong units/hours) would be a much worse hallucination
  risk than the assistant simply not covering that section yet. This is a
  known scope limitation to revisit in a later checkpoint, ideally with
  `pdfplumber`'s table extraction instead of plain text extraction.
- Left the "man dates" → "mandates" -style hyphenation artifacts as a known,
  documented limitation rather than trying to auto-correct them, since a
  general spell-correction pass risks silently changing the meaning of
  actual policy language — which would be worse than an obvious, spottable
  typo in a legal/policy document.

The main lesson: real institutional PDFs bring structural and extraction
noise that a synthetic dataset never has to deal with, and the single
highest-leverage decision in this checkpoint wasn't the character-level
cleaning regex — it was choosing to chunk by the document's own Article/
Chapter structure instead of by a fixed size, which should pay off directly
in retrieval quality in Checkpoint 2.
