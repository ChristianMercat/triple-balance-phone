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
  It includes descriptive text, tooltips and hooks for the game's translated
  score marker; the CSV provides exact data. The axis runs from the minimum
  successful score to the maximum (currently 7.5–53). Zero-count rectangles are
  omitted while keeping the spacing for their score intervals.
- `score-distribution.json`: compact lookup data for successful paths, containing
  sorted attainable `scores`, their integer `cumulativeCounts`, `totalPaths`
  and the population identifier. Failed paths and empty bins are excluded.

## Game lookup functions

StoryScript embeds the generated distribution, so lookup functions are available
immediately without fetching a file or changing saved game state:

```javascript
window.TripleBalanceScores.percentile(37);       // 97.52294649061848
Math.floor(window.TripleBalanceScores.percentile(37)); // 97 for display
window.TripleBalanceScores.minimumScore(90);    // 33
```

`percentile(score)` returns the **unrounded** percentage of successful paths
scoring at or below the supplied score. Tied scores receive the same percentile;
scores between bins use the preceding bin, without interpolation. Values below
the successful minimum return 0; values at or above the maximum return 100.

`minimumScore(percentile)` returns the lowest attainable score whose cumulative
percentage reaches the requested value. It accepts values from 0 through 100,
including decimals; 0 explicitly returns the minimum successful score. This is
a discrete quantile lookup rather than a one-to-one inverse.

Both functions require finite JavaScript numbers; numeric strings are rejected.
An out-of-range percentile is rejected rather than silently clamped. The
distribution is exposed as read-only `window.TripleBalanceScores.distribution`.

Current thresholds are:

| Requested percentile | Minimum score |
| ---: | ---: |
| 0 | 7.5 |
| 20 | 21 |
| 40 | 24.5 |
| 60 | 27 |
| 90 | 33 |
| 100 | 53 |

End3 uses these lookups directly in its native conditions. Lower bounds are
inclusive and upper bounds exclusive: barely survived `[7.5, 21)`, poor
`[21, 24.5)`, average `[24.5, 27)`, good `[27, 33)`, outstanding `[33, 53)`,
and the separate perfect-score assessment at 53. The shared translated score
line displays the integer percentile rounded down, including in the perfect-score
case. The replay link is unconditional after `[continue]`.

After gameplay changes, regenerate results **and** refresh the embedded copy:

```sh
python3 analysis/count_paths.py --update-story
```

This replaces the data between the generated-distribution markers in
`tripleBalance.twee` and writes the generated SVG to `images/score-histogram.svg`.
The SVG is identical to the analysis output and is the static chart loaded by
the game. The command does not change evaluation text, assessment boundaries,
or `index.html`; publish the updated source from Twine to refresh the HTML.
Import the updated source into Twine before publishing so its editor copy also
contains the new data. The ordinary command without `--update-story` writes
analysis outputs only. Generated data is not maintained by hand. The summary's
source hash includes the updated embedded data when this option is used.

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
node analysis/test_score_lookup.cjs
```

They cover merged paths retaining their counts, individual path export, resource
floors, native condition reset, Game Over precedence, hidden rolls, cycle
rejection and unsupported expressions.
The JavaScript checks compare the embedded data to the generated lookup and
verify CDF/quantile behavior, fractional thresholds, score ties, boundary values,
round trips and invalid inputs. Node.js is needed only for these JavaScript
checks, not for running the Python analysis or playing the game.
The same JavaScript test also checks the actual End3 conditions at each boundary,
that each successful score has one assessment, and the shared EN/DE score line.

## In-game histogram

End6 uses `{score histogram: score, successful: gameSuccessful}`. The custom element loads the generated
`images/score-histogram.svg` once, clones its static bars, highlights the current
score bin, and adds a vertical line plus an arrow labelled “You” only for a
successful completed game. The score is
captured when the element is created; language changes do not rerender the
passage, reapply resource changes or reroll events.

Chart labels, bar tooltips, the marker and the accessible description use
`end.end6.chart` keys in the main dictionaries. Axis numbers and path counts use
the active locale. End6's playthrough count comes from the same generated
distribution and uses i18next number formatting. Only successful paths are
counted in both the text and the histogram.

The read-only Chapbook lookup `gameSuccessful` checks that `End1` was visited
after the latest Start or Game Over, and that happiness and money remain positive.
It prevents a win from a previous run carrying over after a restart. Failed and
unfinished runs get the general chart introduction and accessible description,
without a player marker or percentile footer. Both Game Over footers link
directly to End4, so the score explanation and general histogram remain available.
If the insert's `successful` option is omitted, it defaults to false.

The chart has a responsive height and scrolls inside its own focusable container
on narrow screens. Each chart instance has unique accessible title/description
IDs. It is populated directly through SVG DOM nodes; SVG markup is not permitted
inside translation strings or passed through the rich-text insert.
When horizontal scrolling is needed, the chart initially centers on the score
marker and recenters after a container resize when a successful score is shown.
