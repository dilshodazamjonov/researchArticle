# qa_report.md

Verification of the text-only revision (prompt sections 5 and 6). Tools: pdflatex (TeX Live), texcount, latexdiff, aspell (en_GB), Python 3 with pypdf. Scripts ran in the session scratchpad; their essential code is reproduced at the end.

## 5.1 Build

| Document | Passes | Pages | Errors | Undefined references or citations | Multiply defined labels | Overfull boxes |
|---|---|---|---|---|---|---|
| Reviewed manuscript (baseline, `submission/revision_baseline.pdf`) | 3 | 35 | 0 | 0 | 0 | 0 |
| Revised manuscript (`submission/manuscript.pdf`) | 3 | 36 | 0 | 0 | 0 | 0 |
| `submission/supplementary.pdf` | 2 | 4 | 0 | 0 | 0 | 0 |
| latexdiff (`submission/manuscript_diff.pdf`, `-t CFONT`) | 3 | 40 | 0 | 0 | 0 | – |

Warnings: the only warnings in both the baseline and the revised logs are pdfTeX "destination with the same identifier (name{table.N})" messages caused by the `\setcounter{table}{0}` resets at the start of each appendix (15 in the baseline, 14 in the revised build); they are pre-existing and harmless. No new overfull box (the baseline had none; the revised build has none).

## 5.2 Rendered-text checks (PDF text extracted with pypdf)

Searched the revised manuscript and the supplement for "Section Appendix", "Table Table", "Figure Figure", "Section Section", "TODO", "TBD", "XX", "??", "[citation needed]" and stray `\commands`: none found. Doubled-word scan: only extraction artefacts (the dataset name "Home Credit Credit Risk Model Stability" and table-column fragments); no doubled word in the source.

## 5.3 Number inventory

See `number_inventory_report.md`: 853 of 855 distinct numeric tokens of the reviewed version appear unchanged; the two absent tokens (0.51, 0.54) are rounded restatements of values kept at three decimals in Table `tab:stability`; the 17 new tokens are layout parameters and raw coordinates of the new figure's code. No result number changed.

## 5.4 Consistency

- Every value of Table `tab:robustness` was checked against its source in the reviewed manuscript: DEV-rule row (Table `tab:confirmatory`: $+0.013$ to $+0.052$, $0.010$); third pairing ($-0.027$, `subsec:primary_results`); native categorical (at most $0.005$, ordering unchanged in three cases); family cap ($0.009$–$0.064$, $0.021$–$0.077$, $-0.003$; Table `tab:diversity`); depth-0 ($0.060$, $0.058$); matured cohort ($+0.018$, $+0.011$) and term split ($+0.022$/$+0.012$, $+0.014$/$+0.010$; `subsec:primary_results` prose and Table `tab:lc_maturity`); monthly breakdown (all nine months); obfuscation ($-0.0012$, $+0.0042$; Table `tab:obfuscation`); lineage ($-0.0064$ to $+0.0066$; Table `tab:mechanical`); repeated calls (0.0095, 0.0092, twenty refits; `subsec:stability_results`); L1 (below the classical leader in every case). The prompt's proposed values agreed with the manuscript in every row, so no substitution was needed.
- Abstract numbers: 1,959; 1,526,659; 20 and 40; $+0.012$ to $+0.051$; $+0.013$ to $+0.052$; $-0.010$ to $-0.027$; 522 and 21 seconds; 100-feature pool — all in the reviewed manuscript.
- Highlights: 1,959; 5 of 6 — in the manuscript.
- `fig:scale`: 99,092; 598,649; 1,157,512; 529; 675; 1,959; 373; 675; 1,068; 60; 100; 20; 40 — all from Table `tab:datasets`, `subsec:hybrid_fs` and `subsec:feature_budgets`.
- `tab:cost_structure`: every row checked against `subsec:pipeline`, `subsec:classical_fs`, `subsec:llm_fs` and `subsec:hybrid_fs` (missingness screen once per dataset; IV/WOE on the training partition; mRMR relevance and up to $\Kfeat$ redundancy estimates per candidate from Eq. (2); Boruta shadow copies and $\alpha$-level test; RFE removing 20% per step; SHAP over a 10,000-row sample; five bootstrap runs of the RF/correlation filter; semantic calls per partition on Home Credit, per partition and budget on LendingClub, once on Stability 2024). No row was dropped.
- Rule 1.8: no new or summarising text generalises about response sampling on Home Credit and LendingClub; the abstract, highlights, robustness table, new subsections and Discussion summaries cite only the Stability 2024 ten-repeat evidence (spreads 0.0095 and 0.0092, direction unchanged in all twenty refits). The pre-existing sentences on the Home Credit and LendingClub per-fold spreads keep their meaning in `subsec:stability_results`.

## 5.5 Spelling

Every changed or added line of `manuscript.tex` and `supplementary.tex` (186 lines) was stripped of LaTeX commands, identifiers and references and checked with `aspell --lang=en_GB`. No genuine misspelling was found. Words flagged and accepted as technical terms, names or code: LLM, LLMs, LLM's, CatBoost, CatBoost's, AUC, LendingClub, DEV, mRMR, Boruta, materiality, pre (pre-screen), Nogueira, RFE, Jaccard, SHAP, et al., reproducibility, recency, comparator(s), untuned, Brier, GPT, HC, USD, decile, PCA, ROC, categoricals, missingness, recalibration, screener, Anthropic, Ballegeer, Cawley, DeLong, Holm, JSON, Jelizarow, Jeong, Kaggle, Kalousis, Kuncheva, Tibshirani, Zhang, LaTeX, TikZ, GiB, cardinalities, covariate, differentially, preprocessing, quantiles, retuning, uncached, unscreened, runtimes, author names, colour macros (cBlue, cOrange, cGreen, cGrey), pgfplots keys (xbar, xmode, xtick, ytick, coords…) and symbolic coordinates (bLR, bCB, pLR, pCB).

## 5.6 Journal limits (script output)

```
abstract words: 243 (limit 250)
keywords: 7 (limit 7): Credit scoring \sep Big data \sep Feature selection \sep Large language models \sep Temporal validation \sep High-dimensional data \sep Selection stability
highlights: 5 (3 to 5)
   81 chars (limit 85) OK
   83 chars (limit 85) OK
   78 chars (limit 85) OK
   82 chars (limit 85) OK
   69 chars (limit 85) OK
```

## 5.7 Cross-references to moved or relabelled items

Every `\ref` to `tab:lc_maturity`, `tab:diversity`, `tab:dimension`, `tab:stages`, `app:protocol`, `app:robustness`, `subsec:robustness`, `subsec:drivers`, `subsec:stability_drift`, `tab:robustness`, `tab:cost_structure`, `tab:response_lists`, `fig:scale`, `subsec:deployment_scale`, `subsec:source_concentration`, `app:subsets`, `subsec:protocol_development` and `subsec:cost_runtime` (78 occurrences) was listed with its sentence and read. Sentences rewritten because their target moved: `subsec:pipeline` step 6 (changes "summarised in Section 4.6 and recorded in Appendix E, Table E.1"); `subsec:preprocessing` (width of every headline subset → Appendix F, Table F.3; native handling → Section 6.2 and Appendix F); `subsec:classical_fs` and the `tab:methods` caption and row (diversity controls → Section 6.2); `subsec:feature_budgets` (column counts → Appendix F, Table F.3); Related Work (LASSO comparator → Section 6.2 and Appendix F); `subsec:cross_dataset` (monthly breakdown → Appendix F); the `tab:diversity` caption; `subsec:mechanical_results` (base definitions → Section 4.4); `subsec:llm_fs` (description preparation → Appendix E). In the rendered text every appendix reference reads "Appendix X" (bare `\ref`), and no "Section Appendix" occurs.

## 5.8 Neutral-or-favourable audit

The diff (`submission/manuscript_diff.pdf`, 40 pages) was read change by change: no number changed; no claim was strengthened beyond the manuscript's numbers (the new framing sentences state what follows from the method definitions and are labelled as such); no claim was weakened; every disclosure of rule 1.6 remains (protocol evolution: `subsec:protocol_development`, `app:protocol`, Limitations; held-out populations inspected earlier: same places and the `fig:pipeline` caption; Stability 2024 cutoff moved: `subsec:dev_oot`, `subsec:protocol_development`, Limitations; development rule specified after the HO-rule results: `subsec:inference`, `tab:confirmatory` caption, Limitations; untuned full-feature reference: `subsec:models`, `tab:primary_results` caption, Limitations; protected attributes: `subsec:llm_fs`, `subsec:primary_results`, Limitations; memorisation of public material: Limitations; LendingClub resolved loans only: `subsec:dev_oot`, `app:robustness`; Home Credit recency holdout: Introduction, `subsec:datasets`, `tab:datasets` caption, `subsec:dev_oot`); no new caveat was added. Borderline rewordings are listed with their original wording in `REVISION_CHANGELOG.md`, section 5.

## 5.9 Read-through

The whole rendered manuscript (title to references) was read once after the final build; the dangling "next paragraph", "above" and "below" created by the moves were resolved (the appendix paragraphs keep their internal order so their "likewise", "next paragraph" and "reported above" still hold), the roadmap sentence was updated, and no repeated definition or orphaned sentence was found.

## Word counts (texcount "Words in text": headers, captions, tabular cells and TikZ text excluded; same command before and after)

| Section | Before | After | Change |
|---|---|---|---|
| 1 Introduction | 709 | 887 | +25.1% |
| 2 Related Work | 468 | 476 | +1.7% |
| 3 Background | 752 | 752 | +0.0% |
| 4 Methodology | 3,521 | 3,011 | -14.5% |
| 5 Experimental Setup | 3,797 | 3,830 | +0.9% |
| 6 Results | 5,289 | 4,099 | -22.5% |
| 7 Discussion | 2,636 | 2,775 | +5.3% |
| 8 Conclusion | 576 | 579 | +0.5% |
| Sections 1–8 | 17,748 | 16,409 | -7.5% |
| Sections 6+7 | 7,925 | 6,874 | -13.3% |

New material, measured with the same method: F2 scale paragraph 133 words; F4 pointer sentence 33; F5 rebuilt subsection 436 (it replaces the reviewed cost subsection of 376 words); F6 200; W3 introduction 169 (the table itself is not counted by texcount). The W2 summary (148 words) and the W5 drivers summary (154 words) condense existing content and are counted as ordinary text.

W10 targets:

| Target | Computation | Result |
|---|---|---|
| Sections 6+7 down ≥30% excluding the new material of F5, F6 and W3 | (6,874 − 805) / 7,925 | 6,069 words, **-23.4%** (like for like, also excluding the reviewed cost subsection from "before": -19.6%) |
| Sections 1–8 down ≥20% excluding the same new material (plus F2 and F4) | (16,409 − 971) / 17,748 | 15,438 words, **-13.0%** (like for like: -11.1%) |

Neither target is reached. Rule 1.5 (no content loss) was applied throughout: every fact, number and caveat of the reviewed version is still in the main text, an appendix or the supplement, and the main text points to where it went. The shrinkage came from moving material (protocol history, detailed robustness checks, subset lists) and from thinning number-dense prose; the Methodology and Experimental Setup sections, which hold method and disclosure detail, were not cut.

Page counts: 35 (reviewed) → 36 (revised), plus 4 pages of supplement; the six subset tables (about 5 pages) left the manuscript, and the new figure, three new tables, the extended table and two new appendices entered it.

## 5.10 Self-assessment (as a critical reviewer)

**Writing and presentation: 7/10** (from the self-review's 4). Gains: the Results section is ordered by the reader's questions (headline, robustness, drivers, stability, cost) with one summary table per question; the twelve robustness checks are visible at a glance; the development-rule paragraph and the stability text state direction first and keep numbers in tables; the protocol history, subset lists and detailed checks are out of the main flow; each caveat has one canonical home. Remaining weaknesses a referee may still flag: the main text is still about 16,400 words, of which Methodology and Experimental Setup are 6,800; several paragraphs remain long (Limitations, the LendingClub dataset description, the second stability paragraph at about 330 words); the headline subsection still carries five paragraphs of dense comparison; a number of sentences remain long and clause-heavy; the manuscript relies on many cross-reference pointers, which cost the reader page turns.

**Fit to *Big Data Research*: 7/10** (from 4). Gains: title, abstract, highlights, keywords, Introduction and contributions now put the scale of the data (1,959 features, 1,526,659 decisions) and the row-independence of the semantic stage at the centre; Figure `fig:scale` shows the scale of the selection problem; the "Scalability and cost" subsection leads with the one matched measurement and a cost-structure table; the Discussion has a "Deployment at scale" subsection. Remaining weaknesses: no article from the journal is cited (F7 skipped for lack of access to the publisher's pages); the scalability evidence is one matched fold-level measurement, the other runtimes being unmatched; all runs were on one laptop with no distributed or accelerator setting; the big-data framing rests on the size of the universes and populations rather than on a systems contribution.

## Scripts (essential code)

Number inventory (`number_inventory.py`, applied to the reviewed and revised `.tex` and to `supplementary.tex`):

```python
date_re = re.compile(r'\d{4}-\d{2}(?:-\d{2})?')
num_re  = re.compile(r'(?<![\w.])([+\-\u2212]?)((?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)(\\%|\s?per cent)?')
# body only (between \begin{document} and \end{document}), comments stripped; keep decimals, percentages,
# signed numbers, dates and integers of four or more digits; compare Counter(token) before and after.
```

Limits: `len(abstract.replace('$','').split()) <= 250`; `keywords.count('\\sep')+1 <= 7`; `3 <= len(highlights) <= 5 and all(len(h) <= 85)`.

Word counts: `texcount -sub=section -sum -nocol -q submission/manuscript.tex` (before and after); new material measured by wrapping the extracted text in a minimal document and running `texcount -sum -total`.

Spelling: added lines = lines of the revised files whose stripped content does not occur in the reviewed file; LaTeX commands, `$…$`, identifiers with digits and references stripped with regular expressions; `aspell list --lang=en_GB`.
