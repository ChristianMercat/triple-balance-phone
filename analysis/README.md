# Gameplay path analysis

Run from the repository root with Python 3.9 or later. No packages are needed:

```sh
python3 analysis/count_paths.py
```

The script reads `tripleBalance.twee`, including its resource assignments,
conditional links, random-event rolls, Game Over overrides and score lookup.
It does not edit the story, dictionaries or the game's graph image.

## Output

Generated files are in `analysis/results/`:

- `summary.json`: counts, minimum/maximum scores, example paths reaching each
  extreme, the score formula and the source hash used for the calculation.
- `terminal-states.csv`: final resources, score and number of paths for each
  distinct terminal state. Multiple paths with identical results are grouped;
  their multiplicities are preserved.
- `score-histogram.csv`: half-point bins, including empty bins, with separate
  columns for successful paths, both Game Over causes and all terminal paths.
- `score-histogram.svg`: a standalone histogram of **successful** final scores.
  It includes descriptive text and tooltips; the CSV provides exact data.

To record every individual path and its score, request an additional CSV:

```sh
python3 analysis/count_paths.py --paths /tmp/triple-balance-paths.csv
```

This exports over four million rows and takes considerably more time and disk
space than the grouped analysis. Avoid committing this large file.

Other source and output locations can be selected with `--source` and `--output`.
Regenerate the results after gameplay changes; `summary.json` records the source
SHA-256 so stale results can be identified.

## What counts as a path?

A path is a sequence of gameplay choices and visible random outcomes. Research
investment, policy choices, technology choices and event responses all count.
Each random assignment branches into outcomes 1–4, including the no-event route.
Distinct sequences count separately even when they reach identical resources.
The script combines equivalent states to calculate their counts efficiently.

Successful paths stop on reaching `End1`, before the informational ending pages.
Failed paths stop on reaching `Game over` or `Game over2`. Explanatory detours,
credits, shared UI links and restarts are excluded. Counting arbitrary navigation
through restart and explanation loops would allow infinitely many paths.

Game Over overrides apply to Continue links where the story includes
`{game over override}`. Happiness failure takes precedence when both happiness
and money are depleted, matching the story. Resource floors such as
`Math.max(0, circle - 1)` are applied as written.

By default, a random roll immediately hidden by Game Over does not create a
separate visible path. To count all underlying draws, use:

```sh
python3 analysis/count_paths.py --count-hidden-rolls --output /tmp/hidden-rolls
```

Counts are **not probabilities**. Routes have different numbers of random draws,
and no probability distribution is assigned to player choices.

## Verified baseline

For the current gameplay, the default definition gives:

| Ending              |     Paths | Minimum score | Maximum score |
| ------------------- | --------: | ------------: | ------------: |
| Successful          | 3,597,500 |           7.5 |            53 |
| Happiness Game Over |    55,757 |             1 |            36 |
| Budget Game Over    |   400,923 |             3 |            47 |
| All terminal paths  | 4,054,180 |             1 |            53 |

Counting hidden rolls changes the total to 4,055,791; successful paths and their
score distribution are unchanged.

## Scope and checks

This is a restricted interpreter for the constructs used by this story, not a
general Chapbook engine. It supports sequential integer resource assignments,
arithmetic, `Math.max`/`Math.min`, the current four-way random formula, native
`[if]`/`[continue]` modifiers and graph-readable `[[...]]` destinations. It reads
the score lookup's arithmetic expression directly. It does not execute story
JavaScript, render inserts, or analyze probabilities. Gameplay added through
JavaScript or new custom inserts requires extending the model.

Unknown gameplay assignments, unsupported expressions/modifiers, missing
destinations and gameplay cycles produce errors. New terminal or informational
passages may require updating the explicit passage lists near the top of the
script. The chart currently assumes scores fall on half-point boundaries.

Run the fixture checks with:

```sh
python3 -m unittest discover -s analysis -p 'test_*.py'
```

They cover merged paths retaining their counts, individual path export, resource
floors, native condition reset, Game Over precedence, hidden rolls, cycle
rejection and unsupported expressions.
