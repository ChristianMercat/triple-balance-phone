# Comparison with Bianca_spiel_v4.m

The original file is `analysis2/Bianca_spiel_v4.m`. Neither MATLAB nor Octave was
available in the analysis environment, so these are **Python/NumPy reproductions
of its numerical logic**, not results from native MATLAB execution. The original
MATLAB file has not been changed.

`compare_bianca.py` reads its policy, event and technology tables, constructs and
sorts the same combinations, and preserves the original skip condition and
zero-initialized output behavior. An independent, literal replay of the original
loop checks the first 20,000 combinations against the vectorized calculation.
Console messages and plotting are not executed.

## Results

| Measurement                                     | Reproduced MATLAB logic |    Story-based Python model |
| ----------------------------------------------- | ----------------------: | --------------------------: |
| Theoretical full-length combinations            |              10,001,880 | Not the counting definition |
| Successful paths reported                       |               3,224,630 |                   3,597,500 |
| Early terminations counted                      |                 190,776 |                     456,680 |
| Skipped full combinations                       |               6,586,474 |      No skipped-result rows |
| Successful score range, excluding skipped zeros |                  7.5–53 |                      7.5–53 |
| All terminal gameplay paths                     |    Not reliably counted |                   4,054,180 |

The MATLAB theoretical total is `3^6 × 7^3 × (1 + 3 + 9 + 27)`:
six policy rounds, three event slots with seven possibilities each, and 40
technology sequences for initial research investments of zero through three.
It includes full-length combinations whose later steps become unreachable after
Game Over. This total is therefore different from a count of terminal paths.

**Without the original skip filter, the MATLAB tables produce exactly 3,597,500
successful combinations. Their entire half-point score histogram matches the
story-based Python histogram, not just its minimum and maximum.**

## Why the counts differ

The MATLAB skip test compares only the choice at the previous failure's column:

```matlab
choices(death_occured_in) == death_last_col_value
```

That does not establish that the preceding game state is identical. In addition,
the initial research payment is inferred from future technology selections in
columns 4, 10 and 12. Two rows with identical earlier choices can therefore have
different initial budgets. Skipping their shared prefix can skip a valid game.

A concrete example in the sorted matrix:

- Row 11,509 pays for three technologies and fails at step 9.
- Row 11,512 has identical choices through step 9 but pays for only two
  technologies. It would finish successfully, yet the skip filter skips it.

The reproduction finds **372,870 valid successful combinations** skipped this
way. Adding them back gives `3,224,630 + 372,870 = 3,597,500`.

The early-termination counter is also affected by this unsafe deduplication. A
safe failure-prefix key must include the initial research investment and the
complete relevant choice prefix or state, rather than one column value.

## Why the histogram and minimum differ

`circle_vec`, `happy_vec` and `money_vec` are initialized with zeros. Processed
failures are replaced by NaN, but skipped rows remain zero. The score vector and
histogram therefore contain **6,586,474 artificial zero-score entries**.
MATLAB's [`min` omits missing values by default](https://www.mathworks.com/help/matlab/ref/double.min.html).
The printed minimum is therefore zero, despite the successful minimum being
7.5. The histogram contains 9,811,104 entries, rather than 3,224,630 successes.

The MATLAB `BinMethod = 'Integers'` also combines adjacent half-point scores into
integer-centered bins, as described in the
[histogram documentation](https://www.mathworks.com/help/matlab/ref/matlab.graphics.chart.primitive.histogram-properties.html).
The Python histogram keeps exact half-point bins.

The comparison exports both the exact score counts and integer-centered bins.
The integer-bin export reproduces the intended numeric binning, not a native
MATLAB rendering or its automatic axis choices.

## Reproduce and inspect

NumPy is required for this optional comparison; the main `count_paths.py` remains
standard-library only. Run:

```sh
python3 analysis2/compare_bianca.py
```

Outputs in `analysis2/`:

- `bianca-comparison.json`: counts, ranges, source hash and example skipped rows.
- `bianca-score-histogram.csv`: exact scores comparing the original filter,
  zero-contaminated output, unfiltered successes and the story model.
- `bianca-integer-histogram.csv`: original-style integer-centered bins, including
  skipped zeros.

Regenerate the main results before comparing after a story edit. To validate the
original function in an installed MATLAB runtime, run from the project root:

```sh
matlab -batch "addpath('analysis2'); Bianca_spiel_v4;"
```

The original function uses [`fullfact`](https://www.mathworks.com/help/stats/fullfact.html)
from the Statistics and Machine Learning Toolbox, and creates a histogram. Its declared return variable is not
a summary structure: the structure-building code is commented out, leaving the
last effects cell array in `results`.

No changes were made to the game's published count or graph. Neither model's
verified successful count matches the currently published value of 3,824,020.
