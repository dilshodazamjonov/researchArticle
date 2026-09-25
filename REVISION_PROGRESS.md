# REVISION_PROGRESS.md

Progress file for the text-only revision run (prompt: `prompt.md`), completed 2026-09-25. All tasks are done except F7 (skipped, reason below); an interrupted rerun would find every task committed on branch `revision/presentation-and-fit`.

## Locations

- **Manuscript revised:** `submission/manuscript.tex` (the newest copy, with the layout fixes committed as the baseline and the `headline_subsets.csv` sentence that task W7 refers to). The root `manuscript.tex` is an older duplicate, left untouched.
- **Git:** branch `revision/presentation-and-fit` from `main`; first commit = pre-existing uncommitted changes, unmodified; then one commit per task ID (list in `REVISION_CHANGELOG.md`, section 8). Nothing pushed.
- **Deliverables:** `submission/manuscript.tex` + `.pdf`, `submission/supplementary.tex` + `.pdf`, `submission/highlights.txt`, `submission/revision_baseline.pdf` + `.log`, `submission/manuscript_diff.tex` + `.pdf` (latexdiff); `REVISION_CHANGELOG.md`, `number_inventory_report.md`, `qa_report.md`, `REVISION_PROGRESS.md` in the repository root.

## Task status

| Task | Status | Notes |
|---|---|---|
| 2.1 Locate everything | done | CSV inventory below |
| 2.2 Baseline | done | 3 pdflatex passes; 35 pages; no overfull boxes; only hyperref duplicate-destination warnings |
| 2.3 Number inventory | done | 1,732 tokens, 855 distinct |
| F1 Title | done | `\title` and `pdftitle` |
| F2 Introduction scale paragraph, contribution, Related Work | done | |
| F3 Keywords and highlights | done | `submission/highlights.txt`; lengths 81/83/78/82/69 |
| F4 Scale figure | done | `fig:scale` after `tab:datasets` |
| F5 Scalability and cost | done | `tab:cost_structure`; runtimes moved to `app:robustness`; no per-call tokens (no CSV has them) |
| F6 Deployment at scale | done | 198 words |
| F7 Big Data Research citations | **skipped** | Crossref metadata reachable; publisher pages return HTTP 403 and no browser is installed, so abstracts could not be read on the publisher's page; candidates listed in the changelog for the authors |
| F8 AI declaration | done | authors must affirm it |
| W1 Caveats once | done | |
| W2 Protocol history to appendix | done | `app:protocol`; provenances to `subsec:llm_fs` |
| W3 Robustness table and appendix | done | `subsec:robustness`, `tab:robustness`, `app:robustness` |
| W4 Numbers in tables | done | new `tab:response_lists`; extended `tab:response_spread` |
| W5 Results restructured | done | 6.1–6.5 |
| W6 Paragraph length | done | |
| W7 Supplementary | done | `submission/supplementary.tex` (Tables S1–S6) |
| W8 Abstract | done | 243 words |
| W9 One meaning per term | done | |
| W10 Word counts | reported | targets not reached (rule 1.5); figures in `qa_report.md` |
| W11 Captions | done | |
| W12 Appendix order | done | E and F after A–D |
| 5.1–5.10 Verification | done | `qa_report.md` |
| 6 Deliverables | done | see Locations |

## 2.2 Baseline build

- `submission/revision_baseline.pdf` (35 pages), `submission/revision_baseline.log`; warnings: 15 pdfTeX "destination with the same identifier" messages from the appendix table-counter resets; no undefined references; no overfull or underfull boxes.

## 2.2 Word counts (texcount "Words in text")

| Section | Before | After |
|---|---|---|
| 1 Introduction | 709 | 887 |
| 2 Related Work | 468 | 476 |
| 3 Background | 752 | 752 |
| 4 Methodology | 3,521 | 3,011 |
| 5 Experimental Setup | 3,797 | 3,830 |
| 6 Results | 5,289 | 4,099 |
| 7 Discussion | 2,636 | 2,775 |
| 8 Conclusion | 576 | 579 |
| Sections 1–8 | 17,748 | 16,409 |
| Sections 6+7 | 7,925 | 6,874 |

## 2.1 CSV inventory (none is modified by this run)

| CSV | Contents | Manuscript correspondence |
|---|---|---|
| `appendix_e_subsets.csv` | the 12 headline subsets, one row per subset | Tables of the "Headline subsets" appendix (`tab:subsets_*`) |
| `archive/full_matrix_pre_brier_2026-09-20.csv` | superseded selector matrix without Brier | none (superseded) |
| `priority_1/dev_feature_budget_auc.csv` | mean DEV fold AUC per selector at K = 10…50 | `fig:budgets`, `tab:budgets`, DEV means of `tab:confirmatory` |
| `priority_1/full_matrix.csv` | HO AUC, KS, Capture@10, Brier and fold AUCs of every selector | `tab:full_matrix`, `tab:secondary`, `tab:confirmatory` |
| `priority_1/pairwise.csv` | paired ΔAUC with bootstrap CI under the HO and DEV rules | `tab:primary_results`, `tab:confirmatory`, `fig:primary` |
| `priority_1/stability_2024_llm_then_boruta.csv` | Nogueira/Jaccard of LLM then Boruta on Stability 2024 | two rows of `tab:stability` |
| `priority_2/boruta_subset_sizes.csv` | subset size reached by each Boruta-based selector per partition | "104 of 108 refits reached budget" statement (`subsec:primary_results`) |
| `priority_2/catboost_native_cat_ho_auc.csv` | CatBoost native-categorical re-run | native-handling paragraph (`subsec:primary_results`) |
| `priority_2/conservative_pair_interval.csv` | third-rule pair on Home Credit LR (−0.0267 with an interval) | third-rule sentence (`subsec:primary_results`; the manuscript reports the point estimate only) |
| `priority_2/diversity_capped_ho_auc.csv`, `diversity_capped_subsets.csv` | family-cap and depth-0 controls | `tab:diversity` |
| `priority_2/domain_rules_leakage_flags.csv` | the five flagged Home Credit features | `subsec:classical_fs` |
| `priority_2/headline_subsets.csv` | the 12 headline subsets, one row per rank | `tab:subsets_*`; named in `app:subsets` |
| `priority_2/ho_brier.csv` | Brier per selector | `tab:secondary` |
| `priority_2/homecredit_rankings.csv` | named Home Credit rankings per partition | overlaps and ranks of `tab:obfuscation` |
| `priority_2/iv_above_cap_status.csv` | count of features with IV ≥ 0.50 (0) | pipeline step 3 (`subsec:pipeline`) |
| `priority_2/l1_selector_ho_auc.csv` | L1 selector HO AUC | L1 paragraph (`subsec:primary_results`) |
| `priority_2/lc_base_column_overlap.csv` | base-column overlap of LC IV then Boruta subsets | not cited in the manuscript |
| `priority_2/lc_ho_by_maturity.csv`, `lc_ho_maturity_filters.csv`, `lc_maturity_by_cohort.csv` | LendingClub sub-population re-scoring | `tab:lc_maturity`, `subsec:dev_oot` |
| `priority_2/lc_missingness_distribution.csv` | 566 / 2 / 107 missingness blocks | `subsec:datasets` |
| `priority_2/mrmr_pool_timing.csv` | mRMR 522.15 s over 1,959 features, 20.52 s over 100 | matched measurement (522 and 21 seconds) in `subsec:cost_runtime` |
| `priority_2/obfuscated_ho_auc.csv`, `obfuscated_lists_armA.csv`, `obfuscated_lists_armB.csv` | obfuscation arms | `tab:obfuscation` |
| `priority_2/onehot_dimension.csv` | columns per headline subset | `tab:dimension` |
| `priority_2/perfold_rankings_ho_auc.csv` | HO AUC of each per-fold ranking (HC, LC) | first four rows of `tab:response_spread` |
| `priority_2/repeated_calls_*.csv` | the ten repeated Stability 2024 calls | `subsec:stability_results`, last two rows of `tab:response_spread` |
| `priority_2/selected_feature_psi.csv` | PSI mean/median/max per headline subset | PSI columns of `tab:primary_results`, `subsec:secondary_results` |
| `priority_2/stability_fold_pair_jaccard.csv` | min/max fold-pair Jaccard | Min/Max columns of `tab:stability` |
| `priority_2/stability_full_refs_20200201.csv` | full-feature references on Stability 2024 | "Full" column of `tab:primary_results` |
| `priority_2/stability_monthly_ho_auc_20200201.csv` | monthly HO AUC on Stability 2024 | monthly-breakdown paragraph (`subsec:primary_results`) |
| `todo/44_mechanical.csv`, `45_repeated_calls.csv`, `47_obfuscation.csv` | empty skeletons | none |
| `todo_done/44_mechanical.csv` | lineage-only arm | `tab:mechanical` |
| `todo_done/45_repeated_calls.csv`, `47_obfuscation.csv` | repeated calls on HC/LC and obfuscation on LC | not reported in the manuscript; not used (rule 1.8, no new results) |

No CSV records token usage, so the per-call token option of task F5 is not available.
