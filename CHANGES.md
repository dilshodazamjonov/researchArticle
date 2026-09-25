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
- `metrics_after_p2.json`: the same, after Prompt 2.

**Tools.** All four use the Python 3 standard library only.

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
- Since Prompt 2, `extract(path, text=None)` also accepts the file content directly; this is used to read a file at a given commit. The output is unchanged, and baseline output was re-verified as identical.

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

### `tools/check_p2.py`

Usage: `python3 tools/check_p2.py --p1-commit 901c263 [--compile-dir DIR | --log LOG] [-o REPORT.json]`. It runs checks S1–S5 and P1–P8 of Prompt 2 on `submission/manuscript.tex`.
- "Sections 2–8" means the numbered sections from `\section{Related Work}` to the Conclusion, excluding the unnumbered back matter (CRediT to Data availability). Its running-text word count is the sum of `measure.py`'s `per_section` totals for Related Work to Conclusion; the baseline is 15,824 words.
- S1: optionally compiles twice into DIR, then reads the log.
- S2 and S5: as in `check_p1.py`, against `baseline/`.
- S3: compares every table body, matched by label, with the file at the Prompt 1 commit (read through `git show`) plus the supplement.
- S4: finds `all_body` tokens absent from baseline main ∪ supplement and checks that each is under "Derived numbers".
- P1: reduction of the Sections 2–8 running-text words against the baseline; passes at 25% or more.
- P2: takes the numeric tokens of the baseline Sections 2–8 span (text, captions, notes and cells). Each must occur somewhere in the new main file, or appear in back-quotes under "### Removed duplicates" in this file.
- P3: phrase counts over Sections 2–8 in three scopes: running text; plus captions and table notes; plus table cells. The pass test uses the second scope, which covers all editable text; the third scope is reported.
- P4: table/table* count before `\appendix`, the position of the two moved labels, and the absence of undefined references.
- P5: checks that `\label{subsec:dev_to_ho}` exists; that every paragraph of the Headline comparison subsection is 120 words or fewer; that nine protected-attribute facts occur in the Discussion; and that none is left in the Results.
- P6: sentences of Sections 2–8 over 45 and over 60 words.
- P7: Conclusion words, and the location of "522" in the running text of Sections 2–8.
- P8: byte comparison of the Introduction, abstract, keywords and highlights block with the Prompt 1 commit.

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

### Step 0: precheck

- On branch `revision-presentation` at `901c263`. The Prompt 1 self-check is all PASS, Unresolved was empty, and `tools/` was present.
- No Prompt 1 correction was undone:
  - A1: the response-sampling statement stays in §6.6.1, the note to `tab:response_spread` and §7.7, with short versions in §6.4 and §7.1. The LendingClub LR DEV/HO ranking note is in §6.2 and §7.1. The `tab:robustness` row is unchanged.
  - A2: the overlap wording is in §6.5.1. A3: "0.13 to 0.42" is in §6.6.1. A4: the union-denominator explanation is in §6.6.1.
  - A6: "unscreened 1,959-feature universe" appears at every mention of the timing measurement (§3.1, §6.7, §7.5, Appendix F).

### Step 1: edits

**Method.** Sections 2–8 were rewritten from the post-Prompt-1 text. A build script took every table, figure and equation verbatim from the Prompt 1 commit and placed them by label into the new running text. Table bodies, figure code and equations are therefore byte-identical (S3); only captions and the table-note sentences listed below changed.

**B1, each caveat stated once.**
- HO is calendar-later only for LendingClub and Stability 2024, and a recency-based covariate-shift holdout for Home Credit.
  - Home: §5.1 and §5.2.
  - Replaced by pointers in §3.3, §6.6.2 and §7.7.
  - Deleted from the captions of Figure 1 and `tab:datasets`.
- The HO-rule comparison is descriptive, and its intervals are not adjusted for selection.
  - Home: §5.6.
  - Kept in the captions of `tab:primary_results`, `tab:confirmatory` and `fig:primary`.
  - Removed from §6.1, §7.1 and §8; §7.7 keeps a one-clause pointer.
- The protocol evolved with knowledge of held-out results.
  - Home: §4.6.
  - Pointers in §4.1, §5.2, §5.6 and §5.7; one clause in §7.7.
  - Deleted from the Figure 1 caption.
- The materiality bar of 0.010.
  - Home: §5.6, where it is named "the materiality bar" once; everywhere else it is "the bar".
  - The value was removed from the captions of `tab:robustness`, `tab:mechanical` and `tab:response_spread` and from the notes, which now point to §5.6.
- Balanced class weights make the Brier score uninformative about calibration.
  - Home: §5.5.
  - Pointers in §6.6.2 and in the `tab:secondary` caption; §7.7 keeps a short clause.
- Nogueira values are not comparable across universe sizes $d$.
  - Home: §3.4.
  - Pointers in §6.6.1 and in the `fig:stability` caption.
  - Removed from the `tab:response_lists` caption; the `tab:stability` note was shortened.

**B2, leader-rule names.** §5.6 defines the three names:
- the *HO rule*;
- the *DEV rule*;
- the *mixed rule*, which pairs the DEV-rule LLM-assisted leader with the HO-rule classical leader and is the least favourable pairing for the LLM-assisted family.

Every variant in the text and captions of Sections 2–8 was replaced: "held-out rule" and "held-out-rule", "development rule" and "development-rule", "most adversarial pairing". The `tab:confirmatory` caption now reads "Held-out (HO) comparison under the DEV rule". Counts are under P3 below.

**B3, Results restructured.**
- New order:
  - §6.1 Headline comparison: four paragraphs of 119, 119, 84 and 112 words, covering the HO rule, the DEV rule, the mixed rule, and why the rules are not independent checks.
  - §6.2 Development-to-holdout degradation (new, `subsec:dev_to_ho`). It carries the 0.008–0.022 against −0.010 to +0.012 finding, its link to the agreement between the rules, and the LendingClub LR note from Prompt 1.
  - §6.3 Within-family comparison (new, `subsec:within_family`). It is the condensed paragraph: means of the non-floor selectors, pure LLM against the hybrids, and the LLM then Boruta budget note.
  - §6.4 Robustness, §6.5 What drives the result, §6.6 Stability, drift and secondary metrics, §6.7 Scalability and cost.
- The protected-attributes paragraph moved to the new §7.6 "Governance and protected attributes" (`subsec:governance`), with every fact. The protected-attribute sentence of the Limitations was merged into it.
- The protected-attribute paragraph of §4.4 was tightened and kept.

**B4, table moves.**
- `tab:response_lists` is now Table F.4 and `tab:cost_structure` Table F.5, both at the end of `app:robustness`.
- Their one-sentence summaries with `\ref` pointers stay in §6.6.1 and §6.7.
- Tables before `\appendix`: 13 → 11.
- Further moves are only proposed (Author decisions).

**B5, Discussion.**
- §7.1 was rewritten to interpret, with at most one number per claim and a table pointer.
- §6.7 now reports measurements only: timing, tokens and cost, hardware and memory, plus the Table F.5 pointer.
- The cost-structure interpretation moved to §7.5.
- The 522 s / 21 s sentence appears only in §6.7. §3.1 and §7.5 refer to the measurement without its numbers and keep "unscreened 1,959-feature universe".

**B6, Conclusion.** 585 → 348 words, in the order findings, practical implication, research implication, next steps. It adds no new claim.

**B7, style.**
- No sentence of Sections 2–8 exceeds 45 words; in the baseline 125 did, and 46 exceeded 60.
- In the running text, ΔAUC values were rounded to three decimals, and AUC stays at four:
  - obfuscation: −0.0012, +0.0042, −0.0290 and −0.0310 become −0.001, +0.004, 0.029 and 0.031;
  - lineage-only arm: −0.0064 to +0.0066, +0.0086 and −0.0018 become −0.006 to +0.007, +0.009 and −0.002;
  - voting: +0.0020 to +0.0129 becomes +0.002 to +0.013;
  - fold-response margins: 0.0008 to 0.0083 becomes 0.001 to 0.008, and 0.0117 to 0.0192 becomes 0.012 to 0.019.
  - The four-decimal exceptions are listed under Author decisions.
- LR is defined at first use in the running text (§5.3).
- Tightened without dropping facts:
  - §4.1 with its list: 538 → 311 words;
  - §5.1: 1,014 → 851;
  - §5.2: 685 → 534;
  - §4.4: 1,374 → 794.
  - Also §6.1: 1,324 → 434; §7.1: 738 → 455; §7.7: 992 → 590.

**B8, captions.** Method descriptions that repeat the text were cut, keeping what is needed to read each float:
- Figure 1: dropped the ordering-index sentence and the earlier-inspection caveat.
- `tab:methods`, `tab:datasets` and `fig:scale`: shortened.
- `tab:primary_results`, `tab:confirmatory` and `fig:primary`: the HO-rule caveat kept (B1).
- `tab:full_matrix`, `tab:robustness`, `tab:obfuscation`, `tab:mechanical`, `tab:stability`, `tab:response_spread`, `tab:response_lists`, `fig:stability` and `tab:secondary`: shortened.
- The `tab:stability` notes [a] and [b] and the second `tab:response_spread` note were shortened. In that note, "materiality bar" became "bar" and "held-out-rule" became "HO-rule".
- All five AI-assistance notes are unchanged (S5).

**Appendices.** Only duplicated caveats were removed:
- "read against the materiality bar of 0.010" in the captions of `tab:lc_maturity` and `tab:diversity`, now a pointer to §5.6;
- the clause "so this difference describes the resolved-loan population and should be read with that construction in mind" in the LendingClub paragraph of `app:robustness`.

### Step 2: self-check

Run with `python3 tools/check_p2.py --p1-commit 901c263 --compile-dir <scratch>`.

| Check | Result | Evidence |
|---|---|---|
| S1 | PASS | pdflatex twice, exit 0 on both passes. 0 Overfull `\hbox` (baseline 0); 1 Underfull `\hbox`, as in the baseline. No undefined references or citations. 33 pages (baseline 36). Pass 2 reports "Label(s) may have changed", as the baseline does; pass 3 writes an identical `.aux` with no warning. |
| S2 | PASS | All 83 baseline labels exist. The new labels are `subsec:dev_to_ho`, `subsec:within_family` and `subsec:governance`, none duplicated. The 55 cite keys are the same set. `thebibliography` is byte-identical. |
| S3 | PASS | All 25 table bodies (19 main, 6 supplement) equal their state at the Prompt 1 commit, matched by label. The two moved tables are included. |
| S4 | PASS | Tokens absent from baseline main + supplement: +0.002, +0.007, −0.001, −0.002, −0.006, 0.012, 0.019 and 0.029 (new in Prompt 2), plus the seven from Prompt 1. All are under Derived numbers. |
| S5 | PASS | 14 R6 blocks are identical to the baseline. |
| P1 | PASS | Sections 2–8 went from 15,824 to 11,757 words, 25.7% shorter. This is above the 25% floor but below the 30% target (Author decisions). |
| P2 | PASS | Every baseline Sections 2–8 token still occurs in the document except `0.027`, `29` and `0.14`, which are listed under "Removed duplicates" below with the place where each value survives. |
| P3 | PASS | Counts in the text, captions and table notes of Sections 2–8 are within the limits: "materiality bar" 2 (≤ 6), "covariate-shift" 1 (≤ 3), "not adjusted" 4 (≤ 4), "descriptive" 5 (≤ 6). "held-out rule", "development rule", "development-rule" and "most adversarial" are all 0. Counting table cells as well, "development rule" is 1: a cell of the `tab:robustness` row added in Prompt 1, which R3 protects (Unresolved). |
| P4 | PASS | 11 table/table* environments before `\appendix`. `tab:response_lists` and `tab:cost_structure` are in `app:robustness` (Tables F.4 and F.5). Every `\ref` resolves. |
| P5 | PASS | `\label{subsec:dev_to_ho}` exists. The §6.1 paragraphs are 119, 119, 84 and 112 words. All nine protected-attribute facts are in §7.6, and none is left in the Results. |
| P6 | PASS | No sentence of Sections 2–8 exceeds 60 words, and none exceeds 45, so there is nothing to justify. The four long sentences left in the document are in the Introduction, which is reserved for Prompt 3. |
| P7 | PASS | The Conclusion is 348 words. In Sections 2–8, "522" occurs only in §6.7 (`subsec:cost_runtime`). |
| P8 | PASS | Introduction, abstract, keywords and highlights block are byte-identical to the Prompt 1 commit. |

### Removed duplicates

- `0.027`: the unsigned Home Credit LR mixed-rule margin ("mRMR by 0.021 and 0.027", baseline §7.1). The summary sentence was dropped because the three rule paragraphs of §6.1 carry each value. It survives as −0.027 in §6.1 (mixed-rule paragraph), in `tab:robustness` and in the abstract.
- `29`: "about 29%" of the 307,511 Home Credit applications (baseline §5.1). It was merged with the exact figure, which survives as "28.7 per cent" in §5.1 (moved there from §7.7, with 219,145 of 307,511).
- `0.14`: not a duplicate. It is the erroneous "0.14 to 0.42" corrected in Prompt 1 (A3); the correct 0.13 is in §6.6.1.

### Before/after metrics

| Metric | Baseline | After Prompt 1 | After Prompt 2 |
|---|---|---|---|
| Words, Sections 2–8 | 15,824 | 16,324 | 11,757 (−25.7%) |
| Related Work | 479 | 479 | 426 |
| Background | 786 | 795 | 702 |
| Methodology | 3,048 | 3,048 | 2,031 |
| Experimental Setup | 3,871 | 3,871 | 3,149 |
| Results | 4,229 | 4,600 | 3,149 |
| Discussion | 2,826 | 2,946 | 1,952 |
| Conclusion | 585 | 585 | 348 |
| Words, Sections 1–8 incl. back matter (measure.py) | 16,889 | 17,389 | 12,822 |
| Introduction (unchanged) | 898 | 898 | 898 |
| Abstract | 243 | 243 | 243 |
| Sentences > 45 / > 60 words, Sections 2–8 | 125 / 46 | – | 0 / 0 |
| Sentences > 45 / > 60 words, Sections 1–8 | 129 / 49 | 126 / 46 | 4 / 3 (all in the Introduction) |
| "materiality bar", S2–8 text + captions | 16 | – | 2 |
| "covariate-shift" | 5 | – | 1 |
| "not adjusted" | 2 | – | 4 |
| "descriptive" | 10 | – | 5 |
| "held-out rule" / "development rule" / "development-rule" / "most adversarial" | 1 / 6 / 5 / 4 | – | 0 / 0 / 0 / 0 |
| Tables before `\appendix` | 13 | 13 | 11 |
| Pages | 36 | 37 | 33 |
| Overfull / Underfull `\hbox` | 0 / 1 | 0 / 1 | 0 / 1 |

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

These were the only numeric tokens absent from the baseline after Prompt 1 (S4). Section numbers in these rows follow the Prompt 1 numbering; after Prompt 2 the response-sampling text is in §6.6.1 and the robustness text in §6.4. Two related changes are not new tokens:
- The number word "thirteen" in `subsec:robustness` is the twelve baseline rows plus the new one.
- Printed values reused in new sentences without change: 0.7402, 0.7436, 0.7935, 0.7335, 0.8344, 0.8784, 0.7106, 0.7181, 0.7098, 0.6989, 0.0075, 11, 12, 18, 24, 26, 33, 1,068, 1,959 and 100.

**Prompt 2.** Every new number comes from rounding a printed four-decimal ΔAUC to three decimals in the running text (B7). No other arithmetic was done.

| Number | Used in (Prompt 2 numbering) | Computation from printed values | Full precision / check |
|---|---|---|---|
| −0.001 | §6.5.1 | arm A LR Δ −0.0012 (`tab:obfuscation`) → −0.001 | – |
| +0.004 | §6.5.1 | arm A CatBoost Δ +0.0042 → +0.004 (token already in baseline) | – |
| 0.029, 0.031 | §6.5.1 ("falls by") | arm B Δ −0.0290 and −0.0310 → 0.029 and 0.031 (0.031 already in baseline) | – |
| −0.006, +0.007 | §6.5.2 | range of mechanical-minus-cached Δ, −0.0064 to +0.0066 (`tab:mechanical`) → −0.006 to +0.007 | – |
| +0.009 | §6.5.2 | widest interval bound +0.0086 (`tab:mechanical`, Stability 2024 LR) → +0.009 (token already in baseline) | – |
| −0.002 | §6.5.2 | stable core + LLM fill Δ −0.0018 (`tab:mechanical`) → −0.002 | – |
| +0.002, +0.013 | §7.2 | voting ΔAUC range +0.0020 to +0.0129 (`tab:voting_cross`) → +0.002 to +0.013 (+0.013 already in baseline) | – |
| 0.001, 0.008 | §6.4, §6.6.1 | fold-response margins over IV then Boruta, 0.0008 to 0.0083 (Prompt 1 derived) → 0.001 to 0.008 (both tokens already in baseline) | 0.000833 → 0.001; 0.008298 → 0.008 |
| 0.012, 0.019 | §6.4, §6.6.1 | fold-response margins over RFE CatBoost, 0.0117 to 0.0192 (Prompt 1 derived) → 0.012 to 0.019 | 0.011755 → 0.012; 0.019220 → 0.019. At three decimals the rounding discrepancy noted for 0.0117 in Prompt 1 disappears. |

## Unresolved

None in Prompt 1. The abstract and Introduction mentions of the timing measurement are deferred to Prompt 3 by instruction (A6), not unresolved.

**Prompt 2.**
- **Leader-rule wording inside a table cell.** "development rule" survives once, inside a table cell: the Result cell of the `tab:robustness` row added in Prompt 1 ends "... 0.0117 to 0.0192 under the development rule". R3 (no change to existing cells) and S3 (table bodies equal their Prompt 1 state) forbid renaming it to "DEV rule".
  - In the text, captions and notes of Sections 2–8, which the prompt allows me to edit, all four banned phrases count 0, so P3 is marked PASS on that scope.
  - If P3 is read as covering table cells too, this one cell is the only miss. The fix is a one-word change to that cell ("development rule" → "DEV rule"), which needs the authors' approval under R3.
  - Two more table cells keep the older wording but fall outside P3's phrase list: "Held-out-rule margins in five cases" in `tab:robustness` (a baseline cell) and "development-rule comparison" in `tab:stages` (appendix). R3 protects both.

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

**Prompt 2.**

12. **Meaning of "Sections 2–8".** P1 and P3 measure the numbered sections Related Work to Conclusion. The unnumbered back matter (CRediT to Data availability) is excluded; R6 fixes it anyway.
13. **30% target not reached.** Sections 2–8 are 25.7% shorter, above the 25% floor of P1.
    - After four de-duplication passes the remaining text is almost entirely unique facts: dataset construction, method settings, the numbers the Results argue from, and the caveats in their home sections. Going further would have meant removing unique claims or numbers, which B1 and P1 forbid.
    - Cutting the numbers the Results repeat from tables was considered and rejected, because the text argues from them.
14. **Where the condensed paragraph went (B3).** B3 asks for four headline paragraphs and a separate condensed paragraph (family means, pure LLM against the hybrids, Boruta budget). The condensed paragraph is its own short subsection, §6.3 "Within-family comparison" (`subsec:within_family`), placed after `subsec:dev_to_ho` and before Robustness. §6.1 thus holds exactly the four rule paragraphs.
15. **New Discussion subsection.** "Governance and protected attributes" is §7.6 (`subsec:governance`), placed after Deployment at scale and before Limitations. The Limitations and §4.4 point to it.
16. **Appendix wording (B2).** The appendices keep their wording ("development-data rule" in `app:protocol`; cells of `tab:stages`), because the scope allows only duplicated caveats to be removed there. B2 applies to Sections 2–8.
17. **Precision exceptions (B7).** These stay at four decimals in the running text:
    - the response-sampling spreads (0.0095, 0.0092, 0.0075, 0.0296);
    - the two shortfalls below the bar (0.0014, 0.0003);
    - PSI, Nogueira and Jaccard values.

    Rounding a spread to three decimals would turn 0.0095 into 0.010, which reads as "at the bar" when the paper's point is that it lies inside it, and the shortfalls would become 0.001 and 0.000. Table notes keep the four-decimal values that match their cells, for example 0.0008 to 0.0083 in the `tab:response_spread` note.
18. **Proposed further table moves (not made, B4).**
    - `tab:mechanical`: its result is one row of `tab:robustness` and one paragraph of §6.5.2.
    - `tab:secondary`: secondary metrics are not headline results.
    - Possibly `tab:obfuscation`: its per-arm overlaps are discussed in §6.5.1, so the text would need Appendix F pointers.

    Each would bring the tables before `\appendix` to 10 or 9.
19. **Things a reader may notice that were left unchanged, because the scope did not allow the edit:**
    - The Introduction's roadmap sentence does not list the new §6.2 and §6.3. It is reserved for Prompt 3.
    - The Appendix F introduction does not mention the two moved tables, which are referenced from the main text.
    - Appendix F's "(Section~`subsec:primary_results`)" pointer for LLM then Boruta now lands on §6.1, while the note is in §6.3.
    - Suggested for Prompt 3 or for the authors.
20. **Stale clause removed.** "which matters for the transfer experiments" (§5.1) was deleted: the transfer experiments were removed in an earlier revision (last row of `tab:stages`), so the clause pointed at nothing.
21. **Ambiguous antecedent kept.** In the LendingClub paragraph of §5.1, "None of them appears anywhere in the cached semantic rankings" follows the missingness breakdown (566, two, 107). It is ambiguous whether "them" means the late-introduced features or the 107 features at 60–82%. The result files (`priority_2/lc_missingness_distribution.csv`) do not settle it, so the baseline sentence order was kept. The authors should clarify.
22. **Result file contradicts the paper (not changed).**
    - §6.1 says the Home Credit LR mixed-rule difference (−0.027) is "reported as a point estimate, its interval not computed".
    - `priority_2/conservative_pair_interval.csv` holds an interval for that pair ([−0.0285, −0.0250]).
    - Adding the interval would add numbers absent from the manuscript (R2), and changing the claim is outside this prompt's scope. The authors should decide, and a referee comparing the paper with the repository would flag it.
23. **Wording fix in §5.6.** "responses of the language model, of which there is one per case, ten on Stability 2024" became "one language-model response per case in the headline tables". The old wording ignored the five per-fold responses of Home Credit and LendingClub reported in §6.6.1 (Prompt 1 observation).
24. **Method of the rewrite.** A scratchpad script (not part of the repository) assembled Sections 2–8 from new text templates. Floats and equations were taken verbatim from the Prompt 1 commit, and only captions and the listed note sentences were replaced; the script checked that each AI-assistance sentence survives in its caption. This is why S3 and S5 hold by construction and are also verified by `tools/check_p2.py`.
25. **PDFs and zip, again not rebuilt.** As in Prompt 1, `submission/manuscript.pdf` and the zip are left for the rebuild after Prompt 3. The Prompt 2 build is in the scratchpad (33 pages).
