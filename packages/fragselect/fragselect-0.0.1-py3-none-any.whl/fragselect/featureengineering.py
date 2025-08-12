import numpy as np
import pandas as pd
from joblib import Parallel, delayed
import scipy.stats as stats
from sklearn.impute import SimpleImputer
from numba import njit
from fragselect.utils import get_logger

logger = get_logger()

imputer = SimpleImputer(
    missing_values=np.nan, strategy="median", keep_empty_features=True
)


@njit
def _calculate_mean_distance(data):
    n_samples, n_features = data.shape
    mean_distances = np.zeros((n_samples, n_features))

    for i in range(n_samples):
        for k in range(n_features):
            sum_distance = 0.0
            count = 0
            for j in range(n_samples):
                if not np.isnan(data[i, k]) and not np.isnan(data[j, k]):
                    sum_distance += np.abs(data[i, k] - data[j, k])
                    count += 1
            if count > 0:
                mean_distances[i, k] = sum_distance / count
            else:
                mean_distances[i, k] = np.nan

    return mean_distances


@njit
def _calculate_variance_distance(data):
    n_samples, n_features = data.shape
    variance_distances = np.zeros((n_samples, n_features))

    for i in range(n_samples):
        for k in range(n_features):
            distances = []
            for j in range(n_samples):
                distances.append(np.abs(data[i, k] - data[j, k]))
            distances_array = np.array(distances)
            variance_distances[i, k] = np.nanvar(distances_array)

    return variance_distances


@njit
def _nan_correlation_matrix(data: np.ndarray) -> np.ndarray:
    """
    Calculate the correlation matrix of the data.

    Parameters:
        data: numpy array of shape (n_fragments, n_samples)
            The data to calculate the correlation matrix of.

    Returns:
        numpy array of shape (n_fragments, n_fragments)
        containing the correlation matrix of the data.
    """
    n = len(data)
    correlation_matrix = np.ones((n, n))

    for i in range(n):
        for j in range(i + 1, n):  # Only compute upper triangle
            mask = np.isfinite(data[i]) & np.isfinite(data[j])
            if np.sum(mask) > 1:
                xi = data[i][mask]
                xj = data[j][mask]
                std_dev_i = np.std(xi)
                std_dev_j = np.std(xj)

                if (std_dev_i > 0) and (std_dev_j > 0):
                    mean_i = np.mean(xi)
                    mean_j = np.mean(xj)
                    sparsity = np.mean(mask)
                    covariance = np.mean((xi - mean_i) * (xj - mean_j))
                    corr = covariance / (std_dev_i * std_dev_j)
                    correlation_matrix[i, j] = corr * sparsity
                    correlation_matrix[j, i] = (
                        corr * sparsity
                    )  # Mirror to lower triangle

    return correlation_matrix


# @njit
def _nan_correlation_w_ref(data_ref_pairs: tuple[np.ndarray, np.ndarray]) -> np.ndarray:
    """
    Calculate the correlation between each row of data and the reference row.

    Parameters:
        data_ref_pairs: tuple[np.ndarray, np.ndarray]
            A tuple containing two numpy arrays:
            - data: numpy array of shape (n_fragments, n_samples)
            - ref: numpy array of shape (n_fragments, n_samples)
                The ref contains the reference as n_fragments duplicates,
                which is why only the first row of ref is used.

    Returns:
        numpy array of shape (n_samples, n_features)
        containing the correlation between each row of data and the reference row.
    """

    data, ref = data_ref_pairs

    if ref.shape[0] == 1:
        ref = ref[0]

    n = data.shape[0]
    correlation_matrix = np.zeros(data.shape)
    ref_mask = np.isfinite(ref)

    for i in range(n):  # Compute all elements
        mask = np.isfinite(data[i]) & ref_mask

        if np.sum(mask) > 1:  # Ensure there are at least two data points
            xi = data[i][mask]
            xj = ref[mask]
            std_dev_i = np.std(xi)
            std_dev_j = np.std(xj)

            if (std_dev_i > 0) and (std_dev_j > 0):
                mean_i = np.mean(xi)
                mean_j = np.mean(xj)
                sparsity = np.mean(mask)
                covariance = np.mean((xi - mean_i) * (xj - mean_j))
                corr = covariance / (std_dev_i * std_dev_j)
                correlation_matrix[i] = corr * sparsity

    return correlation_matrix


@njit
def _nan_correlation_w_ref_v2(data: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """
    Calculate the correlation between each row of data and the reference row.

    Parameters:
        data_ref_pairs: tuple[np.ndarray, np.ndarray]
            A tuple containing two numpy arrays:
            - data: numpy array of shape (n_fragments, n_samples)
            - ref: numpy array of shape (n_fragments, n_samples)
                The ref contains the reference as n_fragments duplicates,
                which is why only the first row of ref is used.

    Returns:
        numpy array of shape (n_samples, n_features)
        containing the correlation between each row of data and the reference row.
    """

    n = data.shape[0]
    correlation_matrix = np.zeros(data.shape)

    for i in range(n):  # Compute all elements
        mask = np.isfinite(data[i]) & np.isfinite(ref[i])

        if np.sum(mask) > 1:  # Ensure there are at least two data points
            xi = data[i][mask]
            xj = ref[i][mask]
            std_dev_i = np.std(xi)
            std_dev_j = np.std(xj)

            if (std_dev_i > 0) and (std_dev_j > 0):
                mean_i = np.mean(xi)
                mean_j = np.mean(xj)
                sparsity = np.mean(mask)
                covariance = np.mean((xi - mean_i) * (xj - mean_j))
                corr = covariance / (std_dev_i * std_dev_j)
                correlation_matrix[i] = corr * sparsity

    return correlation_matrix


class FeatureEngineeringPipeline:
    """
    Pipeline for feature engineering.
    """

    def __init__(
        self,
    ):
        self._feat_eng = FeatureEngineering()

    def feature_engineering_pipeline_for_unaligned_data(self, data):
        """
        Feature engineering pipeline for intensity data.
        """
        logger.info("Feature engineering pipeline for unaligned data.")

        ranks = self._feat_eng.parallel_process(
            data,
            self._feat_eng.feature_engineering,
            func="rank_intensity",
            n_jobs=10,
            axis=0,
        )
        return [ranks]

    def feature_engineering_pipeline_for_height_and_ms1_intensity(self, data):
        logger.info("Calculating additional features.")
        mean_corr, std_corr = zip(
            *self._feat_eng.parallel_process(
                data, self._feat_eng.feature_engineering, func="corr", n_jobs=10
            )
        )

        return [
            std_corr,
            mean_corr,
        ]

    def feature_engineering_pipeline_for_intensity(self, data):
        """
        Feature engineering pipeline for intensity data.
        """

        no_of_datapoints_across_fragments = self._feat_eng.parallel_process(
            data,
            self._feat_eng.feature_engineering,
            func="count_no_of_datapoints",
            n_jobs=10,
            axis=0,
        )

        no_of_datapoints_across_samples = self._feat_eng.parallel_process(
            data,
            self._feat_eng.feature_engineering,
            func="count_no_of_datapoints",
            n_jobs=10,
            axis=1,
        )

        return [
            no_of_datapoints_across_fragments,
            no_of_datapoints_across_samples,
        ]


class FeatureEngineering:
    """
    This class encapsulates methods for feature engineering.
    """

    def __init__(self):
        self.corr_matrices = []

    def feature_engineering(self, data, func, **kwargs):
        func_mapping = {
            "std": np.nanstd,
            "var": np.nanvar,
            "min": np.nanmin,
            "median": np.nanmedian,
            "mean": np.nanmean,
            "sum": np.nansum,
            "mad": self._mad,
            "cv": self._coefficient_of_variation,
            "rank_intensity": self._rank_intensity,
            "SNR": self._calculate_snr,
            "L2": self._l2_norm,
            "sparsity": self._sparsity,
            "percentile": self._assign_percentiles,
            "mean_distance": _calculate_mean_distance,
            "var_distance": _calculate_variance_distance,
            "corr": self.nan_mean_std_corr_across_fragments,
            "median_std_offset": self._calculate_median_std_offset,
            "derivative": self._calculate_derivative,
            "count_no_of_datapoints": self._count_no_of_datapoints,
            "weighted_variance": self._calculate_weighted_variance,
        }

        feat_eng = func_mapping[func]
        result = feat_eng(data, **kwargs)

        if func in [
            "std",
            "var",
            "median",
            "mean",
            "sum",
            "mad",
            "cv",
            "L2",
            "sparsity",
            "median_std_offset",
            "count_no_of_datapoints",
            "weighted_variance",
        ]:
            axis = kwargs.get("axis")

            if axis == 0:
                result = np.tile(result, (data.shape[0], 1))

            elif axis == 1:
                result = np.tile(result, (data.shape[1], 1)).T

        return result

    def _repeater(self, data, function, instance_method, **kwargs):
        if instance_method:
            return [getattr(subset, function)(**kwargs) for subset in data]
        else:
            return [function(subset, **kwargs) for subset in data]

    def _calculate_weighted_variance(self, data, axis=0):
        return np.nanvar(data, axis=axis) * self._sparsity(data, axis=axis)

    def _count_no_of_datapoints(self, data, axis=0):
        return np.sum(np.isfinite(data), axis=axis)

    def _calculate_median_std_offset(self, data, axis=1):
        stds = np.nanstd(data, axis=axis)
        median_stds = np.nanmedian(stds)
        return np.abs(stds - median_stds)

    def _calculate_mean_distance(self, data, axis=1):
        distance = np.abs(data[:, np.newaxis] - data)
        mean_distances = np.nanmean(distance, axis=axis)
        return mean_distances

    def _calculate_mean_distances(self, inputs):
        results = Parallel(n_jobs=10)(
            delayed(self._calculate_mean_distance)(input) for input in inputs
        )
        return results

    def _sparsity(self, data, axis=0):
        return np.isnan(data).mean(axis=axis)

    def _l2_norm(self, data, axis=0):
        return np.linalg.norm(np.where(data > 0, data, 0), axis=axis)

    def _mad(self, data, axis=0):
        return stats.median_abs_deviation(data, axis=axis, nan_policy="omit")

    def _coefficient_of_variation(self, data, axis=0):
        # return stats.variation(data, axis=axis, nan_policy='omit',)
        return np.nanvar(data, axis=axis) / np.nanmedian(data, axis=axis)

    def _rank_intensity(self, data, axis=0):
        return np.argsort(np.nan_to_num(data, 0), axis=axis)

    def _calculate_snr(self, data, axis=0):
        if axis == 0:
            return data - np.nanmedian(data, axis=0).reshape(1, -1)

        elif axis == 1:
            return data - np.nanmedian(data, axis=1).reshape(-1, 1)

    def _calculate_derivative(self, data, axis=1, order=2):
        """
        Calculate the derivative of the data
        """

        derivatives = np.zeros_like(data)

        imputed_data = imputer.fit_transform(data)

        if axis == 1:
            x = np.arange(0, data.shape[1])
            for i, row in enumerate(imputed_data):
                if row.shape[0] > 1:  # check if theres more than one value in the row
                    if order == 1:
                        derivatives[i] = np.gradient(row, x)
                    elif order == 2:
                        derivatives[i] = np.gradient(np.gradient(row, x), x)

            return derivatives

        if axis == 0:
            x = np.arange(0, data.shape[0])
            for i in range(imputed_data.shape[1]):
                if (
                    imputed_data[:, i].shape[0] > 1
                ):  # check if theres more than one value in the col
                    if order == 1:
                        derivatives[:, i] = np.gradient(imputed_data[:, i], x)
                    elif order == 2:
                        derivatives[:, i] = np.gradient(
                            np.gradient(imputed_data[:, i], x), x
                        )

            return derivatives

    def _growth_decay_rate(self, data, axis=0):
        imputed_data = imputer.fit_transform(data)
        imputed_data = np.where(imputed_data == 0, np.nan, imputed_data)

        if axis == 0:
            coef = np.empty(imputed_data.shape[1])
            for i in range(imputed_data.shape[1]):
                coeffs = np.polyfit(
                    imputed_data[:, i], np.arange(len(imputed_data[:, i])), 1
                )
                coef[i] = coeffs[0]
            coefs = np.tile(coef, (imputed_data.shape[0], 1))
            return coefs

        elif axis == 1:
            coef = np.empty(imputed_data.shape[0])
            for i in range(imputed_data.shape[0]):
                coeffs = np.polyfit(
                    imputed_data[i, :], np.arange(len(imputed_data[i, :])), 1
                )
                coef[i] = coeffs[0]
            coefs = np.tile(coef, (imputed_data.shape[1], 1)).T
            return coefs

    def nan_mean_std_corr_across_fragments(self, data):
        mean_corr = self._mean_tile(_nan_correlation_matrix(data), data.shape[1])
        std_corr = self._std_tile(_nan_correlation_matrix(data), data.shape[1])

        return mean_corr, std_corr

    def _nan_corrs(self, inputs):
        return Parallel(n_jobs=10)(
            delayed(_nan_correlation_matrix)(input) for input in inputs
        )

    def _mean_tile(self, data, samples):
        mean = np.mean(data, axis=0)
        mean = np.tile(mean, (samples, 1)).T
        return mean

    def _std_tile(self, data, samples):
        std_data = np.std(data, axis=0)
        std_data = np.tile(std_data, (samples, 1)).T
        return std_data

    def _assign_percentiles(self, data, axis=0):
        # Calculate ranks across axis=0
        ranks = np.argsort(np.argsort(np.nan_to_num(data, 0), axis=axis), axis=axis)

        # Convert ranks to percentiles
        percentiles = ranks / (data.shape[axis] - 1) * 100

        return percentiles

    def parallel_process(self, inputs, method, n_jobs=10, **kwargs):
        """
        Parellel processing.

        Parameter
        -------
        inputs: list
            List of datasets to parallel process in
            conjunction with processing method.

        njobs: int
            Number of threads to process with.

        **kwargs:


        Return
        -------
            result: list
                List of preprocessed objects.
        """
        return Parallel(n_jobs=n_jobs)(
            delayed(method)(input, **kwargs) for input in inputs
        )

    def calculate_ms1_ms2_corr(
        self,
        ms1_data_extracted: list[np.ndarray],
        ms2_data_extracted: list[np.ndarray],
    ) -> pd.DataFrame:
        """
        Calculate the correlation between the ms1 and ms2 data.

        Parameters:
            ms1_data_extracted: list[np.ndarray]
                The ms1 data extracted from the precursor data.
            ms2_data_extracted: list[np.ndarray]
                The ms2 data extracted from the precursor data.
        Returns:
            ms1_ms2_corr_data: pd.DataFrame
                The ms1-ms2 correlation data.
        """

        zipped_data = zip(ms2_data_extracted, ms1_data_extracted)
        ms1_ms2_corr = self.parallel_process(
            inputs=zipped_data, method=_nan_correlation_w_ref, n_jobs=10
        )
        ms1_ms2_corr = pd.DataFrame(np.vstack(ms1_ms2_corr))
        return ms1_ms2_corr

    def calculate_mean_corr_and_tile(self, group):
        # Calculate correlation matrix directly
        corr_matrix = _nan_correlation_matrix(group.values)

        # Calculate mean correlation for each row (more efficient than calculating full matrix first)
        mean_corrs = np.mean(corr_matrix, axis=1)

        # Create result directly without intermediate tiled array
        # This avoids creating the intermediate tiled_corrs array
        result = pd.DataFrame(
            # This line does the efficient tiling using matrix multiplication:
            # 1. mean_corrs.reshape(-1, 1): reshapes the 1D array of mean correlations into a column vector (n×1)
            # 2. np.ones((1, group.shape[1])): creates a row vector of ones with width equal to number of columns in group
            # The matrix multiplication (@) broadcasts the mean correlation values across all columns,
            # effectively creating a matrix where each row contains the same mean correlation value repeated
            # This creates a tiled matrix where each row i contains the mean correlation value for row i repeated across all columns
            mean_corrs.reshape(-1, 1) @ np.ones((1, group.shape[1])),
            index=group.index,
            columns=group.columns,
        )

        return result

    # Parallel processing version
    def compute_mean_corr_and_tile(self, df, n_jobs=-1):
        # Create a copy with a unique ID column
        df_with_id = df.copy()
        df_with_id["_unique_id"] = np.arange(len(df))

        groups = df_with_id.groupby("pg")

        def process_group(name, group_df):
            # Keep the unique ID column during processing
            result = self.calculate_mean_corr_and_tile(
                group_df.drop(columns=["_unique_id"])
            )
            result["_unique_id"] = group_df["_unique_id"].values
            return name, result

        results = Parallel(n_jobs=n_jobs)(
            delayed(process_group)(name, group) for name, group in groups
        )

        # Concatenate all results
        result_df = pd.concat([df for _, df in results])

        # Sort by the unique ID to restore original order, then remove the ID column
        result_df = result_df.sort_values("_unique_id").drop(columns=["_unique_id"])

        return result_df

    def count_no_of_datapoints(
        self, data: pd.DataFrame, axis: int = 0
    ) -> dict[str, pd.DataFrame]:
        """
        Count the number of non-NaN values in the data along a specific axis
        for axis = 1, count the number of non-NaN values for each fragment trace,
        for axis = 0, count the number of non-NaN values for each sample.
        """
        no_of_datapoints = np.isfinite(data).sum(axis=axis).values
        no_of_datapoints = no_of_datapoints.reshape(-1, 1) @ np.ones(
            (1, data.shape[axis])
        )

        if axis == 0:
            no_of_datapoints = no_of_datapoints.T

        # Create DataFrame with the same column structure as the input data
        # but with the count of non-NaN values
        no_of_datapoints = pd.DataFrame(
            no_of_datapoints,
            columns=data.columns,
        )

        return no_of_datapoints

    def calculate_variance(
        self, data: pd.DataFrame, axis: int = 0
    ) -> dict[str, pd.DataFrame]:
        """
        Calculate the variance of the data along a specific axis
        for axis = 1, calculate the variance for each fragment trace,
        for axis = 0, calculate the variance for each sample.
        """
        no_of_datapoints = np.nanvar(data, axis=axis)
        no_of_datapoints = no_of_datapoints.reshape(-1, 1) @ np.ones(
            (1, data.shape[axis])
        )

        if axis == 0:
            no_of_datapoints = no_of_datapoints.T

        # Create DataFrame with the same column structure as the input data
        # but with the count of non-NaN values
        no_of_datapoints = pd.DataFrame(
            no_of_datapoints,
            columns=data.columns,
        )

        return no_of_datapoints
