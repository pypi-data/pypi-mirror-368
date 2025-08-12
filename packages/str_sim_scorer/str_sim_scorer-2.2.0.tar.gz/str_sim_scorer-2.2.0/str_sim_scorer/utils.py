from __future__ import annotations

import logging
import warnings
from concurrent.futures import ThreadPoolExecutor
from math import ceil
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import sparse


def collect_alleles(
    df: pd.DataFrame, sample_id_col_name: str, locus_col_names: List[str]
) -> pd.DataFrame:
    """
    Given a data frame and the column names containing sample IDs and allele counts at
    STR loci, create a long data frame of unique alleles at observed loci for every
    sample.

    :param df: DataFrame containing STR profile data
    :param sample_id_col_name: Name of the column containing sample IDs
    :param locus_col_names: Names of columns containing allele counts at STR loci
    :return: a data frame of unique (sample ID, locus, allele count) records
    """

    # get all allele counts as a long data frame (one allele per profile-locus)
    alleles = df.melt(
        id_vars=[sample_id_col_name],
        value_vars=locus_col_names,
        var_name="locus",
        value_name="allele",
    ).dropna()

    alleles = alleles.set_index([sample_id_col_name, "locus"])

    # make data frame of unique (sample ID, locus, allele count) records
    alleles = (
        alleles["allele"]
        .str.extractall(r"(?P<allele>\d+(?:\.\d)?)")
        .reset_index()
        .drop(columns="match")
        .drop_duplicates()
        .sort_values([sample_id_col_name, "locus", "allele"])
        .reset_index(drop=True)
    )

    # use categories since this data frame and its derivations might be large
    alleles[[sample_id_col_name, "locus", "allele"]] = alleles[
        [sample_id_col_name, "locus", "allele"]
    ].astype("category")

    return alleles


def count_matching_alleles(
    df: pd.DataFrame,
    sample_id_col_name: str,
    locus_col_name: str,
    allele_col_name: str,
    sample_ids: List[str],
) -> np.ndarray:
    """
    Given a long data frame with columns for sample ID, STR locus name (e.g. "tpox"),
    and count of a single allele (e.g. "11.1"), construct a symmetric numpy array such
    that cells `(i, j)` and `(j, i)` are the number of shared allele counts across all
    STR loci in samples `i` and `j`.

    :param df: a data frame prepared by `collect_alleles`
    :param sample_id_col_name: name of column containing a sample ID
    :param locus_col_name: name of column containing an STR locus name
    :param allele_col_name: name of column containing an allele count
    :param sample_ids: list of sample IDs (the output array rows/cols will be ordered
    by this list)
    :return: a symmetric matrix counting the matching alleles for pairs of samples
    """

    _df = df.copy()

    # create indicator before pivoting into a sparse array
    _df["present"] = True

    if sample_ids is not None:
        # ensure _df is pivoted using the provided order of sample IDs
        _df[sample_id_col_name] = pd.Categorical(
            _df[sample_id_col_name], categories=sample_ids, ordered=True
        )

    # pivot into wide data frame indicating presence of each allele counts at each locus
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=FutureWarning)
        _df = _df.pivot(
            values="present",
            index=[locus_col_name, allele_col_name],
            columns=sample_id_col_name,
        ).notna()

    if len(_df) == 0:
        # this might happen if intial _df has no rows
        return np.zeros((len(sample_ids), len(sample_ids)), dtype=np.uint16)

    # ensure pivot has a column for every sample ID
    _df = _df.reindex(columns=sample_ids, fill_value=False)

    # convert to sparse matrix (sample_id_col_name by locus_allele_cols)
    x = sparse.csc_array(_df, dtype=np.uint16)

    # get symmetric matrix (ID by ID) of pairwise intersection set sizes
    x = chunked_gram_matrix(x, max_chunk_size=500)

    return x


def chunked_gram_matrix(x: sparse.csc_array, max_chunk_size: int) -> np.ndarray:
    """
    Calculate the gram matrix ((x^T)x) for a given matrix `x` in chunks.

    :param x: a numpy array
    :param max_chunk_size: the maximum number of columns per chunk
    :return: the gram matrix
    """

    n_col = x.shape[1]  # pyright: ignore
    n_chunks = 1 + n_col // max_chunk_size
    chunk_size = n_col / n_chunks

    y = np.zeros((n_col, n_col), dtype=np.uint16)

    def compute_chunk(i: int) -> Tuple[int, int, np.ndarray]:
        """
        Compute the gram matrix of a subset of `x`.

        :param i: the chunk index
        :return: a tuple of the row indexes and dense numpy array for this chunk
        """

        logging.info(f"Calculating gram matrix (chunk {i + 1} of {n_chunks})")

        i1 = ceil(i * chunk_size)
        i2 = min(ceil((i + 1) * chunk_size), n_col)

        chunk = x[:, i1:i2]  # pyright: ignore
        result = chunk.T.dot(x).toarray()

        return i1, i2, result

    with ThreadPoolExecutor() as executor:
        for i1, i2, result in executor.map(compute_chunk, range(n_chunks)):
            y[i1:i2, :] = result

    return y


def count_common_loci(
    df: pd.DataFrame,
    sample_id_col_name: str,
    locus_col_name: str,
    sample_ids: List[str],
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Given a long data frame with columns for ID (i.e. sample ID), STR locus name (e.g.
    "tpox"), and count of a single allele (e.g. "11.1"), construct symmetric numpy
    arrays counting the common loci and total alleles at those loci for all pairs of
    samples.

    :param df: a data frame prepared by `collect_alleles`
    :param sample_id_col_name: name of column containing a sample ID
    :param locus_col_name: name of column containing an STR locus name
    :param sample_ids: list of sample IDs (the output array rows/cols will be ordered
    by this list)
    :return: a tuple of (1) symmetric matrix counting common loci for pairs of samples
             and (2) symmetric matrix counting total alleles at common loci for pairs
    """

    _df = df.copy()

    # create indicator before pivoting into a sparse array
    _df["present"] = True

    if sample_ids is not None:
        # ensure _df is pivoted using the provided order of sample IDs
        _df[sample_id_col_name] = pd.Categorical(
            _df[sample_id_col_name], categories=sample_ids, ordered=True
        )

    # pivot into wide data frame counting alleles observed at each locus
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=FutureWarning)
        _df = _df.pivot_table(
            values="present",
            index=sample_id_col_name,
            columns=locus_col_name,
            aggfunc=np.sum,  # pyright: ignore
        )

    if len(_df) == 0:
        # this might happen if intial _df has no rows
        zeros = np.zeros((len(sample_ids), len(sample_ids)), dtype=np.uint16)
        return zeros, zeros

    # ensure pivot has a row for every sample ID
    _df = _df.reindex(index=sample_ids, fill_value=0)

    # Minkowski addition gives us the pairwise sums of the rows
    m = np.array(_df)
    x = (m[:, None] + m).reshape(-1, m.shape[1])

    # construct another matrix of the same shape, but this time use 0/1 to indicate
    # which loci are present in both profiles for each pair
    m[m > 0] = 1
    xz = (m[:, None] * m).reshape(-1, m.shape[1])
    common_loci = np.sum(xz, axis=1).reshape((m.shape[0], m.shape[0]))

    # sum the number of alleles in each pair, but only at loci where both profiles
    # had allele data
    nz_pair_combs = x * xz  # element-wise
    total_common_alleles = np.sum(nz_pair_combs, axis=1).reshape(
        (m.shape[0], m.shape[0])
    )

    return common_loci, total_common_alleles


def compute_tanabe_scores(
    n_matching_alleles: np.ndarray, n_total_alleles: np.ndarray
) -> np.ndarray:
    """
    Compute the Tanabe score for pairs of samples, given previously-calculated counts of
    shared alleles and total alleles at common loci.

    :param n_matching_alleles: symmetric array from `count_matching_alleles`
    :param n_total_alleles: symmetric array from `count_common_loci` (total alleles)
    :return: symmetric array with Tanabe scores for pairs of samples
    """

    (
        np.testing.assert_array_equal(n_matching_alleles.shape, n_total_alleles.shape),
        "Matrices for n_matching_alleles and n_total_alleles must be the same shape",
    )

    return np.divide(
        2 * n_matching_alleles.astype(np.float64),
        n_total_alleles.astype(np.float64),
        out=np.zeros_like(n_matching_alleles, dtype=np.float64),
        where=n_total_alleles != 0,
        dtype=np.float64,
    )


def scores_array_to_df(
    sample_id_col_name: str,
    sample_ids: List[str],
    n_common_loci: np.ndarray,
    n_matching_alleles: np.ndarray,
    n_total_alleles: np.ndarray,
    tanabe_scores: np.ndarray,
    symmetric: bool = False,
) -> pd.DataFrame:
    f"""
    Convert symmetric score matrices into a long-form Pandas DataFrame.

    :param sample_id_col_name: name of column for sample IDs
    :param sample_ids: list of sample IDs corresponding to matrix rows/columns
    :param n_common_loci: symmetric array from `count_common_loci` (common loci count)
    :param n_matching_alleles: symmetric array from `count_matching_alleles`
    :param n_total_alleles: symmetric array from `count_common_loci` (total alleles)
    :param tanabe_scores: symmetric array from `compute_tanabe_scores`
    :param symmetric: if True, include both (id1, id2) and (id2, id1) rows
    :return: DataFrame with columns ```[
        '{sample_id_col_name}1',
        '{sample_id_col_name}2',
        'n_common_loci',
        'n_matching_alleles',
        'n_total_alleles',
        'tanabe_score'
    ]```
    """

    i_upper, j_upper = np.triu_indices_from(tanabe_scores, k=1)
    sample_id1 = pd.Categorical.from_codes(i_upper, categories=sample_ids)
    sample_id2 = pd.Categorical.from_codes(j_upper, categories=sample_ids)

    df = pd.DataFrame(
        {
            f"{sample_id_col_name}1": sample_id1,
            f"{sample_id_col_name}2": sample_id2,
            "n_common_loci": n_common_loci[i_upper, j_upper],
            "n_matching_alleles": n_matching_alleles[i_upper, j_upper],
            "n_total_alleles": n_total_alleles[i_upper, j_upper],
            "tanabe_score": tanabe_scores[i_upper, j_upper],
        }
    ).astype(
        {
            "n_common_loci": "uint16",
            "n_matching_alleles": "uint16",
            "n_total_alleles": "uint16",
            "tanabe_score": "float64",
        }
    )

    if symmetric:
        df = pd.concat(
            [
                df,
                df.rename(
                    columns={
                        f"{sample_id_col_name}1": f"{sample_id_col_name}2",
                        f"{sample_id_col_name}2": f"{sample_id_col_name}1",
                    }
                )[::-1],
            ],
            ignore_index=True,
        )

    return df.reset_index(drop=True)  # pyright: ignore
