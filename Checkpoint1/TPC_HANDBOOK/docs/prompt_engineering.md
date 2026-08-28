# Prompt Engineering Document

**Project:** TPC Handbook Assistant — RAG Q&A over the Talibon Polytechnic
College Student Handbook
**Checkpoint 2 Deliverable 6**

Each prompt below is a system/instruction prompt used to constrain the
Chat Completion model's behavior when answering questions grounded in
retrieved handbook passages. Every prompt states its purpose and includes
one example showing how it prevents hallucination or an off-topic/unsafe
answer. All four prompts are implemented and exercised in
`src/api_integration_demo.py`.

---

## Prompt 1 — Grounded Answering (anti-hallucination)

**Purpose:** Force the model to answer *only* from the retrieved handbook
passages passed in as context, and to explicitly say when the handbook
doesn't cover something, instead of inventing a policy from general
knowledge of "how colleges usually work."

```
You are the TPC Handbook Assistant, an assistant for the Talibon
Polytechnic College Student Handbook. You must answer ONLY using the
CONTEXT passages provided below. Do not use any outside knowledge about
how colleges or universities "typically" handle a policy, even if you
believe it is a reasonable guess.

If the answer is not contained in the CONTEXT, respond exactly with:
"I don't have that in the TPC Student Handbook knowledge base." Do not
guess or generalize from other institutions' policies.

Always mention which Article/Chapter/Section your answer came from.

CONTEXT:
{retrieved_passages}
```

**Example — hallucination prevented:**
User asks: *"Is there a shuttle service between campuses?"* No section of
the handbook currently in the knowledge base discusses campus
transportation. A model without this prompt might answer confidently
based on general assumptions about what colleges commonly provide. With
this prompt, since no shuttle-related passage is retrieved/passed in as
CONTEXT, the model is constrained to respond with the fixed "I don't
have that in the TPC Student Handbook knowledge base" line instead of
inventing a plausible-sounding but unverified policy.

---

## Prompt 2 — Out-of-Scope / Excluded-Content Refusal

**Purpose:** Explicitly decline questions about the course curriculum
"Prospectus" tables (units, hours, course sequencing), which were
deliberately excluded from the Checkpoint 1 dataset because table data
extracted via plain-text PDF extraction is unreliable — see
`docs/reflection.md`. This prevents the model from fabricating a
course-unit answer from a nearby but unrelated passage.

```
If the user's question is specifically about course curriculum details
(units, contact hours, course codes, prerequisites, or year-level
sequencing), do NOT attempt to answer even if a loosely related passage
was retrieved. Respond that the curriculum/Prospectus tables are not yet
part of this assistant's verified knowledge base, and recommend checking
the official Prospectus or the Registrar's Office directly.

Otherwise, answer normally using the CONTEXT and Prompt 1's grounding
rules.
```

**Example — off-topic/unsafe answer prevented:**
User asks: *"How many units is the OJT/Practicum course worth?"* The
retrieved context (Article IX, On-the-Job Training policy) discusses OJT
*policy* — hours of duty, conduct, evaluation — but not its specific
unit-credit value, which only lives in the excluded Prospectus tables.
With this prompt, the model recognizes the question is asking for a
curriculum/unit detail and declines rather than guessing a unit count
from the OJT policy text it does have.

---

## Prompt 3 — Structured Answer Format

**Purpose:** Keep policy answers consistent and easy to verify — a
one-line answer, the specific handbook citation, and any conditions —
rather than a free-form paragraph that's harder to check against the
source during grading/QA of a legal/policy document.

```
When you do answer from CONTEXT, structure your response as:

Policy Summary: <1-2 sentence plain-language answer>
Conditions/Exceptions: <1-2 sentences, or "None specifically noted in this section.">
Source: <Article/Chapter/Section label and filename of the retrieved document>

Keep the whole answer under 120 words.
```

**Example — prevents vague/unverifiable answers:**
User asks: *"What happens if I fail a subject twice?"* Without
structure, a model might blend the retention rule, the probation
process, and possible dismissal grounds into one vague paragraph that's
hard to check line-by-line. With this prompt, the answer is forced into
checkable fields, e.g. "Source: Article II, Chapter 9: Retention
Policies (12_chapter-9-retention-policies.txt)" — making it easy during
grading or a real student dispute to open that section and confirm the
answer matches the actual written policy.

---

## Prompt 4 — Multi-Turn Follow-Up Handling

**Purpose:** Prevent the model from losing grounding when a student asks
a short follow-up that only makes sense with conversation history (used
going into Checkpoint 3's conversational memory feature) — important in
a handbook assistant because students often ask a chain of related
questions ("what's the policy," then "what if I already did that,"
then "who do I file it with").

```
The user may ask short follow-up questions that refer back to the
policy or office discussed in the previous turn (e.g., "who approves
that?" after asking about a leave-of-absence policy). Resolve these
references using the CONVERSATION HISTORY provided, then apply Prompt
1's grounding rule using CONTEXT retrieved for the *resolved* question,
not the literal follow-up text.

If the previous turn's topic can't be determined from CONVERSATION
HISTORY, ask the user to clarify which policy or office they mean
instead of guessing.

CONVERSATION HISTORY:
{conversation_history}
```

**Example — prevents topic-drift hallucination:**
Turn 1: *"What's the process for requesting a leave of absence?"* →
answer grounded in the Academic Information chapter. Turn 2: *"Who do I
submit that to?"* Without this prompt, "that" is ambiguous and a naive
RAG call might re-retrieve using only the literal string "who do I
submit that to," pulling an unrelated passage (e.g. about scholarship
applications). With this prompt, the model resolves "that" to
"leave-of-absence request" using history first, so retrieval and the
final answer both stay grounded in the correct section.
