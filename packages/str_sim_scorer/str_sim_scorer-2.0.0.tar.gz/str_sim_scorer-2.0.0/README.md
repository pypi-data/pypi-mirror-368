# STR Similarity Scorer

This repository contains a Python package to compute the [Tanabe score](https://www.cellosaurus.org/str-search/help.html) ("non-empty markers" mode) for pairs of records in an input data frame.


This package computes the number of matching and total alleles and common loci largely through matrix algebra, so it's fast enough to be run on thousands of samples (millions of pairs).

## Usage

The `StrSimScorer` class provides an object-oriented interface with caching for efficient computation:

```py
import pandas as pd
from str_sim_scorer import StrSimScorer

df = pd.DataFrame(
    [
        {
            "id": "sample1",
            "csf1po": "11, 13",
            "d13s317": "11, 12",
            "d16s539": "9, 12",
            "d18s51": "11, 19",
            "d21s11": "29, 31.2",
            "d3s1358": "17",
            "d5s818": "13",
            "d7s820": "10",
            "d8s1179": "12, 13",
            "fga": "24",
            "penta_d": "9, 12",
            "penta_e": "7, 13",
            "th01": "6, 8",
            "tpox": "11",
        },
        {
            "id": "sample2",
            "csf1po": "12",
            "d13s317": "11, 12",
            "d16s539": "8, 12",
            "d18s51": "17, 18",
            "d21s11": "28, 33.2",
            "d3s1358": "16",
            "d5s818": "11",
            "d7s820": "8, 13",
            "d8s1179": "9, 10",
            "fga": "21, 25",
            "penta_d": "9, 12",
            "penta_e": "7",
            "th01": "7, 9.3",
            "tpox": "8",
        },
        {
            "id": "sample3",
            "csf1po": "11, 12",
            "d13s317": "8",
            "d16s539": "11",
            "d18s51": "18",
            "d21s11": pd.NA,
            "d3s1358": "16",
            "d5s818": "10, 11",
            "d7s820": "12",
            "d8s1179": "11",
            "fga": "26",
            "penta_d": pd.NA,
            "penta_e": "13.1, 12.1",
            "th01": "6, 9.3",
            "tpox": "12",
        },
    ]
)

# Create the comparison object
comp = StrSimScorer(
    df,
    sample_id_col_name="id",
    locus_col_names=[
        "csf1po",
        "d13s317",
        "d16s539",
        "d18s51",
        "d21s11",
        "d3s1358",
        "d5s818",
        "d7s820",
        "d8s1179",
        "fga",
        "penta_d",
        "penta_e",
        "th01",
        "tpox",
    ],
)

# Get Tanabe scores as a DataFrame (upper triangle only)
tanabe_scores = comp.tanabe_scores(output="df")
```

### Output formats

Using `output="df"` returns a DataFrame for distinct pairs of IDs:
```
>>> print(tanabe_scores)
       id1      id2  n_common_loci  n_matching_alleles  n_total_alleles  tanabe_score
0  sample1  sample2             14                   6               46      0.260870
1  sample1  sample3             12                   2               35      0.114286
2  sample2  sample3             12                   5               35      0.285714
```

Using `output="symmetric_df"` returns the same data with both (id1, id2) and (id2, id1) rows:
```
>>> tanabe_scores_sym = comp.tanabe_scores(output="symmetric_df")
>>> print(tanabe_scores_sym)
       id1      id2  n_common_loci  n_matching_alleles  n_total_alleles  tanabe_score
0  sample1  sample2             14                   6               46      0.260870
1  sample1  sample3             12                   2               35      0.114286
2  sample2  sample3             12                   5               35      0.285714
5  sample3  sample2             12                   5               35      0.285714
4  sample3  sample1             12                   2               35      0.114286
3  sample2  sample1             14                   6               46      0.260870
```

Using `output="array"` returns the raw symmetric matrix:
```
>>> tanabe_array = comp.tanabe_scores(output="array")
>>> print(tanabe_array)
array([[1.        , 0.26086957, 0.11428571],
       [0.26086957, 1.        , 0.28571429],
       [0.11428571, 0.28571429, 1.        ]])
```

### Accessing individual components

The `StrSimScorer` class also provides access to intermediate matrices:

```py
# Get the processed alleles DataFrame
alleles = comp.alleles()

# Get individual matrices
common_loci = comp.n_common_loci()
matching_alleles = comp.n_matching_alleles()
total_alleles = comp.n_total_alleles()
```

## Development

### Installation

1. Install the required system dependencies:
   - [pyenv](https://github.com/pyenv/pyenv)
   - [Poetry](https://python-poetry.org/)
   - [pre-commit](https://pre-commit.com/)
 
3. Install the required Python version (>=3.9):
	```bash
	pyenv install "$(cat .python-version)"
	```

4. Confirm that `python` maps to the correct version:
	```
	python --version
	```

5. Set the Poetry interpreter and install the Python dependencies:
	```bash
	poetry env use "$(pyenv which python)"
	poetry install
	```

Run `poetry run pyright` to check static types with [Pyright](https://microsoft.github.io/pyright).

### Testing

```bash
poetry run pytest
```
