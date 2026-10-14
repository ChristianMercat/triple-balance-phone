# Bianca's MATLAB model

See [bianca-comparison.md](bianca-comparison.md) for the comparison with
`analysis2/Bianca_spiel_v4.m`, including the skip-filter and histogram issues.
The optional `compare_bianca.py` reproduction requires NumPy; it does not execute
MATLAB. Its unfiltered successful counts and score histogram match the main
story-based model in [`../analysis/`](../analysis/README.md).

From the repository root, regenerate the main results and run the comparison:

```sh
python3 analysis/count_paths.py
python3 analysis2/compare_bianca.py
```

The comparison requires NumPy and reads the main model's `summary.json` and
`score-histogram.csv` from `analysis/results/`. It writes its own comparison
JSON and CSV files to `analysis2/`; it does not write to `analysis/`.
The main analysis does not depend on this directory or on NumPy.

Changes specific to this comparison are recorded in [changelog.md](changelog.md).
