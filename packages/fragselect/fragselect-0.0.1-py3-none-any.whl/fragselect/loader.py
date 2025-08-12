import os
from typing import List

import pandas as pd
from fragselect.shared_state import shared_state
from fragselect.preprocessing import Preprocessing
from fragselect.constants import DataConfig, ColumnConfig
from fragselect.ms1_features import FeatureConfig
from fragselect.utils import get_logger

logger = get_logger()


class Loader:
    """
    Loading files
    This class is responsible for loading files from a given directory.
    The files are expected to be in the following format:
    - intensity.csv
    - mass_error.csv
    - correlation.csv
    - height.csv
    - charge.csv
    - mz_observed.csv
    - type.csv
    - number.csv

    The files are expected to be in the same directory.

    """

    def __init__(
        self,
    ):
        self.df = None
        self.prec_idx = None
        self.preprocessing = Preprocessing()
        self.PG_DATA = "pg.matrix.tsv"
        self.PECURSOR_DATA = "precursor.matrix.tsv"
        self.PG_DATA_MAPPED = "pg.matrix.mapped.tsv"
        self.PREC_DATA_MAPPED = "precursor.matrix.mapped.tsv"

    def load_pg_data(
        self, output_folder: str, categorical_features: list = None
    ) -> pd.DataFrame:
        """
        Load the protein group data from a given directory and
        prprocess it. The preprocessing includes sorting columns
        by name, splitting pg names into species names, replacing
        0 with np.nan and log2 transformation.


        Parameters
        ----------
        output_folder : str
            The directory where the data is stored.
        categorical_features : list, optional
            The features to treat as categorical. Default is None.
        Returns
        -------
        pd.DataFrame
            The preprocessed protein group data.
        """
        if categorical_features:
            self.preprocessing.CATEGORICAL_FEATURES = categorical_features
        if self.PG_DATA_MAPPED in os.listdir(output_folder):
            filepath = os.path.join(output_folder, self.PG_DATA_MAPPED)
        else:
            filepath = os.path.join(output_folder, self.PG_DATA)
        data = pd.read_csv(filepath, delimiter="\t")
        return self.preprocessing.preprocess_pg_data(data)

    def load_features(self, output_folder: str) -> pd.DataFrame:
        """
        Load the features from a given directory.
        """
        precursor_features = self.load_precursor_file(output_folder)
        fragment_features = self.load_fragment_data_files(output_folder)
        features = {
            "ms1": precursor_features,
            "ms2": fragment_features,
        }
        return self._check_if_all_dataframes_have_the_same_columns(features)

    def load_precursor_data(
        self, output_folder: str, categorical_features: list = None
    ) -> pd.DataFrame:
        """
        Load the precursor tablefrom a given directory and
        prprocess it. The preprocessing includes sorting columns
        by name, splitting pg names into species names, replacing
        0 with np.nan and log2 transformation.


        Parameters
        ----------
        output_folder : str
            The directory where the data is stored.
        categorical_features : list, optional
            The features to treat as categorical. Default is None.
        Returns
        -------
        pd.DataFrame
            The preprocessed protein group data.
        """
        if categorical_features:
            self.preprocessing.CATEGORICAL_FEATURES = categorical_features
        if self.PREC_DATA_MAPPED in os.listdir(output_folder):
            filepath = os.path.join(output_folder, self.PREC_DATA_MAPPED)
        else:
            filepath = os.path.join(output_folder, self.PECURSOR_DATA)
        data = pd.read_csv(filepath, delimiter="\t")
        return self.preprocessing.preprocess_pg_data(data)

    def load_fragment_data_files(
        self, directory: str = None, feature_folder: str = "features"
    ) -> List[pd.DataFrame]:
        """
        Load all fragment data files from a given directory. The files
        are expected to be in the following format:
        - intensity.csv
        - mass_error.csv
        - correlation.csv
        - height.csv
        - charge.csv
        - mz_observed.csv
        - type.csv
        - number.csv

        Parameters
        ----------
        directory : str
            The directory where the data is stored.
        Returns
        -------
        List[pd.DataFrame]
            A list of dataframes containing the fragment data.
        """

        fragment_data_dict = {}

        # if no directoy is provided, use the current directory
        if not directory:
            directory = os.getcwd()

        directory = os.path.join(directory, feature_folder)

        for feature_name in DataConfig.MS2_FEATURE_NAMES:
            file_name = feature_name + ".csv"
            file_path = os.path.join(directory, file_name)
            df = pd.read_csv(file_path, index_col=0)
            logger.info("Reading MS2 feature: %s", feature_name)
            feature_name = "ms2_" + feature_name

            fragment_data_dict[feature_name] = df
        shared_state.ms2_identifiers = fragment_data_dict["ms2_intensity"][
            ColumnConfig.IDENTIFIERS
        ]
        return fragment_data_dict

    def _check_if_all_dataframes_have_the_same_columns(self, features: dict):
        """
        Check if all dataframes have the same columns.
        """

        identifiers = set(ColumnConfig.IDENTIFIERS)

        # Collect column sets for all MS1 and MS2 tables, excluding identifiers, and keep track of keys
        ms1_colsets = []
        ms1_keys = []
        for key in features["ms1"].keys():
            ms1_colsets.append(set(features["ms1"][key].columns) - identifiers)
            ms1_keys.append(key)

        ms2_colsets = []
        ms2_keys = []
        for key in features["ms2"].keys():
            ms2_colsets.append(set(features["ms2"][key].columns) - identifiers)
            ms2_keys.append(key)

        all_colsets = ms1_colsets + ms2_colsets
        all_keys = ms1_keys + ms2_keys

        # Find all unique columns (excluding identifiers)
        all_columns = set.union(*all_colsets)

        # For each column, check if it is present in every dataframe, and if not, which ones are missing it
        not_in_all = []
        missing_info = {}
        for col in all_columns:
            missing_keys = [
                k for k, colset in zip(all_keys, all_colsets) if col not in colset
            ]
            if missing_keys:
                not_in_all.append(col)
                missing_info[col] = missing_keys

        if not_in_all:
            logger.warning(
                "Columns not present in every dataframe (except for identifiers):"
            )
            for col in sorted(not_in_all):
                logger.warning(f"{col} (missing from: {', '.join(missing_info[col])})")
            # Remove these columns from all dataframes
            for key in features["ms1"].keys():
                logger.warning(f"Removing columns {not_in_all} from ms1 {key}")
                features["ms1"][key] = features["ms1"][key].drop(
                    columns=[
                        col for col in not_in_all if col in features["ms1"][key].columns
                    ],
                    errors="ignore",
                )
            for key in features["ms2"].keys():
                logger.warning(f"Removing columns {not_in_all} from ms2 {key}")
                features["ms2"][key] = features["ms2"][key].drop(
                    columns=[
                        col for col in not_in_all if col in features["ms2"][key].columns
                    ],
                    errors="ignore",
                )
        else:
            logger.warning(
                "All dataframes have the same columns (except for identifiers)."
            )

        return features

    def load_precursor_file(self, directory: str = None) -> pd.DataFrame:
        """
        Load the precursor data from a given directory and pivot
        the data by the given features.

        Parameters
        ----------
        directory : str
            The directory where the data is stored.
        Returns
        -------
        pd.DataFrame
            The pivoted precursor data.
        """
        # read data

        if not self.df:
            if not directory:
                directory = os.getcwd()
            file_path = os.path.join(directory, "precursors.tsv")
            logger.info("Reading precursor file from: %s", file_path)
            self.df = pd.read_csv(file_path, sep="\t", index_col=0)

        # pivot table by features
        precursor_df = self._pivot_table_by_feature(
            FeatureConfig.DEFAULT_FEATURES, self.df
        )

        return precursor_df

    def _pivot_table_by_feature(self, features: list, data: pd.DataFrame):
        precursor_data_dict = {}
        if isinstance(features, list):
            for feat in features:
                logger.info("Pivoting table by MS1 feature: %s", feat)
                if feat == "sequence":
                    data["prec_len"] = data["sequence"].str.len()
                    feat = "prec_len"

                prec_data = data.pivot_table(
                    index=["mod_seq_charge_hash", "pg", "precursor_idx"],
                    columns="run",
                    values=feat,
                ).reset_index()
                feat = "ms1_" + feat
                precursor_data_dict[feat] = prec_data

        else:
            logger.info("Pivoting table by feature: %s", features)
            prec_data = data.pivot_table(
                index=["mod_seq_charge_hash", "pg", "precursor_idx"],
                columns="run",
                values=features,
            ).reset_index()
            features = "ms1_" + features
            precursor_data_dict[features] = prec_data

        return precursor_data_dict
