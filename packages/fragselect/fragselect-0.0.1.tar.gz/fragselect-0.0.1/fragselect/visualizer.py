import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from fragselect.var_model import Model
from fragselect.dataloader import DataLoader


class Visualizer:
    def __init__(self):
        pass

    @staticmethod
    def plot_traces_from_one_protein(
        dataloader: DataLoader,
        protein_id: str,
        linestyle="solid",
        color="lightgrey",
        alpha=0.3,
        **kwargs,
    ):
        plt.plot(
            dataloader.intensity_layer[protein_id].numpy(),
            marker=".",
            linestyle=linestyle,
            color=color,
            alpha=alpha,
            **kwargs,
        )

    @staticmethod
    def plot_loss(
        train_losses: np.ndarray, val_losses: np.ndarray, filename: str = None
    ):
        plt.plot(train_losses, label="train")
        plt.plot(val_losses, label="val")
        plt.xlabel("Epochs")
        plt.ylabel("Loss")
        plt.legend()
        if filename is not None:
            plt.savefig(filename, bbox_inches="tight", transparent=True, dpi=300)
            plt.close()
        else:
            plt.show()

    @staticmethod
    def plot_weight_distribution(model: Model, filename: str = None, **kwargs):
        plt.hist(
            np.concatenate(model.quality_score).flatten(),
            alpha=0.5,
            bins=100,
            rasterized=True,
            **kwargs,
        )
        plt.xlabel("Quality score")
        plt.ylabel("Frequency")
        if filename is not None:
            plt.savefig(filename, bbox_inches="tight", transparent=True, dpi=300)
            plt.close()
        else:
            plt.show()

    @staticmethod
    def plot_protein_score_distribution(model: Model, filename: str = None, **kwargs):
        protein_score = model.calculate_protein_score()
        sns.histplot(protein_score, **kwargs)
        plt.xlabel("Protein score")
        plt.ylabel("Frequency")
        if filename is not None:
            plt.savefig(filename, bbox_inches="tight", transparent=True, dpi=300)
            plt.close()
        else:
            plt.show()

    @staticmethod
    def plot_proportion_retained_datapoints(
        model: Model, cutoff: float = 0.9, filename: str = None
    ):
        proportion_retained_datapoints = model.calculate_proportion_retained(
            cutoff=cutoff
        )
        sns.histplot(proportion_retained_datapoints, rasterized=True)
        plt.xlabel("Proportion of retained datapoints")
        plt.ylabel("Frequency")
        if filename is not None:
            plt.savefig(filename, bbox_inches="tight", transparent=True, dpi=300)
            plt.show()
        else:
            plt.show()

    @staticmethod
    def plot_protein_score_vs_proportion_retained_datapoints(
        model: Model, cutoff: float = 0.9, filename: str = None
    ):
        proportion_retained_datapoints = model.calculate_proportion_retained(
            cutoff=cutoff
        )
        protein_score = model.calculate_protein_score()
        sns.histplot(x=protein_score, y=proportion_retained_datapoints)
        plt.xlabel("Protein score")
        plt.ylabel("Proportion of retained datapoints")
        if filename is not None:
            plt.savefig(filename, bbox_inches="tight", transparent=True, dpi=300)
            plt.close()
        else:
            plt.show()

    @staticmethod
    def plot_pca(data, hue=None, ax=None, filename: str = None, **kwargs):
        """
        Plot the PCA of the data. Data should look as follows:
        index: protein names
        columns: sample names
        values: log2(intensity)

        data: pd.DataFrame
        hue: str, optional
            The column to use for the hue
        kwargs: dict, optional
            Additional arguments to pass to sns.scatterplot

        Returns:
            None
        """
        imputed_data = data.replace(np.nan, 0)
        scaler = StandardScaler()
        std_data = scaler.fit_transform(imputed_data.T)
        pca = PCA(n_components=2)
        transf_data = pca.fit_transform(std_data)
        transf_data = pd.DataFrame(
            transf_data, index=imputed_data.columns, columns=["PC1", "PC2"]
        )

        variance_explained = pca.explained_variance_ratio_
        if hue is not None:
            sns.scatterplot(
                data=transf_data, x="PC1", y="PC2", hue=hue, ax=ax, **kwargs
            )
        else:
            sns.scatterplot(
                data=transf_data,
                x="PC1",
                y="PC2",
                hue=transf_data.index,
                ax=ax,
                **kwargs,
            )

        if ax is not None:
            ax.set_xlabel(f"PC1 ({variance_explained[0]:.2%})")
            ax.set_ylabel(f"PC2 ({variance_explained[1]:.2%})")
        else:
            plt.xlabel(f"PC1 ({variance_explained[0]:.2%})")
            plt.ylabel(f"PC2 ({variance_explained[1]:.2%})")
        if filename is not None:
            plt.savefig(filename, bbox_inches="tight", transparent=True, dpi=300)
            plt.close()
        else:
            plt.show()
