# Tasks for the authors — what is needed, why, and what each outcome does to the paper

Written 2026-09-15. Step numbers are the frozen numbers of `progress.md`. Files go in `priority_2/` unless stated; comma-delimited like `priority_1/full_matrix.csv`. Where a short answer in text is enough, that is said. Every task ends with the three outcomes ranked: **favours** the paper, **neutral**, **worsens** it.

| # | Task | Deliverable | Cost |
|---|---|---|---|
| 25 | LendingClub missingness distribution | text or small CSV | minutes |
| 9 | Selected-feature PSI for headline pipelines | `selected_feature_psi.csv` | hours, existing artefacts |
| 1 | B6 name obfuscation, two arms | two list files, one AUC file, one line | 12 API calls, 24 refits |
| 2 | Repeated calls on one partition | two CSVs, one line | 10 API calls, 20 refits |
| 5 | Features with IV > 0.50 | text list or CSV | minutes |
| 6 | Domain-rules leakage flags | text list | minutes |
| 12 | LendingClub base-column overlap | small CSV | hour |
| 13 | LendingClub HO loans that could not mature | CSV by term and month | hour |
| 14 | Monthly Stability HO AUC | CSV | hour, existing predictions |
| 15 | Stability full-feature references on the final cohort | CSV | two fits |
| 21 | Brier column for `full_matrix.csv` | one column added | hour, existing predictions |

---

## 25. LendingClub missingness distribution on the earliest training fold

**Problem.** Section 5.1 now says no LendingClub feature exceeds the 90% threshold, so all 675 pass the screen, and describes the late-introduced credit-file fields only as "higher missingness in DEV than in HO". The ceiling and the shape of the distribution are not stated.

**Why it matters.** A referee reads two sentences side by side: some fields were introduced late and are sparse in DEV, yet every feature passes a 90% screen. Both can be true, but the paper currently asserts it without the number that makes it so.

**Needed.** Text is enough: over the columns that carry missing values on the earliest training fold, the count of such columns, the distribution in bins (0–20, 20–40, 40–60, 60–75, 75–90, above 90), the maximum, and the missingness of the late-introduced fields as a group. If easier, `lc_missingness_fold1.csv` with `feature;missing_rate_fold1` for all 675.

**Outcomes.** Maximum comfortably below 90% (say ≤ 80%) → **favours**: the sentence gets its ceiling and the point closes. Maximum in the 85–89% band → **neutral**: true but the wording has to be careful. Any feature above 90% → **worsens**: "all 675 pass" is false, the LendingClub candidate set changes, and Table 3, Section 4.1 and Table 9 ($d = 675$) all move.

---

## 9. Selected-feature PSI for the headline pipelines

**Problem.** Section 6.2 reports feature drift only as the best case per dataset (lowest mean PSI, one maximum) and then concedes these minima "do not describe … necessarily the AUC-leading pipelines." The twelve pipelines the paper headlines in Table 4 have no drift figure anywhere.

**Why it matters.** Drift is one of the paper's four declared outcomes, and the prompt explicitly asks the model to favour "plausible temporal durability". Whether the LLM's subsets drift less than the classical selectors' is the only measurable test that the instruction did anything. Reporting a best-case minimum instead tells the referee nothing; both referee reports asked for the real values.

**Needed.** `selected_feature_psi.csv`, columns `dataset,backbone,selector,K,psi_mean,psi_median,psi_max,psi_max_feature` — DEV-versus-HO PSI of the features selected by the frozen full-DEV refit, binning as in Section 5.5. At minimum the twelve Table 4 leaders; preferably all 78 pipelines (13 selectors × 6 cases) so the grid matches Table 6.

**Outcomes.** LLM-assisted leaders drift less than classical leaders → **favours**: direct evidence the semantic screen picked more stable inputs, as instructed. Similar drift → **neutral**: one sentence, the caveat disappears. LLM leaders drift more → **worsens** the governance framing of Section 7.3, though no AUC number moves. Separately, if `psi_max_feature` on Home Credit is a previous-application recency field, that **worsens** more: it contradicts the step-7 closure that such features are outside the candidate set.

---

## 1. B6 — name obfuscation, two arms

**Problem.** The model's training data almost certainly include the Home Credit and LendingClub data dictionaries and winning-solution write-ups. Part of its ranking may be recall of which names are known to predict default rather than reasoning from meaning. The definition-only prompt withholds statistics but not names. The clearest symptom: `EXT_SOURCE_3, _2, _1` sit at ranks 1, 2, 3 in every Home Credit partition while the rest of the list churns at Jaccard 0.31–0.41 — the three are metadata-identical, so nothing semantic can produce that order.

**Why it matters.** It is the one objection that can sink the paper. The September-14 read called it a condition of acceptance. Limitations concede it fully, but a concession is not a test; only an ablation separates the two explanations, and a finding volunteered reads very differently from one a referee extracts.

**Needed.** Home Credit only, six ranking calls per arm (five folds plus full DEV), everything identical to the cached run except the feature records: snapshot `gpt-4.1-mini-2025-04-14`, temperature 0, JSON response, Appendix A template, `definitions_only`, the same 373 candidates, strict validation.
- Arm A, names removed: replace every name with `F001 …` by a **seeded shuffle** (not alphabetical or file order), scrub every literal occurrence of the original name from inside the description text as well.
- Arm B, descriptions removed: names kept, descriptions blank.
- `obfuscated_lists_armA.csv` and `obfuscated_lists_armB.csv`: `dataset,partition,rank,feature_id,original_feature_name` (600 rows each; `partition` in fold1..fold5, full_dev; the original-name column is the key and never goes to the model).
- `obfuscated_ho_auc.csv`: `arm,dataset,backbone,K,ho_auc,fold1_auc,…,fold5_auc` (four rows: two arms × lr K=20, catboost K=40).
- One line confirming snapshot, temperature, template, evidence mode, and giving the shuffle seed.
- Optional: one pairwise row per arm and backbone from the routine that produced `pairwise.csv` (obfuscated against named, 0.743635 LR and 0.793450 CatBoost), which upgrades the comparison from descriptive to tested.

Full specification, unchanged, at the foot of `progress.md`.

**Outcomes.** HO AUC holds with lists overlapping the named lists → **favours** (strongest possible answer: the ranking is driven by meaning). HO AUC holds with lists diverging → **favours**, slightly less: the claim stands and the divergence is consistent with the non-determinism already reported. **HO AUC drops materially (more than the 0.010 bar)** → **worsens**: reported as a negative, the contribution narrows to datasets the model has seen, and the abstract, contributions list and Conclusion are rewritten. The third outcome is the reason to run it now rather than let a referee suspect it. Caveat in every branch: a description can be recognisable too, so the ablation weakens the name channel rather than removing it.

---

## 2. Repeated calls on one partition

**Problem.** Stability 2024's LLM ranking is one API response; it served every fold and carries two of the five headline wins (+0.013, +0.024). The paper concedes that identical calls returned different orderings on the other datasets, and that run-to-run variance was never measured.

**Why it matters.** If the HO AUC spread across repeats is wide, the headline margins are draws from a distribution, not measurements, and Section 7.3's governance framing begins to argue against the paper's own conclusion. After B6 this is the most damaging open point.

**Needed.** Ten calls on the Stability 2024 full-DEV partition at temperature 0, same snapshot, template, evidence mode and 1,068 records; refit top-20 to logistic regression and top-40 to CatBoost per response; score on the same HO.
- `repeated_calls_lists.csv`: `dataset,repeat_id,rank,feature_name` (1,000 rows).
- `repeated_calls_ho_auc.csv`: `dataset,repeat_id,backbone,K,ho_auc` (20 rows).
- One line confirming snapshot and temperature. Optional second arm on the Home Credit full-DEV call, same schema, `dataset = homecredit`.

**Outcomes.** HO AUC spread across repeats below 0.010 and pairwise top-$K$ Jaccard high → **favours**: the single-response caveat retires and the margins are measurements. Spread around 0.010 → **neutral**: reported as a variance figure beside the margin. Spread comparable to or larger than the margins (≥ 0.013) → **worsens**: the headline is reframed as a distribution, Section 7.3 rewritten, abstract hedged.

---

## 5. Features with IV > 0.50

**Problem.** The IV/WOE ranker and the IV-then-Boruta screen keep only $0.01 \le \mathrm{IV} \le 0.50$. The upper cap drops features that predict "too well" — scorecard practice reads IV > 0.5 as a leakage warning. Which features it dropped is never stated.

**Why it matters.** IV then Boruta is the classical leader in three headline cases. If the cap removed a strong *legitimate* predictor, those classical selectors were handicapped while the LLM faced no cap, and part of the LLM's margin is the cap's doing.

**Needed.** Text is enough: the list of features with IV > 0.50 on the earliest training fold, per dataset. Or `iv_above_cap.csv` with `dataset,feature,iv_fold1`.

**Outcomes.** Empty list → **favours**: one sentence in Section 4.1 says the cap removed nothing. Only leakage-like features (post-decision fields, target proxies) → **neutral**: named, with the reason. Legitimate strong predictors on it (an external score, say) → **worsens**: the classical side was understated, and the paper must say so where the classical leader is IV then Boruta.

---

## 6. Domain-rules leakage flags

**Problem.** The domain-rules scorer sets feature priority, "which aggregation suffixes and leakage status adjust." Somewhere in that rule set is a list of Home Credit features treated as leaky. It is not in the paper.

**Why it matters.** If the rule set knows a feature is leaky but the feature stayed in the 373 for the other twelve selectors, any selector that picked it has an HO AUC a referee can call contaminated. If the flagged features are outside the 373, one sentence closes the point.

**Needed.** Text is enough: the list of Home Credit features the domain-rules scorer marks as leakage, and for each whether it is inside or outside the 373-feature candidate set.

**Outcomes.** All outside the 373 → **favours**: one sentence in Section 4.3. Inside the 373 but in no headline subset (step 11 shows this) → **neutral**: stated as such. Inside a headline subset → **worsens**: that pipeline's HO AUC is challengeable and the case needs a sentence or a refit.

---

## 12. LendingClub base-column overlap

**Problem.** LendingClub's 675 features are built in families from about 93 columns: `open_acc` appears in 48 features, `total_acc` in 46, and 65 are monotone transforms of variables already present. A univariate filter cannot tell a feature from its log; the prompt asks the model to avoid near-duplicate aggregates. Whether this asymmetry explains the LendingClub margin (the largest in the study) is untested — one version of the hypothesis was already tested and refuted on 2026-09-14, so nothing is written until the count exists.

**Why it matters.** It would be a *mechanism* for the paper's biggest result, and a referee who knows the dataset will propose it either way; better to have measured it.

**Needed.** `lc_base_column_overlap.csv`: `backbone,selector,K,n_features,n_sharing_base_column,n_distinct_base_columns` for the full-DEV subsets of the LendingClub classical leaders (IV then Boruta, LR and CatBoost) and the LLM-assisted leaders (pure LLM LR, LLM then mRMR CatBoost). Four rows.

**Outcomes.** Classical subsets heavily redundant, LLM subsets not → **favours**: a stated mechanism for the LendingClub margin. Similar redundancy → **neutral**: the hypothesis is dropped, nothing enters the paper. LLM subsets more redundant → **neutral**, since the paper claims nothing about it, though the prompt's deduplication instruction then demonstrably did not work.

---

## 13. LendingClub HO loans that could not have matured

**Problem.** HO is loans issued in 2016, evaluated as resolved by the 2019-05-01 snapshot. No 60-month loan issued in 2016 had matured by then, nor any 36-month loan issued after May 2016. Keeping "resolved loans only" therefore keeps early payoffs and charge-offs for those cohorts — informative censoring that acts more strongly on HO than DEV and is consistent with the event-rate rise from 19.5% to 23.3%. The paper's largest effect, +0.051, is measured on this population.

**Why it matters.** Section 5.2 now carries the caveat, but the referee's minimum ask — how large the affected share is — is unreported. Without it the reader cannot judge how much of the HO population is "early resolvers".

**Needed.** `lc_maturity_by_cohort.csv`: `issue_month;term;n_ho_loans;n_could_have_matured;share_could_not_mature;event_rate` — 12 months × 2 terms, 24 rows.

**Outcomes.** Small affected share → **favours**: the caveat gets a number and shrinks. Moderate share → **neutral**: stated, the +0.051 keeps its caveat. Large share (most of HO could not have matured) → **worsens**: the +0.051 needs a heavier qualification, or a fixed-horizon target and a rerun.

---

## 14. Monthly Stability HO AUC

**Problem.** The Stability 2024 HO window, February to October 2020, spans the onset of the pandemic. The paper reports one AUC for the whole window and says in Section 7.4 that the results "should not be read as demonstrated robustness to a regime shift."

**Why it matters.** Whether the LLM-assisted margin is uniform across those months or concentrated in one period is the difference between a result and an artefact of the window. Cheap, and probably strengthening.

**Needed.** `stability_monthly_ho_auc.csv`: `month,backbone,selector,n,n_events,ho_auc` for the four Stability headline pipelines (pure LLM LR and CatBoost; RFE CatBoost LR; CatBoost SHAP CatBoost), February through October — 36 rows. Predictions already exist.

**Outcomes.** Margin uniform across months → **favours**: one sentence and a small figure, and the regime-shift caveat softens. Margin varies but its sign is stable → **neutral**: reported. Sign flips after March 2020 → **worsens**: the Stability wins depend on the pre-pandemic months and Section 7.4 must say so.

---

## 15. Stability full-feature references on the final cohort

**Problem.** The two Stability 2024 full-feature reference values in Table 4 come from the earlier complete run on the 2020-02-26 cohort; the headline pipelines are on 2020-02-01. Table 4 note a and eleven cross-cohort caveats exist because of this.

**Why it matters.** Every other number in the headline table is on one population. A referee sees a footnote on the reference column and asks why two fits were not redone.

**Needed.** Refit the two full-feature models (1,959 features, both backbones, fixed configuration) on the 2020-02-01 DEV and score the 2020-02-01 HO. `stability_full_refs_20200201.csv`: `backbone,n_features,ho_auc,dev_oof_auc`. Two rows.

**Outcomes.** Full-feature references remain below the compact leaders → **favours**: note a and the caveats retire, nothing else changes. Full-feature references above the compact leaders → **neutral** for the claims (the paper dropped "compact beats full" and reports Full as untuned context only), though the Discussion sentence on the reference is reworded. There is no outcome that worsens the paper; the current cross-cohort state is the worst case.

---

## 21. Brier column for `full_matrix.csv`

**Problem.** Table 8's KS and Capture@10 columns were rebuilt on 2026-09-14 from `priority_1/full_matrix.csv`, which showed the old values came from a superseded run. The Brier column could not be rebuilt because the file has no Brier field and nothing on disk does. Its three values (0.1534, 0.2024, 0.1792) and the two prose claims that the lowest Brier is an LLM-assisted CatBoost pipeline in every dataset (Sections 6.2 and 7.4) are therefore unverified — and if KS and Capture@10 were stale, Brier almost certainly is.

**Why it matters.** One unverified column in a table whose other two columns were just corrected is the kind of thing a careful referee spots by recomputing Lift from Capture. It also holds up the consistency sweep of Gate 3.

**Needed.** One column `brier` added to `priority_1/full_matrix.csv` as the eighth field, between `capture10` and `fold1_auc`, so the header reads `dataset,backbone,selector,K,ho_auc,ks,capture10,brier,fold1_auc,…,fold5_auc`. One value on each of the 84 data rows: the HO Brier score of the frozen full-DEV refit, computed on the same prediction vector that produced `ho_auc`, `ks` and `capture10`. The blank second line and the repeated header on line 3 need the extra `;` too, or should be removed.

**Outcomes.** Brier leaders as currently stated → **favours**: the column is confirmed and the sentence stands. Different leaders but still LLM-assisted → **neutral**: Table 8 rebuilt, sentence adjusted. A classical pipeline leads Brier somewhere → **worsens** slightly: the Section 7.4 sentence "an LLM-assisted pipeline attains the highest KS, the lowest Brier score and the highest top-decile capture in all three datasets" loses one of its three clauses.
