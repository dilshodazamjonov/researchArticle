# Checks: `priority_1/full_matrix.csv` and `priority_1/pairwise.csv` against `manuscript.tex`

Revised 2026-09-12 after both files were rewritten. Only defects are listed. Line numbers refer to `manuscript.tex`. HC = Home Credit, LC = LendingClub v2, ST = Stability 2024, LR / CB = backbones.

Fixed in this revision of `pairwise.csv`: the schema is the agreed ten columns with nothing missing, the hypothesis-test and significance columns are gone, the fabricated standard errors are gone, `n_ho` is present, and all six deltas now equal `auc_A` minus `auc_B` exactly. Everything still open below concerns the values inside those columns, not the schema.

## 1. Full matrix vs manuscript

| Case | Method | Metric | Manuscript | full_matrix | Where in paper |
|---|---|---|---|---|---|
| HC LR | Pure LLM | AUC | 0.7400 | 0.7436 | Table 5 |
| HC LR | LLM then mRMR | AUC | 0.7381 | 0.7432 | Table 5, Table C.1 |
| HC LR | LLM then Boruta | AUC | 0.6488 | 0.7337 | Table 5 |
| HC CB | mRMR | AUC | 0.7668 | 0.7599 | Table C.1, Fig C.1 |
| HC CB | LLM then mRMR | AUC | 0.7630 | 0.7758 | Table 5, Table C.1, l.779 |
| HC CB | LLM then Boruta | AUC | 0.7592 | 0.7657 | Table 5 |
| HC CB | Stable core + LLM fill | AUC | 0.7683 | 0.7809 | Table 5 |
| LC LR | LLM then mRMR | AUC | 0.6907 | 0.7179 | Table 5 |
| LC LR | LLM then Boruta | AUC | 0.6479 | 0.6793 | Table 5 |
| LC LR | Stable core + LLM fill | AUC | 0.6840 | 0.7048 | Table 5 |
| LC CB | Pure LLM | AUC | 0.7137 | 0.7335 | Table 5; l.506 gap becomes 0.037, not 0.057 |
| LC CB | LLM then Boruta | AUC | 0.6850 | 0.7002 | Table 5 |
| LC CB | Stable core + LLM fill | AUC | 0.7028 | 0.7277 | Table 5 |
| ST LR | RFE CatBoost | AUC, leader | IV then Boruta 0.8030 leads | 0.8214, leads the classical family | Table 4, Fig 2 |
| ST LR | Stable core + LLM fill | AUC | 0.6815 | 0.8261 | l.506 |
| ST LR | CLIP-ranked | AUC | 0.6777 | 0.7842 | Table B.1 |
| ST CB | CatBoost SHAP | AUC, leader | RFE CatBoost 0.8500 leads | 0.8546, leads the classical family | Table 4, Fig 2 |
| ST CB | Stable core + LLM fill | AUC | 0.8146 | 0.8592 | l.506 |
| ST CB | CLIP-ranked | AUC | 0.7729 | 0.8239 | Table B.1 |
| HC CB | Pure LLM | KS | 0.4505 | 0.4264 | Table 6 |
| LC CB | LLM then mRMR | KS | 0.3943 | 0.3898 | Table 6 |
| ST CB | LLM then mRMR | KS, best | 0.5934 is best | 0.5112; Pure LLM CB 0.5559 is best | Table 6 |
| HC CB | Pure LLM | Capture@10 | 0.3581 by RFE CatBoost is best | 0.3630 Pure LLM CB is higher | Table 6, l.620 |
| LC CB | IV then Boruta | Capture@10 | 0.2269 is best | 0.2469; Pure LLM LR 0.2751 is best | Table 6 |
| ST CB | RFE CatBoost | Capture@10 | 0.5076 is best | 0.4547; Pure LLM CB 0.4671 is best | Table 6 |
| all | Brier | column | Table 6 reports it | not carried | see Section 4; a manuscript edit, not a data defect |

17 of 29 checkable AUC cells disagree. The 12 that agree are the six LLM leaders and six classical leaders, which are Fig 2's coordinates written into the file.

## 2. Pairwise vs manuscript

`pairwise.csv` was rebuilt on the development-chosen pairs. All six rows now use the pair that highest mean fold AUC selects, the AUCs match full_matrix to six decimals, every delta equals `auc_A` minus `auc_B`, every delta lies inside its interval, and `n_ho` matches Table 3 in all three datasets. One defect remains.

**The intervals were re-centred, not recomputed.** Five of six rows changed which two methods are compared, yet every half-width survived the change.

| Case | Pair changed | Old half-width | New half-width |
|---|---|---|---|
| HC LR | yes | 0.01085 | 0.01100 |
| HC CB | yes | 0.01050 | 0.01050 |
| LC LR | yes | 0.00465 | 0.00450 |
| LC CB | yes | 0.00455 | 0.00450 |
| ST LR | no | 0.00600 | 0.00600 |
| ST CB | yes | 0.00600 | 0.00600 |

A paired bootstrap interval depends on the correlation between the two score vectors being compared. Changing one of the two methods changes that correlation, so the width cannot stay fixed. These widths are the old ones moved onto the new point estimates.

Two consequences. The four Home Credit and LendingClub widths are still 1.36 to 1.41 times an unpaired normal interval at the stated held-out size, which is the wrong direction for a paired interval, since pairing on positively correlated scores should narrow it. And the Home Credit logistic regression interval now reads [-0.021, +0.001], so it crosses zero; whether the remaining exception is distinguishable from zero cannot be decided until the interval is genuinely recomputed.

Deltas under the new pairs, against what the manuscript currently states:

| Case | Manuscript Δ | pairwise.csv Δ |
|---|---|---|
| HC LR | −0.021033 vs mRMR | −0.010179 vs IV then Boruta |
| HC CB | +0.012024 vs RFE CatBoost | +0.024700 vs IV then Boruta |
| LC LR | +0.030431 vs IV then Boruta | +0.041353 vs RFE CatBoost |
| LC CB | +0.050517 vs IV then Boruta | +0.051702 vs RFE CatBoost |
| ST LR | +0.031444 vs IV then Boruta | +0.013006 vs RFE CatBoost |
| ST CB | +0.028431 vs RFE CatBoost | +0.028431 vs RFE CatBoost |

Five of six still favour the LLM-assisted leader. The reported range becomes +0.013 to +0.052, against the "+0.012 to +0.051" of l.119, l.502 and l.816, and the exception is now a 0.010 loss to IV then Boruta rather than a 0.021 loss to mRMR.

## 3. Between the two files

| Item | full_matrix.csv | pairwise.csv |
|---|---|---|
| Method pairs | per-family HO maxima in all six cases | identical in all six cases, so the two files agree on who is compared |
| HC LR mRMR | 0.76989 | 0.769900, a wrong rounding of 0.769890 |
| ST LR RFE CatBoost | 0.82139442 | 0.821400 |
| ST CB CatBoost SHAP | 0.85464446 | 0.854600 |
| Delimiter | semicolon | comma |
| Formatting | clean | stray space before `ci95_high` on the two Stability rows |

## 4. Further errors

**B1 is not closed, only de-contradicted.** Both files still select by highest held-out AUC. Removing the p-values makes the file consistent with Section 5.6, but it does not implement the pre-specified design B1 asks for. Under a development rule of highest mean fold AUC the compared pair changes in five of six cases:

| Case | DEV-rule pair | HO Δ | File pair |
|---|---|---|---|
| HC LR | LLM then mRMR vs IV then Boruta | −0.0102 | Stable core vs mRMR |
| HC CB | Pure LLM vs IV then Boruta | +0.0247 | Pure LLM vs RFE CatBoost |
| LC LR | Pure LLM vs RFE CatBoost | +0.0414 | Pure LLM vs IV then Boruta |
| LC CB | LLM then mRMR vs RFE CatBoost | +0.0517 | LLM then mRMR vs IV then Boruta |
| ST LR | Pure LLM vs RFE CatBoost | +0.0130 | same |
| ST CB | Pure LLM vs RFE CatBoost | +0.0284 | Pure LLM vs CatBoost SHAP |

Five of six still favours the LLM-assisted leader, and the Home Credit LR exception survives. Note that the development rule reproduces Table 4's Stability CatBoost row exactly, comparator and delta.

**Stability cohort provenance.** `n_ho` now says 369,147 on both Stability rows. The two values it labels, 0.821394 and 0.854644, carried `ho_n = 304,916` in the first matrix received. The same numbers are now attributed to a different population, and nothing in either file shows which scoring run produced them.

**Home Credit LR mRMR is still the weakest cell in the study.** Held-out 0.76989 against a fold mean of 0.7245, a gap of +0.045 where every other Home Credit LR classical row sits between −0.012 and +0.016. Its KS of 0.3486 is below seven selectors with lower AUC. This single cell carries the headline exception, Section 4.6 l.329, the Table C.1 full-pool reference and the Conclusion.

**Table 6 needs a manuscript edit, not a data fix.** Brier is unavailable locally, so that column should come out of Table 6 and the removal should be stated, the same way score PSI was handled under C3. Capture@10 has been restored to full_matrix, so KS and Capture@10 can both be rebuilt, but all six of those Table 6 values disagree with the file. Neither column affects B1 or B2.

**Two blank rows at the end of full_matrix.csv** (lines 86 and 87, all semicolons). An export artefact that breaks strict parsers.

**No full-feature rows.** Table 4's Full column (0.7715, 0.7860, 0.7109, 0.7230, 0.7734, 0.8105) still cannot be checked.

## 5. `pairwise_manuscript_reference.csv`

A transcription of Table 4, Fig 2 and Table 3, not a result. All pairs, AUCs, deltas, intervals, held-out sizes, event rates, budgets, resample count, seed and the "no test" flags match the manuscript, so it is a valid target to reproduce. Four issues in it:

| Item | Reference file | Manuscript / arithmetic |
|---|---|---|
| `interval_method` | "paired percentile bootstrap" | Sec 5.6 and the Table 4 caption say "paired bootstrap"; "percentile" appears only for the voting family (l.1158) |
| Interval shape | all six exactly symmetric about Δ | a percentile bootstrap is not symmetric to six decimals; these are Δ ± 1.96·SE |
| Interval width | implied SE 0.0055, 0.0054, 0.0024, 0.0023, 0.0057, 0.0051 | 1.2 to 2.5 times an unpaired Hanley-McNeil SE; a paired design should give less, not more |
| Tolerances | 5e-7 on AUC, Δ and CI | `auc` fields hold 4 and 5 decimal values, so only the pasted numbers can pass |
