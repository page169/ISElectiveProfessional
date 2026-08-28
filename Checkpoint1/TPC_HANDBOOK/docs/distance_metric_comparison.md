# Distance Metric Comparison — Cosine vs Euclidean vs Dot Product

Corpus: 41 TPC Handbook section documents. Embedding model: `sentence-transformers/all-MiniLM-L6-v2`. Index: FAISS.
Document lengths range from 3450 to 184641 characters -- this corpus is intentionally length-variable (short annex sections vs. long chapters like Requirements/Admission Requirements), which is exactly the condition where dot product and Euclidean distance are expected to diverge from cosine similarity.

## Query: "What is the grading system and passing grade?"

**Cosine similarity** (lower is more similar for Euclidean; higher is more similar for the other two)

| Rank | Document | Score |
|---|---|---|
| 1 | 08_handbook_section.txt | 0.3903 |
| 2 | 09_handbook_section.txt | 0.3837 |
| 3 | 03_handbook_section.txt | 0.3753 |

**Euclidean (L2) distance** (lower is more similar for Euclidean; higher is more similar for the other two)

| Rank | Document | Score |
|---|---|---|
| 1 | 08_handbook_section.txt | 1.2194 |
| 2 | 09_handbook_section.txt | 1.2326 |
| 3 | 03_handbook_section.txt | 1.2494 |

**Dot Product** (lower is more similar for Euclidean; higher is more similar for the other two)

| Rank | Document | Score |
|---|---|---|
| 1 | 08_handbook_section.txt | 0.3903 |
| 2 | 09_handbook_section.txt | 0.3837 |
| 3 | 03_handbook_section.txt | 0.3753 |

## Query: "What are the grounds for disciplinary action or dismissal?"

**Cosine similarity** (lower is more similar for Euclidean; higher is more similar for the other two)

| Rank | Document | Score |
|---|---|---|
| 1 | 07_handbook_section.txt | 0.1924 |
| 2 | 03_handbook_section.txt | 0.1300 |
| 3 | 05_handbook_section.txt | 0.0899 |

**Euclidean (L2) distance** (lower is more similar for Euclidean; higher is more similar for the other two)

| Rank | Document | Score |
|---|---|---|
| 1 | 07_handbook_section.txt | 1.6151 |
| 2 | 03_handbook_section.txt | 1.7400 |
| 3 | 05_handbook_section.txt | 1.8202 |

**Dot Product** (lower is more similar for Euclidean; higher is more similar for the other two)

| Rank | Document | Score |
|---|---|---|
| 1 | 07_handbook_section.txt | 0.1924 |
| 2 | 03_handbook_section.txt | 0.1300 |
| 3 | 05_handbook_section.txt | 0.0899 |

## Query: "How do I apply for a scholarship?"

**Cosine similarity** (lower is more similar for Euclidean; higher is more similar for the other two)

| Rank | Document | Score |
|---|---|---|
| 1 | 01_handbook_section.txt | 0.1423 |
| 2 | 07_handbook_section.txt | 0.1218 |
| 3 | 05_handbook_section.txt | 0.1212 |

**Euclidean (L2) distance** (lower is more similar for Euclidean; higher is more similar for the other two)

| Rank | Document | Score |
|---|---|---|
| 1 | 01_handbook_section.txt | 1.7155 |
| 2 | 07_handbook_section.txt | 1.7564 |
| 3 | 05_handbook_section.txt | 1.7576 |

**Dot Product** (lower is more similar for Euclidean; higher is more similar for the other two)

| Rank | Document | Score |
|---|---|---|
| 1 | 01_handbook_section.txt | 0.1423 |
| 2 | 07_handbook_section.txt | 0.1218 |
| 3 | 05_handbook_section.txt | 0.1212 |

## Query: "What services does the library offer?"

**Cosine similarity** (lower is more similar for Euclidean; higher is more similar for the other two)

| Rank | Document | Score |
|---|---|---|
| 1 | 03_handbook_section.txt | 0.2492 |
| 2 | 09_handbook_section.txt | 0.2330 |
| 3 | 01_handbook_section.txt | 0.2307 |

**Euclidean (L2) distance** (lower is more similar for Euclidean; higher is more similar for the other two)

| Rank | Document | Score |
|---|---|---|
| 1 | 03_handbook_section.txt | 1.5016 |
| 2 | 09_handbook_section.txt | 1.5341 |
| 3 | 01_handbook_section.txt | 1.5385 |

**Dot Product** (lower is more similar for Euclidean; higher is more similar for the other two)

| Rank | Document | Score |
|---|---|---|
| 1 | 03_handbook_section.txt | 0.2492 |
| 2 | 09_handbook_section.txt | 0.2330 |
| 3 | 01_handbook_section.txt | 0.2307 |

## Query: "What are the requirements for on-the-job training or practicum?"

**Cosine similarity** (lower is more similar for Euclidean; higher is more similar for the other two)

| Rank | Document | Score |
|---|---|---|
| 1 | 07_handbook_section.txt | 0.4087 |
| 2 | 06_handbook_section.txt | 0.3996 |
| 3 | 05_handbook_section.txt | 0.3828 |

**Euclidean (L2) distance** (lower is more similar for Euclidean; higher is more similar for the other two)

| Rank | Document | Score |
|---|---|---|
| 1 | 07_handbook_section.txt | 1.1825 |
| 2 | 06_handbook_section.txt | 1.2007 |
| 3 | 05_handbook_section.txt | 1.2343 |

**Dot Product** (lower is more similar for Euclidean; higher is more similar for the other two)

| Rank | Document | Score |
|---|---|---|
| 1 | 07_handbook_section.txt | 0.4087 |
| 2 | 06_handbook_section.txt | 0.3996 |
| 3 | 05_handbook_section.txt | 0.3828 |

## Discussion

Across the 5 test queries above, Cosine and Dot Product produced the **same top-3 ranking** in 5/5 cases, and Cosine and Euclidean (L2) produced the same top-3 ranking in 5/5 cases.

Dot product matched cosine's ranking on every test query in this run, even with real document-length variance in the corpus. This is worth re-checking as the corpus grows further and more queries are tested; it is not a guarantee that magnitude sensitivity won't surface on other queries.

Euclidean (L2) distance matched cosine's ranking on every test query in this run.

- **Cosine similarity** measures only the angle between vectors, ignoring magnitude, so a long chapter and a short section can both rank highly purely on topical relevance rather than one being artificially favored for being longer. This property matters directly for this corpus, which mixes long Article/Chapter text with short annex/reference sections.

## Recommendation

**Cosine similarity** is recommended for the TPC Handbook Assistant's retrieval index going into Checkpoint 3. It is the metric `sentence-transformers/all-MiniLM-L6-v2` (our production embedding model) is explicitly trained and benchmarked against, and -- unlike dot product and Euclidean distance -- it is inherently insensitive to the handbook's real document-length variance (a short annex definition section next to a long chapter like Admission Requirements), which is the exact scenario where the other two metrics carry the most risk of ranking a longer-but-less-relevant section above a shorter, more directly on-topic one.
