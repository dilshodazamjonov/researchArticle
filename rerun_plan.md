# Rerun plan: decision rules fixed before running

Written 2026-09-25, before any rerun call or refit. At this date every result column of the five rerun CSVs in `Feature-Selection-Research/todo/` is empty. The rules below are taken verbatim from Step 0 of `Feature-Selection-Research/todo/README_reruns.md`. The reruns are judged against these rules and no others.

## Decision rules

- **Response repeats.** A case counts as a material LLM-assisted win under a rule if the **median** margin over that rule's classical leader, across the 10 new repeats, is at least 0.010. Report the full distribution either way.
- **Pool controls.** A case supports the semantic reading if LLM pool − IV pool is at least +0.010 with a 95% interval excluding 0. If IV pool is within ±0.010 of LLM pool, the gain is attributed to pre-screening, not semantics. The random pools are the floor.

## Held fixed

Everything not listed in `README_reruns.md` stays exactly as in the frozen protocol:
- the model: GPT-4.1 mini `gpt-4.1-mini-2025-04-14`, temperature 0, JSON response format, `definitions_only`, the Appendix A template and the same candidate records;
- validation: strict, with up to three retries and no fallback;
- the pipelines: the frozen LR and CatBoost configurations with seed 42, each refitted on full DEV and scored once on HO.

The pool controls are controls, like the diversity controls: they enter no family, leader or count.
