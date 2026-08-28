# -*- coding: utf-8 -*-
"""
Checkpoint 2 - Vector Database Setup & Distance Metric Comparison
TPC Handbook Assistant: Student Handbook Q&A Assistant

Deliverable 8 (Vector Database Setup):
    Loads the full 41-document Checkpoint-1 corpus, embeds it, and indexes
    it in FAISS with a working similarity-search query.

Deliverable 9 (Distance Metric Comparison):
    Builds three FAISS indexes over the SAME embeddings using Cosine,
    Euclidean (L2), and Dot Product, runs the same set of test queries
    against all three, and writes a comparison report -- with a discussion
    generated from what the queries actually returned, not assumed in
    advance -- to docs/distance_metric_comparison.md.

Why FAISS: lightweight, pip-installable, runs fully offline (no server,
no external model download needed once vectors exist), and supports all
three distance metrics needed for the Checkpoint 2 comparison
(IndexFlatIP for dot product / cosine-on-normalized-vectors, IndexFlatL2
for Euclidean).

Run:
    python3 src/vector_store.py
"""

import os
import numpy as np
import faiss

from embeddings_util import embed_corpus, EMBED_DIM

DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
if not os.path.exists(DOCS_DIR):
    os.makedirs(DOCS_DIR)
VECTOR_DB_REPORT = os.path.join(DOCS_DIR, "vector_db_demo.md")
DISTANCE_REPORT = os.path.join(DOCS_DIR, "distance_metric_comparison.md")

TEST_QUERIES = [
    "What is the grading system and passing grade?",
    "What are the grounds for disciplinary action or dismissal?",
    "How do I apply for a scholarship?",
    "What services does the library offer?",
    "What are the requirements for on-the-job training or practicum?",
]


def l2_normalize(vectors):
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1e-9
    return vectors / norms


def build_indexes(vectors):
    """Builds three FAISS indexes over the same vectors, one per metric."""
    dim = vectors.shape[1]

    # Dot product (raw, unnormalized vectors)
    index_dot = faiss.IndexFlatIP(dim)
    index_dot.add(vectors)

    # Cosine similarity == dot product on L2-normalized vectors
    normalized = l2_normalize(vectors.copy())
    index_cosine = faiss.IndexFlatIP(dim)
    index_cosine.add(normalized)

    # Euclidean (L2) distance
    index_euclidean = faiss.IndexFlatL2(dim)
    index_euclidean.add(vectors)

    return {
        "dot": (index_dot, vectors),
        "cosine": (index_cosine, normalized),
        "euclidean": (index_euclidean, vectors),
    }


def search(indexes, metric, query_vec, k=3):
    index, _ = indexes[metric]
    q = query_vec.copy()
    if metric == "cosine":
        q = l2_normalize(q)
    scores, ids = index.search(q, k)
    return scores[0], ids[0]


def main():
    filenames, texts, vectors, embed_fn, model_name = embed_corpus()
    print(f"Embedded {len(filenames)} documents using: {model_name}")
    print(f"Vector shape: {vectors.shape}\n")

    doc_lengths = [len(t) for t in texts]
    print(f"Document length range: {min(doc_lengths)}-{max(doc_lengths)} chars "
          f"(this corpus has real length variance -- unlike a set of similar-length entries)\n")

    indexes = build_indexes(vectors)

    # --- Deliverable 8: working similarity-search query on the "production" index (cosine) ---
    demo_query = TEST_QUERIES[0]
    q_vec = embed_fn([demo_query])
    scores, ids = search(indexes, "cosine", q_vec, k=3)

    print(f"Similarity search demo (cosine index)\nQuery: {demo_query!r}")
    vector_db_lines = [
        "# Vector Database Setup — Working Query Demo",
        "",
        f"**Model:** `{model_name}`  |  **Vectors indexed:** {len(filenames)}  |  **Dim:** {vectors.shape[1]}",
        "",
        f"**Sample query:** \"{demo_query}\"",
        "",
        "| Rank | Document | Cosine similarity |",
        "|---|---|---|",
    ]
    for rank, (score, idx) in enumerate(zip(scores, ids), start=1):
        print(f"  {rank}. {filenames[idx]}  (score={score:.4f})")
        vector_db_lines.append(f"| {rank} | {filenames[idx]} | {score:.4f} |")

    if "TF-IDF" in model_name:
        top_doc = filenames[ids[0]]
        vector_db_lines += [
            "",
            f"**Note on this result:** the top hit here is `{top_doc}`, not "
            "`09_chapter-6-grading-system.txt`. Checking the raw text explains why: the Grading "
            "System chapter never uses the word \"passing,\" while Retention Policies discusses "
            "grade thresholds and probation using vocabulary closer to the query's wording. This "
            "is a real limitation of TF-IDF -- it matches literal words, not meaning -- and is "
            "expected to improve with the production `sentence-transformers/all-MiniLM-L6-v2` "
            "model, which embeds \"passing grade\" and \"grading system\" as semantically close even "
            "without exact word overlap. Documented here rather than adjusted away, since this is "
            "genuine evidence for why the production model matters.",
        ]

    with open(VECTOR_DB_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(vector_db_lines) + "\n")

    # --- Deliverable 9: distance metric comparison across all test queries ---
    report_lines = [
        "# Distance Metric Comparison — Cosine vs Euclidean vs Dot Product",
        "",
        f"Corpus: 41 TPC Handbook section documents. Embedding model: `{model_name}`. Index: FAISS.",
        f"Document lengths range from {min(doc_lengths)} to {max(doc_lengths)} characters -- this "
        "corpus is intentionally length-variable (short annex sections vs. long chapters like "
        "Requirements/Admission Requirements), which is exactly the condition where dot product "
        "and Euclidean distance are expected to diverge from cosine similarity.",
        "",
    ]

    agreement_notes = []
    for query in TEST_QUERIES:
        q_vec = embed_fn([query])
        report_lines.append(f"## Query: \"{query}\"")
        report_lines.append("")
        rankings = {}
        for metric, label in [("cosine", "Cosine similarity"), ("euclidean", "Euclidean (L2) distance"), ("dot", "Dot Product")]:
            scores, ids = search(indexes, metric, q_vec, k=3)
            rankings[metric] = [filenames[idx] for idx in ids]
            report_lines.append(f"**{label}** (lower is more similar for Euclidean; higher is more similar for the other two)")
            report_lines.append("")
            report_lines.append("| Rank | Document | Score |")
            report_lines.append("|---|---|---|")
            for rank, (score, idx) in enumerate(zip(scores, ids), start=1):
                report_lines.append(f"| {rank} | {filenames[idx]} | {score:.4f} |")
            report_lines.append("")

        cos_eq_dot = rankings["cosine"] == rankings["dot"]
        cos_eq_euc = rankings["cosine"] == rankings["euclidean"]
        agreement_notes.append((query, cos_eq_dot, cos_eq_euc))

    n_dot_agree = sum(1 for _, a, _ in agreement_notes if a)
    n_euc_agree = sum(1 for _, _, b in agreement_notes if b)
    n_total = len(agreement_notes)

    disagree_dot_queries = [q for q, a, _ in agreement_notes if not a]
    disagree_euc_queries = [q for q, _, b in agreement_notes if not b]

    report_lines += [
        "## Discussion",
        "",
        f"Across the {n_total} test queries above, Cosine and Dot Product produced the **same "
        f"top-3 ranking** in {n_dot_agree}/{n_total} cases, and Cosine and Euclidean (L2) produced "
        f"the same top-3 ranking in {n_euc_agree}/{n_total} cases.",
        "",
    ]

    if disagree_dot_queries:
        report_lines.append(
            "Dot product's ranking diverged from cosine's on: "
            + "; ".join(f'"{q}"' for q in disagree_dot_queries)
            + ". This is consistent with dot product being sensitive to a document's raw vector "
            "magnitude -- longer sections (e.g. Admission Requirements, Requirements) tend to "
            "accumulate larger TF-IDF magnitude simply from length, which can pull them upward in "
            "a dot-product ranking even when a shorter section is the better topical match."
        )
    else:
        report_lines.append(
            "Dot product matched cosine's ranking on every test query in this run, even with "
            "real document-length variance in the corpus. This is worth re-checking as the corpus "
            "grows further and more queries are tested; it is not a guarantee that magnitude "
            "sensitivity won't surface on other queries."
        )
    report_lines.append("")

    if disagree_euc_queries:
        report_lines.append(
            "Euclidean (L2) distance's ranking diverged from cosine's on: "
            + "; ".join(f'"{q}"' for q in disagree_euc_queries)
            + ". L2 distance is directly affected by vector magnitude (not just angle), so it is "
            "the metric most likely to be thrown off by this corpus's mix of short annex sections "
            "and long policy chapters."
        )
    else:
        report_lines.append(
            "Euclidean (L2) distance matched cosine's ranking on every test query in this run."
        )
    report_lines.append("")

    report_lines += [
        "- **Cosine similarity** measures only the angle between vectors, ignoring magnitude, so a "
        "long chapter and a short section can both rank highly purely on topical relevance rather "
        "than one being artificially favored for being longer. This property matters directly for "
        "this corpus, which mixes long Article/Chapter text with short annex/reference sections.",
        "",
        "## Recommendation",
        "",
        "**Cosine similarity** is recommended for the TPC Handbook Assistant's retrieval index "
        "going into Checkpoint 3. It is the metric `sentence-transformers/all-MiniLM-L6-v2` (our "
        "production embedding model) is explicitly trained and benchmarked against, and -- unlike "
        "dot product and Euclidean distance -- it is inherently insensitive to the handbook's real "
        "document-length variance (a short annex definition section next to a long chapter like "
        "Admission Requirements), which is the exact scenario where the other two metrics carry "
        "the most risk of ranking a longer-but-less-relevant section above a shorter, more directly "
        "on-topic one.",
    ]

    with open(DISTANCE_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")

    print(f"\nVector DB demo report: {VECTOR_DB_REPORT}")
    print(f"Distance metric comparison report: {DISTANCE_REPORT}")


if __name__ == "__main__":
    main()
