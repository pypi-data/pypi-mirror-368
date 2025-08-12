from sklearn.metrics import roc_curve, roc_auc_score, accuracy_score
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from scipy.stats import gaussian_kde
from fragselect.directlfq import DirectlfqSimulation
import pandas as pd
import torch


class PerformanceEvaluation:
    def __init__(self):
        self.dlfq = DirectlfqSimulation()

    def plot_roc_auc_curve(
        self, model, data, simulation, path="../../images/roc_auc_curve.pdf"
    ):
        y_true = self.get_y_true_from_simulation(data, simulation)

        y_pred = self.get_y_pred_from_simulation(data, model)

        fpr, tpr, _ = roc_curve(y_true, y_pred)
        score = roc_auc_score(y_true, y_pred)

        plt.figure()
        plt.title(f"ROC AUC: {score :.5}")
        plt.plot(fpr, tpr)
        plt.xlabel("False positive rate")
        plt.ylabel("True positive rate")

        if path:
            plt.savefig(path, bbox_inches="tight", transparent=True)

    def get_y_true_from_simulation(self, data, simulation):
        y_true = []
        for i in range(len(data)):
            y = np.empty(data[i].shape[:2])
            index = simulation.sim_indices[i]
            y[:index] = True
            y[index:] = False
            y_true.append(y.flatten())

        y_true = np.concatenate(y_true)

        return y_true

    def get_y_pred_from_simulation(self, data, model):
        y_pred = []
        for i in data:
            y_pred.append(np.nan_to_num(model(i).detach().numpy().flatten(), 0))

        y_pred = np.concatenate(y_pred, axis=0)

        return y_pred

    def plot_confusion_matrix(
        self, data, model, simulation, path="../../images/confusion_matrix.pdf"
    ):
        y_pred = self.get_y_pred_from_simulation(data, model)
        y_true = self.get_y_true_from_simulation(data, simulation)

        fpr, tpr, threshold = roc_curve(y_true, y_pred)
        idx = np.argmax(tpr - fpr)
        thresh = threshold[idx]

        y_pred = y_pred >= thresh

        cm = confusion_matrix(y_true, y_pred)
        plt.figure()
        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
        disp.plot()

        if path:
            plt.savefig(path, bbox_inches="tight", transparent=True)

    def plot_weight_distribution(
        self, data, model, path="../../images/weight_distribution.pdf"
    ):
        plt.hist(
            model(torch.vstack(data)[:, :, 1:]).detach().numpy().flatten(), bins=100
        )
        if path:
            plt.savefig(path, bbox_inches="tight", transparent=True)

    def plot_weight_median_distance_correlation_distribution(
        self,
        data,
        model,
        path="../../images/weight_median_distance_corr_distribution.pdf",
    ):
        corrs = np.empty(len(data))
        for index, data in enumerate(data):
            # make weigh prediction
            weights = model(data)
            weights = np.array(weights.detach()).flatten()

            # retrieve ms accuracy data
            median_distance = np.array(data[:, :, 1].detach()).flatten()

            # calculate the correlation between weights and median distance
            mask_weights = np.isnan(weights)
            mask_ms_accuracy = np.isnan(median_distance)
            mask = mask_weights | mask_ms_accuracy
            corr = np.corrcoef(weights[~mask], median_distance[~mask])[0, 1]
            corrs[index] = corr

        # plot data
        plt.figure()
        sns.histplot(corrs, bins=20, kde=True)
        plt.xlabel("Weight - median distance correlation")

        if path:
            plt.savefig(path, bbox_inches="tight", transparent=True)

    def plot_weight_feature_correlation_distribution(
        self, data, model, path="../../images/weight_feature_corr_distribution.pdf"
    ):
        # plot distribution of weight - ms accuracy correlation
        corrs = np.empty(len(data))
        for index, data in enumerate(data):
            # make weight prediction
            weights = model(data)
            weights = np.array(weights.detach()).flatten()

            # retrieve ms accuracy data
            feature = np.array(data[:, :, 1].detach()).flatten()

            # calculate the correlation between weights and ms accuracy
            mask_weights = np.isnan(weights)
            mask_ms_accuracy = np.isnan(feature)
            mask = mask_weights | mask_ms_accuracy

            corr = np.corrcoef(weights[~mask], feature[~mask])[0, 1]
            corrs[index] = corr

        plt.figure()
        sns.histplot(corrs, bins=10, kde=True)
        plt.xlabel("Weight - Feature correlation")

        if path:
            plt.savefig(path, bbox_inches="tight", transparent=True)

    def plot_y_pred_y_true_correlation_distribution(
        self,
        data,
        model,
        ground_truth,
        path="../../images/y_pred_y_true_corr_distribution.pdf",
    ):
        # plot distribution of y_pred - y_true correlation
        # predict avg ion trace
        y_preds = model.predict(data)
        y_preds_shifted = self._shift_by_mean(y_preds)
        ground_truth_shifted = self._shift_by_mean(ground_truth)

        # collect correlation coeffs
        corrs = np.empty(len(data))

        for index, (y_pred, y_true) in enumerate(
            zip(y_preds_shifted, ground_truth_shifted)
        ):
            # calculate pearson's corr
            corrs[index] = np.corrcoef(y_pred, y_true)[0, 1]

        plt.figure()
        sns.histplot(corrs, kde=True)
        plt.xlabel("y_true - y_pred correlation")

        if path:
            plt.savefig(path, bbox_inches="tight", transparent=True)

    def calculate_ground_truth_from_simulation(self, data, simulation):
        ground_truth = np.empty((len(data), data[0].shape[1]))

        for index, sim_index in enumerate(simulation.sim_indices):
            # calculate y_true
            y_trues = data[index][:sim_index, :, 0]
            ground_truth[index] = np.nanmean(y_trues, axis=0)

        return ground_truth

    def plot_true_pred_intensity_scatter(
        self, y_pred, ground_truth, path="../../images/true_pred_intensity_scatter.pdf"
    ):
        # combine data for density calculation
        y_pred_shifted = self._shift_by_mean(y_pred)
        ground_truth_shifted = self._shift_by_mean(ground_truth)

        stacked = np.concatenate(
            [y_pred_shifted.reshape(1, -1), ground_truth_shifted.reshape(1, -1)],
        )
        kde = gaussian_kde(stacked)
        density = kde(stacked)

        # caluclate correlation between y_true and y_pred
        corr = np.corrcoef(y_pred_shifted.flatten(), ground_truth_shifted.flatten())[
            0, 1
        ]
        plt.figure()
        plt.title(f"{corr}")

        # plot
        plt.scatter(
            x=y_pred_shifted.flatten(),
            y=ground_truth_shifted.flatten(),
            c=density,
            alpha=0.8,
        )

        plt.xlabel("Predicted intensity")
        plt.ylabel("True intensity")

        # Add gradient bar with label
        plt.colorbar(label="Density")

        if path:
            plt.savefig(path, bbox_inches="tight", transparent=True)

    def get_selectlfq_output(self, data, model):
        return model.predict(data)

    def get_intensity_data_from_simulation(self, data):
        return [np.array(i[:, :, 0]) for i in data]

    def get_directlfq_output(self, data):
        return self.dlfq.get_directlfq_trace_per_protein(data)

    def plot_y_pred_true_squared_difference_distribution(
        self,
        y_pred,
        directfq_pred,
        ground_truth,
        path="../../images/y_pred_true_difference_distribution.pdf",
    ):
        # shift data by mean
        y_pred_shifted = self._shift_by_mean(y_pred)
        ground_truth_shifted = self._shift_by_mean(ground_truth)
        directfq_pred_shifted = self._shift_by_mean(directfq_pred)

        # calclate the squared  diffs
        y_pred_true_diffs = self.calculate_y_pred_true_squared_difference(
            y_pred_shifted, ground_truth_shifted
        )
        directlfq_int_true_diffs = self.calculate_y_pred_true_squared_difference(
            directfq_pred_shifted, ground_truth_shifted
        )

        # plot the distribution of squared diffs
        plt.figure()
        sns.histplot(y_pred_true_diffs.flatten(), kde=True, label="selectLFQ")
        sns.histplot(directlfq_int_true_diffs.flatten(), kde=True, label="directLFQ")

        plt.xlabel("y_pred - y_true squared difference")
        plt.legend()

        if path:
            plt.savefig(path, bbox_inches="tight", transparent=True)

    def calculate_y_pred_true_squared_difference(self, y_pred, ground_truth):
        # y_pred = model.predict(data)
        y_pred_true_diffs = np.empty((len(y_pred),))

        # for index, (pred, y) in enumerate(zip(y_pred, ground_truth)):
        #     y_pred_true_diffs[index] = np.nanmean((pred - y)**2)

        y_pred_true_diffs = np.nanmean((y_pred - ground_truth) ** 2, axis=0)

        return y_pred_true_diffs

    def _shift_by_mean(self, data):
        return data - np.nanmean(data, axis=1).reshape(-1, 1)

    def best_worst_prediction(
        self, simulation, best, y_pred, directlfq_output, ground_truth, path
    ):
        y_pred_true_diffs = self.calculate_y_pred_true_squared_difference(
            y_pred, ground_truth
        )

        worst_index = y_pred_true_diffs.argsort()[-1]
        best_index = y_pred_true_diffs.argsort()[0]

        if best == True:
            idx = best_index.copy()
        else:
            idx = worst_index.copy()

        plt.figure()
        # for trace in model.inputs[idx][:, :, 0]:
        #     plt.plot(trace, lw=1, color='lightgrey', alpha=0.4, label='random error')

        # shift data by mean
        y_pred_shifted = self._shift_by_mean(y_pred)
        ground_truth_shifted = self._shift_by_mean(ground_truth)
        directlfq_output_shifted = self._shift_by_mean(directlfq_output)

        plt.plot(ground_truth_shifted[idx], color="green", label="ground truth")
        plt.plot(y_pred_shifted[idx], color="blue", label="selectLFQ")
        plt.plot(directlfq_output_shifted[idx], color="red", label="directLFQ")
        plt.xlabel("acquisitions")
        plt.ylabel("intensity")

        plt.legend()
        plt.title("Similarity percentage: {}".format(simulation.sim_percent[idx]))
        plt.xlabel("Run")
        plt.ylabel("Fragment Intensity")

        if (path) and (best == True):
            plt.savefig(path, bbox_inches="tight", transparent=True)

        elif (path) and (best == False):
            plt.savefig(path, bbox_inches="tight", transparent=True)

    def calculate_accuracy_score_from_simulation(self, data, simulation, model):
        y_true = self.get_y_true_from_simulation(data, simulation)
        y_pred = self.get_y_pred_from_simulation(data, model)

        fpr, tpr, thresholds = roc_curve(y_true, y_pred)

        optimal_idx = np.argmax(tpr - fpr)
        optimal_threshold = thresholds[optimal_idx]

        y_pred[y_pred >= optimal_threshold] = 1
        y_pred[y_pred < optimal_threshold] = 0

        return accuracy_score(y_true, y_pred)

    def mixed_species_plot(self, y_pred, orig_data, path=False):
        # create protein group table with normalized intensities
        int_norm = pd.DataFrame(y_pred).replace(0, np.nan)
        int_norm.columns = sorted(orig_data.columns)[:-6]

        # calculate means
        sa1 = np.nanmean(int_norm.filter(regex="sample1"), axis=1)
        sa2 = np.nanmean(int_norm.filter(regex="sample2"), axis=1)
        sa3 = np.nanmean(int_norm.filter(regex="sample3"), axis=1)
        sa4 = np.nanmean(int_norm.filter(regex="sample4"), axis=1)

        # calculate ratios
        sa1_sa2 = sa1 - sa2
        sa1_sa3 = sa1 - sa3
        sa1_sa4 = sa1 - sa4
        sa2_sa3 = sa2 - sa3
        sa2_sa4 = sa2 - sa4
        sa3_sa4 = sa3 - sa4

        # create protein group table with ratios
        species = [
            group.split("_")[1] for group in list(orig_data.groupby("pg").groups.keys())
        ]
        replacer = {"ECODH": "ECOLI", "ECOBW": "ECOLI"}
        species_replaced = [replacer.get(item, item) for item in species]

        true_ratios = {
            "sa1_sa2": {
                "human": np.log2(1 / 1),
                "yeast": np.log2(1 / 2),
                "ecoli": np.log2(10 / 9),
            },
            "sa1_sa3": {
                "human": np.log2(1 / 1),
                "yeast": np.log2(1 / 4),
                "ecoli": np.log2(10 / 7),
            },
            "sa1_sa4": {
                "human": np.log2(1 / 1),
                "yeast": np.log2(1 / 10),
                "ecoli": np.log2(10 / 1),
            },
            "sa2_sa3": {
                "human": np.log2(1 / 1),
                "yeast": np.log2(1 / 2),
                "ecoli": np.log2(9 / 7),
            },
            "sa2_sa4": {
                "human": np.log2(1 / 1),
                "yeast": np.log2(1 / 5),
                "ecoli": np.log2(9 / 1),
            },
            "sa3_sa4": {
                "human": np.log2(1 / 1),
                "yeast": np.log2(2 / 5),
                "ecoli": np.log2(7 / 1),
            },
        }

        prot_ratios = [sa1_sa2, sa1_sa3, sa1_sa4, sa2_sa3, sa2_sa4, sa3_sa4]
        xs = [sa1, sa1, sa1, sa2, sa2, sa3]

        for index, (true_ratio, prot_ratio, x) in enumerate(
            zip(list(true_ratios.keys()), prot_ratios, xs)
        ):
            # plot scatterplot
            fig, ax = plt.subplots(1, 2, figsize=(20, 5))
            fig.suptitle(f"{true_ratio}")
            plt.subplots_adjust(wspace=0.05)

            sns.scatterplot(
                x=x, y=prot_ratio, s=10, hue=species_replaced, alpha=0.5, ax=ax[0]
            )
            sns.boxplot(
                y=prot_ratio, x=species_replaced, hue=species_replaced, ax=ax[1]
            )

            # Add horizontal line
            for a in ax:
                a.axhline(
                    y=true_ratios[true_ratio]["human"],
                    linestyle="dashed",
                    color="lightgrey",
                )
                a.axhline(
                    y=true_ratios[true_ratio]["ecoli"],
                    linestyle="dashed",
                    color="lightgrey",
                )
                a.axhline(
                    y=true_ratios[true_ratio]["yeast"],
                    linestyle="dashed",
                    color="lightgrey",
                )

            ax[0].set_xlabel("log2(A)")
            ax[0].set_ylabel("log2(A:B)")
            ax[1].set_ylabel("")

            boxplot_position = ax[1].get_position()
            new_position = [
                boxplot_position.x0,
                boxplot_position.y0,
                boxplot_position.width * 0.3,
                boxplot_position.height,
            ]
            ax[1].set_position(new_position)
            ax[1].set_yticks([])

            if path:
                plt.savefig(
                    f"{path}_{index}.png", bbox_inches="tight", transparent=True
                )

            plt.show()
