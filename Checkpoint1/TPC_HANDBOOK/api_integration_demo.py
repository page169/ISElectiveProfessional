# -*- coding: utf-8 -*-
"""
Checkpoint 2 - API Integration Demo
TPC Handbook Assistant: Student Handbook Q&A Assistant

Deliverable 7: a working script that sends the Checkpoint 2 prompts
(docs/prompt_engineering.md) to a Chat Completion API along with
retrieved context, and returns a grounded response.

Flow per query:
  1. Embed the query and retrieve top-k passages from the FAISS cosine
     index built in vector_store.py (Deliverable 8).
  2. Build a system prompt from Prompts 1-3 (grounding + excluded-content
     refusal + structured format) in docs/prompt_engineering.md.
  3. Call the OpenAI Chat Completions API with the system prompt +
     retrieved context + user question.
  4. Print/save the grounded response.

A note on this environment
---------------------------
This script calls the real OpenAI Chat Completions API exactly as it
should be called in production (see `call_openai_chat`). This sandbox's
network allowlist does not include api.openai.com, and no API key is
configured here, so `call_openai_chat` will raise -- this is expected
and is caught on purpose. When that happens, the script falls back to
`mock_grounded_answer`, which deterministically builds a structured
answer directly from the retrieved passage's own text (no generation, no
invented policy language) purely so the retrieval -> prompting -> answer
pipeline is demonstrably runnable end-to-end without external network
access. Run this file with a real OPENAI_API_KEY set and internet access
to exercise the actual Chat Completion call.
"""

import os
import re

from vector_store import build_indexes, search
from embeddings_util import embed_corpus

DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
if not os.path.exists(DOCS_DIR):
    os.makedirs(DOCS_DIR)
REPORT_PATH = os.path.join(DOCS_DIR, "api_integration_demo_output.md")

SYSTEM_PROMPT = """You are the TPC Handbook Assistant, an assistant for the Talibon
Polytechnic College Student Handbook. You must answer ONLY using the
CONTEXT passages provided below. Do not use any outside knowledge about
how colleges or universities "typically" handle a policy, even if you
believe it is a reasonable guess.

If the answer is not contained in the CONTEXT, respond exactly with:
"I don't have that in the TPC Student Handbook knowledge base." Do not
guess or generalize from other institutions' policies.

If the user's question is specifically about course curriculum details
(units, contact hours, course codes, prerequisites, or year-level
sequencing), do NOT attempt to answer even if a loosely related passage
was retrieved. Respond that the curriculum/Prospectus tables are not yet
part of this assistant's verified knowledge base, and recommend checking
the official Prospectus or the Registrar's Office directly.

Otherwise, structure your response as:
Policy Summary: <1-2 sentence plain-language answer>
Conditions/Exceptions: <1-2 sentences, or "None specifically noted in this section.">
Source: <Article/Chapter/Section label and filename of the retrieved document>

Keep the whole answer under 120 words.
"""

# Queries chosen to demonstrate: (1) normal grounded answer,
# (2) knowledge-base gap -> refusal, (3) excluded-content (curriculum units) -> scoped refusal
DEMO_QUERIES = [
    {"query": "What happens if I fail a subject twice?", "type": "grounded"},
    {"query": "What is the current US dollar to Philippine peso exchange rate?", "type": "out_of_scope"},
    {"query": "How many units is the OJT/Practicum course worth?", "type": "excluded_content"},
]

CURRICULUM_KEYWORDS = ["units", "unit", "contact hours", "course code", "prerequisite", "prospectus"]


def retrieve_context(query, embed_fn, filenames, texts, indexes, k=2):
    q_vec = embed_fn([query])
    scores, ids = search(indexes, "cosine", q_vec, k=k)
    passages = [(filenames[i], texts[i], float(s)) for s, i in zip(scores, ids)]
    return passages


def call_openai_chat(system_prompt, user_prompt):
    """
    Real production call. Requires `pip install openai` and a valid
    OPENAI_API_KEY environment variable with network access to
    api.openai.com. Left exactly as it should be called in deployment.
    """
    from openai import OpenAI  # local import so the rest of the demo runs without the package installed

    client = OpenAI()  # reads OPENAI_API_KEY from environment
    response = client.chat.completions.create(
        model="gpt-4.0-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=250,
    )
    return response.choices[0].message.content


def extract_source_label(clean_text):
    """Pulls the 'Section: Article X - Chapter Y: Title' header line straight
    out of a processed document -- used only by the offline mock so the
    fallback answer is provably grounded in the retrieved passage's own
    citation, not invented."""
    m = re.search(r"Section:\s*(.+)", clean_text)
    return m.group(1).strip() if m else "Unknown section"


def first_meaningful_paragraph(clean_text, min_len=60):
    """Grabs the first substantial paragraph after the header block, to use
    as a plain-language summary snippet in the offline mock."""
    body = re.sub(r"^TPC STUDENT HANDBOOK\nSection:.*\n\n", "", clean_text)
    for para in body.split("\n\n"):
        para = para.strip().replace("\n", " ")
        if len(para) >= min_len:
            return para[:280] + ("..." if len(para) > 280 else "")
    return body[:280]


def mock_grounded_answer(query, passages, query_type, fname):
    """Offline fallback -- see module docstring. Deterministically applies
    the same system-prompt rules without calling an external API."""
    if query_type == "excluded_content" or any(k in query.lower() for k in CURRICULUM_KEYWORDS):
        return (
            "The curriculum/Prospectus tables (course units, contact hours, sequencing) are not "
            "yet part of this assistant's verified knowledge base -- see docs/reflection.md for "
            "why they were excluded from Checkpoint 1. Please check the official Prospectus or the "
            "Registrar's Office directly for exact unit values."
        )

    if not passages or passages[0][2] < 0.1:  # similarity too low -> treat as not covered
        return "I don't have that in the TPC Student Handbook knowledge base."

    top_fname, top_text, top_score = passages[0]
    source_label = extract_source_label(top_text)
    snippet = first_meaningful_paragraph(top_text)
    return (
        f"Policy Summary: {snippet}\n"
        f"Conditions/Exceptions: See the full section for specific conditions -- "
        f"not fully summarized in this offline demo mock.\n"
        f"Source: {source_label} ({top_fname})"
    )


def main():
    filenames, texts, vectors, embed_fn, model_name = embed_corpus()
    indexes = build_indexes(vectors)
    print(f"Loaded {len(filenames)} documents, embedding model: {model_name}\n")

    report_lines = [
        "# API Integration Demo — Output Log",
        "",
        f"Embedding model: `{model_name}`  |  Retrieval index: FAISS (cosine)",
        "",
        "System prompt used (Prompts 1-3 combined, see docs/prompt_engineering.md):",
        "```",
        SYSTEM_PROMPT.strip(),
        "```",
        "",
    ]

    for item in DEMO_QUERIES:
        query, qtype = item["query"], item["type"]
        passages = retrieve_context(query, embed_fn, filenames, texts, indexes, k=2)

        print(f"Query ({qtype}): {query}")
        for fname, _, score in passages:
            print(f"  retrieved: {fname}  (cosine={score:.4f})")

        try:
            user_prompt = (
                f"CONTEXT:\n" + "\n---\n".join(t for _, t, _ in passages) + f"\n\nQUESTION: {query}"
            )
            answer = call_openai_chat(SYSTEM_PROMPT, user_prompt)
            source = "OpenAI Chat Completions API"
        except Exception as e:
            print(f"  [info] OpenAI API unavailable in this environment ({type(e).__name__}); using offline mock.")
            top_fname = passages[0][0] if passages else None
            answer = mock_grounded_answer(query, passages, qtype, top_fname)
            source = "offline mock (deterministic, grounded in retrieved passage only)"

        print(f"  answer source: {source}")
        print(f"  answer:\n{answer}\n")

        report_lines += [
            f"## Query ({qtype}): \"{query}\"",
            "",
            "Retrieved passages: " + ", ".join(f"{fname} ({score:.4f})" for fname, _, score in passages),
            "",
            f"**Answer source:** {source}",
            "",
            "```",
            answer,
            "```",
            "",
        ]

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")
    print(f"Full output log written to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
