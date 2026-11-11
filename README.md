# Unemployment and Mental Health in Canada, 2002–2022

**Question:** Is the unemployment rate associated with mental health outcomes in Canada, and does the association vary by gender and province?

**Answer:** No. After controlling for age, gender, province and survey year, unemployment has no detectable association with past-year depression (β = −0.15, p = 0.46), and the effect does not differ by gender (p = 0.67) or province (p = 0.20). The raw positive link was confounded by age. The standout finding is 2022: fair or poor self-rated mental health among women aged 15–24 rose from 10% (2012) to 29% (2022), while unemployment fell.

## Data
Statistics Canada (not included in this repo because of file size; download the CSVs into the project root):
- [Table 13-10-0465](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1310046501): mental health indicators by age group and gender (2002, 2012, 2022)
- [Table 14-10-0017](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410001701): labour force characteristics, monthly (unemployment rate)

## Method
1. **Cleaning (pandas):** kept Percent rows and the unemployment rate; standardized gender and age-group labels; converted text dates to numeric years; averaged monthly unemployment into annual rates; removed overlapping totals so no one is counted twice; audited the merge (unique keys, unmatched rows).
2. **Missing data:** values suppressed by Statistics Canada (F, x) dropped (complete-case analysis), leaving 87 of 240 province × age × gender × year groups; "use with caution" (E) values kept.
3. **Models (statsmodels, HC3 robust standard errors):**
   - Model 1: simple linear regression (β = +0.16, p = 0.10)
   - Model 2: multiple regression with age, gender, province and year controls (β = −0.15, p = 0.46)
   - Model 3: interaction terms for gender and province (joint tests not significant)
4. **Robustness:** dropping the 65+ group, an alternative outcome (fair or poor mental health), and province-level fixed effects all gave the same conclusion.

## Key findings
| Finding | Result |
|---|---|
| Raw correlation (depression vs unemployment) | r = 0.16 |
| Within ages 15–24 | r = −0.62 (age confounding / Simpson's paradox) |
| Variance explained, Model 1 → Model 2 | R² 0.03 → 0.71 |
| Women 15–24, fair or poor mental health | 10.1% → 29.0% (2012 → 2022), p < 0.001 |
| National unemployment | 7.7% → 5.3% (2002 → 2022) |

**Limitations:** group-level data (no conclusions about individuals), only 87 usable groups, three survey years, and association rather than causation. Next step: individual-level CCHS microdata.

## Repository contents
| File | Description |
|---|---|
| `final_analysis.ipynb` | Final analysis notebook: cleaning, models, robustness, province analysis, 2022 findings |
| `exploratory_analysis.ipynb` | Earlier exploratory notebook: indicator screening and first models |
| `results/regressions.py` | Standalone script that rebuilds the merged dataset and runs the models |
| `results/merged_depression_12m.csv` | Analysis dataset (87 groups) |
| `results/unemp_sub.csv` | Unemployment rate subset for 2002, 2012, 2022 |
| `results/tableau/` | Tableau-ready CSVs used in the dashboard |
| `tableau/Tableau_Story_Unemployment_Mental_Health.pdf` | PDF export of the Tableau story |

## Tableau
Interactive story (5 views: young women 2022, provinces 2002 vs 2022, age confounding, adding controls, province slopes):
**[View on Tableau Public](TABLEAU_PUBLIC_LINK)** · [PDF version](tableau/Tableau_Story_Unemployment_Mental_Health.pdf)

## Tools
Python (pandas, statsmodels, matplotlib, seaborn), Jupyter, Tableau, Git
