import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests
import statsmodels.api as sm
import plotly.express as px
from typing import List


class MixedSpeciesPerformanceEvaluation:
    """
    Class to evaluate the performance of the mixed species experiment
    Dataframe should look like this:
    """

    def __init__(self):
        self.melted_residuals = None

    def calculate_protein_specific_fdr(
        self,
        pvals: pd.DataFrame,
        regularatory_proteins: str = "YEAST|ECO",
        non_regulatory_proteins: str = "HUMAN",
    ):
        """
        Calculate protein specific FDR for each p-value of interest.
        Protein specific FDR is defined as the number of non regularatory proteins
        with p-value < pval_of_interest divided by the number of all proteins with
        p-values < pval_of_interest.

        Parameters:
        ----------
        pvals : pd.DataFrame
            Dataframe of p-values with shape (n_proteins, n_comparisons)
            index should include the species name eg. 1433B_HUMAN, 1433B_MOUSE etc.

        regularatory_proteins : str
            String to select regularatory proteins
            Default: "YEAST|ECO" (selects all yeast and ecoli proteins)
            Each species should be separated by a "|"

        non_regulatory_proteins : str
            String to select non regulatory proteins
            Default: "HUMAN" (selects all human proteins)
            Each species should be separated by a "|"

        Returns:
        --------
        fdrs : list of np.ndarray
            list of array of protein specific FDRs with shape (n_pvals_of_interest, n_comparisons)

        """
        fdrs = []
        for comparison in range(pvals.shape[1]):
            pvals_of_interest_index = (
                pvals[pvals.index.str.contains(regularatory_proteins)]
                .iloc[:, comparison]
                .index
            )

            pvals_of_interest = (
                pvals[pvals.index.str.contains(regularatory_proteins)]
                .iloc[:, comparison]
                .values
            )

            constant_protein_pvals = (
                pvals[pvals.index.str.contains(non_regulatory_proteins)]
                .iloc[:, comparison]
                .values
            )
            all_pvals = pvals.iloc[:, comparison].values

            # remove missing values
            pvals_of_interest = pvals_of_interest[~np.isnan(pvals_of_interest)]
            constant_protein_pvals = constant_protein_pvals[
                ~np.isnan(constant_protein_pvals)
            ]
            all_pvals = all_pvals[~np.isnan(all_pvals)]

            fdrs.append(
                self.calculate_protein_specific_fdr_1D_array(
                    pvals_of_interest, constant_protein_pvals, all_pvals
                )
            )

        fdr_data = pd.DataFrame(
            data=np.vstack(fdrs).T, index=pvals_of_interest_index, columns=pvals.columns
        )

        return fdr_data

    def calculate_protein_specific_fdr_1D_array(
        self,
        pvals_of_interest: np.ndarray,
        constant_protein_pvals: np.ndarray,
        pvals: np.ndarray,
    ):
        """
        Calculate protein specific FDR for each p-value of interest.
        Protein specific FDR is defined as the number of non regularatory proteins
        with p-value < pval_of_interest divided by the number of all proteins with
        p-values < pval_of_interest.

        Parameters:
        ----------
        pvals_of_interest : np.ndarray
            Array of p-values of interest with shape (n_pvals_of_interest, )

        constant_protein_pvals : np.ndarray
            Array of p-values of constant proteins with shape (n_constant_proteins, )

        pvals : np.ndarray
            Array of all p-values with shape (n_pvals, )

        Returns:
        --------
        fdrs : np.ndarray
            Array of protein specific FDRs with shape (n_pvals_of_interest, )

        """
        fdrs = np.empty(len(pvals_of_interest))

        for idx, pval in enumerate(pvals_of_interest):
            false_hits = np.sum(constant_protein_pvals < pval)
            total_hits = np.sum(pvals < pval)
            fdrs[idx] = false_hits / total_hits

        return fdrs

    def differential_expression_analysis(
        self, data: pd.DataFrame, comparisons: List[tuple]
    ):
        """
        Perform differential expression analysis using welcht test

        Parameters:
        ----------
        data : pd.DataFrame
            Dataframe with shape (n_proteins, n_samples)

        comparisons : list of tuples
            List of tuples with comparisons to perform eg. [("a", "b"), ("a", "c")]


        Returns:
            pval: pd.DataFrame
                Dataframe of p-values with shape (n_proteins, n_comparisons)

            qval: pd.DataFrame
                Dataframe of q-values with shape (n_proteins, n_comparisons)
        """
        pval = pd.DataFrame(index=data.index)
        qval = pd.DataFrame(index=data.index)
        fc = pd.DataFrame(index=data.index)

        for a, b in comparisons:
            # calculate fold change
            fold_change = np.nanmedian(data[a], axis=1) - np.nanmedian(data[b], axis=1)
            pvals = ttest_ind(data[a], data[b], axis=1, nan_policy="omit")[1]
            mask = np.isfinite(pvals)
            pvals_no_nan = pvals[mask]
            qvals = multipletests(pvals_no_nan, method="fdr_bh")[1]

            pval.loc[mask, f"{a}:{b}"] = pvals_no_nan
            qval.loc[mask, f"{a}:{b}"] = qvals
            fc.loc[mask, f"{a}:{b}"] = fold_change[mask]

        return pval, qval, fc

    def calculate_detection_rate(
        self,
        n_bins: int,
        reg_prot_mask: np.ndarray,
        qval: np.ndarray,
        abundance: np.ndarray,
    ):
        """
        Calculate detection rate for each bin.
        Detection rate is defined as the number of proteins with q-value < 0.05.

        Parameters:
        ----------
        n_bins : int
            Number of bins to bin the data into

        reg_prot_mask : np.ndarray
            Boolean mask to select regular proteins with shape (n_proteins, )

        qval : np.ndarray or pd.DataFrame
            Array or dataframe of q-values with shape (n_proteins, ) or (n_proteins, n_comparisons)

        abundance : np.ndarray
            Array of protein intensities with shape (n_proteins, )

        Returns:
        --------
        detection_rate : np.ndarray
            Detection rate for each bin with shape (n_bins + 1, )
        """

        digitized = self.bin_data(n_bins, abundance, reg_prot_mask)
        detection_rates = np.full((n_bins, len(qval.columns)), np.nan)

        if isinstance(qval, pd.DataFrame):
            for col_idx in range(qval.shape[1]):
                detection_rates[:, col_idx] = self._calculate_detection_rate_1d_array(
                    digitized, reg_prot_mask, qval.iloc[:, col_idx]
                )

        elif isinstance(qval, np.ndarray):
            detection_rates = self._calculate_detection_rate_1d_array(
                digitized, reg_prot_mask, qval
            )

        return detection_rates

    def bin_data(self, n_bins: int, abundance: np.ndarray, reg_prot_mask: np.ndarray):
        """
        Bin data into n_bins bins

        Parameters:
        ----------
        n_bins : int
            Number of bins to bin the data into

        abundance : np.ndarray
            Array of protein abundances with shape (n_proteins, )

        reg_prot_mask : np.ndarray
            Boolean mask to select regular proteins with shape (n_proteins, )

        Returns:
        --------
        digitized : np.ndarray
            Array of bin labels. Each label represents
            one bin with shape (n_proteins, )
        """
        quantiles = np.linspace(0, 1, n_bins)
        reg_prot_intensity = np.nan_to_num(abundance[reg_prot_mask], 0)

        bins = np.quantile(reg_prot_intensity, quantiles)
        digitized = np.digitize(reg_prot_intensity, bins, right=True)

        return digitized

    def _calculate_detection_rate_1d_array(
        self, digitized: np.ndarray, reg_prot_mask: np.ndarray, qval: np.ndarray
    ):
        """
        Calculate detection rate for each bin using 1d arrays only.
        Detection rate is defined as the number of proteins with q-value < 0.05.

        Parameters:
        ----------
        digitized : np.ndarray
            Array of bin labels. Each label represents
            one bin with shape (n_proteins, )

        reg_prot_mask : np.ndarray
            Boolean mask to select regulartory proteins with shape (n_proteins, )

        qval : np.ndarray
            Array of q-values with shape (n_proteins, )

        Returns:
        --------
        detection_rate : np.ndarray
            Detection rate for each bin with shape (n_bins + 1, )
        """

        detection_rate = []
        for i in range(len(set(digitized))):
            mask = digitized == i
            qval_of_interest = qval[reg_prot_mask][mask]
            num = np.sum(qval_of_interest < 0.05)
            denom = np.sum(mask)
            detection_rate.append(num / denom)

        return detection_rate

    def plot_mixed_species(
        self,
        plotting_data: pd.DataFrame,
        x: str,
        y: str,
        hue: str,
        alpha: float,
        ground_truth: List[float],
        figsize: tuple,
        path: str = None,
        title: str = None,
        lowess_line: bool = False,
        color_palette: List[str] = None,
        **kwargs,
    ):
        """
        Plot mixed species experiment. The plot will contain a scatter plot
        and a boxplot. The boxplot will contain the median and standard deviation
        of the log2(a:b) ratio for each species. The scatter plot will contain
        the log2(a) against log2(a:b) ratio for each protein. The ground truth
        ratios will be plotted as dashed lines.

        Parameters:
        ----------
        plotting_data : pd.DataFrame
            Dataframe with columns should be ["log2(a)", "log2(a:b)", "species", "index"]
            eg. index	log2(a)	log2(a:b)	species
                0	0	26.754471	0.164120	HUMAN
                1	1	26.745103	0.155729	HUMAN
                2	2	24.411493	0.198889	HUMAN
                3	3	25.290676	0.027163	HUMAN
                4	4	19.220515	-0.075973	HUMAN
                ...	...	...	...	...
                11536	11536	21.677138	0.158225	HUMAN
                11537	11537	20.368945	0.360359	HUMAN
                11538	11538	21.838798	0.054542	HUMAN
                11539	11539	19.882714	-0.077599	HUMAN
                11540	11540	19.565205	-0.481696	HUMAN

        x : str
            Column name of x-axis
        y : str
            Column name of y-axis
        hue : str
            Column name of hue
        alpha : float
            Alpha value for the scatter plot
        ground_truth : list
            List of ground truth ratios
        figsize : tuple
            Figure size
        path : str
            Path to save the figure
        title : str
            Title of the plot
        lowess_line : bool
            Whether to add lowess line to the plot
        **kwargs : dict
            Additional arguments to pass to the scatter plot
        """
        fig, ax = plt.subplots(1, 2, figsize=figsize, sharey=True)

        # mathc each key in ground_truth to the sns.coro palette
        if color_palette is None:
            color_palette = sns.color_palette()
        palette = {k: v for k, v in zip(ground_truth.keys(), color_palette)}

        plt.subplots_adjust(wspace=0.05)
        plt.suptitle(title)
        sns.scatterplot(
            data=plotting_data,
            x=x,
            y=y,
            hue=hue,
            alpha=alpha,
            ax=ax[0],
            linewidth=0,
            rasterized=True,
            palette=palette,
            **kwargs,
        )

        handles, labels = ax[0].get_legend_handles_labels()
        for handle in handles:
            handle.set_alpha(1)
            handle.set_markersize(3)
        ax[0].legend(handles=handles, labels=labels, title="")

        sns.violinplot(
            data=plotting_data,
            y=y,
            x=hue,
            hue=hue,
            ax=ax[1],
            palette=palette,
        )
        # Add horizontal line
        for a in ax:
            for y_coord in ground_truth.values():
                a.axhline(
                    y=y_coord,
                    linestyle="dashed",
                    color="red",
                    linewidth=1,
                )

        median_annotation = plotting_data.groupby("species")["log2(a:b)"].median()
        res_annotation = median_annotation - pd.Series(
            data=ground_truth.values(), index=ground_truth.keys()
        )
        std_annotation = plotting_data.groupby("species")["log2(a:b)"].std()

        if lowess_line:
            # add lowess line
            for spec in plotting_data["species"].unique():
                plotting_data_filt = plotting_data[plotting_data["species"] == spec]
                lowess_line = self._calculate_lowess_line(plotting_data_filt)
                ax[0].plot(
                    lowess_line[:, 0],
                    lowess_line[:, 1],
                    color=palette[spec],
                    linestyle="--",
                    linewidth=1,
                )
        max_val = np.nanmax(plotting_data["log2(a)"])
        for ground_truth_val, (_, std_val), (_, res_val) in zip(
            ground_truth.values(), std_annotation.items(), res_annotation.items()
        ):
            # ax[0].annotate(
            #     f"{res_val:.3f} Res",
            #     xy=(max_val - 2, median_val),
            #     xytext=(4, 0),
            #     textcoords="offset points",
            #     ha="left",
            #     va="center",
            #     fontsize=8,
            # )

            ax[0].annotate(
                f"{std_val:.3f} SD",
                xy=(max_val - 2, ground_truth_val),
                xytext=(4, 10),
                textcoords="offset points",
                ha="left",
                va="center",
                fontsize=8,
            )

        ax[1].set_ylabel("")

        boxplot_position = ax[1].get_position()
        new_position = [
            boxplot_position.x0,
            boxplot_position.y0,
            boxplot_position.width * 0.15,
            boxplot_position.height,
        ]
        ax[1].set_position(new_position)
        ax[1].set_xticks([])
        ax[1].set_xlabel("")

        # ax[1].set_ylim(-8, 8)
        # ax[0].set_ylim(-8, 8)
        ax[1].set_rasterized(True)

        if path:
            fig.savefig(path, bbox_inches="tight", transparent=True, dpi=300)

    def _calculate_lowess_line(self, plotting_data: pd.DataFrame):
        """
        Calculate lowess line for the mixed species experiment
        """

        y = plotting_data["log2(a:b)"].values
        x = plotting_data["log2(a)"].values
        smoothed = sm.nonparametric.lowess(exog=x, endog=y, frac=0.2)

        return smoothed

    def calculate_ratio_data(
        self, data: pd.DataFrame, a: str, b: str, species: List[str]
    ):
        """
        Calculate the ratio data for the mixed species experiment

        Parameters:
        ----------
        data : pd.DataFrame
            Dataframe with shape (n_proteins, n_samples)

        a : str
            Column name of first sample

        b : str
            Column name of second sample

        species : list
            List of unique species names

        Returns:
        --------
        plotting_data : pd.DataFrame
            Dataframe with columns ["log2(a)", "log2(a:b)"]
        """
        # ESTIMATED Y-PSEUDO
        a_b = np.nanmedian(data.filter(regex=a), axis=1) - np.nanmedian(
            data.filter(regex=b), axis=1
        )
        a = np.nanmedian(data.filter(regex=a), axis=1)

        plotting_data = pd.DataFrame(np.vstack([a, a_b])).T
        plotting_data.columns = ["log2(a)", "log2(a:b)"]
        plotting_data["species"] = species
        plotting_data["pg"] = data.index.values
        plotting_data = plotting_data.reset_index()

        return plotting_data

    def plot_interactive_scatter_plot_by_species(
        self, data: pd.DataFrame, ground_truth: List[float]
    ):
        """
        Plot interactive scatter plot by species

        Parameters:
        ----------
        data : pd.DataFrame
            Dataframe with shape (n_proteins, 3). Columns should be ["log2(a)", "log2(a:b)", "species", "index"]

        ground_truth : list
            List of ground truth ratios

        Returns:
        --------
        fig : plotly.graph_objects.Figure
            Plotly figure
        """

        fig = px.scatter(
            data,
            x="log2(a)",
            y="log2(a:b)",
            color="species",
            template="simple_white",
            width=1000,
            height=400,
            opacity=0.1,
            hover_data="index",
        )

        for y_coord in ground_truth:
            fig.add_hline(y=y_coord, line_width=3, line_dash="dash", line_color="grey")
        fig.show()

    def create_ground_truth_data(
        self,
        ground_truth: List[float],
        species_list: List,
        species: List[str],
    ):
        """
        Create ground truth data for the mixed species experiment

        Parameters:
        ----------
        ground_truth : list
            List of ground truth ratios

        species_list : list
            List of all species eg. ["HUMAN", "HUMAN", "HUMAN", "YEAST", ...]

        species : list
            List of unique species names eg. ["HUMAN", "YEAST", "ECOLI"]

        Returns:
        --------
        ground_truth_ratio : pd.DataFrame
            Dataframe with ground truth ratios with shape (n_proteins, 1)
        """
        ground_truth_ratio = pd.DataFrame(data=species_list).set_index(0)

        # Create masks for HUMAN and YEAST conditions

        masks = [pd.Series(species_list).str.contains(s).values for s in species]

        for i, mask in enumerate(masks):
            ground_truth_ratio.loc[mask, "sample1:sample2"] = ground_truth[i]

        return ground_truth_ratio

    def calculate_residuals(
        self, data: pd.DataFrame, ground_truth_data: pd.DataFrame, a: str, b: str
    ):
        """
        Calculate residuals between ground truth and predicted ratios

        Parameters:
        ----------
        data : pd.DataFrame
            Dataframe with shape (n_proteins, 1)

        ground_truth_data : pd.DataFrame
            Dataframe with ground truth ratios with shape (n_proteins, 1)

        a : str
            Column name of first sample

        b : str
            Column name of second sample

        Returns:
        --------
        residuals : pd.DataFrame
            Data of residuals with shape (n_proteins, 1)
        """
        ratio = np.nanmedian(data[a] - data[b].values, axis=1)
        residuals = ground_truth_data - ratio.reshape(-1, 1)
        return residuals

    def plot_binned_residuals_per_species(
        self,
        intensity_data: pd.DataFrame,
        residuals_datasets: List[pd.DataFrame],
        method_names: List[str],
        figsize: tuple = (18, 6),
        bins: int = 10,
    ):
        """
        Plot binned residuals of the mixed species experiment per species

        Parameters:
        ----------
        intensity_data : pd.DataFrame
            Intensity data with shape (n_proteins, n_samples)

        residuals_datasets : list of pd.DataFrame
            List of dataframes with residuals for each method.
            eg. 	sample1:sample2
                index
                HUMAN	-0.172046
                HUMAN	-0.258223
                HUMAN	-0.283861
                HUMAN	-0.258223
                      ...

        method_names : list of str
            List of method names

        figsize : tuple
            Figure size

        bins : int
            Number of bins to bin the data into
        """

        bins = self._bin_data(intensity_data["Sample1"], bins)

        # Concatenate residuals
        residuals = pd.concat(residuals_datasets, axis=1)
        residuals.columns = method_names
        residuals = residuals.reset_index(names="species")
        residuals["bins"] = bins.values.astype("float")

        # Perform melting operation with explicit column selection
        melted_residuals = pd.melt(
            residuals,
            id_vars=["species", "bins"],
            value_vars=method_names,
            var_name="method",
            value_name="residuals",
        )

        # Create boxplot with explicit parameter passing
        fig, ax = plt.subplots(1, len(method_names), figsize=figsize, sharey=True)

        for a, method_name in zip(ax, method_names):
            a.set_title(method_name)
            sns.boxplot(
                data=melted_residuals[melted_residuals["method"] == method_name],
                y="residuals",
                x="species",
                hue="bins",
                showfliers=False,
                ax=a,
            )
            a.set_xlabel("")
            a.axhline(0, color="lightgrey", linestyle="--")

        fig.show()

    def _bin_data(
        self, abundance_data: np.array, bins: int, equal_counts: bool = False
    ):
        if equal_counts:
            bins, _ = pd.qcut(abundance_data, q=bins, labels=False, retbins=True)

        else:
            bins = pd.cut(abundance_data, bins=bins, labels=list(np.arange(bins)))
        return bins

    def plot_binned_residuals(
        self,
        intensity_data: pd.DataFrame,
        residuals_datasets: List[pd.DataFrame],
        method_names: List[str],
        figsize: tuple = (18, 6),
        bins: int = 10,
    ):
        """
        Plot binned residuals of the mixed species experiment, regardless of species

        Parameters:
        ----------
        intensity_data : pd.DataFrame
            Intensity data with shape (n_proteins, n_samples)

         residuals_datasets : list of pd.DataFrame
            List of dataframes with residuals for each method.
            eg. 	sample1:sample2
                index
                HUMAN	-0.172046
                HUMAN	-0.258223
                HUMAN	-0.283861
                HUMAN	-0.258223
                      ...

        method_names : list of str
            List of method names

        figsize : tuple
            Figure size

        bins : int
            Number of bins to bin the data into
        """
        intensity_median = intensity_data["Sample1"].median(axis=1)
        bins = pd.cut(intensity_median, bins=bins, labels=list(np.arange(bins)))

        residuals = pd.concat(residuals_datasets, axis=1)
        residuals.columns = method_names
        residuals = residuals.reset_index(names="species")
        residuals["bins"] = bins.values.astype("float")

        # Perform melting operation with explicit column selection
        self.melted_residuals = pd.melt(
            residuals,
            id_vars=["species", "bins"],
            value_vars=method_names,
            var_name="method",
            value_name="residuals",
        )

        plt.figure(figsize=figsize)

        # Create boxplot
        sns.boxplot(
            data=self.melted_residuals,
            y="residuals",
            x="method",
            hue="bins",
            showfliers=False,
        )
        plt.legend(loc="upper right", title="abundance")
        plt.axhline(0, color="lightgrey", linestyle="--")
        plt.show()

    def plot_binned_residuals_per_species_subplot(
        self,
        residuals: pd.DataFrame,
        figsize: tuple = (10, 3),
        path: str = None,
        annot: bool = False,
        **kwargs,
    ):
        """
        Plot binned residuals of the mixed species experiment per species.
        For each species a suplot will be generated. Each subplot will
        contain the residuals of each method across the abundance range.

        Parameters:
        ----------
        residuals : pd.DataFrame
            Dataframe with residuals for each method.
            eg. 	species	sample1:sample2	method	abundance rank
                0	HUMAN	-0.172046	selectlfq	8.0
                1	HUMAN	-0.258223	selectlfq	8.0
                2	HUMAN	-0.283861	selectlfq	6.0
                3	HUMAN	-0.050361	selectlfq	7.0
                4	HUMAN	0.063080	selectlfq	3.0
                ...	...	...	...	...
                23077	HUMAN	-0.158225	directlfq	5.0
                23078	HUMAN	-0.360359	directlfq	4.0
                23079	HUMAN	-0.054542	directlfq	5.0
                23080	HUMAN	0.077599	directlfq	3.0
                23081	HUMAN	0.481696	directlfq	3.0
                                    ...

        path : str
            Path to save the figure

        Returns:
        --------
        fig : matplotlib.figure.Figure
            Matplotlib
        """
        n_cols = len(np.unique(residuals["species"]))

        fig, ax = plt.subplots(1, n_cols, figsize=figsize, sharey=True)
        for axes, spec in zip(ax.flatten(), np.unique(residuals["species"].unique())):
            plot_data = residuals[residuals["species"] == spec]

            # Create boxplot
            sns.boxplot(
                x="abundance rank",
                y="sample1:sample2",
                hue="method",
                data=plot_data,
                ax=axes,
                showfliers=False,
                **kwargs,
            )
            axes.set_ylabel("residuals (sample1:sample2)")

            if annot:
                # Get counts for one method only (since they're the same for both)
                method = plot_data["method"].unique()[0]  # use first method
                for rank in sorted(plot_data["abundance rank"].unique()):
                    # Get count for this rank
                    mask = (plot_data["method"] == method) & (
                        plot_data["abundance rank"] == rank
                    )
                    count = sum(mask)

                    # Get x position for the annotation
                    x_pos = sorted(plot_data["abundance rank"].unique().tolist()).index(
                        rank
                    )

                    # Add annotation at the bottom
                    axes.text(
                        x_pos,
                        axes.get_ylim()[0] + 0.3,
                        f"n={count}",
                        horizontalalignment="center",
                        verticalalignment="top",
                        color="black",
                    )

            axes.axhline(0, color="lightgrey", linestyle="--", linewidth=1)
            axes.set_title(spec)

        plt.tight_layout()
        if path:
            plt.savefig(path, bbox_inches="tight", transparent=True)

    def calculate_fold_change_and_residual_data(
        self, data, comparison, species, ground_truth_fold_change_data
    ):
        """
        Calculate fold change and residuals for a given comparison

        data: pd.DataFrame
            Dataframe with shape (n_proteins, n_samples)

        comparison: str
            Comparison to calculate fold change and residuals for.

        species: list of str
            List of species names

        ground_truth_fold_change_data: pd.DataFrame
            Dataframe with ground truth fold change data with shape (n_proteins, 1)

        Returns:
        --------
        fold_changes: pd.DataFrame
            Dataframe with fold change and residuals with shape (n_proteins, 3)
            Columns: "log2(a:b)", "log2(a)", "deviation from ground truth"
        """

        a = comparison.split(":")[0]
        b = comparison.split(":")[1]
        fold_changes = pd.DataFrame(np.nanmedian(data[a] - data[b].values, axis=1))
        fold_changes.columns = ["log2(a:b)"]
        fold_changes.index = species
        log2_a = data.select_dtypes(include=["float64"]).mean(axis=1).values
        fold_changes["log2(a)"] = log2_a
        fold_changes["deviation from ground truth"] = (
            fold_changes["log2(a:b)"] - ground_truth_fold_change_data
        )
        return fold_changes


class Evaluation:
    def __init__(self):
        pass

    def permute_layer_preserve_nan(
        self, array_list: List[np.ndarray], layer_index: int
    ) -> List[np.ndarray]:
        """
        Permute a specific layer while keeping NaN values in their original positions
        """
        result_list = []

        for arr in array_list:
            new_arr = arr.copy()

            # Extract the layer
            layer = arr[:, :, layer_index].copy()

            # Find positions of NaN values
            nan_mask = np.isnan(layer)

            # Extract non-NaN values
            non_nan_values = layer[~nan_mask]

            # Permute only the non-NaN values
            permuted_values = np.random.permutation(non_nan_values)

            # Create new layer with permuted values
            new_layer = layer.copy()
            new_layer[~nan_mask] = permuted_values

            # Replace the layer in the array
            new_arr[:, :, layer_index] = new_layer

            result_list.append(new_arr)

        return result_list
