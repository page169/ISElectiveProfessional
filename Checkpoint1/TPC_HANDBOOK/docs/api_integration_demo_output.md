# API Integration Demo — Output Log

Embedding model: `sentence-transformers/all-MiniLM-L6-v2`  |  Retrieval index: FAISS (cosine)

System prompt used (Prompts 1-3 combined, see docs/prompt_engineering.md):
```
You are the TPC Handbook Assistant, an assistant for the Talibon
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
```

## Query (grounded): "What happens if I fail a subject twice?"

Retrieved passages: 03_handbook_section.txt (0.2759), 08_handbook_section.txt (0.2535)

**Answer source:** offline mock (deterministic, grounded in retrieved passage only)

```
Policy Summary: 2nd Year First Semester  Course  Code 	Descriptive Title 	Units	Hours Per Week	Pre/Co Requisite  			Lecture	Lab 	 GE  ELECTIVE  2 	Indigenous Creative Crafts 	3 	3 	0 	GE  ELECTIVE  1  PATHFIT 3 	Individual and Dual Sports 	2 	2 	0 	PATHFIT 2  	TOTAL 	23 	23 	0 	 2nd Year, Second...
Conditions/Exceptions: See the full section for specific conditions -- not fully summarized in this offline demo mock.
Source: Unknown section (03_handbook_section.txt)
```

## Query (out_of_scope): "What is the current US dollar to Philippine peso exchange rate?"

Retrieved passages: 04_handbook_section.txt (0.1816), 05_handbook_section.txt (0.1691)

**Answer source:** offline mock (deterministic, grounded in retrieved passage only)

```
Policy Summary: 2nd Year First Semester  Course  Code 	Descriptive Title 	Units	Hours Per Week	Pre/Co Requisite  			Lecture	Lab 	 FILIPINO 3 	Mabisa at Masining sa  Pagpapahayag 	3 	3 	0 	FILIPINO 2  PATHFIT 3 	Individual and Dual Sports 	2 	2 	0 	PATHFIT 2  	TOTAL 	20 	20 	0 	 2nd Year, Second ...
Conditions/Exceptions: See the full section for specific conditions -- not fully summarized in this offline demo mock.
Source: Unknown section (04_handbook_section.txt)
```

## Query (excluded_content): "How many units is the OJT/Practicum course worth?"

Retrieved passages: 05_handbook_section.txt (0.4472), 06_handbook_section.txt (0.4039)

**Answer source:** offline mock (deterministic, grounded in retrieved passage only)

```
The curriculum/Prospectus tables (course units, contact hours, sequencing) are not yet part of this assistant's verified knowledge base -- see docs/reflection.md for why they were excluded from Checkpoint 1. Please check the official Prospectus or the Registrar's Office directly for exact unit values.
```

