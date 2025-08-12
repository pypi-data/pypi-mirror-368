from __future__ import annotations

from typing import List, Literal, Optional, Union

import numpy as np
import pandas as pd

from str_sim_scorer.utils import (
    collect_alleles,
    compute_tanabe_scores,
    count_common_loci,
    count_matching_alleles,
    scores_array_to_df,
)


class StrSimScorer:
    """
    A class for performing STR (Short Tandem Repeat) profile comparisons.

    This class provides an object-oriented interface for computing Tanabe scores
    between STR profiles, encapsulating the data processing pipeline and allowing
    for reuse of intermediate results.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        sample_id_col_name: str,
        locus_col_names: List[str],
    ) -> None:
        """
        Initialize the StrSimScorer with STR profile data.

        :param df: DataFrame containing STR profile data
        :param sample_id_col_name: Name of the column containing sample IDs
        :param locus_col_names: Names of columns containing allele counts at STR loci
        """

        self.df = df.copy()
        self.sample_id_col_name = sample_id_col_name
        self.locus_col_names = locus_col_names

        # computed results
        self._sample_ids: Optional[List[str]] = None
        self._alleles: Optional[pd.DataFrame] = None
        self._n_matching_alleles: Optional[np.ndarray] = None
        self._n_common_loci: Optional[np.ndarray] = None
        self._n_total_alleles: Optional[np.ndarray] = None
        self._tanabe_scores: Optional[np.ndarray] = None

    def sample_ids(self) -> List[str]:
        """
        Get the list of sample IDs in the dataset.

        :return: List of sorted sample IDs from the input DataFrame
        """

        if self._sample_ids is None:
            assert bool(~self.df[self.sample_id_col_name].duplicated().any()), (
                "There are duplicate sample IDs in the data frame"
            )
            self._sample_ids = list(
                self.df.sort_values(self.sample_id_col_name)[self.sample_id_col_name]
            )

        return self._sample_ids

    def alleles(self) -> pd.DataFrame:
        """
        Extract and process alleles from the STR profile data.

        Converts the wide-format STR data into a long-format DataFrame containing unique
        (sample_id, locus, allele count) records.

        :return: DataFrame with columns [sample_id_col_name, 'locus', 'allele']
        containing unique allele observations
        """

        if self._alleles is None:
            self._alleles = collect_alleles(
                self.df, self.sample_id_col_name, self.locus_col_names
            )

        return self._alleles

    def n_matching_alleles(self) -> np.ndarray:
        """
        Count matching alleles between all pairs of profiles.

        Computes a symmetric matrix where element (i,j) represents the number of alleles
        shared between profiles i and j across all STR loci. This implements the
        numerator of the Tanabe score algorithm.

        :return: Symmetric matrix of matching allele counts
        """

        if self._n_matching_alleles is None:
            self._n_matching_alleles = count_matching_alleles(
                df=self.alleles(),
                sample_id_col_name=self.sample_id_col_name,
                locus_col_name="locus",
                allele_col_name="allele",
                sample_ids=self.sample_ids(),
            )

        return self._n_matching_alleles

    def n_common_loci(self) -> np.ndarray:
        """
        Count common loci between all pairs of profiles.

        Computes a symmetric matrix where element (i,j) represents the number
        of loci where both profiles i and j have data. This isn't used in Tanabe score
        calculation but quantifies the available evidence for the calculation.

        :return: Symmetric matrix of common loci counts
        """

        if self._n_common_loci is None:
            self._n_common_loci, self._n_total_alleles = count_common_loci(
                df=self.alleles(),
                sample_id_col_name=self.sample_id_col_name,
                locus_col_name="locus",
                sample_ids=self.sample_ids(),
            )

        return self._n_common_loci

    def n_total_alleles(self) -> np.ndarray:
        """
        Count total alleles at common loci between all pairs of profiles.

        Computes a symmetric matrix where element (i,j) represents the total number of
        alleles observed in profiles i and j at loci where both profiles have data. This
        implements the denominator of the "non-empty markers" model of the Tanabe score
        algorithm.

        :return: Symmetric matrix of total allele counts at common loci
        """

        if self._n_total_alleles is None:
            self._n_common_loci, self._n_total_alleles = count_common_loci(
                df=self.alleles(),
                sample_id_col_name=self.sample_id_col_name,
                locus_col_name="locus",
                sample_ids=self.sample_ids(),
            )

        return self._n_total_alleles

    def tanabe_scores(
        self, output: Literal["array", "df", "symmetric_df"]
    ) -> Union[np.ndarray, pd.DataFrame]:
        """
        Compute Tanabe similarity scores for all profile pairs using the "non-empty
        markers" model.

        :param output: Output format (DataFrame outputs include columns for all matrices
        and not juist the scores)
            - 'array' for symmetric matrix
            - 'df' for a long DataFrame (just one of the triangulars of the array)
            - 'symmetric_df' for a long DataFrame (both triangulars)
        :return: Tanabe scores in the requested format
        """

        if self._tanabe_scores is None:
            self._tanabe_scores = compute_tanabe_scores(
                n_matching_alleles=self.n_matching_alleles(),
                n_total_alleles=self.n_total_alleles(),
            )

        if output == "array":
            return self._tanabe_scores
        elif output == "df":
            return scores_array_to_df(
                sample_ids=self.sample_ids(),
                n_matching_alleles=self.n_matching_alleles(),
                n_common_loci=self.n_common_loci(),
                n_total_alleles=self.n_total_alleles(),
                tanabe_scores=self._tanabe_scores,
                symmetric=False,
            )
        elif output == "symmetric_df":
            return scores_array_to_df(
                sample_ids=self.sample_ids(),
                n_matching_alleles=self.n_matching_alleles(),
                n_common_loci=self.n_common_loci(),
                n_total_alleles=self.n_total_alleles(),
                tanabe_scores=self._tanabe_scores,
                symmetric=True,
            )

    def empty(self) -> None:
        """
        Clear all cached computation results.
        """

        self._alleles = None
        self._sample_ids = None
        self._n_matching_alleles = None
        self._n_common_loci = None
        self._n_total_alleles = None
        self._tanabe_scores = None

    @property
    def n_profiles(self) -> int:
        """
        Get the number of profiles in the dataset.

        :return: Number of unique profiles
        """

        return len(self.sample_ids())

    @property
    def n_loci(self) -> int:
        """
        Get the number of STR loci being analyzed.

        :return: Number of locus columns specified during initialization
        """

        return len(self.locus_col_names)
