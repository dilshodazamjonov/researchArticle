# REVISION_CHANGELOG.md

Text-only revision of `submission/manuscript.tex` for *Big Data Research*, run from `prompt.md` on 2026-09-25 on branch `revision/presentation-and-fit` (one commit per task ID; nothing pushed; no history rewritten). Every number, interval, count, subset, ranking, leader identity and conclusion of the reviewed version is unchanged; material was moved, condensed, reordered or reframed only.

Locations: the manuscript revised is `submission/manuscript.tex` (the newest copy, the one the submission zip was built from). The root `manuscript.tex` is an older duplicate and was left untouched. LaTeX deliverables are in `submission/`; the Markdown reports are in the repository root.

## 1. Changes by task ID

Line numbers refer to the reviewed version ("before") and the revised version ("after") of `submission/manuscript.tex`; `git show <commit>` gives the exact diff of each task.

| Task | Change | Before | After | Reason |
|---|---|---|---|---|
| Baseline | Pre-existing uncommitted layout changes committed unmodified | – | commit `3d78c42` | so that each later commit is one task ID |
| 2.1–2.3 | Baseline build (`revision/revision_baseline.pdf`, `.log`), texcount, number inventory, CSV inventory | – | `REVISION_PROGRESS.md` | orientation |
| F1 | Title replaced in `\title{}` and `pdftitle` | L55, L114 | same lines | prompt F1 |
| F2 | New paragraph "Scale sharpens the case for such a pre-screen…" inserted after the Introduction's second paragraph (numbers verbatim; "Stability 2024" and "mRMR" used as the manuscript uses them) | after L148 | L150 | scale made central |
| F2 | First contribution names the scale: "…whose semantic stage reads no data rows, across three credit portfolios of up to 1,959 engineered features and 1.5 million decisions (1,526,659)…" (both the rounded and the exact figure kept) | L155 | L157 | prompt F2 |
| F2 | Related Work: the Bolón-Canedo sentence moved to the front of the paragraph "Classical selection and its stability" and sharpened: "In wide data it is the cost of selection, its redundancy handling and its stability, not raw relevance, that dominate the practical difficulty" (its three original terms kept) | L168 | L170 | prompt F2; no new claim |
| F3 | Keyword "Covariate shift" → "High-dimensional data" (seven keywords) | L135 | L137 | prompt F3 |
| F3 | Five new highlights in the comment block and in `submission/highlights.txt` (lengths 81/83/78/82/69) | L101–108 | same | prompt F3 |
| F4 | New Figure `fig:scale`, "Scale of the selection problem" (pgfplots, `paper` style, Okabe–Ito colours, log axis), after Table `tab:datasets`, with a pointer sentence at the start of `subsec:datasets`; no reduction ratio drawn (conservative) | – | L400–433, L366 | prompt F4 |
| F5 | `subsec:cost_runtime` retitled "Scalability and cost" and rebuilt: (1) matched measurement first, (2) new Table `tab:cost_structure` introduced as following from the method definitions, (3) usage and cost sentences verbatim, (4) peak memory verbatim, (5) one pointer to the appendix; unmatched wall-clock times moved verbatim to `app:robustness`, paragraph "Unmatched wall-clock times", with their caveat ("with the one exception noted at the end of this section" → "reported in Section~\ref{subsec:cost_runtime}"; "quoted above" → "quoted here") | L994–997 | L984–1026; L1425 | prompt F5 |
| F5 | Per-call token figures: **not added**; no CSV records token usage | – | – | prompt F5 (add nothing) |
| F6 | New Discussion subsection "Deployment at scale" (`subsec:deployment_scale`, 198 words) after `subsec:cross_dataset` | – | L1062–1065 | prompt F6 |
| F7 | **Skipped**: see section 3 | – | – | publisher pages not readable |
| F8 | Generative-AI declaration: first sentence extended to the restructuring and to the code of Figure `fig:scale` and Tables `tab:cost_structure`, `tab:robustness`, `tab:response_lists`; "four figures" → "five figures"; everything else unchanged | L1544 | L1528 | prompt F8 |
| W1 | Caveats stated once: HO-rule descriptive caveat kept in full in `subsec:inference`, one clause in the captions of `tab:primary_results` and `fig:primary`, pointers elsewhere (first paragraph of `subsec:primary_results`, `subsec:supplementary_discussion`, Limitations last paragraph, `tab:confirmatory` caption); full-feature caveat canonical in `subsec:models` with one clause in the `tab:primary_results` caption and pointers in `subsec:primary_results` and `subsec:main_findings`; Brier clause added to the `tab:secondary` caption; duplicate "not a confidence interval" sentence removed from the stability text (kept in `subsec:inference` and the `tab:response_spread` caption) | various | various | prompt W1 |
| W2 | Full protocol history and Table `tab:stages` moved verbatim to new appendix `app:protocol` ("The protocol above" → "The protocol of Section~\ref{sec:methodology}"); 150-word summary kept as `subsec:protocol_development`; the three provenances and the template clause moved verbatim to `subsec:llm_fs` with a one-sentence pointer left in the appendix; referencing sentences in `subsec:pipeline` and `subsec:mechanical_results` adjusted | L349–390 | L351–355; L334; L1355–1395 | prompt W2 |
| W3 | New subsection `subsec:robustness` with Table `tab:robustness` (twelve checks, every value checked against its source) and a 169-word introduction; L1 selector, native categorical handling, LendingClub resolution filter and matured cohort, family cap and depth-0 controls, Stability 2024 monthly breakdown, Boruta budget attainment and effective dimension moved verbatim to `app:robustness` with Tables `tab:lc_maturity`, `tab:diversity`, `tab:dimension`; pointer sentences left in `subsec:primary_results` | L531–543, 635–725 | L693–735; L1397–1500 | prompt W3 |
| W3 follow-up | Restored the original indentation of 219 code lines that a whitespace normalisation in the W3 commit had collapsed (no content change; the verbatim prompt listing was verified identical to the baseline) | – | – | keep the diff readable |
| W4 | Prose thinned to at most three numbers per sentence in `subsec:primary_results` (development-rule paragraph follows the model text; the leader-identity changes, "five of six margins wider" and "Stability 2024 LR keeps its pair" kept in one sentence), the three stability paragraphs, `subsec:secondary_results`, `subsec:obfuscation_results`, `subsec:mechanical_results`, `subsec:main_findings`, `subsec:performance_vs_stability`, Conclusion; numbers that appeared nowhere else moved into Table `tab:response_spread` (new columns Median, s.d., Margin over classical leader), new Table `tab:response_lists` (Nogueira, Jaccard, names in all draws, distinct names) and the note of `tab:obfuscation` (pairwise Jaccard of the arm lists) | various | various | prompt W4 |
| W5 | Results reordered: 6.1 Headline comparison (`subsec:primary_results`), 6.2 Robustness (`subsec:robustness`), 6.3 What drives the result (`subsec:drivers`: 6.3.1 obfuscation, 6.3.2 lineage, 6.3.3 source concentration `subsec:source_concentration`), 6.4 Stability, drift and secondary metrics (`subsec:stability_drift`: 6.4.1 `subsec:stability_results`, 6.4.2 `subsec:secondary_results`), 6.5 Scalability and cost; roadmap sentence updated; nine referencing sentences updated (listed in `qa_report.md`) | L523–1000 | L527–1026 | prompt W5 |
| W6 | Stability paragraph split into three (fold agreement; response sampling; hybrids); Main Findings first paragraph split into three; Performance vs Stability split into two; Limitations third paragraph split; Conclusion paragraphs split | various | various | prompt W6 |
| W7 | Six subset tables moved to `submission/supplementary.tex` (standalone, Tables S1–S6; compiles to 4 pages); `app:subsets` reduced to one paragraph with the overlap counts; its pointer for the external-score ranks corrected from `subsec:stability_results` to `subsec:obfuscation_results` (the fact is stated there) | L1307–1533 | L1302; `supplementary.tex` | prompt W7 |
| W8 | Abstract replaced (243 words by script; comment updated) | L130 | L132 | prompt W8 |
| W9 | "Most reproducible classical selector" in the `fig:stability` legend and in every stability passage that quotes the refitted classical rows of `tab:stability` (`subsec:stability_results`, `subsec:main_findings`, `subsec:performance_vs_stability`); "classical leader" kept for AUC leaders only | L912, 915 and prose | L880, 883 and prose | prompt W9 |
| W10 | Word counts reported in `qa_report.md`; targets not reached (rule 1.5 kept every fact) | – | – | prompt W10 |
| W11 | Captions of `tab:primary_results`, `tab:confirmatory` and `fig:primary` shortened by removing wording carried by the canonical homes; no column or symbol definition removed | L550, 577, 784 | L558, 585, 688 | prompt W11 |
| W12 | `app:protocol` and `app:robustness` placed after the existing appendices (letters A–D unchanged), counters reset, bare `\ref` used; rendered text checked for "Section Appendix" (none) | – | L1355, 1397 | prompt W12 |

## 2. Provenance log for new numbers

No new result number was introduced. The only numeric tokens absent from the reviewed version are:

| Token | Where | Provenance |
|---|---|---|
| 4.4, 10.2, 0.1, 0.985, 6.2, −6.2 | `fig:scale` code | pgfplots layout parameters (bar width, axis width, limit enlargement, legend position, bar shifts) |
| 100000, 1000000, 100,000, 1,000,000, 10,100, 10,100,100 | `fig:scale` code | axis tick positions and labels |
| 1068, 1959, 1157512, 598649, 99092 | `fig:scale` code | the manuscript's 1,068; 1,959; 1,157,512; 598,649; 99,092 without thousands separators (plot coordinates) |
| "at most 0.0075" | `subsec:stability_results` | the largest of the four Home Credit and LendingClub spreads 0.0053, 0.0072, 0.0075, 0.0038 (Table `tab:response_spread`) |
| "1.5 million decisions (1,526,659)" | contributions | both figures already in the manuscript (L155 and `subsec:dev_oot`) |

Every value in `tab:robustness`, `tab:cost_structure`, `tab:response_lists`, the new columns of `tab:response_spread`, `fig:scale`, the abstract and the highlights was copied from the reviewed manuscript (sources in the QA report). No ratio was computed for `fig:scale`.

## 3. Skipped tasks

- **F7 (cite *Big Data Research*)**: skipped, nothing added. Crossref (the publisher's DOI deposits) was reachable and returned candidate articles with title, authors, year, volume, article number and DOI, but no abstracts; the publisher's pages (ScienceDirect) answered HTTP 403 to automated fetches and no browser is installed on this machine, so the abstract could not be read on the publisher's page as the prompt requires. Candidates the authors may wish to verify themselves: 10.1016/j.bdr.2025.100524 (Efficient, interpretable and automated feature engineering for bank data, 2025, vol. 40, art. 100524); 10.1016/j.bdr.2026.100642 (A feature-based predictive optimization framework for early-stage bankruptcy risk assessment, 2026, vol. 46, art. 100642); 10.1016/j.bdr.2025.100556 (A decentralized metaheuristic approach to feature selection…, 2025, vol. 41, art. 100556); 10.1016/j.bdr.2025.100537 (Bankruptcy risk prediction…, 2025, vol. 41, art. 100537). None was cited.
- **F5 per-call tokens**: not added (no CSV records token usage).
- **W10 targets**: not reached; actual figures in `qa_report.md`.

## 4. Choices made where the prompt allowed one

- Manuscript revised: `submission/manuscript.tex` rather than the older root copy.
- Pre-existing uncommitted changes committed as a baseline commit on the branch rather than folded into a task commit.
- `fig:scale` drawn as one log-axis bar chart (rows: DEV decisions, universe, candidate set, semantic pool, budget; the pool and budget rows shown once as "same in all three datasets"); no reduction ratio drawn; the table-row fallback of F4 was not needed.
- `tab:cost_structure` caption carries no AI-assistance note (the existing table captions carry none); the declaration names the table.
- In F2's paragraph "Stability 2024" and "mRMR" are used as the manuscript uses them (mRMR is never expanded in the manuscript).
- Boruta-budget detail and the Stability 2024 monthly breakdown moved to `app:robustness` with the key figure kept in prose (the prompt lists the monthly breakdown; the Boruta detail was moved for the same reason).
- New helper tables (`tab:response_lists`; extended `tab:response_spread`) added so that no unique number had to be dropped from the thinned prose.
- Robustness-table "Source" for checks whose detail moved: `\ref{app:robustness}`.
- The stability subsection carries the new label `subsec:stability_drift`; the old labels remain on the subsubsections.

## 5. Borderline changes (5.8), with the original wording

1. `tab:confirmatory` caption: "…is read against the materiality bar of $0.010$; no hypothesis test is reported (Section~\ref{subsec:inference}). The holdout plays no part in the choice of the compared methods; the rule was specified after the results of Table~\ref{tab:primary_results} were known (Section~\ref{subsec:protocol_development})." → "…is read against the materiality bar (Section~\ref{subsec:inference}). The holdout plays no part in the choice of the compared methods, but the rule was specified after the results of Table~\ref{tab:primary_results} were known (\ref{app:protocol})."
2. Limitations, last paragraph: "…formal inference is confined to the pre-declared classical voting family of \ref{app:voting}, the headline comparisons of Tables~\ref{tab:primary_results} and \ref{tab:confirmatory} are reported as effect sizes with intervals and no test (Section~\ref{subsec:inference}), and the HO-rule comparisons are descriptive for the reason given above." → the last clause dropped (the reason stands two paragraphs above).
3. `subsec:stability_results`: sentence "These refits vary the cached response only and, like the Stability 2024 repeats, are not a confidence interval." removed (the `tab:response_spread` caption and `subsec:inference` carry it).
4. `subsec:main_findings`: "The full-feature reference was not tuned for the wide problem, so the study makes no claim about compact subsets against the full feature set." → "The full-feature reference is untuned and context only (Section~\ref{subsec:models})." (the "no claim" statement remains in `subsec:primary_results` and `subsec:models`).
5. `subsec:supplementary_discussion`: "…is reported as an effect size with an interval and no test, either because the compared methods were identified on the held-out results or because the rule that chose them was specified after those results were known (Section~\ref{subsec:inference})." → "…with an interval and no test (Section~\ref{subsec:inference})."
6. Development-rule paragraph: dropped "The ordering is unchanged.", "every one of the five above the materiality bar", "Choosing the leaders without the holdout therefore leaves the five-of-six result intact." and "so the development-rule margin there is out-of-sample in both directions" (implied by the model text's "not the outcome" and by the margins $+0.013$ to $+0.052$ against the bar of $0.010$).
7. `subsec:primary_results`: "no claim is made that compact subsets outperform the full feature set" → "supports no claim about compact subsets against the full feature set".
8. `subsec:stability_results`: new comparative phrase "Stable core plus LLM fill is the more reproducible hybrid in every case" (follows from the rows of `tab:stability`: 0.69–0.76 against 0.42–0.63).
9. `subsec:stability_results`: "Held-out AUC spans $0.0053$ and $0.0072$ … and $0.0075$ and $0.0038$ on LendingClub" → "spans at most 0.0075 across the five responses in the four Home Credit and LendingClub cases (Table~\ref{tab:response_spread})".
10. `subsec:obfuscation_results`: the overlap counts, full-DEV ranks and arm-list Jaccard values replaced by pointers to `tab:obfuscation` and its note ("Each arm's subset shares only part of its names…"); the figures are in the table.
11. `tab:cost_structure`, Boruta row: "repeated for the confirmation test" is inferred from the $\alpha$-level shadow test with two-step correction described in `subsec:classical_fs`.
12. `subsec:robustness` intro: "only the family cap, a control that handicaps the classical selector, brings the two families level there" summarises the note of `tab:diversity`.
13. `app:subsets`: pointer "as noted in Section~\ref{subsec:stability_results}" corrected to `subsec:obfuscation_results`.
14. F2 contribution: "up to 1.5 million decisions and 1,959 engineered features" → "up to 1,959 engineered features and 1.5 million decisions (1,526,659)".

## 6. Observations for the authors (no manuscript change made)

- `priority_2/conservative_pair_interval.csv` holds a bootstrap interval for the third-rule Home Credit LR pair ($-0.0267$, $[-0.0285, -0.0250]$) whereas the manuscript says that interval was not computed; not changed (no new numbers were allowed).
- `todo_done/45_repeated_calls.csv` and `todo_done/47_obfuscation.csv` hold repeated calls on Home Credit and LendingClub and an obfuscation run on LendingClub that the manuscript does not report; not used (rule 1.8).
- In `todo_done/44_mechanical.csv` the "mechanical" and "cached" columns of the stable-core row appear swapped relative to the header; the manuscript's values are self-consistent.
- The root `manuscript.tex` is a stale copy of the reviewed version. `submission/manuscript_source.zip` was rebuilt from the revised files on 2026-09-25 (manuscript.tex, manuscript.pdf, supplementary.tex, supplementary.pdf, highlights.txt); the latexdiff and the baseline build were moved to `revision/`, and the submission folder holds only the submission files and the zip.

## 7. Checklist before submission

- [ ] Read and affirm the generative-AI declaration (F8): it now states that Claude (Anthropic) restructured the presentation and generated the code of Figure `fig:scale` and Tables `tab:cost_structure`, `tab:robustness` and `tab:response_lists`.
- [ ] New citations: none were added (F7 skipped); nothing to verify.
- [ ] Approve the new title (also in `pdftitle`) and the new abstract (243 words).
- [ ] Approve the keyword change and the five highlights (`submission/highlights.txt`).
- [ ] Check `submission/supplementary.tex` / `.pdf` (Tables S1–S6) and upload it as supplementary material.
- [ ] Review the borderline changes of section 5 and revert any you disagree with.
- [x] `submission/manuscript_source.zip` rebuilt (2026-09-25). Still open: decide what to do with the stale root `manuscript.tex`.
- [ ] Merge or keep the branch `revision/presentation-and-fit`; `revision/manuscript_diff.pdf` is the latexdiff against the reviewed version.

## 8. Commits on the branch (newest first)

- 00c80f8 F8 follow-up: declaration names the new tables by label
- cab0180 W4: obfuscation and lineage paragraphs thinned; arm-list Jaccard moved to the obfuscation table note
- 91710ba W4 follow-up: keep the signed +0.028 and the stable-core Nogueira and Jaccard ranges in prose (number inventory)
- 7fd190b W1/W11: caveats stated once in their canonical homes with short clauses in the headline captions; captions shortened; duplicate confidence-interval caveat removed
- 053d3ad W9: 'most reproducible classical selector' in the stability figure legend; Discussion sentences on stability use the same term
- 08eacf6 W4/W6: Discussion and Conclusion prose thinned and long paragraphs split (main findings, performance vs stability, limitations, conclusion)
- c1bac44 W4: stability and secondary-metrics prose thinned; repeat-call medians, s.d. and margins added to tab:response_spread; new tab:response_lists holds list-agreement counts; stability passages use 'most reproducible classical selector' (W9)
- da83ba4 W3 follow-up: restore original indentation of code lines collapsed by a whitespace normalisation (no content change)
- bdf33d4 W6: stability paragraph split into fold-to-fold agreement, response sampling and hybrids
- 62483c9 W4: headline-comparison prose thinned to direction plus the number that matters; development-rule paragraph follows the model text
- 67cb753 W5: Results restructured around questions (headline, robustness, drivers, stability/drift/secondary, cost); labels kept; references and roadmap updated
- 7fc3d43 W3: robustness summary table and subsection (subsec:robustness); detailed checks and Tables lc_maturity, diversity, dimension moved verbatim to app:robustness with pointers
- bdd20f3 W2: protocol history moved to new appendix app:protocol (with tab:stages); ~150-word summary kept as subsec:protocol_development; description provenances moved to subsec:llm_fs; references adjusted
- 17778b8 W7: six headline-subset tables moved to supplementary.tex (Tables S1-S6); app:subsets reduced to one paragraph with overlap counts
- cba2bf9 W8: abstract replaced (word count checked by script)
- e09c6b5 F8: generative-AI declaration extended to the restructuring and the new figure and tables
- 4bfb9b0 F6: trim 'Deployment at scale' to under 200 words
- 6b8642b F6: new Discussion subsection 'Deployment at scale' after subsec:cross_dataset
- 24a83de F5: 'Scalability and cost' rebuilt (matched measurement first, cost-structure table, usage and memory), unmatched runtimes moved to new appendix app:robustness
- 435309a F4: 'Scale of the selection problem' figure (fig:scale) in the datasets subsection with a pointer sentence
- 5211d26 F3: keyword Covariate shift -> High-dimensional data; five new highlights in the .tex comment block and highlights.txt
- e7dfde2 F2: scale paragraph in the Introduction, first contribution names the scale, big-data framing moved forward in Related Work
- e6ecb8c F1: new title in \title and pdftitle
- 42ffcf8 2.1-2.3: orientation (baseline build, word counts, number inventory, CSV inventory)
- 3d78c42 Baseline: pre-existing uncommitted layout changes committed unmodified before the revision
