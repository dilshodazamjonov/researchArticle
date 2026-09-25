# number_inventory_report.md

Method: every numeric token in the body of the `.tex` (between `\begin{document}` and `\end{document}`, comments stripped) was extracted with its line number: integers of four or more digits (thousands separators allowed), all decimals, percentages, signed numbers and dates. The reviewed version (`git show 3d78c42:submission/manuscript.tex`) is compared with the revised `submission/manuscript.tex` plus `submission/supplementary.tex`. Presence is checked token by token (a token must occur at least once in the revised files); counts are reported as well. Script: `number_inventory.py` (reproduced in `qa_report.md`).

## Totals

| | Tokens | Distinct tokens |
|---|---|---|
| Reviewed manuscript | 1732 | 855 |
| Revised manuscript | 1666 | 842 |
| Supplementary file | 55 | 30 |
| Revised manuscript + supplement | 1721 | 870 |

Reviewed tokens by kind: {'integer4': 374, 'decimal': 1242, 'percent': 33, 'signed': 35, 'date': 48}. Revised manuscript tokens by kind: {'integer4': 364, 'decimal': 1182, 'percent': 35, 'signed': 35, 'date': 50}.

## Result

- Tokens of the reviewed version present unchanged in the revised files: **853 of 855** distinct tokens.
- Tokens absent from the revised files: **2**, both rounded restatements of values that remain in a table at higher precision (listed below). No number was changed.
- Tokens new to the revised files: **17**, all layout parameters or raw coordinate forms in the code of the new figure `fig:scale`; none is a result number (listed below with provenance).

## Tokens of the reviewed version absent from the revised files

| Token | Occurrences before | Reviewed line | Where the value remains |
|---|---|---|---|
| 0.51 | 1 | L816 | rounded restatement of the Max column value 0.509 of the Home Credit CatBoost pure LLM row of Table tab:stability (the sentence now points to the Min and Max columns) |
| 0.54 | 1 | L816 | rounded restatement of the Max column value 0.538 of the LendingClub v2 CatBoost pure LLM row of Table tab:stability (same sentence) |

## Tokens new to the revised files (provenance)

| Token | Occurrences | Provenance |
|---|---|---|
| 4.4 | 1 | fig:scale bar width (layout) |
| 10.2 | 1 | fig:scale axis width (layout) |
| 10,100,100 | 1 | fig:scale tick-label list fragment |
| 100000 | 1 | fig:scale tick position |
| 1000000 | 1 | fig:scale tick position |
| 10,100 | 1 | fig:scale tick list fragment (10,100,1000,...) |
| 100,000 | 1 | fig:scale tick label |
| 1,000,000 | 1 | fig:scale tick label |
| 0.1 | 1 | fig:scale enlarge y limits (layout) |
| 0.985 | 1 | fig:scale legend position (layout) |
| -6.2 | 1 | fig:scale bar shift (layout) |
| 1068 | 1 | raw form of 1,068 (plot coordinate) |
| 1959 | 1 | raw form of 1,959 (plot coordinate) |
| 1157512 | 1 | raw form of 1,157,512 (plot coordinate) |
| 598649 | 1 | raw form of 598,649 (plot coordinate) |
| 6.2 | 1 | fig:scale bar shift (layout) |
| 99092 | 1 | raw form of 99,092 (plot coordinate) |

## Tokens that occur less often than before (duplicates consolidated; each still present)

73 distinct tokens occur fewer times than in the reviewed version because repeated statements were consolidated into tables, captions or single canonical sentences (rule 1.5 of the prompt: the content is preserved elsewhere and pointed to). Every one of them still appears at least once. The full list, as (token, before, after):

(+0.0007, 2, 1), (+0.0052, 2, 1), (+0.0086, 5, 4), (+0.012, 12, 11), (+0.0181, 2, 1), (+0.0194, 2, 1), (+0.024, 4, 3), (+0.0286, 2, 1), (+0.030, 3, 2), (+0.051, 9, 7), (0.0024, 4, 3), (0.0038, 3, 2), (0.0045, 2, 1), (0.0053, 4, 2), (0.0072, 2, 1), (0.0085, 2, 1), (0.0097, 2, 1), (0.0104, 2, 1), (0.0125, 4, 2), (0.0129, 2, 1), (0.0189, 4, 3), (0.23, 2, 1), (0.25, 5, 3), (0.40, 6, 5), (0.481, 4, 2), (0.509, 4, 3), (0.538, 2, 1), (0.60, 4, 3), (0.600, 2, 1), (0.667, 6, 3), (0.67, 3, 2), (0.702, 3, 2), (0.7091, 3, 2), (0.7106, 2, 1), (0.7146, 2, 1), (0.7181, 2, 1), (0.7324, 2, 1), (0.7358, 2, 1), (0.7362, 2, 1), (0.7410, 2, 1), (0.7424, 2, 1), (0.7432, 4, 2), (0.7436, 6, 5), (0.7471, 2, 1), (0.7554, 2, 1), (0.7599, 2, 1), (0.7625, 2, 1), (0.7699, 9, 6), (0.7758, 3, 1), (0.7793, 5, 4), (0.7860, 6, 5), (0.7926, 2, 1), (0.7935, 9, 7), (0.7977, 2, 1), (0.7998, 2, 1), (0.8123, 2, 1), (0.818, 6, 3), (0.8300, 2, 1), (0.8344, 9, 7), (0.8395, 2, 1), (0.8435, 2, 1), (0.8740, 2, 1), (0.8784, 10, 8), (0.8832, 2, 1), (0.905, 7, 5), (0.96, 4, 3), (14.2, 2, 1), (16.2, 2, 1), (2.75, 2, 1), (23.2, 2, 1), (28.8, 2, 1), (3.63, 2, 1), (4.67, 2, 1)


Numbers moved between files: the six headline-subset tables (Tables S1–S6) now live in `submission/supplementary.tex`; their captions' overlap counts (4 of 20, 16 of 40, 4 of 20, 21 of 40, 1 of 20, 4 of 40) are also stated in the main-text appendix `app:subsets`.
