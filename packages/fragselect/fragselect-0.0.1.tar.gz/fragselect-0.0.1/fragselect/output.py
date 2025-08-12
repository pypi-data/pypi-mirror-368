import os
from typing import Union, Dict, Any, Optional

import pandas as pd
import numpy as np

from fragselect.preprocessing import PreprocessingPipeline
from fragselect.loader import Loader
from fragselect.var_model import Model
from fragselect.dataloader import DataLoader
from fragselect.visualizer import Visualizer
from fragselect.utils import get_logger
from fragselect.shared_state import shared_state
from fragselect.config import FragSelectConfig, ModelConfig

logger = get_logger()


def run_model(
    output_path: str,
    config: Union[Dict[str, Any], FragSelectConfig] = None,
    level: str = "pg",
    standardize: bool = True,
    plot_loss: bool = True,
    cutoff: float = 0.9,
    min_num_fragments: int = 12,
    no_const: int = 3000,
    save_quality_scores: bool = False,
    save_normalized_data: bool = False,
) -> pd.DataFrame:
    """
    Run the SelectLFQ model pipeline for protein quantification.

    Parameters
    ----------
    output_path : str
        Path to the directory containing feature files
    config : Union[Dict[str, Any], FragSelectConfig], optional
        Configuration for model parameters. Can be either:
        - A dictionary with keys: "criterion_params", "model_params", "optimizer_params", "fit_params"
        - A FragSelectConfig object
        - None to use default parameters
    level : str, default="pg"
        Level to predict: "pg" for protein groups or "mod_seq_charge_hash" for precursors
    standardize : bool, default=True
        Whether to standardize the input features
    plot_loss : bool, default=True
        Whether to plot training and validation loss curves
    cutoff : float, default=0.9
        Quality score cutoff used to remove low quality datapoints
    threshold : int, default=12
        Minimum number of datapoints per sample required for aggregation
    no_const : int, default=3000
        Number of proteins/precursors to use for sample-wise normalization
    save_normalized_data : str, optional
        Path to save the normalized data. If None, data won't be saved.
    save_quality_scores : bool, default=True
        Whether to save the quality scores for each protein/precursor.

    Returns
    -------
    pd.DataFrame
        Normalized prediction data with samples for columns
        and pg or precursor as rows.
    """
    # Load and process features
    features = Loader().load_features(output_path)

    # Initialize preprocessing pipeline
    pipeline = PreprocessingPipeline(standardize=standardize)

    # Process data at specified level
    feature_layer, intensity_layer = pipeline.process(data=features, level=level)

    # Create dataloader object
    dataloader = DataLoader(
        feature_layer=feature_layer, intensity_layer=intensity_layer
    )

    # Handle configuration - support both new FragSelectConfig and legacy dict format
    if config is None:
        # Use default configuration
        fragselect_config = FragSelectConfig()
    elif isinstance(config, FragSelectConfig):
        # Use provided FragSelectConfig
        fragselect_config = config
    elif isinstance(config, dict):
        # Convert legacy dict format to FragSelectConfig
        fragselect_config = FragSelectConfig.from_dict(config)
    else:
        raise ValueError(
            f"config must be None, FragSelectConfig, or dict, got {type(config)}"
        )

    # Initialize model with configuration
    model, optimizer, criterion = Model.initialize_for_training(
        dataloader=dataloader,
        criterion_params=fragselect_config.CONFIG["criterion_params"],
        model_params=fragselect_config.CONFIG["model_params"],
        optimizer_params=fragselect_config.CONFIG["optmizer_params"],
    )

    # Train model with fit parameters from config
    fit_params = fragselect_config.CONFIG["fit_params"]
    model.fit(
        criterion=criterion,
        optimizer=optimizer,
        dataloader=dataloader,
        fit_params=fit_params,
    )

    if plot_loss:
        # Plot training progress
        Visualizer.plot_loss(model.train_loss, model.val_loss)

    # Generate predictions
    normalized_data = model.predict(
        dataloader=dataloader,
        cutoff=cutoff,
        min_num_fragments=min_num_fragments,
        no_const=no_const,
    )

    if save_normalized_data:
        _save_normalized_data(normalized_data, _get_identifiers(features), output_path)

    if save_quality_scores:
        _save_quality_scores(model, _get_identifiers(features), output_path)

    return normalized_data, model


def _save_normalized_data(
    normalized_data: pd.DataFrame, identifiers: pd.DataFrame, path: str
) -> None:
    if shared_state.level == "pg":
        filename = "pg.matrix.normalized.tsv"
    else:
        filename = "precursor.matrix.normalized.tsv"
        identifiers = identifiers.drop_duplicates(subset=["mod_seq_charge_hash"])

    filepath = os.path.join(path, filename)
    logger.info(f"Saving normalized {filename} to {filepath}")

    if shared_state.level == "mod_seq_charge_hash":
        normalized_data = normalized_data.reset_index(names="mod_seq_charge_hash")
        normalized_data = normalized_data.merge(
            identifiers[["mod_seq_charge_hash", "pg"]].drop_duplicates(
                subset=["mod_seq_charge_hash"]
            ),
            on="mod_seq_charge_hash",
            how="left",
        )
        normalized_data["mod_seq_charge_hash;pg"] = (
            normalized_data["mod_seq_charge_hash"].astype("string")
            + ";"
            + normalized_data["pg"].astype("string")
        )
        normalized_data = normalized_data.drop(columns=["mod_seq_charge_hash", "pg"])
        normalized_data = normalized_data.set_index("mod_seq_charge_hash;pg")
    normalized_data.to_csv(filepath, sep="\t")


def _match_pg_and_mod_seq_charge_hash(
    normalized_data: pd.DataFrame, identifiers: pd.DataFrame
) -> pd.DataFrame:
    normalized_data = normalized_data.reset_index(names="mod_seq_charge_hash")
    normalized_data = normalized_data.merge(
        identifiers[["mod_seq_charge_hash", "pg"]].drop_duplicates(
            subset=["mod_seq_charge_hash"]
        ),
        on="mod_seq_charge_hash",
        how="left",
    )
    normalized_data["mod_seq_charge_hash;pg"] = (
        normalized_data["mod_seq_charge_hash"].astype("string")
        + ";"
        + normalized_data["pg"].astype("string")
    )
    normalized_data = normalized_data.drop(columns=["mod_seq_charge_hash", "pg"])
    normalized_data = normalized_data.set_index("mod_seq_charge_hash;pg")
    return normalized_data


def _save_quality_scores(
    model: Model, identifiers: pd.DataFrame, save_path: str
) -> None:
    """
    Save the quality scores for each protein/precursor.
    """

    quality_scores = pd.DataFrame(np.vstack(model.quality_score))
    if shared_state.sorted_columns is not None:
        quality_scores.columns = shared_state.sorted_columns
    else:
        print("No sorted columns found. DataFrame will be saved without column names.")
    quality_scores = pd.concat([identifiers, quality_scores], axis=1)

    filename = "quality.score.matrix.tsv"
    if shared_state.level == "pg":
        filename = "pg.quality.score.matrix.tsv"
    else:
        filename = "precursor.quality.score.matrix.tsv"
        identifiers = identifiers.drop_duplicates(subset=["mod_seq_charge_hash"])

    logger.info(f"Saving {filename} to {save_path}.")
    filepath = os.path.join(save_path, filename)
    quality_scores.to_csv(filepath, sep="\t")


def _get_identifiers(features: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Get the fragment level identifiers.
    """
    return pd.concat(
        [
            g
            for _, g in features["ms2"]["ms2_intensity"][
                ["precursor_idx", "ion", "pg", "mod_seq_hash", "mod_seq_charge_hash"]
            ].groupby(shared_state.level)
        ]
    ).reset_index(drop=True)
