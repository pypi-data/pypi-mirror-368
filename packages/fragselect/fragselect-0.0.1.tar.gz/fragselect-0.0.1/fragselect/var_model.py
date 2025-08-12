"""
This module defines the `Model` class, which implements a
Multi-Layer Perceptron (MLP) model for the SelectLFQ package.
The model is designed to predict quality scores and intensity
data for proteins based on input features.
It includes methods for training, validation, and prediction,
as well as utilities for data preprocessing and loss computation.

Classes:
    Model: A class that defines the MLP model, including methods for
           forward pass, weight initialization,
           quality score prediction, intensity prediction, training,
           validation, and loss computation.

Dependencies:
    - numpy
    - pandas
    - torch
    - torch.nn
    - tqdm
    - selectlfq.preprocessing.Preprocessing
    - selectlfq.loss.Loss
    - selectlfq.visualizer.Visualizer
    - selectlfq.dataloader.DataLoader
"""

from typing import Union, List, Optional, Dict, Any

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from joblib import Parallel, delayed

from fragselect.dataloader import DataLoader
from fragselect.utils import rank, rank_by_no_valid_vals
from fragselect.shared_state import shared_state
from fragselect.utils import get_logger
from fragselect.config import FragSelectConfig
from fragselect.loss import Loss
from fragselect.preprocessing import Preprocessing

logger = get_logger()


class Model(nn.Module):
    """
    This class creates a Multi-Layer Perceptron (MLP) model for the SelectLFQ package.

    Parameters
    ----------
    input_size : int
        The number of input dimensions.
    hidden_sizes : list[int] or int
        Either a list specifying the size of each hidden layer, or an int specifying
        the number of hidden layers (all with the same size as input_size).
    dropout_rate : float or None
        The dropout rate. If None or 0, no dropout is applied.
    activation : nn.Module
        The activation function for hidden layers.
    init : str
        The initialization method for weights.
    batch_norm : bool
        Whether to use batch normalization.
    normalize : bool
        Whether to normalize the output data. Output data will be divided by the max value
        of output data for a more binomial distribution.
    output_activation : str
        The activation function for the output layer.
    preprocessor : PreprocessingPipeline or None
        The preprocessing pipeline.
    output_size : int
        The number of output dimensions.
    """

    def __init__(
        self,
        dataloader: DataLoader,
        hidden_sizes: Union[List[int], int] = 5,
        dropout_rate: Optional[float] = None,
        activation: nn.Module = nn.ReLU(),
        init: str = "uniform",
        batch_norm: bool = False,
        normalize: bool = False,
        output_activation: str = "sigmoid",
        output_size: int = 1,
    ):
        super().__init__()

        # Initialize attributes
        self.input_size = dataloader.no_features
        self.hidden_sizes = hidden_sizes
        self.dropout_rate = dropout_rate
        self.activation = activation
        self.batch_norm = batch_norm
        self.normalize = normalize
        self.output_activation = output_activation
        self.output_size = output_size

        # Initialize tracking variables
        self.train_loss = None
        self.val_loss = None
        self.filtered_intensity_layers_after_prediction = None
        self.intensity_layer_filt = None
        self.quality_score = None

        # Initialize helper objects
        self.prep = Preprocessing()
        self.loss = Loss()

        # Build the model
        self._build_model()
        self._init_weights(kind=init)

    def _build_model(self):
        """Build the sequential neural network based on the specified architecture."""
        layers = []

        hidden = (
            [self.input_size] * self.hidden_sizes
            if isinstance(self.hidden_sizes, int)
            else self.hidden_sizes
        )
        layer_dims = [self.input_size] + hidden + [self.output_size]

        use_bias = not self.batch_norm

        for i in range(len(layer_dims) - 2):
            layers.append(nn.Linear(layer_dims[i], layer_dims[i + 1], bias=use_bias))
            if self.batch_norm:
                layers.append(nn.BatchNorm1d(layer_dims[i + 1]))
            layers.append(self.activation)
            if self.dropout_rate and self.dropout_rate > 0:
                layers.append(nn.Dropout(self.dropout_rate))
        layers.append(nn.Linear(layer_dims[-2], layer_dims[-1], bias=True))

        activation_map = {
            "sigmoid": nn.Sigmoid(),
            "softmax": nn.Softmax(dim=1),
            "relu": nn.ReLU(),
            "tanh": nn.Tanh(),
            "leaky_relu": nn.LeakyReLU(),
        }

        if self.output_activation in activation_map:
            layers.append(activation_map[self.output_activation])
        elif self.output_activation is not None:
            raise ValueError(
                f"Unsupported activation function: {self.output_activation}"
            )

        self.model = nn.Sequential(*layers)

    @classmethod
    def initialize_for_training(
        cls,
        dataloader,
        model_params=None,
        optimizer_params=None,
        criterion_params=None,
        config: Optional[Union[Dict[str, Any], FragSelectConfig]] = None,
    ):
        """
        Initialize model and optimizer with configuration parameters.

        Parameters
        ----------
        dataloader : DataLoader
            The data loader instance
        model_params : dict, optional
            Override default model parameters
        optimizer_params : dict, optional
            Override default optimizer parameters
        criterion_params : dict, optional
            Override default criterion parameters
        config : Union[Dict[str, Any], FragSelectConfig], optional
            Configuration object or dictionary. If provided, overrides individual params.
        """
        # Handle configuration - support both FragSelectConfig and dict format
        if config is not None:
            if isinstance(config, FragSelectConfig):
                fragselect_config = config
            elif isinstance(config, dict):
                fragselect_config = FragSelectConfig.from_dict(config)
            else:
                raise ValueError(
                    f"config must be FragSelectConfig or dict, got {type(config)}"
                )

            # Use configuration from FragSelectConfig
            model_config = fragselect_config.CONFIG["model_params"].copy()
            optimizer_config = fragselect_config.CONFIG["optmizer_params"].copy()
            criterion_config = fragselect_config.CONFIG["criterion_params"].copy()
        else:
            # Use default configuration
            default_config = FragSelectConfig()
            model_config = default_config.CONFIG["model_params"].copy()
            if model_params:
                model_config.update(model_params)

            optimizer_config = default_config.CONFIG["optmizer_params"].copy()
            if optimizer_params:
                optimizer_config.update(optimizer_params)

            criterion_config = default_config.CONFIG["criterion_params"].copy()
            if criterion_params:
                criterion_config.update(criterion_params)

        # Initialize model and optimizer
        model = cls(dataloader=dataloader, **model_config)

        # Use the appropriate optimizer based on configuration
        optimizer_type = optimizer_config.get("optimizer_type", "Adam")

        # Remove optimizer_type from config as it's not a valid parameter for PyTorch optimizers
        optimizer_params = {
            k: v for k, v in optimizer_config.items() if k != "optimizer_type"
        }

        if optimizer_type == "Adam":
            optimizer = torch.optim.Adam(model.parameters(), **optimizer_params)
        elif optimizer_type == "SGD":
            optimizer = torch.optim.SGD(model.parameters(), **optimizer_params)
        elif optimizer_type == "AdamW":
            optimizer = torch.optim.AdamW(model.parameters(), **optimizer_params)
        elif optimizer_type == "RMSprop":
            optimizer = torch.optim.RMSprop(model.parameters(), **optimizer_params)
        else:
            # Default to Adam if unknown optimizer type
            optimizer = torch.optim.Adam(model.parameters(), **optimizer_params)

        criterion = Loss(**criterion_config)

        return model, optimizer, criterion

    def forward(self, x: torch.Tensor, normalize: bool = False) -> torch.Tensor:
        """
        Forward pass through the model.

        Parameters
        ----------
        x : torch.Tensor
            The input data.
        normalize : bool, optional
            Whether to normalize the output, by default False.

        Returns
        -------
        torch.Tensor
            The output of the model.
        """
        x = self.model(x)
        if normalize:
            x = x / x.max()
        return x

    def _init_weights(self, kind: str = "uniform"):
        for layer in self.model:
            if isinstance(layer, nn.Linear):
                if kind == "uniform":
                    nn.init.uniform_(layer.weight, a=-0.1, b=0.1)

                elif kind == "zero":
                    nn.init.zeros_(layer.weight)

                elif kind == "xavier":
                    torch.nn.init.xavier_uniform_(layer.weight)

                elif kind == "kaiming":
                    torch.nn.init.kaiming_uniform_(
                        layer.weight, a=0, mode="fan_in", nonlinearity="relu"
                    )

    def _predict_quality_scores(self, dataloader: DataLoader) -> List[np.ndarray]:
        """
        Prediction of quality scores.

        Parameters
        ----------
        dataloader : DataLoader
            Input DataLoader containing the data to make predictions on.

        Returns
        -------
        output_split : List[np.array]
            List of arrays containing predicted quality scores.
            Each array has shape (n_samples, n_fragments).
        """
        logger.info("Predicting quality scores.")
        # concatenate the feauture layers for all proteins
        x, _ = dataloader.merge()

        # turn 3d tensor into 2d tensor
        x_reshaped = self.prep.preprocessing_for_forward_prop(x)

        # forward pass
        output = self(x_reshaped)

        # reshape the output form 1d to 2d
        output_reshaped = self.prep.reshape_from_1d_to_2d(output)
        output_conv = output_reshaped.detach().numpy()

        # split in the original shapes for each proteins
        output_split = self._split_by_protein(output_conv, dataloader.original_rows)
        return output_split

    def _split_by_protein(
        self, data: Union[np.ndarray, torch.Tensor], orig_fragment_sizes: List[int]
    ) -> List[Union[np.ndarray, torch.Tensor]]:
        """
        Split concatenated data by the original fragment size.

        Parameters
        ----------
        data : np.ndarray or torch.Tensor
            The data to split.
        orig_fragment_sizes : List[int]
            List of the original fragment sizes for each protein.

        Returns
        -------
        List[Union[np.ndarray, torch.Tensor]]
            List of arrays containing the data for each protein.
        """
        # Handle single protein case
        if len(orig_fragment_sizes) == 1:
            return [data]

        if isinstance(data, np.ndarray):
            indices = np.cumsum(orig_fragment_sizes)[:-1]
            data_split = np.array_split(data, indices)
            return data_split

        elif isinstance(data, torch.Tensor):
            indices = torch.cumsum(torch.tensor(orig_fragment_sizes), dim=0)[:-1]
            data_split = torch.tensor_split(data, indices)
            return data_split

        else:
            raise ValueError(
                "Data type not supported. Expected numpy array or torch tensor."
            )

    def predict(
        self,
        dataloader: DataLoader,
        cutoff: float,
        min_num_fragments: int = 12,
        no_const: int = 3000,
    ) -> pd.DataFrame:
        """
        Prediction of intensity data. Using the quality scores to filter the data,
        based on a cutoff value.

        Parameters:
        ----------
            dataloader (DataLoader): Dataloader.
                Input data.
            cutoff (float): Cutoff value.
                cutoff value to remove low quality scores
            min_num_fragments (int): Minimum number of valid values in a sample.
                minimum number of valid values in a sample
            no_const (int): Number of values to infer systematic
                biases for sample wise normalization

        Returns:
        ----------
            predicted_intensity (np.array): Final predicted intensity.
                Median of remaining data after filtering.
        """
        logger.info("Starting prediction.")
        self.quality_score = self._predict_quality_scores(dataloader)

        self.quality_score = self._normalize_quality_scores()

        intensity_layer_filt = self._get_intensity_layer_filt(
            dataloader, cutoff, self.quality_score, min_num_fragments
        )

        self.intensity_layer_filt = self.prep.init_align(intensity_layer_filt)

        logger.info("Estimating intensity.")
        predicted_intensity = np.array(
            [np.nanmedian(y, axis=0) for y in self.intensity_layer_filt]
        )

        if shared_state.lin_scaled_data is not None:
            shifted_prediction = self._shift_prediction(
                predicted_intensity, shared_state.lin_scaled_data
            )
        else:
            logger.info("No linear scaled data provided, using predicted intensity.")
            shifted_prediction = predicted_intensity

        normalized_prediction = self.prep.normalize_by_sample(
            prediction=shifted_prediction, no_const=no_const
        )

        prediction_data = pd.DataFrame(
            normalized_prediction,
            columns=shared_state.sorted_columns,
            index=shared_state.level_information,
        )
        return prediction_data

    def _normalize_quality_scores(self):
        """
        Normalize the quality scores to be between 0 and 1.
        """
        logger.info("Normalizing quality scores.")
        return [qs / np.nanmax(qs, axis=0, keepdims=True) for qs in self.quality_score]

    def calculate_protein_score(self):
        """
        Calculate the protein score. The protein score is the sum of the quality scores
        of the protein. The protein score is then normalized to be between 0 and 1.
        The protein score is then centered around 0.5.
        Returns
        -------
        protein_score : np.ndarray
            The protein score.
        """

        # if self.quality_score is None:
        #     raise ValueError(
        #         "Quality scores have not been calculated yet, run predict() first."
        #     )
        # raw_protein_score = np.log2(
        #     np.array([np.nansum(qs) for qs in self.quality_score])
        # )
        # protein_score = raw_protein_score / np.nanmax(raw_protein_score)
        # protein_score_centered = (
        #     protein_score + 0.5 - np.nanmean(protein_score)
        # )  # center around 0.5
        # return protein_score_centered

        return np.array([np.nanmean(qs) for qs in self.quality_score])

    def calculate_proportion_retained(
        self, data: list[np.ndarray] = None, cutoff: float = 0.9
    ):
        """
        Calculate the proportion of retained datapoints.
        Returns
        -------
        proportion_retained_datapoints : np.ndarray
            The proportion of retained datapoints.
        """
        if data is None:
            if self.has_quality_scores:
                no_retained = np.array(
                    [np.array(qs > cutoff).sum() for qs in self.quality_score]
                )
                no_removed = np.array(
                    [np.array(qs < cutoff).sum() for qs in self.quality_score]
                )
                total_no = no_retained + no_removed
                return no_retained / total_no
            else:
                raise ValueError(
                    "Quality scores have not been calculated yet, run predict() first."
                )
        else:
            no_retained = np.array([np.array(qs > cutoff).sum() for qs in data])
            no_removed = np.array([np.array(qs <= cutoff).sum() for qs in data])
            total_no = no_retained + no_removed
            return no_retained / total_no

    @property
    def has_quality_scores(self):
        """Check if quality scores have been calculated."""
        if self.quality_score is None:
            raise ValueError(
                "Quality scores have not been calculated yet, run predict() first."
            )
        return True

    def _shift_prediction(
        self, prediction: np.ndarray, lin_scaled_data: np.ndarray
    ) -> np.ndarray:
        logger.info("Shifting prediction based in intensity on linear scale.")
        # transfrom back to original scale for shifting
        transf_prediction = 2**prediction

        # this is based on the equation a * x = b  -> x = b/a
        sum_per_protein = np.nansum(transf_prediction, axis=1)
        pred_filt_masks = [
            np.isfinite(x) for x in self.filtered_intensity_layers_after_prediction
        ]
        sum_int_unaligned = np.array(
            [
                x[m].sum()
                for x, m in zip(
                    lin_scaled_data,
                    pred_filt_masks,
                )
            ]
        )
        multiplier = np.expand_dims(sum_int_unaligned / sum_per_protein, axis=1)

        # multiply the prediction by the multiplier to shift the data up
        shifted_prediction = np.log2(transf_prediction * multiplier)

        return shifted_prediction

    def _get_intensity_layer_filt(
        self,
        dataloader: DataLoader,
        cutoff: float,
        quality_score: np.ndarray,
        min_num_fragments: int = 12,
    ):
        logger.info("Removing low quality fragments based on quality scores.")
        self.filtered_intensity_layers_after_prediction = [
            self._filter(i, q, cutoff, min_num_fragments)
            for i, q in zip(dataloader.intensity_layer, quality_score)
        ]
        return self.filtered_intensity_layers_after_prediction

    def _filter(
        self,
        intensity_layer: np.ndarray,
        quality_score: np.ndarray,
        cutoff: float = 0.5,
        min_num_fragments: int = 12,
    ):
        if quality_score.shape[1] > 1:
            weight_mask = quality_score >= cutoff
            agg_weights_mask = weight_mask.sum(axis=0)
            sample_mask = agg_weights_mask <= min_num_fragments

            if sample_mask.any():
                intensity_layer_copy = intensity_layer.copy()
                ranked_weights = rank(quality_score, axis=0)
                ranked_threshold_mask = ranked_weights < min_num_fragments
                weight_mask[:, sample_mask] = ranked_threshold_mask[:, sample_mask]
                intensity_layer_copy[~weight_mask] = np.nan

                return intensity_layer_copy

            else:
                return np.where(weight_mask, intensity_layer, np.nan)

        else:
            weight_mask = rank(quality_score).reshape(
                -1,
            ) > min_num_fragments | (quality_score > cutoff).reshape(
                -1,
            )
            intensity_layer_copy = intensity_layer.copy()
            intensity_layer_copy[~weight_mask] = np.nan
            return intensity_layer_copy

    def fit(
        self,
        criterion: Loss,
        optimizer: torch.optim,
        dataloader: DataLoader,
        fit_params: dict = None,
        **kwargs,
    ):
        """
        Train the model. The training process is visualized with a loss plot.
        Training and validation losses are calculated for each epoch.
        Training and validation are done using a random split of the input data.
        The first half of the data is used for training and the second half for validation.

        Parameters
        ----------
        criterion : Loss
            The loss function to evaluate the model's performance.
        optimizer : torch.optim.Optimizer
            The optimizer to update the model's parameters.
        dataloader : DataLoader
            The input data for the model.
        fit_params : dict, optional
            The parameters for the fit, by default None.
            The parameters are:
            - epochs: int, optional
                The number of epochs to train the model, by default 1.
            - batch_size: int, optional
                The number of proteins in each batch, by default None.
            - shuffle: bool, optional
                Whether to shuffle the data before splitting into batches, by default True.
            - train_size: int, optional
                The number of proteins to use for training, by default 200.
            - verbose: bool, optional
                Whether to print the loss after training, by default True.
        **kwargs : dict
            Additional arguments.

        Returns
        -------
        tuple
            A tuple containing the training losses and validation losses for each epoch.
        """
        logger.info("Training the model.")

        # Handle fit parameters
        if fit_params is not None:
            # Use provided fit parameters
            fit_config = fit_params.copy()
        else:
            # Use default fit parameters
            default_config = FragSelectConfig()
            fit_config = default_config.CONFIG["fit_params"].copy()

        dl = self._select_dataloader(dataloader, fit_config["train_size"])

        train_losses = np.empty(shape=(fit_config["epochs"], int(len(dl) / 2)))
        val_losses = np.empty(shape=(fit_config["epochs"], int(len(dl) / 2)))

        for epoch in range(fit_config["epochs"]):
            # randomise the data before splitting into train and validation
            dataloader_val = dl[0::2]
            dataloader_train = dl[1::2]

            # prepare the dataloaders for training and validation
            dataloader_train, dataloader_val = self._prepare_batched_dataloaders(
                dataloader_train,
                dataloader_val,
                fit_config["batch_size"],
                fit_config["shuffle"],
            )

            train_losses, val_losses = self._train_val(
                dataloader_train,
                dataloader_val,
                criterion,
                optimizer,
                train_losses,
                val_losses,
                epoch,
                **kwargs,
            )

            if fit_config["verbose"]:
                train_mean = train_losses[: epoch + 1].mean(axis=1)
                val_mean = val_losses[: epoch + 1].mean(axis=1)
                logger.info(
                    f"Epoch {epoch+1}/{fit_config['epochs']} - Training Loss: {train_mean[-1]:.4f} - "
                    f"Validation Loss: {val_mean[-1]:.4f}"
                )

        self.train_loss = train_losses.mean(axis=1)
        self.val_loss = val_losses.mean(axis=1)

    def _select_dataloader(self, dataloader: DataLoader, train_size: int = 200):
        ranks = rank_by_no_valid_vals(dataloader.intensity_layer)
        return dataloader[list(ranks[:train_size])]

    def _prepare_batched_dataloaders(
        self,
        dataloader_train: DataLoader,
        dataloader_val: DataLoader,
        batch_size: int,
        shuffle: bool = True,
    ):
        """Prepare training and validation dataloaders with optional batching and shuffling.

        Parameters
        ----------
        dataloader_train : DataLoader
            Training data
        dataloader_val : DataLoader
            Validation data
        batch_size : int or None
            Size of batches. If None, no batching is performed
        shuffle : bool, default=True
            Whether to shuffle the data before batching

        Returns
        -------
        tuple
            (batched_train_dataloader, batched_val_dataloader)
        """
        if batch_size is None:
            return dataloader_train, dataloader_val

        if shuffle:
            perm = tuple(np.random.permutation(len(dataloader_train)))
            dataloader_train = self._split_data_in_batches(
                dataloader_train[perm], batch_size
            )
            dataloader_val = self._split_data_in_batches(
                dataloader_val[perm], batch_size
            )
        else:
            dataloader_train = self._split_data_in_batches(dataloader_train, batch_size)
            dataloader_val = self._split_data_in_batches(dataloader_val, batch_size)

        return dataloader_train, dataloader_val

    def _split_data_in_batches(self, data: DataLoader, batch_size: int) -> list:
        """
        Split data into batches.
        The numbers of proteins in each batch is defined by the batch_size.

        Parameters
        ----------
        data : dataloader
            The input data to be split.
        batch_size : int
            The number of proteins in each batch.
        Returns
        -------
        list
            List of data split into.
        """
        return [data[i : i + batch_size] for i in range(0, len(data), batch_size)]

    def _train_val(
        self,
        dataloader_train: DataLoader,
        dataloader_val: DataLoader,
        criterion: Loss,
        optimizer: torch.optim,
        train_losses: np.ndarray,
        val_losses: np.ndarray,
        epoch: int,
        **kwargs,
    ):
        for train_dataloader, val_dataloader in zip(dataloader_train, dataloader_val):
            # training
            train_loss = self._train(optimizer, train_dataloader, criterion, **kwargs)
            train_losses[epoch, :] = train_loss

            # validation
            val_loss = self._val(val_dataloader, criterion, **kwargs)
            val_losses[epoch, :] = val_loss

        return train_losses, val_losses

    def _train(
        self,
        optimizer: torch.optim.Adam,
        dataloader: DataLoader,
        criterion: Loss,
        **kwargs,
    ) -> torch.Tensor:
        self.train()
        optimizer.zero_grad()
        loss = self._forward_prop_and_compute_loss(dataloader, criterion, **kwargs)
        loss.backward()
        optimizer.step()

        return loss.item()

    def _val(
        self,
        dataloader: DataLoader,
        criterion: Loss,
        **kwargs,
    ) -> torch.Tensor:
        self.eval()
        with torch.inference_mode():
            return self._forward_prop_and_compute_loss(
                dataloader, criterion, **kwargs
            ).item()

    def _forward_prop_and_compute_loss(
        self,
        dataloader: DataLoader,
        criterion: Loss,
        **kwargs,
    ) -> torch.Tensor:
        if isinstance(dataloader, DataLoader):
            feature_layer, _ = dataloader.merge()
            output_reshaped = self._preprocess_forward_reshape(feature_layer)
            # SPLIT THE OUTPUT INTO THE ORIGINAL SHAPES
            output_reshaped_split = self._split_by_protein(
                output_reshaped, dataloader.original_rows
            )
            return self._batch_loss(
                criterion, dataloader, output_reshaped_split, **kwargs
            )

        else:
            feature_layer, intensity_layer = dataloader
            output_reshaped = self._preprocess_forward_reshape(feature_layer)
            return criterion(self, intensity_layer, output_reshaped, **kwargs)

    def _preprocess_forward_reshape(self, feature_layer: torch.Tensor) -> torch.Tensor:
        # preprocessing input data
        input_data_processed = self.prep.preprocessing_for_forward_prop(feature_layer)

        # forward pass
        output = self(input_data_processed)

        # reshape the output
        output_reshaped = self.prep.reshape_from_1d_to_2d(output)

        return output_reshaped

    def _batch_loss(
        self,
        criterion: Loss,
        dataloader: DataLoader,
        output: List[torch.tensor],
        **kwargs,
    ) -> torch.Tensor:
        losses = []
        for out, intensity in zip(output, dataloader.intensity_layer_torch):
            loss_value = criterion(self, intensity, out, **kwargs)
            losses.append(loss_value)
        loss = torch.stack(losses)
        return loss.mean()
