"""
Configuration module for FragSelect.

This module provides a comprehensive configuration system for the FragSelect package,
including model parameters, training parameters, and validation.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field, asdict
import torch.nn as nn
import torch.optim as optim


@dataclass
class CriterionConfig:
    """Configuration for loss function parameters."""

    alpha: float = 0.8
    epsilon: float = 1e-8
    kind: str = "WVL"
    lambda1: float = 0.0

    def __post_init__(self):
        """Validate criterion parameters after initialization."""
        if not 0.0 <= self.alpha <= 1.0:
            raise ValueError(f"alpha must be between 0.0 and 1.0, got {self.alpha}")
        if self.epsilon <= 0:
            raise ValueError(f"epsilon must be positive, got {self.epsilon}")
        if self.kind not in ["WVL", "MSE", "MAE"]:
            raise ValueError(
                f"kind must be one of ['WVL', 'MSE', 'MAE'], got {self.kind}"
            )
        if self.lambda1 < 0:
            raise ValueError(f"lambda1 must be non-negative, got {self.lambda1}")


@dataclass
class ModelConfig:
    """Configuration for neural network model parameters."""

    hidden_sizes: Union[int, List[int]] = 4
    dropout_rate: Optional[float] = None
    activation: nn.Module = field(default_factory=lambda: nn.ReLU())
    init: str = "uniform"
    batch_norm: bool = True
    normalize: bool = False
    output_activation: str = "sigmoid"

    def __post_init__(self):
        """Validate model parameters after initialization."""
        if isinstance(self.hidden_sizes, int) and self.hidden_sizes <= 0:
            raise ValueError(f"hidden_sizes must be positive, got {self.hidden_sizes}")
        if isinstance(self.hidden_sizes, list) and not all(
            h > 0 for h in self.hidden_sizes
        ):
            raise ValueError(
                f"All hidden_sizes must be positive, got {self.hidden_sizes}"
            )

        if self.dropout_rate is not None and not 0.0 <= self.dropout_rate <= 1.0:
            raise ValueError(
                f"dropout_rate must be between 0.0 and 1.0, got {self.dropout_rate}"
            )

        if self.init not in ["uniform", "zero", "xavier", "kaiming"]:
            raise ValueError(
                f"init must be one of ['uniform', 'zero', 'xavier', 'kaiming'], got {self.init}"
            )

        if self.output_activation not in ["sigmoid", "tanh", "relu", "linear"]:
            raise ValueError(
                f"output_activation must be one of ['sigmoid', 'tanh', 'relu', 'linear'], got {self.output_activation}"
            )


@dataclass
class OptimizerConfig:
    """Configuration for optimizer parameters."""

    lr: float = 1e-2
    weight_decay: float = 0.0
    betas: tuple = (0.9, 0.999)
    eps: float = 1e-8
    optimizer_type: str = "Adam"

    def __post_init__(self):
        """Validate optimizer parameters after initialization."""
        if self.lr <= 0:
            raise ValueError(f"learning rate must be positive, got {self.lr}")
        if self.weight_decay < 0:
            raise ValueError(
                f"weight_decay must be non-negative, got {self.weight_decay}"
            )
        if not all(0 < beta < 1 for beta in self.betas):
            raise ValueError(f"betas must be between 0 and 1, got {self.betas}")
        if self.eps <= 0:
            raise ValueError(f"eps must be positive, got {self.eps}")
        if self.optimizer_type not in ["Adam", "SGD", "AdamW", "RMSprop"]:
            raise ValueError(
                f"optimizer_type must be one of ['Adam', 'SGD', 'AdamW', 'RMSprop'], got {self.optimizer_type}"
            )


@dataclass
class FitConfig:
    """Configuration for training parameters."""

    epochs: int = 40
    batch_size: int = 64
    shuffle: bool = False
    train_size: int = 200
    verbose: bool = True
    validation_split: float = 0.2
    early_stopping_patience: Optional[int] = None
    learning_rate_scheduler: Optional[str] = None
    save_best_model: bool = False
    model_save_path: Optional[str] = None

    def __post_init__(self):
        """Validate training parameters after initialization."""
        if self.epochs <= 0:
            raise ValueError(f"epochs must be positive, got {self.epochs}")
        if self.batch_size <= 0:
            raise ValueError(f"batch_size must be positive, got {self.batch_size}")
        if self.train_size <= 0:
            raise ValueError(f"train_size must be positive, got {self.train_size}")
        if not 0.0 < self.validation_split < 1.0:
            raise ValueError(
                f"validation_split must be between 0.0 and 1.0, got {self.validation_split}"
            )
        if (
            self.early_stopping_patience is not None
            and self.early_stopping_patience <= 0
        ):
            raise ValueError(
                f"early_stopping_patience must be positive, got {self.early_stopping_patience}"
            )
        if (
            self.learning_rate_scheduler is not None
            and self.learning_rate_scheduler
            not in ["StepLR", "ReduceLROnPlateau", "CosineAnnealingLR"]
        ):
            raise ValueError(
                f"learning_rate_scheduler must be one of ['StepLR', 'ReduceLROnPlateau', 'CosineAnnealingLR'], got {self.learning_rate_scheduler}"
            )


class FragSelectConfig:
    """
    Main configuration class for FragSelect.

    This class provides a centralized configuration system with validation,
    serialization, and easy parameter management.
    """

    def __init__(
        self,
        criterion_config: Optional[CriterionConfig] = None,
        model_config: Optional[ModelConfig] = None,
        optimizer_config: Optional[OptimizerConfig] = None,
        fit_config: Optional[FitConfig] = None,
    ):
        """
        Initialize FragSelectConfig with optional custom configurations.

        Parameters
        ----------
        criterion_config : CriterionConfig, optional
            Custom criterion configuration
        model_config : ModelConfig, optional
            Custom model configuration
        optimizer_config : OptimizerConfig, optional
            Custom optimizer configuration
        fit_config : FitConfig, optional
            Custom training configuration
        """
        self.criterion_config = criterion_config or CriterionConfig()
        self.model_config = model_config or ModelConfig()
        self.optimizer_config = optimizer_config or OptimizerConfig()
        self.fit_config = fit_config or FitConfig()

    @property
    def CONFIG(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the configuration as a dictionary for backward compatibility.

        Returns
        -------
        Dict[str, Dict[str, Any]]
            Configuration dictionary with the same structure as the original ModelConfig.CONFIG
        """
        return {
            "criterion_params": asdict(self.criterion_config),
            "model_params": asdict(self.model_config),
            "optmizer_params": asdict(self.optimizer_config),
            "fit_params": asdict(self.fit_config),
        }

    def update(self, config_dict: Dict[str, Dict[str, Any]]) -> None:
        """
        Update configuration from a dictionary.

        Parameters
        ----------
        config_dict : Dict[str, Dict[str, Any]]
            Dictionary containing configuration updates
        """
        if "criterion_params" in config_dict:
            for key, value in config_dict["criterion_params"].items():
                if hasattr(self.criterion_config, key):
                    setattr(self.criterion_config, key, value)

        if "model_params" in config_dict:
            for key, value in config_dict["model_params"].items():
                if hasattr(self.model_config, key):
                    setattr(self.model_config, key, value)

        if "optmizer_params" in config_dict:
            for key, value in config_dict["optmizer_params"].items():
                if hasattr(self.optimizer_config, key):
                    setattr(self.optimizer_config, key, value)

        if "fit_params" in config_dict:
            for key, value in config_dict["fit_params"].items():
                if hasattr(self.fit_config, key):
                    setattr(self.fit_config, key, value)

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """
        Convert configuration to dictionary.

        Returns
        -------
        Dict[str, Dict[str, Any]]
            Configuration as dictionary
        """
        return self.CONFIG

    def to_json(self, filepath: Optional[Union[str, Path]] = None) -> str:
        """
        Convert configuration to JSON string or save to file.

        Parameters
        ----------
        filepath : str or Path, optional
            Path to save JSON file. If None, returns JSON string.

        Returns
        -------
        str
            JSON string if filepath is None, otherwise empty string
        """
        config_dict = self.to_dict()

        # Convert torch.nn.Module to string representation
        if isinstance(config_dict["model_params"]["activation"], nn.Module):
            config_dict["model_params"]["activation"] = str(
                config_dict["model_params"]["activation"]
            )

        json_str = json.dumps(config_dict, indent=2, default=str)

        if filepath is not None:
            with open(filepath, "w") as f:
                f.write(json_str)
            return ""

        return json_str

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Dict[str, Any]]) -> "FragSelectConfig":
        """
        Create configuration from dictionary.

        Parameters
        ----------
        config_dict : Dict[str, Dict[str, Any]]
            Configuration dictionary

        Returns
        -------
        FragSelectConfig
            Configuration instance
        """
        criterion_config = CriterionConfig(**config_dict.get("criterion_params", {}))
        model_config = ModelConfig(**config_dict.get("model_params", {}))
        optimizer_config = OptimizerConfig(**config_dict.get("optmizer_params", {}))
        fit_config = FitConfig(**config_dict.get("fit_params", {}))

        return cls(criterion_config, model_config, optimizer_config, fit_config)

    @classmethod
    def from_json(cls, filepath: Union[str, Path]) -> "FragSelectConfig":
        """
        Create configuration from JSON file.

        Parameters
        ----------
        filepath : str or Path
            Path to JSON configuration file

        Returns
        -------
        FragSelectConfig
            Configuration instance
        """
        with open(filepath, "r") as f:
            config_dict = json.load(f)

        return cls.from_dict(config_dict)

    def get_optimizer_class(self):
        """
        Get the optimizer class based on configuration.

        Returns
        -------
        torch.optim.Optimizer
            Optimizer class
        """
        optimizer_map = {
            "Adam": optim.Adam,
            "SGD": optim.SGD,
            "AdamW": optim.AdamW,
            "RMSprop": optim.RMSprop,
        }
        return optimizer_map.get(self.optimizer_config.optimizer_type, optim.Adam)

    def __repr__(self) -> str:
        """String representation of the configuration."""
        return (
            f"FragSelectConfig(\n"
            f"  criterion_config={self.criterion_config},\n"
            f"  model_config={self.model_config},\n"
            f"  optimizer_config={self.optimizer_config},\n"
            f"  fit_config={self.fit_config}\n"
            f")"
        )
