## 2026-10-13 — Compare Bianca's MATLAB gameplay model

- Read `analysis2/Bianca_spiel_v4.m` and added `analysis2/compare_bianca.py` plus
  a written comparison and numerical outputs. MATLAB and Octave were unavailable;
  execution used a Python/NumPy reproduction of the original numeric logic,
  preserving matrix ordering, the skip predicate and zero-filled skipped rows.
  The original MATLAB source is unchanged.
- Reproduced 10,001,880 theoretical combinations, 190,776 counted failures,
  6,586,474 skipped rows and 3,224,630 reported successes. Identified 372,870 valid
  successes skipped by a filter that does not distinguish initial research
  payments or complete prefixes. Unfiltered tables yield 3,597,500 successes.
- Verified that the unfiltered successful score histogram matches the
  story-based Python model at every half-point score. Both give a successful
  range of 7.5–53. The original histogram includes skipped rows as artificial
  zero scores and uses integer bins instead of exact half-point bins.

Validation: independently replayed the original loop for the first 20,000 sorted
combinations, including its skip behavior. Comparison outputs record the MATLAB
source hash and a concrete valid route incorrectly skipped by the filter.
Native MATLAB results remain to be checked in an environment with the runtime
and required toolbox. Story, dictionaries, published graph and count are unchanged.

## 2026-10-14 — Separate the comparison from the main analysis

- Kept the MATLAB source, comparison script, report and generated comparison
  files in `analysis2/`, with their own README and changelog.
- Updated the documented command and the script's default output directory so
  running the comparison writes into `analysis2/` rather than `analysis/results/`.
- Documented the one-way dependency: the comparison reads main-analysis results,
  while the main standard-library tool remains independent of this directory.
