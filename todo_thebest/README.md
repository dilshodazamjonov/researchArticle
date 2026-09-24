# `todo_thebest/` — pre-declared favourable ranges, not results

Written 2026-09-21, before any of the nine runs of `todo/` started. Each file here mirrors a skeleton in `todo/` and states, row by row, the range of values that would favour the paper and the condition in words. Every row carries `status = TARGET_NOT_MEASURED`. Nothing in this folder is a measurement, nothing here is ever copied into `priority_2/`, and no number from this folder enters `manuscript.tex`. The purpose is the one `progress.md` states for every step: the reading of each outcome is decided before the run, so a result cannot be reinterpreted after it is seen.

How to use it: fill the skeleton in `todo/`, then compare each value with the range in the matching file here. Inside the range means the favourable branch of the step; outside means the other branch, whose text is also written in `progress.md`. Both branches end in a written paragraph.

Common threshold: the materiality bar of 0.010 AUC (Section 5.6). "Favourable" is defined per file:

| File | Favourable means |
|---|---|
| `38_conservative_interval.csv` | exact reproduction of the two AUCs; nothing can improve the paper here |
| `39a_onehot_dimension.csv` | the LLM-assisted subset receives no more columns than the classical subset of the same case |
| `39b_native_catboost.csv` | native handling within 0.005 of one-hot for every leader and the ordering unchanged |
| `40_perfold_ho.csv` | every fold draw at least 0.010 above the classical leader, spread at most 0.010 (Home Credit LR: no further deterioration) |
| `37_lc_maturity.csv` | the LendingClub margins on the fully matured cohort within 0.010 of the full-population values, positive and above the bar in every month and term |
| `44_mechanical.csv` | mechanical descriptions within 0.010 of the hand-written ones in all seven rows, overlap at least 60 of 100 |
| `47_obfuscation.csv` | arm A within 0.010 of named; arm B at least 0.015 below named (a drop is the favourable outcome for arm B) |
| `43_diversity_capped.csv` | the capped or depth-0 classical selector at least 0.010 below the LLM-assisted leader; the Stability 2024 depth-0 cells are decisive |
| `45_repeated_calls.csv` | every repeat at least 0.010 above the classical leader and within 0.005 of cached, spread at most 0.010 |

Two of the nine cannot be "won" in any direction and are included for completeness: 38 is a consistency check, and 39a is a disclosure whose favourable reading is a comparison within each case.

The unfavourable branches are not failures of the paper. Each is written in `progress.md` as a narrower, still publishable claim: 44 reframes the contribution as expert metadata routed through a language model; 43 attributes the Stability 2024 margin to source concentration; 47 returns the name-recognition concession for one dataset; 37 rescopes the LendingClub margins to the resolved population; 40 and 45 report a case as sign-unstable; 39b names the case whose ordering depends on the encoding.
