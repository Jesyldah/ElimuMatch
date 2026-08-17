# Intervention Matrix Playbook — Elimu Match

## Purpose
Translate analytics (risk personas + signals) into **sponsor/school actions**.
Sponsors should not see the matrix — they see a simple pay flow.
Ops / schools use this matrix to decide *what* to offer each student.

## Priority scale
| Score | Meaning |
|---|---|
| 0 | Not indicated |
| 1 | Optional |
| 2 | Recommended |
| 3 | Priority |

## Persona × Intervention (policy)

### Health-Constrained
- **Health & Attendance** (Priority) — Medical vouchers + attendance follow-up (~KES 5,000)
- **Psychosocial Counseling** (Recommended) — Counselor hours / peer support (~KES 4,000)
- **School Fee Support** (Recommended) — Pay term fees / bursary (~KES 15,000)
- **Transport / Boarding** (Optional) — Subsidize commute or boarding (~KES 6,000)
- **Academic Tutoring** (Optional) — Fund remedial / catch-up classes (~KES 8,000)
- **Digital Access Kit** (Optional) — Shared device / data bundle (~KES 7,000)

### Academic Strugglers
- **Academic Tutoring** (Priority) — Fund remedial / catch-up classes (~KES 8,000)
- **School Fee Support** (Recommended) — Pay term fees / bursary (~KES 15,000)
- **Digital Access Kit** (Recommended) — Shared device / data bundle (~KES 7,000)
- **Transport / Boarding** (Optional) — Subsidize commute or boarding (~KES 6,000)
- **Health & Attendance** (Optional) — Medical vouchers + attendance follow-up (~KES 5,000)
- **Psychosocial Counseling** (Optional) — Counselor hours / peer support (~KES 4,000)

### Stable Achievers
- **STEM Enrichment** (Priority) — Clubs, mentoring, competitions (~KES 3,000)
- **Digital Access Kit** (Optional) — Shared device / data bundle (~KES 7,000)

## How a student is assigned
1. Start from persona row in the matrix
2. Add signal boosts (SES, cash-flow, failures, commute, health, digital)
3. Weight by dropout risk
4. Rank interventions → primary + secondary recommendation

## Cohort application (primary matches)

- STEM Enrichment: **339** students
- School Fee Support: **282** students
- Academic Tutoring: **222** students
- Health & Attendance: **148** students
- Digital Access Kit: **9** students

## Sponsor experience
Students whose **primary** intervention is School Fee Support appear on `sponsor_portal.html`.
Other interventions are handed to school or partner owners on the Support Hub (owner, next step, handoff status), with the school worklist as the handoff artifact. Progress means listed for review, not completed tutoring or clinic visits.
