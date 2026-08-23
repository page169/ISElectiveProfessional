# -*- coding: utf-8 -*-
"""
Checkpoint 1 - Embedding Generation Demo
TPC Handbook Assistant: Student Handbook Q&A Assistant (Talibon Polytechnic College)

Model choice
------------
Primary (recommended for the actual application, Checkpoints 2-3):
    sentence-transformers/all-MiniLM-L6-v2  (Hugging Face)
    - Open-source, runs locally/offline once downloaded (no per-call API cost)
    - 384-dimension embeddings: small enough for a fast Chroma/FAISS index
      on a laptop-scale, 41-document knowledge base
    - Strong general-purpose semantic similarity performance for short-to-
      medium, single-topic passages like our handbook chapter/article
      sections
    - Easy drop-in swap for a larger/multilingual model later (e.g.
      paraphrase-multilingual-MiniLM-L12-v2) if the handbook's Filipino-
      language sections (e.g. quoted policy text) need better coverage

Why this matters for RAG: the vector index built in Checkpoint 2 is only as
good as these embeddings, so a model that reliably tells apart "this is
about the grading system" from "this is about disciplinary sanctions" is
worth the small size cost.

A note on this environment
---------------------------
This script is written to run with sentence-transformers exactly as the
project will use it going forward (see `embed_with_sentence_transformers`
below). Downloading model weights from huggingface.co requires outbound
internet access, which this development sandbox restricts. Run this file
as-is on a normal machine with internet access and it will work.

For an executable, fully-offline sanity check *in this sandbox only*, the
script falls back to a TF-IDF vectorizer (scikit-learn) when the
sentence-transformers model can't be downloaded. This fallback is NOT the
embedding technique used in the actual application; it exists purely so we
can demonstrate a working embedding pipeline end-to-end without network
access. This is called out clearly in the printed output and the report.
"""

import os
import json
import numpy as np

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
REPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "embedding_report.md")
SAMPLE_SIZE = 5


def load_sample_docs(n=SAMPLE_SIZE):
    files = sorted(f for f in os.listdir(PROCESSED_DIR) if f.endswith(".json"))[:n]
    docs = []
    for fname in files:
        with open(os.path.join(PROCESSED_DIR, fname), "r", encoding="utf-8") as f:
            data = json.load(f)
        docs.append((data["source_file"], data["clean_text"]))
    return docs


def embed_with_sentence_transformers(texts):
    """
    Production path (Checkpoints 2-3 onward).
    Requires internet access on first run to download the model weights.
    """
    from sentence_transformers import SentenceTransformer  # noqa: local import by design

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(texts, show_progress_bar=False)
    return np.array(embeddings), "sentence-transformers/all-MiniLM-L6-v2"


def embed_with_tfidf_fallback(texts):
    """
    Offline sanity-check path used only because this sandbox has no
    access to huggingface.co. Produces real, inspectable vectors so we
    can verify the pipeline shape (N docs x D dims) and similarity
    behavior end-to-end without internet access.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer

    vectorizer = TfidfVectorizer(max_features=384)  # match dim to MiniLM for a fair comparison
    embeddings = vectorizer.fit_transform(texts).toarray()
    return embeddings, "TF-IDF (offline fallback, sandbox only)"


def cosine_sim(a, b):
    a = a / (np.linalg.norm(a) + 1e-9)
    b = b / (np.linalg.norm(b) + 1e-9)
    return float(np.dot(a, b))


def main():
    docs = load_sample_docs()
    filenames = [d[0] for d in docs]
    texts = [d[1] for d in docs]

    try:
        embeddings, model_used = embed_with_sentence_transformers(texts)
    except Exception as e:
        print(f"[info] sentence-transformers unavailable in this environment ({type(e).__name__}: {e})")
        print("[info] falling back to offline TF-IDF for a runnable local demo.\n")
        embeddings, model_used = embed_with_tfidf_fallback(texts)

    print(f"Model used: {model_used}")
    print(f"Embedding matrix shape: {embeddings.shape}  (docs x dimensions)\n")

    # Show a similarity example: compare doc 0 against every other sample doc
    print(f"Cosine similarity of '{filenames[0]}' vs other sample docs:")
    sims = []
    for i in range(1, len(filenames)):
        sim = cosine_sim(embeddings[0], embeddings[i])
        sims.append((filenames[i], sim))
        print(f"  {filenames[0]} <-> {filenames[i]}: {sim:.4f}")

    write_report(model_used, embeddings.shape, filenames, sims)
    print(f"\nReport written to: {REPORT_PATH}")


def write_report(model_used, shape, filenames, sims):
    lines = [
        "# Embedding Generation Report",
        "",
        "## Model choice",
        "",
        "- **Intended production model:** `sentence-transformers/all-MiniLM-L6-v2` "
        "(Hugging Face, open-source, 384-dim, offline-capable after first download).",
        "- Chosen for a good balance of semantic quality vs. size for a small "
        "(41-document) domain-specific knowledge base, and for zero per-call API cost.",
        "",
        f"- **Model actually used to produce the numbers below in this sandboxed run:** `{model_used}`",
    ]
    if "TF-IDF" in model_used:
        lines += [
            "  - This sandbox has no outbound access to huggingface.co, so the "
            "MiniLM download could not complete here. The TF-IDF fallback exists "
            "solely to demonstrate a working, runnable embedding pipeline in this "
            "environment. `embed_with_sentence_transformers()` in this same file "
            "is the actual code intended for submission/deployment and will run "
            "correctly on any machine with normal internet access.",
        ]

    lines += [
        "",
        f"## Output shape",
        "",
        f"`{shape[0]}` documents embedded into `{shape[1]}`-dimension vectors.",
        "",
        "## Similarity spot-check",
        "",
        f"Cosine similarity between `{filenames[0]}` and the other sampled documents:",
        "",
        "| Compared document | Cosine similarity |",
        "|---|---|",
    ]
    for fname, sim in sims:
        lines.append(f"| {fname} | {sim:.4f} |")

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
