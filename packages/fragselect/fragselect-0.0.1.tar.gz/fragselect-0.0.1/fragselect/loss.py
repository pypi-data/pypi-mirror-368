"""
Module for calculating the loss.
"""

import torch
import torch.nn as nn
from fragselect.preprocessing import Preprocessing


class Loss:
    """
    Calculat loss for backpropagation in the model.
    """

    def __init__(
        self,
        lambda1: float = 0.01,
        lambda2: float = None,
        alpha: float = 0.2,
        epsilon: float = 1e-8,
        kind="WVL",
    ):
        """
        Initialize the Loss class with customizable parameters.

        Parameters
        ----------
        lambda1 : float, optional
            L1 regularization parameter.
            Default is 0.1.
        lambda2 : float or None, optional
            L2 regularization parameter.
            Default is None.
        alpha : float, optional
            Zero-weight penalty weight factor.
            Default is 1.0.
        epsilon : float, optional
            Small constant for numerical stability.
            Default is 1e-8.
        kind : str, optional
            Type of loss function.
            Default is "WVL".
        """
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.alpha = alpha
        self.epsilon = epsilon
        self._preprocessing = Preprocessing()
        self.kind = kind

    def __call__(
        self,
        model,
        intensity_layer: torch.Tensor,
        output: torch.Tensor,
        dim: int = 0,
        thresh: float = 0.5,
        **kwargs,
    ):
        if self.kind == "WVL":
            return self._weighted_var_loss(
                model=model,
                x=intensity_layer,
                qs=output,
                alpha=self.alpha,
                epsilon=self.epsilon,
                lambda1=self.lambda1,
                **kwargs,
            )

        if self.kind == "MAE":
            return self._weighted_avg_mae_loss(
                x=intensity_layer,
                qs=output,
                dim=dim,
                thresh=thresh,
                model=model,
                alpha=self.alpha,
                lambda1=self.lambda1,
                **kwargs,
            )

        if self.kind == "MSE":
            return self._weighted_avg_mse_loss(
                x=intensity_layer,
                qs=output,
                dim=dim,
                thresh=thresh,
                model=model,
                alpha=self.alpha,
                lambda1=self.lambda1,
                **kwargs,
            )

        if self.kind == "offset_mse":
            return self._offset_mse_loss(
                x=intensity_layer,
                y_pred=output,
                dim=dim,
                model=model,
                alpha=self.alpha,
                lambda1=self.lambda1**kwargs,
            )

        if self.kind == "offset_mae":
            return self._offset_mae_loss(
                x=intensity_layer,
                y_pred=output,
                dim=dim,
                model=model,
                alpha=self.alpha,
                lambda1=self.lambda1,
                **kwargs,
            )

        else:
            raise ValueError(
                f"Invalid loss kind: {self.kind}, please choose from 'WVL', 'MAE', or 'MSE'"
            )

    def _offset_mse_loss(
        self,
        x: torch.Tensor,
        y_pred: torch.Tensor,
        dim: int = 0,
        model: nn.Module = None,
        alpha: float = 1.0,
        lambda1: float = 0.1,
        kind: str = "abs",
    ) -> torch.Tensor:
        """
        Calculate the mean squared error loss between two tensors.
        """
        offset = self._compute_offset_from_median(x=x, kind=kind, dim=dim)
        return self._mse(y_pred=y_pred, y=offset) + self._regularization(
            model=model, qs=None, alpha=alpha, lambda1=lambda1
        )

    def _offset_mae_loss(
        self,
        x: torch.Tensor,
        y_pred: torch.Tensor,
        dim: int = 0,
        model: nn.Module = None,
        alpha: float = 1.0,
        lambda1: float = 0.1,
        kind: str = "abs",
    ) -> torch.Tensor:
        """
        Calculate the mean absolute error loss between two tensors.
        """
        offset = self._compute_offset_from_median(x=x, kind=kind, dim=dim)
        return self._mae(y_pred=y_pred, y=offset) + self._regularization(
            model=model, qs=None, alpha=alpha, lambda1=lambda1
        )

    def _weighted_avg_mae_loss(
        self,
        x: torch.Tensor,
        qs: torch.Tensor,
        dim: int = 0,
        thresh: float = 0.5,
        model: nn.Module = None,
        alpha: float = 1.0,
        lambda1: float = 0.1,
    ) -> torch.Tensor:
        """
        Calculate the weighted average mean absolute error loss.
        """

        weighted_avg = self._preprocessing.weighted_average(
            data=x,
            qs=qs,
            dim=dim,
            thresh=thresh,
        )
        y = self._compute_pseudo_ground_truth(x=x, dim=dim)
        loss = self._mae(y_pred=weighted_avg, y=y) + self._regularization(
            model=model, qs=qs, alpha=alpha, lambda1=lambda1
        )
        return loss

    def _weighted_avg_mse_loss(
        self,
        x: torch.Tensor,
        qs: torch.Tensor,
        dim: int = 0,
        thresh: float = 0.5,
        model: nn.Module = None,
        alpha: float = 1.0,
        lambda1: float = 0.1,
    ) -> torch.Tensor:
        """
        Calculate the weighted average mean squared error loss.
        """
        weighted_avg = self._preprocessing.weighted_average(
            data=x,
            qs=qs,
            dim=dim,
            thresh=thresh,
        )
        y = self._compute_pseudo_ground_truth(x=x, dim=dim)
        loss = self._mse(y_pred=weighted_avg, y=y) + self._regularization(
            model=model, qs=qs, alpha=alpha, lambda1=lambda1
        )
        return loss

    def _compute_pseudo_ground_truth(
        self, x: torch.Tensor, dim: int = 0
    ) -> torch.Tensor:
        return torch.nanmedian(x, dim=dim).values

    def _weighted_var_loss(
        self,
        model: nn.Module,
        x: torch.Tensor,
        qs: torch.Tensor,
        alpha: float = 1.0,
        epsilon: float = 1e-8,
        lambda1: float = 0.1,
    ) -> torch.Tensor:
        """
        Improved custom loss function for weighted variance and qs penalization.

        Parameters
        ----------
        model : nn.Module
            The neural network model
        x : torch.Tensor
            Model input.
        qs : torch.Tensor
            qs tensor (weights).
        alpha : float
            Penalty factor for zero weights.
        epsilon : float
            Small value to prevent division by zero.
        reg : bool
            Whether to apply regularization.
        lambda1 : float
            L1 regularization strength.

        Returns
        -------
        torch.Tensor
            Computed loss value.
        """
        # Compute weighted variance
        mean_weighted_var = self._compute_weighted_variance(
            x, qs, epsilon, reduction="mean"
        )

        regularization = self._regularization(model, qs, alpha, lambda1)
        # Compute final loss
        loss = mean_weighted_var + regularization

        return loss

    def _regularization(
        self,
        model: nn.Module,
        qs: torch.Tensor,
        alpha: float,
        lambda1: float,
    ) -> torch.Tensor:
        """
        Calculate regularization terms for the loss function.

        Parameters
        ----------
        model : nn.Module
            The neural network model
        output : torch.Tensor
            Output tensor (weights)
        alpha : float
            Penalty factor for zero weights
        lambda1 : float
            L1 regularization strength

        Returns
        -------
        torch.Tensor
            Combined regularization loss if reg=True, otherwise 0
        """

        # Penalize zero weights
        zero_penalty = self._penalize_zero_weights(qs, alpha=alpha)

        # L1 regularization on model weights
        model_weights = self._get_model_weights(model)
        l1_penalty = self._l1_regularization(model_weights, lambda1=lambda1)
        return zero_penalty + l1_penalty

    def _penalize_zero_weights(
        self, qs: torch.Tensor, alpha: float = 0.7
    ) -> torch.Tensor:
        """
        Calculates penalty loss for weights close to zero in the qs tensor.

        Parameters
        ----------
        qs : torch.Tensor
            The qs tensor containing predicted weights.
        alpha : float
            Penalty factor that controls the strength of zero-weight penalization.
            Higher values increase the penalty.

        Returns
        -------
        torch.Tensor
            The computed penalty loss value for weights close to zero.

        Examples
        --------
        >>> qs = torch.tensor([0.1, 0.01, 0.001, 0.9])
        >>> alpha = 1.0
        >>> zero_penalty = penalize_zero_weights(qs, alpha)
        """
        # Handle NaN values by using masked operations

        if (alpha == 0) or (qs is None):
            return torch.tensor(0.0)

        mask = ~torch.isnan(qs)
        valid_qs = qs[mask]

        if valid_qs.numel() == 0:
            return torch.tensor(0.0, device=qs.device)

        # Calculate mean of (1 - qs) for non-zero weights
        # This penalizes weights close to zero
        zero_penalty = torch.mean(1 - valid_qs) * alpha

        return zero_penalty

    def _get_model_weights(self, model: nn.Module) -> torch.Tensor:
        """
        Get the weights of the model.

        Parameters
        ----------
        model : nn.Module
            The neural network model

        Returns
        -------
        torch.Tensor
            The weights of the model.
        """

        if self.lambda1 == 0:
            return None

        return torch.cat(
            [
                param.view(-1)
                for name, param in model.named_parameters()
                if "weight" in name
            ]
        )

    def _l1_regularization(
        self, model_weights: torch.Tensor, lambda1: float = 5.0
    ) -> torch.Tensor:
        """
        Calculates L1 regularization loss for the model_weights.

        Parameters
        ----------
        model_weights : torch.Tensor
            The model_weights tensor from the model.
        lambda1 : float, default=5.0
            The L1 regularization coefficient controlling sparsity.
            Higher values lead to more sparsity in the model_weights.

        Returns
        -------
        torch.Tensor
            The computed L1 regularization loss value.

        Examples
        --------
        >>> model_weights = torch.randn(100)
        >>> lambda1 = 0.1
        >>> l1_loss = model._l1_regularization(model_weights, lambda1)
        """
        if model_weights is None:
            return torch.zeros(1)

        # Use torch.linalg.vector_norm for more stable L1 norm calculation
        return lambda1 * torch.linalg.vector_norm(model_weights, ord=1)

    def _compute_weighted_variance(
        self,
        x: torch.Tensor,
        output: torch.Tensor,
        epsilon: float = 1e-8,
        dim: int = 0,
        reduction: str = "mean",
    ) -> torch.Tensor:
        """
        Compute the weighted variance of the input tensor.

        This function calculates the weighted variance of the
        input tensor `x` using the quality scores provided in
        from the model's output. It handles NaN values by ignoring
        them in the calculations.

        Parameters
        ----------
        x : torch.Tensor
            Intensity layer.
        output : torch.Tensor
            Quality Score
        epsilon : float, optional
            A small value to avoid division by zero.
            Default is 1e-8.
        dim : int, optional
            The dimension to compute the variance along.
        kind : str, optional
            The type of reduction to apply.
            Default is "mean".

        Returns
        -------
        torch.Tensor
            The mean/var weighted variance of the input tensor.
        """

        # Compute mean intensity, handling NaN values
        intensity_agg = torch.nanmedian(x, dim=dim).values

        # Compute absolute difference to mean
        diff = torch.square(x - intensity_agg)

        # Compute weighted variance
        numerator = torch.nansum(output * diff, dim=dim)
        denominator = torch.nansum(output, dim=dim)
        weighted_var = numerator / (denominator + epsilon)

        if reduction == "mean":
            return torch.nanmean(weighted_var)

        elif reduction == "var":
            return torch.var(weighted_var)

    def _mae(self, y_pred: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        """
        Calculate the mean absolute error loss between two tensors.

        Parameters
        ----------
        y_pred : torch.Tensor
            First input tensor
        y : torch.Tensor
            Second input tensor
        dim : int, optional
            Dimension along which to compute mean. Default is 0.

        Returns
        -------
        torch.Tensor
            Mean absolute error loss, averaged along specified dimension
            while properly handling NaN values.
        """
        # Handle case where tensors have different shapes
        if y_pred.shape != y.shape:
            raise ValueError(
                f"Input shapes must match. Got {y_pred.shape} and {y.shape}"
            )

        # Compute absolute differences and take mean, ignoring NaN values
        abs_diff = torch.abs(y_pred - y)
        return torch.nanmean(abs_diff)

    def _mse(self, y_pred: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        """
        Calculate the mean squared error loss between two tensors.

        Parameters
        ----------
        y_pred : torch.Tensor
            Aligned intensity layer
        y : torch.Tensor
            (Pseudo) ground truth.
        dim : int, optional
            Dimension along which to compute mean. Default is 0.

        Returns
        -------
        torch.Tensor
            Mean squared error loss, averaged along specified dimension
            while properly handling NaN values.
        """
        # Handle case where tensors have different shapes
        if y_pred.shape != y.shape:
            raise ValueError(
                f"Input shapes across axis 1 must match. Got {y_pred.shape} and {y.shape}"
            )

        # Compute squared differences and take mean, ignoring NaN values
        squared_diff = (y_pred - y) ** 2
        return torch.nanmean(squared_diff)

    def _compute_offset_from_median(
        self, x: torch.Tensor, kind: str = "abs", dim: int = 0
    ) -> torch.Tensor:
        """
        Compute the offset of the input tensor.
        """
        median = torch.nanmedian(x, dim=dim)

        if kind == "abs":
            return torch.abs(x - median.values)
        elif kind == "sqr":
            return torch.square(x - median.values)
        else:
            raise ValueError(f"Invalid kind: {kind}, please choose from 'abs' or 'sqr'")

    ### OLD CODE ###

    def _compute_variance(self, x: torch.Tensor, dim: int = 1) -> torch.Tensor:
        """
        Compute the variance of the input tensor.

        This function calculates the variance of the input tensor `x`.
        It handles NaN values by ignoring them in the calculations.

        Parameters
        ----------
        x : torch.Tensor
            Intensity layer.

        Returns
        -------
        torch.Tensor
            The mean variance of the input tensor.
        """

        # Compute mean intensity, handling NaN values
        intensity_mean = torch.nanmean(x, dim=dim, keepdim=True)
        # Compute absolute difference to mean
        squared_diff_to_mean = torch.square(x - intensity_mean)

        # Compute variance
        variance = torch.nanmean(squared_diff_to_mean, dim=dim)

        return variance

    def calculate_pairwise_differences(self, a):
        """
        Calculate the pairwise differences between
        unique pairs of elements within a tensor eg.
        array([1, 2, 3]) -> array([1-2, 1-3, 2-3])

        Parameters
        ----------
        a : torch.Tensor

        Returns
        -------
        pariwise_differences : torch.Tensor
            The pairwise differences between unique
            pairs of elements within a tensor.
        """
        # Expand dimensions to enable broadcasting
        a_expanded = a.unsqueeze(2)
        diff_matrix = a_expanded - a_expanded.transpose(1, 2)

        # Extract the upper triangle indices
        n = a.shape[1]
        i_upper = torch.triu_indices(n, n, offset=1)

        # Use the upper triangle indices to get pairwise differences
        pairwise_differences = diff_matrix[:, i_upper[0], i_upper[1]]

        return pairwise_differences

    def pearsonloss(self, y_pred=None, y=None):
        """

        !!! This function is not used in the current implementation of the model. 
        Because it does not work lel !!!

        Calculate the pearson correlation loss between the\
        predicted and true values. This is used as a loss function.

        Parameters
        ----------
        y_pred : torch.Tensor
            The predicted values of the model.
            1D tensor of shape (n_samples, ).

        y : torch.Tensor
            The true values of the fragments in the sample.
            1D tensor of shape (n_samples, )

        Returns
        -------
        loss : torch.tensor
            The pearson correlation loss between the predicted and true values.
        """
        corrs = torch.empty((y_pred.shape[0],))

        for i in range(y_pred.shape[0]):
            std_dev_i = self._torch_nan_std(y)
            std_dev_j = self._torch_nan_std(y_pred)

            mean_i = torch.nanmean(y)
            mean_j = torch.nanmean(y_pred)

            covariance = torch.nanmean((y - mean_i) * (y_pred - mean_j))
            corrs[i] = covariance / (std_dev_i * std_dev_j)

        transformed_corr = torch.clamp(corrs, min=0)

        return torch.nanmean((1 - transformed_corr) ** 2)

    def _torch_nan_std(self, x):
        return torch.sqrt(
            torch.nansum((x - torch.nanmean(x)) ** 2) / len(x[~x.isnan()])
        )
