# Tableau setup — Elimu Match (Data Exploration)

## Files to connect

| File | Grain | Use for |
|---|---|---|
| `students_exploration.csv` | 1 row per student | Main exploration workbook |
| `schools_summary.csv` | 1 row per school | School comparison dashboards |
| `persona_summary.csv` | 1 row per persona | Persona overview |
| `data_dictionary.csv` | Field list | Documentation / calculated-field notes |

## Suggested Tableau sheets (data exploration section)

1. **Cohort overview** — `Retained` pie/donut; count of students
2. **Retention by SES** — bar: `SES Label` vs AVG(`Retained Flag`) or % retained
3. **Dropout reasons** — filter `Retained` = No; bar of `Dropout Reason`
4. **School comparison** — use `schools_summary.csv` or dual-axis on student table
5. **Distributions** — histograms of `GPA Trend`, `Commute Distance (km)`, `Health Absences (days)` colored by `Retained`
6. **Risk personas** — stacked bar: `Risk Persona` × `Retained`
7. **Fee support map (table)** — filter `Recommended Intervention` = School Fee Support; by `School Name`

## Tips

- Set **Retained Flag** as a measure (0/1) for easy % calculations: `AVG([Retained Flag])`
- Hide or exclude **Model Risk Score (oracle)** from stakeholder views — it is synthetic leakage for ops QA only
- Geographic map: schools are synthetic names without lat/long; use bar charts by school instead unless you add coordinates
- Relationships: if you load multiple tables, relate on `School ID` / `School Name`

## Refresh

```bash
python export_tableau.py
```
