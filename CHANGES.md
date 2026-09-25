# CHANGES

Revision of the Big Data Research manuscript, prompts 1 to 3. Branch `revision-presentation`; baseline commit `336b3f0`.

## Files

**Manuscript files.**
- Main manuscript: `submission/manuscript.tex`, the file containing `\begin{thebibliography}`.
- Supplement: `submission/supplementary.tex`, whose title starts "Supplementary material".
- `manuscript.tex` in the repository root is an older duplicate. It is not edited (see Author decisions).

**Baseline.** `baseline/manuscript.tex` and `baseline/supplementary.tex` are byte-identical copies of the two files at `48050cd`, the tip of `revision/presentation-and-fit`. They were committed unchanged as `336b3f0`.

**Outputs.**
- `baseline/metrics.json`: `tools/measure.py` run on the baseline main file (with the supplement), plus the compile record of the baseline.
- `baseline/tables.json`: `tools/extract_tables.py` run on both baseline files.
- `metrics_after_p1.json`: `tools/measure.py` run on the files after Prompt 1, plus the compile record.

**Tools.** All three use the Python 3 standard library only.

### `tools/measure.py`

Usage: `python3 tools/measure.py MAIN.tex [--supplement SUPP.tex] [--log MAIN.log] [-o OUT.json]`. It writes one JSON object.

**Preprocessing.**
- `lstlisting` blocks are protected from comment removal.
- Comments are removed as TeX does: from an unescaped `%` to the end of the line, together with the line break and the next line's leading blanks.
- The body is the text between `\begin{document}` and `\end{document}`.
- Zero-argument `\newcommand` macros are expanded, for example `\Kfeat` becomes `K`.

**Running text** is the body minus:
- `table`, `table*`, `figure` and `figure*` environments, with their captions;
- display maths (`equation`, `align`, `gather`, `multline`, `eqnarray`, their starred forms, `displaymath`, `\[..\]`, `$$..$$`);
- `lstlisting`, `thebibliography` and `tikzpicture`;
- any stray `\caption{}`.

A removed block that stands on its own lines inside a paragraph does not split the paragraph.

**Paragraphs** are split at blank lines, `\par`, `\item` and the begin or end of `itemize`, `enumerate` and `description`. Titles of `\section`, `\subsection`, `\subsubsection` and `\paragraph` are not counted.

**Plain-text conversion.**
- `\label` and `\cite` are dropped.
- `\ref`, `\eqref` and `\pageref` count as one word each, as do `\url` and `\path`.
- Each inline formula `$..$` counts as one word.
- Other commands are dropped and their braced text is kept, so `\emph{x}` becomes `x`.
- `--` and `---` become dashes, so `0.7106--0.7181` is one word.
- `~` and `\ ` are non-breaking spaces.

**Word:** a whitespace-separated token containing at least one letter or digit.

**Output keys.**
- (a) `words`:
  - `sections_1_8` covers the running text from `\section{Introduction}` to `\appendix`. As the prompt specifies, this includes the five unnumbered sections before `\appendix` (CRediT to Data availability).
  - `sections_1_8_numbered_only` excludes those five sections.
  - `per_section` gives one total per `\section`; `abstract` counts the abstract environment.
- (b) `paragraphs_by_subsection`: word count of every paragraph, grouped by section, subsection and subsubsection.
- (c) `long_sentences`: sentences in Sections 1–8 with more than 45 and more than 60 words (strictly greater), counted and listed.
  - A sentence ends at `.`, `!` or `?`, optionally followed by a closing quote or bracket. It must then be followed by an ordinary space and an upper-case letter, digit, bracket, quote or `$`.
  - A sentence never ends at a non-breaking space.
  - A sentence never ends after `al. e.g. i.e. cf. vs. Eq. Eqs. Fig. Figs. Sec. Secs. No. approx. resp. viz.` or a single capital initial.
- (d) `phrase_counts`: case-insensitive substring counts after whitespace normalisation, so `descriptive` also counts `descriptively`. The phrases are "materiality bar", "covariate-shift", "not adjusted", "descriptive", "held-out rule", "development rule", "development-rule" and "most adversarial". Two sets are given:
  - the running text of Sections 1–8;
  - the whole Sections 1–8 span including tables, captions and table notes, with figure code excluded.
- (e) `tables_before_appendix`: number of `\begin{table}` and `\begin{table*}` before `\appendix`.
- (f) `labels` lists every `\label` key in order (duplicates go to `labels_duplicated`); `cite_keys` is the sorted set of `\cite` keys.
- (g) `numbers`: numeric tokens with their counts.
  - A token is an optional sign followed by one of: an ISO date or year-month; an integer or decimal with thousands commas (`1,068`); or an integer, decimal or dotted version (`3.13.5`).
  - The sign may be `+`, `-` or U+2212, normalised to `-`. A hyphen counts as a sign only when no letter or digit precedes it.
  - The token must not be joined on its left to a letter, digit, underscore, decimal point or comma, nor on its right to a letter, digit or underscore. So `F001`, `static_0`, `i7` and `24mm` give no token.
  - In maths, commands are dropped, `{,}` is a thousands separator and other commas separate items, so `\{100,200,300\}` gives three tokens.
  - The keys of `\label`, `\ref` and `\cite`, and the contents of `\url` and `\path`, are ignored.
  - Three sets are reported:
    - `running_text_whole_document`: the abstract plus everything after `\end{frontmatter}`, with the running-text exclusions;
    - `running_text_sections_1_8`;
    - `all_body`: the whole body including floats, captions, notes, maths, the verbatim prompt and figure code, but without comments and `thebibliography`.
  - With `--supplement`, the supplement's `all_body` set is added under `supplement`.
- (h) `highlights`: the lines `% - ...` after `% HIGHLIGHTS`, up to the closing `% ---` line. Each length is the character count of the text after `% - `. `keywords` holds the `\sep`-separated items of the keyword environment.
- `--log` adds `compile`, taken from a pdflatex log:
  - counts of `Overfull \hbox`, `Underfull \hbox` and `Overfull \vbox`;
  - undefined references and citations, and whether "There were undefined references" appears;
  - whether "Label(s) may have changed" appears;
  - multiply defined labels and the page count.

### `tools/extract_tables.py`

Usage: `python3 tools/extract_tables.py FILE.tex [FILE2.tex ...] [-o OUT.json]`.
- Comments are removed first.
- For every `table` or `table*` environment, the tool takes the first `\label` inside it as the key, or `unlabelled:FILE:N` when there is none.
- For every `tabular`, `tabular*`, `tabularx` or `longtable` inside, it takes the body: the text between the column specification (after the width argument, if any) and the matching `\end`. Every whitespace run is collapsed to one space.
- Several tabulars in one table are joined with ` ||| `.
- Output: `{"sources": [...], "tables": {label: body}, "colspecs": {label: spec}, "envs": {label: env}, "files": {label: file}, "other_labels": {label: [...]}}`.

### `tools/check_p1.py`

Usage: `python3 tools/check_p1.py --baseline-commit 336b3f0 [--compile-dir DIR | --log LOG] [-o REPORT.json]`. It runs checks S1–S7 of Prompt 1 on `submission/*.tex` against `baseline/`, using the two tools above.
- S1: optionally compiles the main file twice into DIR, then reads the log.
- S2: compares labels, cite keys and the raw `thebibliography` block.
- S3: compares table bodies and column specifications. For the two tables A1 may change, it lists inserted and removed rows (rows are split at `\\`).
- S4: takes the `all_body` tokens of the new main and supplement that are absent from baseline main ∪ supplement, and checks that each appears under "Derived numbers" in this file.
- S5: compares the raw R6 blocks:
  - the title and `pdftitle`;
  - the `lstlisting`;
  - the generative-AI declaration;
  - the CRediT, Funding, Disclaimer, Competing-interest and Data-availability sections;
  - the AI-assistance sentence of each figure caption.
- S6:
  - lists every sentence (text, captions and notes) containing "immaterial" and flags any that says "all three datasets", "all four", "every case" or "all six";
  - checks that the two retired phrases are gone;
  - checks that the identity-line paragraph mentions "union";
  - checks that every paragraph from Section 2 onward that cites the timing measurement says "unscreened 1,959-feature universe";
  - checks the A5 evidence.
- S7: runs `git diff --cached --name-status` against the baseline commit, so the files of the commit must be staged first.

## Prompt 1

### Step 1: safety and baseline

- Branch `revision-presentation` was created from `revision/presentation-and-fit` at `48050cd`. Commit `336b3f0` adds the untouched copies in `baseline/`.
- The baseline was compiled with pdflatex twice in the scratchpad; both passes exited with 0.
  - It has 36 pages, 0 Overfull `\hbox`, 1 Underfull `\hbox` and no undefined references or citations.
  - Pass 2 reports "Label(s) may have changed". A third pass writes an identical `.aux` and the warning disappears. This is recorded in `baseline/metrics.json`.
- Baseline metrics:

  | Metric | Value |
  |---|---|
  | Words, Sections 1–8 | 16,889 (16,722 without the unnumbered back-matter sections) |
  | Words, abstract | 243 |
  | Sentences over 45 / over 60 words | 129 / 49 |
  | Tables before `\appendix` | 13 |
  | Labels | 83 (no duplicates) |
  | Cite keys | 55 |
  | Highlight lengths (characters) | 81, 83, 78, 82, 69 |
  | Keywords | 7 |

### Step 2: corrections

All edits are in `submission/manuscript.tex`. The supplement is unchanged.

**A1, LendingClub LR response sampling.** Every fact below was checked against `priority_2/perfold_rankings_ho_auc.csv`, `priority_1/full_matrix.csv` and `priority_1/pairwise.csv` (see Derived numbers).

- (a) Immateriality claims found and replaced:
  - `subsec:stability_results`, end of the second paragraph. "Response sampling at a fixed prompt is therefore immaterial at the held-out AUC level in all three datasets" is replaced by four sentences:
    - the five fold spreads leave out the sixth, full-DEV response, which lies inside the fold range or within 0.003 of it in three cases;
    - on LendingClub v2 LR it gives 0.7402, 0.022 above the best fold response, so the six-response spread is 0.0296;
    - the requested statement follows;
    - with any fold response the margin would be 0.0008 to 0.0083 over IV then Boruta (0.7098) and 0.0117 to 0.0192 over RFE CatBoost (0.6989).
  - Note to `tab:response_spread`. "Every spread lies inside the materiality bar, so the choice of cached response is immaterial ... in all three datasets" is replaced by "Every spread over the draws lies inside the materiality bar", followed by the requested statement and the 0.0008 to 0.0083 margin.
  - Limitations, fourth paragraph. "place the response spread inside the materiality bar in all four cases" is replaced by the requested statement.
  - The Discussion and the Conclusion contained no such claim. The Discussion's summary of the response checks (Section 7.1, RQ2 paragraph) now adds the Home Credit and LendingClub result (see (c)).
- (b) `tab:response_spread`:
  - The full-DEV cached value is given in a new first table note, labelled in italics *Full-DEV cached response*. The note gives the six values (0.7436, 0.7935, 0.7402, 0.7335, 0.8344, 0.8784), states that they are not among the draws, and states the 0.022 and 0.0296 facts.
  - No cell was changed. The note replaces the extra column first tried, because that column made the table 36.8 pt too wide (see Author decisions).
  - The text points to the note.
- (c) `tab:robustness`:
  - One row was inserted after "Ten repeated LLM calls (Stability 2024)":
    - Check: "Five per-fold responses (HC, LC)"
    - What it rules out: "A favourable response"
    - Result: the facts above
    - Headline holds?: "Partly (LC LR)"
    - Source: Section `subsec:stability_results`
  - The caption now defines HC, LC and LR.
  - `subsec:robustness` now says "thirteen checks" (was "twelve").
  - The sentence "Under every check the LLM-assisted leader remains ahead in the same five cases" now continues "and the headline holds under all but one". Two new sentences name the exception, with 0.022, 0.0008 to 0.0083 and 0.0117 to 0.0192.
  - "with a repeated response" is now "with a repeated response on Stability 2024".
  - Discussion, Section 7.1 (RQ2 paragraph): two sentences were added after the Stability 2024 repeat sentence. They state the Home Credit and LendingClub result and the requested statement.
- (d) Development-to-holdout asymmetry:
  - Section 6.1, after "The LLM-assisted leaders move by −0.010 to +0.012 and rise in three cases": on Home Credit and LendingClub an LLM-assisted leader's DEV mean comes from the fold rankings and its HO value from the full-DEV ranking. For LendingClub LR, the DEV mean (0.7436) and the HO value (0.7402) come from different rankings, the full-DEV one being the favourable response, so the change also reflects the difference between responses.
  - Section 7.1: one sentence gives the same note for LendingClub LR.

**A2** (`subsec:obfuscation_results`). "the full-DEV overlaps lying at the low end of the fold ranges" is replaced. The full-DEV overlap lies below the fold range for arm A with LR (11 against 12 to 18) and for arm B with CatBoost (24 against 26 to 33), and in the lower part of the range in the other two rows (17 in 15–28; 14 in 14–19).

**A3** (`subsec:stability_results`). "0.14 to 0.42 wide" is now "0.13 to 0.42 wide".

**A4** (`subsec:stability_results`). The identity-line explanation was rewritten:
- the main reason is the denominators: Jaccard divides the overlap by the union of the two subsets, whereas for subsets of equal size $\hat\Phi$ behaves like the overlap relative to the subset size, which the union exceeds whenever the subsets differ;
- at universe sizes of 373 to 1,068 the chance correction is small;
- the correction grows as the universe shrinks, so a smaller $d$ gives a lower $\hat\Phi$ (kept).

For the record, with fixed subset size $k$ and mean pairwise overlap $\bar r$, Eq. (nogueira) reduces to $(\bar r-k^2/d)/(k-k^2/d)$, which tends to $\bar r/k$ as $d$ grows. Jaccard is $r/(2k-r)$.

**A5.** Resolved by file evidence, and no number was changed.
- `priority_2/diversity_capped_ho_auc.csv` records the family-capped mRMR run on Home Credit LR (`homecredit,lr,family_cap,mRMR,20,0.745693`, with fold AUCs 0.719514 to 0.751122). This confirms the 0.7457 printed in `tab:diversity` and in the `app:robustness` family-cap paragraph.
- The superseded RF/correlation value of `app:protocol` ("the earlier value (0.7457)") is in no result CSV. Its six-decimal record is the archived first manuscript, `archive/manuscript_v1_long.tex:1650`: Table "Stage-2 Home Credit evaluation", row `Full-pool mRMR & LR & $529\rightarrow20$ & 0.745689`.
- 0.745693 and 0.745689 differ in the sixth decimal, so the two four-decimal values come from two different runs and agree only after rounding. Neither was copied from the other.
- For comparison, the RF/correlation reference of the final protocol on the 373-feature candidate set is 0.7448 (`tab:voting_cross`).
- No `% TODO` was added.

**A6.** The measurement is over the unscreened universe (`priority_2/mrmr_pool_timing.csv`: `homecredit_model_stability_2024,fold1,1959,522.15` and `...,100,20.52`). This is now stated at every mention in Sections 2–8 and the appendices:
- Section 3.1 (Background), which cites it without numbers: "one matched measurement, taken over the unscreened 1,959-feature universe of Stability 2024, is reported in ...". The sentence was split in two.
- Section 6.5: "over the unscreened 1,959-feature universe", plus a new sentence: "The unscreened universe is not the pool that stand-alone mRMR searches in the protocol, the 1,068-feature candidate set, and the saving against that set was not measured."
- Section 7.4: "over the unscreened 1,959-feature universe", plus "Stand-alone mRMR in the protocol searches the 1,068-feature candidate set, not the unscreened universe."
- Appendix F, unmatched wall-clock times: "the one exception ..., an mRMR pass over the unscreened 1,959-feature universe of Stability 2024 against one over a 100-feature pool".

The abstract ("over the full universe") and the Introduction (Section 1, third paragraph) are left for Prompt 3, as instructed. No number was changed.

**Sentence lengths.** Three sentences that had grown past 45 words were split: Section 3.1, the identity-line sentence and Section 7.4.

**Size after Prompt 1** (`metrics_after_p1.json` against `baseline/metrics.json`):

| Metric | Baseline | After Prompt 1 |
|---|---|---|
| Words, Sections 1–8 | 16,889 | 17,389 (+500) |
| of which Background | | +9 |
| of which Results | | +371 |
| of which Discussion | | +120 |
| Words, Sections 1–8 without back matter | 16,722 | 17,222 |
| Words, abstract | 243 | 243 |
| Sentences over 45 words | 129 | 126 |
| Sentences over 60 words | 49 | 46 |
| Tables before `\appendix` | 13 | 13 |
| Highlights and keywords | | unchanged |
| Pages | 36 | 37 |

### Step 3: self-check

Run with `python3 tools/check_p1.py --baseline-commit 336b3f0 --compile-dir <scratch>`, with the files of the Prompt 1 commit staged.

| Check | Result | Evidence |
|---|---|---|
| S1 | PASS | pdflatex twice, exit 0 on both passes. 0 Overfull `\hbox` (baseline 0, limit 2); 1 Underfull `\hbox`, as in the baseline. No undefined references or citations. 37 pages. As in the baseline, pass 2 reports "Label(s) may have changed"; a third pass writes an identical `.aux` with no warning. |
| S2 | PASS | All 83 baseline labels present; no new or duplicated labels. The cite-key set is identical (55 keys). The `thebibliography` block is byte-identical. |
| S3 | PASS | 25 tables compared (19 main, 6 supplement). 24 are identical in body and column specification, including `tab:response_spread`, whose A1(b) addition is a table note. `tab:robustness` keeps its column specification; one row is inserted (the A1(c) row, after "Ten repeated LLM calls"), and all 12 existing rows are unchanged and in order. |
| S4 | PASS | Tokens absent from baseline main + supplement: 0.0008, 0.003, 0.0083, 0.0117, 0.0192, 0.0296, 0.13. All are listed under Derived numbers. |
| S5 | PASS | 14 blocks identical to the baseline: title, `pdftitle`, the prompt `lstlisting`, the generative-AI declaration, CRediT, Funding, Disclaimer, Competing interest, Data availability, and the AI-assistance notes of the five figure captions. |
| S6 | PASS | See the list below. |
| S7 | PASS | `git diff --cached --name-status 336b3f0` lists `CHANGES.md`, `baseline/metrics.json`, `baseline/tables.json`, `metrics_after_p1.json`, `submission/manuscript.tex` and `tools/{measure,extract_tables,check_p1}.py`. The supplement is unchanged. `metrics_after_p1.json` is the one file outside the S7 list; Step 3 itself requires it. The unstaged deletion of `checks.md`, which predates this session, is not in the commit. |

**S6 in detail.**

1. Every sentence containing "immaterial". None claims immateriality in all three datasets or in all four Home Credit and LendingClub cases.
   - §5.6: "... a spread below 0.010 being treated as immaterial response sampling." (definition of the bar)
   - §6.4.1: "Both spreads, 0.0095 at K=20 and 0.0092 at K=40, are themselves inside that bar, so on this dataset the choice of cached response is immaterial at both budgets by the study's own standard." (Stability 2024 only)
   - §6.4.1: "Response sampling at a fixed prompt is therefore immaterial on Stability 2024 and in three of the four Home Credit and LendingClub cases."
   - §7.6: "Response sampling is immaterial on Stability 2024 and in three of the four Home Credit and LendingClub cases; on LendingClub logistic regression the headline response is favourable, and with any of the other five cached responses the held-out-rule margin would fall below the bar."
   - Note to `tab:response_spread`: "Response sampling is immaterial on Stability 2024 and in three of the four Home Credit and LendingClub cases; on LendingClub v2 LR the headline response is favourable, and with any of the other five cached responses the margin over the held-out-rule classical leader, IV then Boruta (0.7098), would be 0.0008 to 0.0083, below the bar."
2. "low end of the fold ranges" and "0.14 to 0.42" no longer appear in the source.
3. The `fig:stability` explanation reads: "Jaccard divides the overlap of two subsets by their union, whereas for subsets of equal size $\hat\Phi$ behaves like the overlap relative to the subset size, ...".
4. The 522 s / 21 s measurement is mentioned in four paragraphs from Section 2 onward, and all four say "unscreened 1,959-feature universe": Section 3.1, Section 6.5, Section 7.4 and Appendix F (unmatched wall-clock times). The abstract and the Introduction are deferred to Prompt 3.
5. A5 is resolved with file evidence: the capped value 0.745693 is in `priority_2/diversity_capped_ho_auc.csv`; the superseded value is 0.745689 in `archive/manuscript_v1_long.tex:1650`. The manuscript values are unchanged and there is no `% TODO`.

### Observations outside Prompt 1 (not acted on)

- The headline paragraph of Section 6.1 still says only "for the cached rankings". It gives the Stability 2024 repeat result but not the LendingClub LR response result, which is now in Sections 6.2, 6.4.1 and 7.
- Section 5.6 says the headline comparisons rest on "one [response] per case, ten on Stability 2024". The five per-fold responses of Home Credit and LendingClub are measured in Section 6.4.1.
- With a fold response on HO, the LendingClub LR pure LLM leader would lose 0.026 to 0.033 from its DEV mean (0.7436 − 0.7181, 0.7436 − 0.7106). That is more than the development-rule classical leader loses (0.022). The paper now says that this change mixes responses, but does not quantify it. These two differences are not printed anywhere.

## Prompt 2

## Prompt 3

## Derived numbers

The computations use the four-decimal values printed in the baseline tables. The last column cross-checks them at full precision in the result files (R1: read only, to verify).

| Number | Used in | Computation from printed values | Full precision (result files) |
|---|---|---|---|
| 0.022 | §6.2 (robustness text, "at least 0.022"), §6.4.1, `tab:robustness` new row, note to `tab:response_spread` | LendingClub LR pure LLM full-DEV 0.7402 (`tab:full_matrix`) − best fold response 0.7181 (`tab:response_spread`) = 0.0221 | 0.740234 − 0.718101 = 0.022133 |
| 0.0296 | §6.4.1, `tab:robustness` new row, note to `tab:response_spread` | spread over six cached responses: 0.7402 − 0.7106 = 0.0296 | 0.740234 − 0.710636 = 0.029598 |
| 0.0008 | §6.2, §6.4.1, `tab:robustness`, note to `tab:response_spread` | lowest fold response 0.7106 − IV then Boruta 0.7098 (`tab:primary_results`) = 0.0008 | 0.710636 − 0.709803 = 0.000833 |
| 0.0083 | same places as 0.0008 | highest fold response 0.7181 − 0.7098 = 0.0083 | 0.718101 − 0.709803 = 0.008298 |
| 0.0117 | §6.2, §6.4.1, `tab:robustness` | 0.7106 − RFE CatBoost 0.6989 (`tab:confirmatory`, `tab:full_matrix`) = 0.0117 | 0.710636 − 0.698881 = 0.011755, which rounds to 0.0118 (see Author decisions) |
| 0.0192 | §6.2, §6.4.1, `tab:robustness` | 0.7181 − 0.6989 = 0.0192 | 0.718101 − 0.698881 = 0.019220 |
| 0.003 | §6.4.1, `tab:robustness`, note to `tab:response_spread` | largest distance of a full-DEV response outside its fold range, excluding LendingClub LR: Home Credit LR 0.7436 − 0.7410 = 0.0026 ≤ 0.003. The other four cases lie inside their ranges: Home Credit CatBoost 0.7935 in 0.7926–0.7998, LendingClub CatBoost 0.7335 in 0.7324–0.7362, Stability 2024 LR 0.8344 in 0.8300–0.8395, Stability 2024 CatBoost 0.8784 in 0.8740–0.8832 | 0.743635 − 0.741038 = 0.002597 |
| 0.13 | §6.4.1 (A3) | narrowest fold-pair spread of a pure LLM list, LendingClub CatBoost: Max 0.538 − Min 0.404 = 0.134 (`tab:stability`). The other widths are 0.417, 0.278 and 0.350, so the range is 0.13 to 0.42 | not needed (printed table) |

These are the only numeric tokens absent from the baseline (S4). Two related changes are not new tokens:
- The number word "thirteen" in `subsec:robustness` is the twelve baseline rows plus the new one.
- Printed values reused in new sentences without change: 0.7402, 0.7436, 0.7935, 0.7335, 0.8344, 0.8784, 0.7106, 0.7181, 0.7098, 0.6989, 0.0075, 11, 12, 18, 24, 26, 33, 1,068, 1,959 and 100.

## Unresolved

None in Prompt 1. The abstract and Introduction mentions of the timing measurement are deferred to Prompt 3 by instruction (A6), not unresolved.

## Author decisions

1. **Which files.** The canonical files are `submission/manuscript.tex` and `submission/supplementary.tex`. The root `manuscript.tex`, which also contains `\begin{thebibliography}`, is an older duplicate (24 September) and was not edited. `baseline/`, `tools/`, `CHANGES.md` and `metrics_after_p1.json` sit in the repository root so that `submission/` keeps only submission files.
2. **Existing working-tree change.** An unstaged deletion of the tracked file `checks.md` predates this session. It was left as it is and is not part of either commit.
3. **Note instead of column.** A1(b) is done with a table note, not an extra column. A tenth column made `tab:response_spread` 36.8 pt wider than the text block (Overfull `\hbox`, table in the margin). The note leaves the tabular untouched.
4. **0.0117 kept.** The A1 range 0.0117–0.0192 is kept as specified, because it follows from the printed four-decimal values. At full precision the lower end is 0.011755, which rounds to 0.0118. Writing 0.0118 would not follow from any printed number.
5. **"Any other cached response".** This is rendered as "any of the other five cached responses". On LendingClub the LR pipeline uses the budget-20 ranking of its partition, so the five fold rankings are the other cached responses at that budget.
6. **Where A1(d) was applied.** It was applied where the asymmetry is discussed (Section 6.1) and in Section 7.1. The one-clause restatements in the abstract, the highlights and the Conclusion carry no LendingClub LR values, and adding a clause there would lengthen summary text that Prompts 2 and 3 revise, so they were left unchanged. The last row of `tab:stages` also states the asymmetry, but it is a table cell (R3), so it was not changed.
7. **Discussion summary under A1(c).** A1(c) asks to adjust "any similar summary in the Discussion". This was taken to include the Discussion's summary of the response check (Section 7.1, RQ2 paragraph), which reported Stability 2024 only; two sentences were added there. The headline paragraph of Section 6.1 was not changed (see Observations).
8. **A5 counted as resolved.** A5 is treated as resolved by file evidence. The capped value is in a result CSV. The superseded value's six-decimal record is an archived manuscript table rather than a result CSV. No `% TODO` was added.
9. **Scope of A6.** "Sections 2–8 and the appendices" was read to include the Section 3.1 sentence that cites the measurement without numbers. The abstract and Introduction are unchanged, as instructed.
10. **PDFs and zip not rebuilt.** `submission/manuscript.pdf` and `submission/manuscript_source.zip` were not rebuilt, because S7 restricts the changed files. They now lag `submission/manuscript.tex` and should be rebuilt together after Prompt 3. The compiled PDF of this state is only in the scratchpad (37 pages; the baseline had 36).
11. **Word-count span.** "Sections 1–8" follows the prompt's explicit span, `\section{Introduction}` to `\appendix`, which includes the unnumbered back-matter sections. The total without them is reported alongside.
