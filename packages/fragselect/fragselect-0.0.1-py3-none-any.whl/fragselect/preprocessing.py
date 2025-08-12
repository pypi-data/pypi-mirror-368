"""
This module preprocesses fragment
and precursor level data.

Dependencies:
    - numpy
    - sklearn
    - torch
    - selectlfq
    - copy
    - pandas
"""

from typing import Union, List, Tuple
import math
import numpy as np
import torch
import pandas as pd
from fragselect.shared_state import shared_state
from fragselect.featureengineering import (
    FeatureEngineeringPipeline,
    FeatureEngineering,
)
from fragselect.utils import repeater, get_logger
from fragselect.constants import ColumnConfig, DataConfig
from fragselect.featureengineering import _nan_correlation_w_ref_v2

logger = get_logger()


class PreprocessingPipeline:
    """
    This class encapsulates pipelines for preprocessing
    of precursor and fragment level data.
    """

    def __init__(
        self,
        standardize: bool = True,
    ):
        # self.pe = self._prep.positional_encoding(
        #     embedding_dim, dropout, no_of_samples, sample_list
        # )

        self.intensity_data_extract = None
        self.intensity_frag_data = None
        self.intensity_data = None
        self.feature_data = None
        self.pgs = None
        self.species = None
        self.not_dropped_columns = None
        self.original_columns = None
        self.sorted_columns = None
        self.identifiers = None
        self.feature_names = None
        self._feat_eng_pipe = FeatureEngineeringPipeline()
        self._feat_eng = FeatureEngineering()
        self._prep = Preprocessing()
        self.standardize = standardize

    def process(
        self,
        data: dict[str, pd.DataFrame],
        level: str = "pg",
    ):
        """
        This method preprocesses the data for the given level.

        Returns a list of preprocessed data, where each element
        represents the tokenised form for each protein group or
        precursor. Each element within the list is a 2D tensor
        where the columns represent the different features and
        each row represents each individual datapoint.

        Parameters
        ----------
        data : pd.DataFrame
            The data to be preprocessed.
        log2_indices : list
            Indices of dataframes for log2 transformation and alignment.
        intensity_idx: list
            Indices of dataframes for intensity extraction.
        level : str
            The level of data to be preprocessed. Can either be "pg" for protein group
            or "mod_seq_charge_hash" for precursor level preprocessing.
        kind : str
            What kind of preprocessing method to apply.
        Returns
        -------
        tuple
            The preprocessed data in fragment_data format. First element of tuple are
            the intensity layers, second element are the feature layers.
        """

        shared_state.level = level
        return self._feat_eng_preprocess_pipeline(
            data=data,
            level=level,
        )

    def _feat_eng_preprocess_pipeline(
        self,
        data: dict[str, pd.DataFrame],
        level: str,
    ) -> tuple[list[torch.Tensor], list[torch.Tensor]]:
        logger.info(
            "Processing MS1 data: %d features found - %s",
            len(set(data["ms1"].keys())),
            ", ".join(data["ms1"].keys()),
        )
        logger.info(
            "Processing MS2 data: %d features found - %s",
            len(set(data["ms2"].keys())),
            ", ".join(data["ms2"].keys()),
        )
        self._prep.ms2_identifiers = self._prep.save_identifiers(
            data["ms2"]["ms2_intensity"]
        )

        # feature engineering
        ms1_ms2_corr_feature = self._build_ms1_ms2_corr_data(data=data)

        mean_corr_across_frags_feature = self._build_mean_corr_data(
            data=data["ms2"]["ms2_intensity"]
        )

        fragment_datapoints = self._build_no_of_datapoints_data(
            data["ms2"]["ms2_intensity"], axis=1
        )
        sample_datapoints = self._build_no_of_datapoints_data(
            data["ms2"]["ms2_intensity"], axis=0
        )
        variance_data = self._build_variance_data(data["ms2"]["ms2_intensity"], axis=1)
        ms2_ref_corr_data = self._build_ms2_ref_corr_data(data=data["ms2"], no_traces=6)

        # Synchronize MS1 features with MS2 data structure
        synced_ms1_features = self._prep.sync_ms1_and_ms2_data(data["ms1"])

        # Combine all feature sets into a single dictionary
        combined_data = (
            synced_ms1_features
            | data["ms2"]
            | ms1_ms2_corr_feature
            | mean_corr_across_frags_feature
            | sample_datapoints
            | fragment_datapoints
            | variance_data
            | ms2_ref_corr_data
        )
        logger.info(
            "Processing combined data: %d features found - %s",
            len(set(combined_data.keys())),
            ", ".join(combined_data.keys()),
        )
        logger.info(
            "Number of features in MS1, MS2 and MS1-MS2 correlation data: %d",
            len(set(combined_data.keys())),
        )
        clean_data = self._clean_data(data=combined_data, level=level)
        logger.info(
            "Number of features in processed data after cleaning: %d",
            len(set(clean_data.keys())),
        )

        # extracting only the non log2 transformed data to shift final prediction up
        shared_state.lin_scaled_data = self._prep.extract_data_from_level(
            data=clean_data["ms2_intensity"], level=level
        )

        log_transf_data = self._apply_log2_transform(clean_data)

        data_extr = self._extract_data(data=log_transf_data, level=level)
        logger.info(
            "Number of features in extracted data: %d", len(set(data_extr.keys()))
        )

        std_feature_data, intensity_data = self._prepare_data(data_extr)

        return std_feature_data, intensity_data

    def _build_mean_corr_data(self, data: pd.DataFrame) -> dict[str, pd.DataFrame]:
        logger.info(
            "Building mean correlation across fragments data using intensity layer."
        )

        # prepare for feature engineering
        clean_data = self._clean_data(data=data, level="pg")
        mean_corr_data = self._feat_eng.compute_mean_corr_and_tile(clean_data)

        # build feature dataframe
        mean_corr_data = pd.concat(
            objs=[self._prep.ms2_identifiers, mean_corr_data.reset_index(drop=True)],
            axis=1,
        )
        return {"ms2_mean_corr_across_fragments": mean_corr_data}

    def _build_no_of_datapoints_data(
        self, data: pd.DataFrame, axis: int = 1
    ) -> dict[str, pd.DataFrame]:
        logger.info("Building no of datapoints data for axis %d.", axis)
        clean_data = self._clean_data(data=data, level="pg")
        no_of_datapoints = self._feat_eng.count_no_of_datapoints(clean_data, axis=axis)
        no_of_datapoints = pd.concat(
            objs=[self._prep.ms2_identifiers, no_of_datapoints.reset_index(drop=True)],
            axis=1,
        )

        return {f"no_of_datapoints_data_across_{axis}": no_of_datapoints}

    def _build_variance_data(
        self, data: pd.DataFrame, axis: int = 1
    ) -> dict[str, pd.DataFrame]:
        logger.info("Building variance data for axis %d.", axis)
        clean_data = self._clean_data(data=data, level="pg")

        variance_data = self._feat_eng.calculate_variance(clean_data, axis=axis)
        variance_data = pd.concat(
            objs=[self._prep.ms2_identifiers, variance_data.reset_index(drop=True)],
            axis=1,
        )

        return {f"variance_data_across_{axis}": variance_data}

    def _build_ms1_ms2_corr_data(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        log2_ms1_int_clean, log2_ms2_int_clean = self._prepare_ms1_ms2_data_for_corr(
            data
        )

        ms1_ms2_corr_data = _nan_correlation_w_ref_v2(
            log2_ms1_int_clean.values, log2_ms2_int_clean.values
        )

        ms1_ms2_corr_data = pd.DataFrame(
            ms1_ms2_corr_data,
            index=log2_ms1_int_clean.index,
            columns=log2_ms1_int_clean.columns,
        )
        ms1_ms2_corr_data = pd.concat(
            objs=[self._prep.ms2_identifiers, ms1_ms2_corr_data.reset_index(drop=True)],
            axis=1,
        )

        return {"ms1_ms2_correlation_data": ms1_ms2_corr_data}

    def _build_ms2_ref_corr_data(
        self, data: dict[str, pd.DataFrame], no_traces: int = 5
    ) -> dict[str, pd.DataFrame]:
        log2_transformed_intensity_data, ref_data = (
            self._prepare_for_ms2_ref_corr_calculation(data, no_traces=no_traces)
        )
        ms2_ref_corr_data = _nan_correlation_w_ref_v2(
            log2_transformed_intensity_data.values, ref_data.values
        )

        ms2_ref_corr_data = pd.DataFrame(
            ms2_ref_corr_data,
            index=log2_transformed_intensity_data.index,
            columns=log2_transformed_intensity_data.columns,
        )
        ms2_ref_corr_data = pd.concat(
            objs=[self._prep.ms2_identifiers, ms2_ref_corr_data.reset_index(drop=True)],
            axis=1,
        )

        return {"ms2_ref_corr_data": ms2_ref_corr_data}

    def _clean_data(
        self, data: Union[dict[str, pd.DataFrame], pd.DataFrame], level: str
    ) -> Union[dict[str, pd.DataFrame], pd.DataFrame]:
        clean_data = self._set_index(data, level)

        clean_data = self._drop_columns(clean_data)

        clean_data = self._reorder_columns(clean_data)

        clean_data = self._replacer(clean_data)

        return clean_data

    def _set_index(
        self, data: Union[dict[str, pd.DataFrame], pd.DataFrame], level: str
    ) -> Union[dict[str, pd.DataFrame], pd.DataFrame]:
        # Log intention once
        logger.info("Setting index for level %s.", level)

        # Handle dictionary of dataframes
        if isinstance(data, dict):
            result = {}
            for key, df in data.items():
                # Validate level exists in dataframe
                self._validate_level_exists(df, level, f"Datalayer: {key}")
                # Set index
                result[key] = df.set_index(level)
            return result

        # Handle single dataframe
        elif isinstance(data, pd.DataFrame):
            # Validate level exists in dataframe
            self._validate_level_exists(data, level, "Dataframe")
            # Set index
            return data.set_index(level)

        else:
            raise ValueError(f"Invalid data type: {type(data)}")

    def _validate_level_exists(
        self, df: pd.DataFrame, level: str, context: str = ""
    ) -> None:
        if isinstance(level, str):
            if level not in df.columns:
                raise ValueError(f"{context} - Level '{level}' not found in dataframe.")
        elif isinstance(level, list):
            missing = [lev for lev in level if lev not in df.columns]
            if missing:
                raise ValueError(
                    f"{context} - Levels {missing} not found in dataframe."
                )

    def _drop_columns(
        self, data: Union[dict[str, pd.DataFrame], pd.DataFrame]
    ) -> Union[dict[str, pd.DataFrame], pd.DataFrame]:
        if isinstance(data, dict):
            for k in data.keys():
                data[k] = data[k].drop(
                    columns=ColumnConfig.IDENTIFIERS, errors="ignore"
                )
            return data

        elif isinstance(data, pd.DataFrame):
            logger.info(
                "Columns that are not dropped can be found under attribute 'not_dropped_columns'."
            )
            data = data.drop(columns=ColumnConfig.IDENTIFIERS, errors="ignore")
            return data

        else:
            raise ValueError(f"Invalid data type: {type(data)}")

    def _reorder_columns(
        self, data: Union[dict[str, pd.DataFrame], pd.DataFrame]
    ) -> Union[dict[str, pd.DataFrame], pd.DataFrame]:
        logger.info(
            "Reordering columns. Original column order can be found under attribute 'original_columns'."
        )

        if isinstance(data, dict):
            # Use first processed DataFrame for sorted_columns
            shared_state.sorted_columns = next(iter(data.values())).columns
            # Get first DataFrame to use as reference
            reference_df = next(iter(data.values()))

            # Check if all DataFrames have the same columns
            if not all(
                sorted(df.columns) == sorted(reference_df.columns)
                for df in data.values()
            ):
                raise ValueError("All dataframes must have the same columns.")

            # Store original columns from reference DataFrame
            self.original_columns = reference_df.columns

            # Process each DataFrame in the dictionary
            for k in data.keys():
                data[k] = self._prep.reorder_columns(data[k])

        elif isinstance(data, pd.DataFrame):
            self.original_columns = data.columns
            data = self._prep.reorder_columns(data)
            shared_state.sorted_columns = data.columns

        else:
            raise ValueError(f"Invalid data type: {type(data)}")
        return data

    def _replacer(
        self, data: Union[dict[str, pd.DataFrame], pd.DataFrame]
    ) -> Union[dict[str, pd.DataFrame], pd.DataFrame]:
        logger.info("Replacing invalid values with np.nan.")

        if isinstance(data, dict):
            for k in data.keys():
                data_values = data[k].values
                data[k][data_values == 0] = np.nan
        elif isinstance(data, pd.DataFrame):
            data_values = data.values
            data[data_values == 0] = np.nan
        else:
            raise ValueError(f"Invalid data type: {type(data)}")

        return data

    def _apply_log2_transform(
        self, data: Union[dict[str, pd.DataFrame], pd.DataFrame]
    ) -> Union[dict[str, pd.DataFrame], pd.DataFrame]:
        if isinstance(data, dict):
            for k in data.keys():
                if k in DataConfig.LOG2_TRANSFORM_FEATURES:
                    data[k] = np.log2(data[k])
                    logger.info("Log2 transformation of data %s.", k)
        elif isinstance(data, pd.DataFrame):
            data = np.log2(data)
            logger.info("Log2 transformation of data.")
        else:
            raise ValueError(f"Invalid data type: {type(data)}")

        return data

    def _prepare_data(
        self, data: Union[dict[str, pd.DataFrame], pd.DataFrame]
    ) -> tuple[list[torch.Tensor], list[torch.Tensor]]:
        data_prep = self._prep.init_align(data)

        # convert to list of tensors
        self.feature_names = list(data_prep.keys())
        data_prep = [data_prep[k] for k in data_prep.keys()]
        logger.info("Number of features in data_prep: %d", len(data_prep))

        input_data = self._prep.combine_data(*data_prep)

        fragment_data = self._homogenize_data(input_data)

        # isolate intensity and feature data
        feature_data = self._remove_intensity_layer(fragment_data)

        self.intensity_data = [
            protein[:, :, self.feature_names.index("ms2_intensity")]
            for protein in fragment_data
        ]

        std_feature_data = self._standardize_data(feature_data)
        return std_feature_data, self.intensity_data

    def _standardize_data(self, data: list[torch.Tensor]) -> list[torch.Tensor]:
        if self.standardize:
            logger.info("Standardizing data.")
            return repeater(
                data, function=self._prep.standardize, instance_method=False
            )
        else:
            return data

    def _remove_intensity_layer(self, data):
        logger.info("Removing feature layer: ms2_intensity.")
        idx = self.feature_names.index("ms2_intensity")

        return repeater(
            data, function=np.delete, instance_method=False, axis=2, obj=idx
        )

    def _homogenize_data(self, data):
        logger.info(
            "Homogenizing data. Inconsistent missing values across the 3rd dimension will be replaced with np.nan."
        )

        return repeater(
            data,
            function=self._prep.logical_masking_and_filling,
            instance_method=False,
        )

    def _extract_data(
        self, data: dict[str, pd.DataFrame], level: str
    ) -> dict[str, pd.DataFrame]:
        logger.info("Extracting data from level: %s.", level)

        shared_state.level_information = list(
            data["ms2_intensity"].groupby(level).groups.keys()
        )

        for k in data.keys():
            data[k] = self._prep.extract_data_from_level(
                data[k],
                level=level,
            )

        return data

    def _prepare_for_ms2_ref_corr_calculation(self, data, no_traces: int = 5):
        preprocessed_corr_data = data["ms2_correlation"].set_index(
            ColumnConfig.IDENTIFIERS
        )
        mask = (
            preprocessed_corr_data.mean(axis=1)
            .groupby("pg")
            .rank(ascending=False, method="first")
            < no_traces
        ).values

        clean_intensity_data = self._clean_data(
            data["ms2_intensity"], level=ColumnConfig.IDENTIFIERS
        )
        log2_transformed_intensity_data = self._apply_log2_transform(
            clean_intensity_data
        )

        ref_data = log2_transformed_intensity_data[mask].groupby("pg").mean()
        ref_data = self._prep.ms2_identifiers.merge(
            ref_data, on="pg", how="left"
        ).set_index(ColumnConfig.IDENTIFIERS)

        return log2_transformed_intensity_data, ref_data

    def _prepare_ms1_ms2_data_for_corr(
        self, data: dict[str, pd.DataFrame]
    ) -> tuple[np.ndarray, np.ndarray]:
        ms2_identifiers = data["ms2"]["ms2_intensity"][ColumnConfig.IDENTIFIERS]

        ms1_intensity_tiled = ms2_identifiers.merge(
            data["ms1"]["ms1_intensity"],
            on=["precursor_idx", "pg", "mod_seq_charge_hash"],
            how="left",
        )

        ms1_int_clean = self._clean_data(
            ms1_intensity_tiled, level=ColumnConfig.IDENTIFIERS
        )
        log2_ms1_int_clean = self._apply_log2_transform(ms1_int_clean)

        ms2_int_clean = self._clean_data(
            data["ms2"]["ms2_intensity"], level=ColumnConfig.IDENTIFIERS
        )
        log2_ms2_int_clean = self._apply_log2_transform(ms2_int_clean)

        return log2_ms1_int_clean, log2_ms2_int_clean

    def _repeater(self, data, function, instance_method, **kwargs):
        """
        This function applies a given function to either a single element or a list of elements.
        """
        if not isinstance(data, (list, tuple)):
            data = [data]

        results = []
        for subset in data:
            if instance_method:
                result = getattr(subset, function)(**kwargs)
            else:
                result = function(subset, **kwargs)
            results.append(result)

        return results[0] if len(results) == 1 else results


class Preprocessing:
    """
    This class includes methods for preprocessing
    before data can be used for training.
    """

    def __init__(self):
        # isl_trc_fdr = IsolatedTraceFinder()
        self.sorted_cols = None
        self.pgs_pg_level = None
        self.additional_data_prep = None
        self.orig_data = None
        self.species = None
        self.x_size = None
        self.init_shape = None
        self.data_size = None
        self.mask = None
        self.prec_idx = None
        self.ms2_identifiers = None
        self.agg_features = False

    def save_identifiers(self, data: pd.DataFrame):
        """
        Save the identifiers from the data to merge with features
        thats are engineered that have lost the unique identifiers.
        """
        return data[ColumnConfig.IDENTIFIERS]

    def build_feature_df(self, feature: pd.DataFrame, ms_indices: list[pd.MultiIndex]):
        """
        Build the feature dataframe.
        """
        reconstructed_ids = self.reconstruct_identifiers_after_extraction(ms_indices)
        ms1_ms2_corr_data = pd.concat(objs=[reconstructed_ids, feature], axis=1)

        logger.info(
            "Reconstructed IDs include %d elements, MS1-MS2 correlations include %d elements",
            reconstructed_ids.shape[0],
            ms1_ms2_corr_data.shape[0],
        )

        if reconstructed_ids.shape[0] != ms1_ms2_corr_data.shape[0]:
            logger.warning(
                "Inconsistent IDs, reconstructed Ids have %d elements while MS1-MS2 correlations have %d elements",
                reconstructed_ids.shape[0],
                ms1_ms2_corr_data.shape[0],
            )

        # reorder the data to the original order
        ms1_ms2_corr_data = self.ms2_identifiers.merge(
            ms1_ms2_corr_data, on=ColumnConfig.PRECURSOR_FRAGMENT_IDENTIFIER, how="left"
        )
        return ms1_ms2_corr_data

    def reconstruct_identifiers_after_extraction(
        self, identifiers, identifier_names=None
    ):
        """
        Reconstruct the identifiers after extraction. If no identifiers are provided, the identifiers from the shared state are used.
        If no identifier names are provided, the default names are used in this case the precursor_idx and ion.

        Parameters:
            identifiers: pd.DataFrame
                The identifiers extracted from data. These may include  "precursor_idx","ion","pg","mod_seq_hash","mod_seq_charge_hash",
            identifier_names: list[str]
                The names of the identifiers.
        Returns:
            reconstructed_identifiers: pd.DataFrame
                The reconstructed identifiers.
        """

        # create identifiers for the ms1-ms2 correlation
        all_pairs = []

        if identifier_names is None:
            identifier_names = ColumnConfig.PRECURSOR_FRAGMENT_IDENTIFIER

        for index in identifiers:
            all_pairs.extend(list(index))

        reconstructed_identifiers = pd.DataFrame(all_pairs, columns=identifier_names)
        return reconstructed_identifiers

    def sync_ms1_and_ms2_data(self, data: dict[pd.DataFrame]) -> dict[pd.DataFrame]:
        """
        Sync the ms1 and ms2 data by the precursor index. The data is
        sorted by the ion column, so that the data is in the same order
        for both ms1 and ms2.

        Parameters
        ----------
        data : dict[str, pd.DataFrame]
            The data to sync.
        Returns
        -------
        dict[str, pd.DataFrame]
            The synced data.
        """
        if self.ms2_identifiers is None:
            raise ValueError(
                "Identifiers are not defined, load fragment data first to retrieve precursor index"
            )
        else:
            # merge the identifiers
            for key in data.keys():
                data[key] = self.ms2_identifiers.merge(
                    data[key], on=ColumnConfig.PRECURSOR_IDENTIFIERS, how="left"
                )
            # sort the data by the ion column
            for key in data.keys():
                data[key] = self._sort_by_list(
                    data=data[key],
                    col="ion",
                    reindexed_list=self.ms2_identifiers["ion"].tolist(),
                )
                if (
                    self.ms2_identifiers["ion"].values != data[key]["ion"].values
                ).all():
                    consistencies = (
                        self.ms2_identifiers["ion"].values == data[key]["ion"].values
                    )
                    indices_of_inconsistencies = np.where(~consistencies)[0]
                    logger.warning(
                        "Inconsistent ions for data %s at %s",
                        key,
                        indices_of_inconsistencies,
                    )

            return data

    def _sort_by_list(
        self, data: pd.DataFrame, col: str, reindexed_list: List[int]
    ) -> pd.DataFrame:
        return data.set_index(col).reindex(reindexed_list).reset_index()

    def get_species(self, data: pd.DataFrame, level: str) -> list:
        """
        Extracts and returns a list of group identifiers
        from the given DataFrame.

        Parameters
        ----------
        data : pd.DataFrame
            The input DataFrame containing the data to be processed.
        level : str
            The level at which to group the data in the DataFrame.
            Can be either "pg" for protein group or "mod_seq_charge_hash" for precursor.

        Returns
        -------
        list
            A list of unique group identifiers extracted from the DataFrame.
        """

        if level == "pg":
            species = (
                pd.Series(data[0].groupby(level).groups.keys())
                .str.split("_")
                .str[1]
                .tolist()
            )

            species = np.array(
                pd.Series(species)
                .str.replace("ECODH", "ECOLI")
                .str.replace("ECOBW", "ECOLI")
            )

        elif level == "mod_seq_charge_hash":
            level = ["mod_seq_charge_hash", "pg"]

            species = pd.Series(data[0].groupby(level).groups.keys())
        return species

    def filter_large_dataset_by_pg(self, data: pd.DataFrame, value: str) -> np.array:
        """
        This method creates a mask by
        filtering for a specific value within
        the 'pg' column.

        Parameters
        ----------
        data : pd.DataFrame
            The data to be filtered.
        value : str
            The value to filter by.

        Returns
        -------
        np.array
            A boolean mask.
        """
        return data["pg"].values == value

    def sample_normalizer(
        self, frag_level_intensity_data: pd.DataFrame, threshold: int = 0.3
    ) -> np.array:
        """
        This method normalizes the data by sample.

        Parameters
        ----------
        frag_level_intensity_data : pd.DataFrame
            The data to be normalized.

        Returns
        -------
        np.array
            Normalized data.
        """
        frag_level_aligned_intensity_data = self.align_by_level(
            frag_level_intensity_data
        )
        pg_level_non_reg_intensity_data = (
            self._get_non_regularatory_pg_level_intensity_data(
                frag_level_aligned_intensity_data, threshold=threshold
            )
        )
        values_to_shift = self._get_values_to_shift_for_normalisation_by_sample(
            pg_level_non_reg_intensity_data
        )
        frag_level_sample_normalized_data = self.normalize_by_sample(
            frag_level_aligned_intensity_data, values_to_shift
        )

        return frag_level_sample_normalized_data

    def align_by_level(
        self,
        data: List[pd.DataFrame],
        level: str = "pg",
        indices: List[int] = None,
    ):
        """
        Aligns the fragment level intensity data.

        Parameters
        ----------
        data : pd.DataFrame
            The data to be aligned. The dataframe should contain a string column "pg"
            which is used to level the data and fragment intensity values only.
        level : str
            The column to level by.

        Returns
        -------
        pd.DataFrame
            The aligned data.
        """

        for idx in indices:
            # calculate the median intensity for each group eg. "pg"
            pg_level_median_data = data[idx].groupby(level).median()

            # calculate difference between fragmen level intensity and pg level median intensity
            frag_level_diffs_data = data[idx] - pg_level_median_data

            # calculate the median of the difference
            frag_level_values_to_shift_data = np.nanmedian(
                frag_level_diffs_data.values, axis=1, keepdims=True
            )

            # shift by the median difference
            data[idx] = data[idx] - frag_level_values_to_shift_data

        return data

    def _get_non_regularatory_pg_level_intensity_data(
        self, frag_level_aligned_intensity_data: pd.DataFrame, threshold: int = 0.2
    ):
        """
        Filters out non-regulatory protein groups.

        Regulation of proteins is estimated by calculating the standard deviation of the mean intensity values across all samples. If the standard deviation is below a certain threshold, the protein group is considered non-regulatory.

        Parameters
        ----------
        frag_level_aligned_intensity_data : pd.DataFrame
            The aligned intensity data. Data must be aligned before this method is called.
        threshold : int
            The threshold for the standard deviation. Every protein group with a standard deviation below this threshold is considered non-regulatory.

        Returns
        -------
        pd.DataFrame
            The non-regulatory protein groups.
        """
        pg_level_mean_intensity_data = frag_level_aligned_intensity_data.groupby(
            frag_level_aligned_intensity_data.index
        ).mean()
        pg_level_std = pg_level_mean_intensity_data.std(axis=1)
        mask = pg_level_std < threshold

        pg_level_non_reg_intensity_data = pg_level_mean_intensity_data[mask].dropna()

        return pg_level_non_reg_intensity_data

    def _get_values_to_shift_for_normalisation_by_sample(
        self, pg_level_non_reg_intensity_data: pd.DataFrame
    ) -> np.array:
        """
        This method calculates the values to shift for
        normalisation across samples. The values to shift are
        calculated by taking the median of the median intensity
        within all samples, and then subtracting this median
        from the median intensity of each sample.

        Parameters
        ----------
        pg_level_non_reg_intensity_data : pd.DataFrame
            The non-regulatory protein groups.
            The dataframe must contain the pg level intensity values
            for each sample of non-regulatory protein groups.

        Returns
        -------
        np.array
            The values to shift for normalisation.
        """
        median_intensity_across_sa_data = pg_level_non_reg_intensity_data.median(axis=0)

        overall_median_intensity = np.nanmedian(median_intensity_across_sa_data)
        values_to_shift = median_intensity_across_sa_data - overall_median_intensity

        return values_to_shift

    def _normalize_by_sample_(
        self, frag_level_aligned_intensity_data: pd.DataFrame, values_to_shift: np.array
    ) -> pd.DataFrame:
        """
        This method normalizes the data by sample. The values
        to shift are subtracted from the intensity values.

        Parameters
        ----------
        frag_level_aligned_intensity_data : pd.DataFrame
            The aligned intensity data. Data must be aligned
            before this method is called and should be on
            the fragment level.
        values_to_shift : np.array
            The values to shift for normalisation.

        Returns
        -------
        pd.DataFrame
            The normalized data.
        """
        return frag_level_aligned_intensity_data - values_to_shift.values

    def _get_identifier(self, data: pd.DataFrame, identifier: str) -> list:
        """
        Extracts identifiers from the given DataFrame.

        Parameters
        ----------
        data : pd.DataFrame
            The data from which the identifiers are to be extracted.
        identifier : str
            The identifier to be extracted from the data.

        Returns
        -------
        list
            A list of extracted identifiers.
        """

        return list(data.groupby(identifier).groups.keys())

    def _get_mod_seq_charge_hash_id_and_pg(
        self, data: pd.DataFrame, complementary: bool = False
    ) -> dict:
        """
        Get the mod_seq_charge_hash ids and pg ids from the data.

        This function is used to get the mod_seq_charge_hash ids and
        pg ids from the data. The mod_seq_charge_hash ids are used as
        keys and the pg ids are used as values in the dictionary.
        The complementary parameter is used to switch the keys and
        values in the dictionary.

        Parameters
        ----------
        data : pd.DataFrame
            The data from which the ids are to be extracted.
        complementary : bool
            If False, the keys are the mod_seq_charge_hash ids
            and the values are the pg ids. If True, the keys are
            the pg ids and the values are the mod_seq_charge_hash
            ids.

        Returns
        -------
        dict
            A dictionary with mod_seq_charge_hash and corresponding pg ids.
        """
        if complementary:
            return (
                data.groupby("mod_seq_charge_hash")["pg"]
                .apply(set)
                .apply(lambda s: next(iter(s)))
                .to_dict()
            )

        else:
            return (
                data.groupby("pg")["mod_seq_charge_hash"]
                .apply(set)
                .apply(lambda s: next(iter(s)))
                .to_dict()
            )

    def reorder_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Sort the columns of the data in alphabetical order.

        Parameters
        ----------
        data : pd.DataFrame
            The data to be reordered.

        Returns
        -------
        pd.DataFrame
            The reordered data.
        """
        self.sorted_cols = sorted(data.columns)

        return data[self.sorted_cols]

    def extract_data_from_level(
        self, data: pd.DataFrame, level: str = "pg", return_index: bool = False
    ) -> Union[List[np.ndarray], Tuple[List[np.ndarray], List[np.ndarray]]]:
        """
        Create a list of np.array based on the level to group by.
        The data is grouped by the level and the values are
        extracted and stored in a list.

        Parameters
        ----------
        data : pd.DataFrame
            The data to be processed.
        level : str
            The level to group by. Either "pg" for protein group
            or "mod_seq_charge_hash" for precursor.
        return_index : bool, optional
            If True, the index is also returned. The index is used
            to identify the protein group or precursor the data
            belongs to.

        Returns
        -------
        list
            A list of np.array with the extracted values.
        list, optional
            A list of the index, if return_index is True.
        """
        grouped = data.groupby(level)
        fragment_data_subsets = [(group.index, group.values) for _, group in grouped]

        if return_index:
            fragment_data_subsets, fragment_data_index = zip(*fragment_data_subsets)

            return list(fragment_data_subsets), list(fragment_data_index)
        else:
            fragment_data_subsets = [data for _, data in fragment_data_subsets]
            return fragment_data_subsets

    def combine_data(self, *args: list) -> list:
        """
        Combine data in the third dimension. The data is combined
        by stacking the data along the third dimension.

        Parameters
        ----------
        *args : list
            A list of data to be combined. Every element of this list
            represents a different feature.

        Returns
        -------
        np.array
            The combined data.
        """

        logger.info("Stacking feature layers into 3D tensors.")
        return [np.stack(datasets, axis=2) for datasets in zip(*args)]

    def calculate_variance_sparsity_metric_for_each_protein(
        self, list_of_datasets: list
    ) -> np.array:
        """
        Calculate the intensity's variance * sparsity metric for each fragment
        within a protein. The variance * sparsity metric is calculated
        as the variance multiplied by the sparsity of each fragment.

        Parameters
        ----------
        list_of_datasets : list
            A list of 3D arrays with shape (n_samples, n_fragments, n_features),
            where the intensity is the first feature.

        Returns
        -------
        np.array
            An array of variance * sparsity metric for each fragment
            within a protein.
        """
        var_spar = np.empty(len(list_of_datasets))
        for i, subset in enumerate(list_of_datasets):
            flatten_int = subset[:, :, 0].flatten()
            sparsity = len(flatten_int[~(flatten_int.isnan())]) / len(flatten_int)
            var = np.nanvar(flatten_int)
            var_spar[i] = var * sparsity

        return var_spar

    def train_val_split_for_simulation(self, list_of_datasets: list) -> list:
        """
        Split data into training and validation datasets.

        Parameters
        ----------
        list_of_datasets : list
            A list of 3D arrays with shape (n_samples, n_fragments, n_features).

        Returns
        -------
        tuple
            A tuple containing two lists:
            - The training data.
            - The validation data.
        """
        return list_of_datasets[0::2], list_of_datasets[1::2]

    def train_val_split(self, x: list, y: list, train_size: int):
        """
        Split data into training and validation datasets.

        Parameters
        ----------
        x : list
            A list of 3D arrays with shape (n_samples, n_fragments, n_features).
        y : list
            A list of corresponding labels.
        train_size : int
            The proportion of the dataset to include in the training split.

        Returns
        -------
        tuple
            A tuple containing:
            - x_train : list
            The training data.
            - x_val : list
            The validation data.
            - y_train : list
            The training labels.
            - y_val : list
            The validation labels.
        """

        data_idx = int(train_size * len(x))

        x_train = x[:data_idx]
        x_val = x[data_idx:]

        y_train = y[:data_idx]
        y_val = y[data_idx:]

        return x_train, x_val, y_train, y_val

    def init_align(
        self,
        data: Union[
            list[pd.DataFrame],
            list[torch.Tensor],
            list[np.array],
        ],
    ) -> list[pd.DataFrame]:
        """
        Aligns the data by subtracting the median intensity values.

        This method aligns the data by subtracting the median intensity values
        from the data. The median intensity values are calculated for each sample.

        Parameters
        ----------
        data : torch.Tensor or list
            The data to be aligned.
        indices : list, optional
            The indices of the data to be aligned.

        Returns
        -------
        torch.Tensor or list
            The aligned data.
        """

        if isinstance(data, dict):
            for k in data.keys():
                if k in DataConfig.ALIGN_FEATURES:
                    data[k] = [self._align(arr) for arr in data[k]]
                    logger.info("Aligning data %s.", k)
            return data

        else:
            return [self._align(arr) for arr in data]

    def _align(self, data: np.array) -> np.array:
        """
        Aligns the data by subtracting the median intensity values.
        """

        median_trace = np.nanmedian(data, axis=0)
        differences = data - median_trace
        median_diff = np.nanmedian(differences, axis=1, keepdims=True)
        aligned_data = data - median_diff
        return aligned_data

    def weighted_average(
        self, data: torch.Tensor, qs: torch.Tensor, dim: int = 0, thresh: float = 0.5
    ):
        """
        This method calculates the weighted average of the data.
        Missing values are ignored in the calculation.

        Parameters
        ----------
        data : torch.Tensor
            The data to be averaged.
        qs : torch.Tensor
            The quality scores.
        dim : int, optional
            The dimension along which to calculate the average, by default 0.
        thresh : float, optional
            The threshold for the quality scores. Values below this threshold are ignored
            in the calculation, by default 0.5.

        Returns
        -------
        torch.Tensor
            The weighted average.
        """
        if isinstance(data, np.ndarray):
            qs = np.where(qs < thresh, 0, qs)
            numerator = np.nansum(np.multiply(data, qs), axis=dim)
            denominator = np.nansum(qs, axis=dim)

        else:
            qs = torch.where(qs < thresh, 0, qs)
            numerator = torch.nansum(torch.multiply(data, qs), dim=dim)
            denominator = torch.nansum(qs, dim=dim)

        return numerator / denominator

    def preprocessing_for_forward_prop(self, x: torch.Tensor) -> torch.Tensor:
        """
        Preprocesses the input tensor for forward propagation.

        This method performs several preprocessing steps on the input tensor:
        1. Reshapes the input tensor from 3D to 2D. The shape will change from
           (n_samples, n_fragments, n_features) to (n_samples * n_fragments, n_features).
        2. Removes missing values from the tensor. After flattening the tensor,
           the missing values are removed from the tensor.

        Parameters
        ----------
        x : torch.Tensor
            The input tensor to be preprocessed. It has a shape of
            (n_samples, n_fragments, n_features).

        Returns
        -------
        torch.Tensor
            The preprocessed tensor with a shape of
            (n_samples * n_fragments, n_features).
        """

        # if the data is 3 dimentional that do that

        if x.ndim == 3:
            self.agg_features = False
            x_reshaped = self._reshape_input(x)
            self.x_size = x_reshaped.shape[0]
            x_reshaped_rem = self._remove_missing_values(x_reshaped)

            return x_reshaped_rem
        self.agg_features = True
        return x

    def _reshape_input(
        self, data: Union[np.ndarray, torch.Tensor]
    ) -> Union[np.ndarray, torch.Tensor]:
        """
        Reshapes the input data for processing.

        This method reshapes the input data such that shape changes from
        (n_samples, n_fragments, n_features) to (n_samples * n_fragments, n_features).

        Parameters
        ----------
        data : numpy.ndarray or torch.Tensor
            The input data to be reshaped. It is expected to be a 3-dimensional array.

        Returns
        -------
        numpy.ndarray or torch.Tensor
            The reshaped data with shape (-1, data.shape[2]).
        """

        self.init_shape = data.shape[:2]
        self.data_size = data.shape[2]
        return data.reshape(-1, self.data_size)

    def _remove_missing_values(self, x: torch.Tensor) -> torch.Tensor:
        """
        Remove rows with missing values from the input data.

        This method creates a mask to filter out rows where the first column contains NaN values.
        The mask is stored as an instance variable `self.mask`.

        Parameters
        ----------
        x : torch.Tensor
            The input data from which missing values need to be removed.

        Returns
        -------
        torch.Tensor
            Data with rows containing NaN values removed.
        """
        self.mask = ~x.isnan()[:, 0]
        return x[self.mask]

    def standardize(
        self, x: Union[np.ndarray, torch.Tensor]
    ) -> Union[np.ndarray, torch.Tensor]:
        """
        Standardizes the input array by removing the mean and scaling to unit variance.

        Parameters
        ----------
        x : numpy.ndarray or torch.Tensor
            The input array to be standardized.

        Returns
        -------
        numpy.ndarray
            The standardized array where the mean is 0 and the standard deviation is 1.
        """

        mean = np.nanmean(x, axis=0, keepdims=True)
        std = np.nanstd(x, axis=0, keepdims=True)

        return (x - mean) / (std + 1e-10)

    def reshape_from_1d_to_2d(self, scores: torch.Tensor) -> torch.Tensor:
        """
        Reshape a 1D tensor of scores back to its original 2D shape.

        This method takes a 1D tensor of scores/output from model and reshapes it back to its
        original 2D shape using the initial size and mask stored in the object.

        Parameters
        ----------
        scores : torch.Tensor
            A 1D tensor containing the scores to be reshaped.

        Returns
        -------
        torch.Tensor
            A 2D tensor with the original shape before reshaping.
        """

        # reshape to initial size before self._reshape_input

        if not self.agg_features:
            scores_reshaped = torch.full((self.x_size, 1), torch.nan)
            scores_reshaped[self.mask] = scores
            return scores_reshaped.reshape(self.init_shape)
        return scores

    def _min_max_scaler(self, data, minimum=0, maximum=1, axis=1):
        data_std = (data - np.nanmin(data, axis=axis)) / (
            np.nanmax(data, axis=axis) - np.nanmin(data, axis=axis)
        )
        return data_std * (maximum - minimum) + minimum

    def logical_masking_and_filling(self, data):
        """
        This method applies logical masking to the data.
        Inconsistent missing values across the 3rd dimension
        will be replaced with np.nan, so that across the
        feature dimension the numbers and positions of
        nan values are the same.

        Parameters
        ----------
        data : torch.Tensor
            The data to be masked.

        Returns
        -------
        torch.Tensor
            The masked data with consistent missing values
            across the feature dimension.
        """

        mask = np.isnan(data).any(axis=2, keepdims=True)
        masked_data = np.where(mask, np.nan, data)
        return masked_data

    def _create_mask_for_large_dataset(self, data, value):
        return data["pg"].values == value

    def shift(self, data, shift, dim):
        """
        Shift the data by a given shift. The shift matrix
        will first be aggregated along the sample or fragment
        axis and then subtracted from the data.

        Parameters
        ----------
        data : torch.Tensor
            The intensity matrix data to be shifted, shape (n_samples, n_fragments).
        shift : torch.Tensor
            The shift to be applied, shape (n_samples, n_fragments).
        dim : int
            The dimension along which to shift the data.
            1 means aggregation along the sample axis and within a fragment.
            Shifting will be done along sample axis.
            0 means aggregation along the fragment axis and within a sample.
            Shifting will be done along the fragment axis.

        Returns
        -------
        torch.Tensor
            The shifted data.
        """
        if dim == 1:
            return data - torch.nanmedian(shift, dim=dim, keepdim=True)[0].reshape(
                -1, 1
            )

        elif dim == 0:
            return data - torch.nanmedian(shift, dim=dim, keepdim=True)[0].reshape(
                1, -1
            )

    def remove_features(self, data: np.array, feature: list[int]) -> np.array:
        """
        Remove feature space from 3D tensor data.

        Parameters
        ----------
        data : torch.Tensor
            3D tensor data.
        feature : list[int]
            List of features to remove.

        Returns
        -------
        torch.Tensor
            3D tensor data with features removed.
        """
        removed_data = [np.delete(dataset.numpy(), feature, axis=2) for dataset in data]
        removed_data = [torch.from_numpy(dataset) for dataset in removed_data]
        return removed_data

    def prepare_input_for_train(self, data: np.array) -> tuple:
        """
        Prepares the input data for training by converting it to a PyTorch tensor and standardizing it.

        Parameters
        ----------
        data : np.ndarray
            The input data to be prepared. It is expected to be a 3D numpy array where the first
            dimension represents the samples, the second dimension represents the fragments,
            and the third dimension represents the features.

        Returns
        -------
        tuple
            A tuple containing:
            - input_data (torch.Tensor): The standardized input data as a PyTorch tensor.
            - intensity_layer (torch.Tensor): The intensity layer extracted from the input
              data as a PyTorch tensor.
        """
        input_data = torch.from_numpy(data.copy()).float()
        input_data = self.standardize(input_data)
        intensity_layer = torch.from_numpy(data[:, :, 0]).float()

        return input_data, intensity_layer

    def preprocess_pg_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocesses the protein group data.

        Parameters
        ----------
        data : pd.DataFrame
            The protein group data to be preprocessed.

        Returns
        -------
        pd.DataFrame
            The preprocessed protein group data.
        """

        # sort by column names
        sorted_cols = sorted(data.columns)
        proc_data = data[sorted_cols]
        pg_data = proc_data.drop(columns=ColumnConfig.IDENTIFIERS, errors="ignore")

        # replace 0 with nan
        pg_data = pg_data.replace(0, np.nan)

        # log2 tranfrom data
        pg_data = np.log2(pg_data)

        # merge categorical features back
        valid_cols = list(
            set(ColumnConfig.IDENTIFIERS).intersection(set(proc_data.columns))
        )

        pg_data = pd.concat([pg_data, proc_data[valid_cols]], axis=1)

        return pg_data

    def positional_encoding(
        self,
        embedding_dim: int = 1,
        no_of_samples: int = 10,
        sample_list: np.array = None,
    ):
        """
        Positional encoding.

        Parameters
        ----------
        embedding_dim : int
            The embedding dimension.
        no_of_samples : int, optional
            The number of samples, by default 10
        sample_list : np.array, optional
            The sample list, eg. np.array([0, 0, 0, 1, 1, 1]), means that
            the first 3 samples are the same, the next 3 samples are the same


        Returns
        -------
        torch.tensor
            The positional encoding.
        """
        # create tensor of 0s
        pe = torch.zeros(no_of_samples, embedding_dim)

        # create position column
        k = torch.arange(0, no_of_samples).unsqueeze(1)

        # calc divisor for positional encoding
        div_term = torch.exp(
            torch.arange(0, embedding_dim, 2) * -(math.log(10000.0) / embedding_dim)
        )

        # calc sine on even indices
        pe[:, 0::2] = torch.sin(k * div_term)

        # calc cosine on odd indices
        pe[:, 1::2] = torch.cos(k * div_term)

        pe = pe[sample_list]

        pe = pe.unsqueeze(0)

        return pe

    def normalize_by_sample(self, prediction, no_const=3000):
        """
        Normalize the prediction by sample.

        Parameters
        ----------
        prediction : np.ndarray
            The prediction to normalize.
        no_const : int, optional
            The number of constant proteins to use for normalization, by default 3000.

        Returns
        -------
        np.ndarray
            The normalized prediction.
        """

        if no_const is not None:
            logger.info("Normalizing prediction by sample.")
            indices = ~np.isnan(prediction).any(axis=1)
            filt_matrix = prediction[indices]

            # if complete matrix is empty
            if filt_matrix.shape[0] == 0:
                indices = (
                    np.isfinite(prediction).mean(axis=1).argsort()[::-1][:no_const]
                )
                filt_matrix = prediction[indices]

            constant_proteins_indices = filt_matrix.std(axis=1).argsort()[:no_const]
            ref_trace = np.nanmedian(filt_matrix[constant_proteins_indices], axis=0)
            ref_intensity = np.nanmedian(ref_trace)

            values_to_shift = ref_intensity - ref_trace

            return prediction + values_to_shift

        return prediction


class IsolatedTraceFinder:
    """_summary_

    Args:
        quant_df (_type_): _description_
    """

    def __init__(self, quant_df):
        self._protein_names = quant_df.index.get_level_values(0).to_numpy()
        self._proteome_array_bool = ~np.isnan(quant_df.to_numpy())

        self.indices_to_remove = []

        self._go_through_proteins_and_identify_indices_to_remove()

    def _go_through_proteins_and_identify_indices_to_remove(self):
        indices_of_proteinname_switch = self._find_protein_nameswitch_indices()
        for idx in range(
            len(indices_of_proteinname_switch) - 1
        ):  # go through all proteins
            protein_array = self._get_protein_array(
                indices_of_proteinname_switch, idx
            )  # the numpy array that belongs to one protein
            sorted_idxs = self._get_idxs_sorted_by_num_nas(protein_array)
            idxs_of_isolated_traces = find_isolated_traces(
                protein_array, connected_trace=None, sorted_idxs=sorted_idxs
            )
            if len(idxs_of_isolated_traces) > 0:
                print("found")
            self._extend_indices_to_remove(
                idxs_of_isolated_traces, indices_of_proteinname_switch, idx
            )

    def _find_protein_nameswitch_indices(self):
        change_indices = (
            np.where(self._protein_names[:-1] != self._protein_names[1:])[0] + 1
        )
        start_indices = np.insert(
            change_indices, 0, 0
        )  # add the index 0 for the start of the first element
        start_indices = np.append(
            start_indices, len(self._protein_names)
        )  # Append the index of the last element
        return start_indices

    def _get_protein_array(self, indices_of_proteinname_switch, idx):
        start_switch = indices_of_proteinname_switch[idx]
        end_switch = indices_of_proteinname_switch[idx + 1]
        protein_array = self._proteome_array_bool[start_switch:end_switch]
        return protein_array

    def _get_idxs_sorted_by_num_nas(self, protein_array_bool):
        na_counts = np.sum(protein_array_bool, axis=1)  # Count notNAs in each row
        sorted_idxs_asc = np.argsort(
            na_counts
        )  # Get indices of rows sorted by NA count
        sorted_idxs_desc = sorted_idxs_asc[::-1]
        return sorted_idxs_desc

    def _extend_indices_to_remove(
        self, idxs_of_isolated_traces, indices_of_proteinname_switch, idx
    ):
        start_switch = indices_of_proteinname_switch[idx]
        absolute_idxs_of_isolated_traces = [
            x + start_switch for x in idxs_of_isolated_traces
        ]
        self.indices_to_remove.extend(absolute_idxs_of_isolated_traces)


def find_isolated_traces(protein_array_bool, connected_trace, sorted_idxs):
    """
    This function finds isolated traces in a protein array.
    """
    if connected_trace is None:
        # Initialize connected_trace with the first index
        # in sorted_idxs (the one with the least NAs)
        connected_trace = protein_array_bool[sorted_idxs[0]].copy()

    missing_idxs = []
    for idx in sorted_idxs:
        trace = protein_array_bool[idx]
        has_overlap = np.any(
            connected_trace & trace
        )  # Using logical AND to check overlap, then any() to see if there's any True
        if has_overlap:
            connected_trace |= trace  # Update connected_trace with
        # logical OR to include the current trace
        else:
            missing_idxs.append(idx)
    if set(missing_idxs) == set(sorted_idxs):
        return missing_idxs  # Return any missing indices

    # Recursive call with the updated connected_trace and missing_idxs
    return find_isolated_traces(protein_array_bool, connected_trace, missing_idxs)
