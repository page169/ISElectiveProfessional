# Preprocessing Before/After Report

Checkpoint 1 evidence: text cleaning, normalization, and tokenization
applied to the TPC Student Handbook raw dataset (41 documents, extracted
from the instructor-provided handbook PDF).

## Sample before/after (first 3 documents)

### TPC HANDBOOK.txt

**Raw (240957 chars):**
```
TPC STUDENT HANDBOOK v.04 \nPREFACE \nThis handbook will highlight not only the academic policies of the school but also the history, vision, mission, goals, objectives, philosophy, ...
```

**Cleaned (235556 chars):**
```
TPC STUDENT HANDBOOK v.04\nPREFACE\nThis handbook will highlight not only the academic policies of the school but also the history, vision, mission, goals, objectives, philosophy, th...
```

Tokens produced: 37904

## Summary across all documents

| File | Raw chars | Clean chars | Tokens |
|---|---|---|---|
| TPC HANDBOOK.txt | 240957 | 235556 | 37904 |

**Totals:** 1 documents, 240957 raw chars -> 235556 clean chars (5401 chars removed by cleaning), 37904 tokens generated.