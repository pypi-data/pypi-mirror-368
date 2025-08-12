"""Module for keeping track of feature layers"""

import torch
from fragselect.utils import repeater


class DataLoader:
    """
    A class to handle feature and intensity layers.

    Parameters
    ----------
    feature_layer : list
        List of feature layers in numpy format.
    intensity_layer : list
        List of intensity layers in numpy format.

    Attributes
    ----------
    no_features : int
        Number of features in the feature layer.
    no_samples : int
        Number of samples in the feature layer.
    no_fragments : int
        Number of fragments in the feature layer.
    feature_layer_torch : list
        List of feature layers in torch format.
    intensity_layer_torch : list
        List of intensity layers in torch format.
    original_rows : list
        List of original row counts for each feature layer tensor.

    Methods
    -------
    __len__()
        Returns the number of feature layers/proteins.
    data
        Property to get and set the feature layer.
    __getitem__(idx)
        Returns the feature and intensity layers at given index/indices.
    __iter__()
        Makes the DataLoader iterable.
    from_numpy_to_torch(feature_layer, intensity_layer)
        Converts multiple numpy arrays to torch tensors.
    single_from_numpy_to_torch(data)
        Converts a single numpy array to a torch tensor.
    combine()
        Concatenates each feature layer and returns a single torch tensor.

    Examples
    --------
    >>> loader = DataLoader(feature_layer, intensity_layer)
    """

    def __init__(self, feature_layer, intensity_layer):
        self.feature_layer = feature_layer
        self.intensity_layer = intensity_layer
        self.no_features = feature_layer[0].shape[2]
        self.no_samples = feature_layer[0].shape[0]
        self.feature_layer_torch, self.intensity_layer_torch = (
            self._multi_from_numpy_to_torch(feature_layer, intensity_layer)
        )
        self.original_rows = [t.shape[0] for t in self.feature_layer_torch]

    def __len__(self):
        """
        Returns the number of feature layers/proteins.

        Returns
        -------
        int
            Number of feature layers/proteins.
        """
        return len(self.feature_layer)

    def __getitem__(self, idx):
        # Handle multiple indices
        if isinstance(idx, (tuple, list)):
            # Create new DataLoader with selected indices
            new_loader = DataLoader.__new__(DataLoader)
            new_loader.feature_layer = [self.feature_layer[i] for i in idx]
            new_loader.intensity_layer = [self.intensity_layer[i] for i in idx]

            new_loader.feature_layer_torch = [self.feature_layer_torch[i] for i in idx]
            new_loader.intensity_layer_torch = [
                self.intensity_layer_torch[i] for i in idx
            ]

            new_loader.no_features = self.no_features
            new_loader.no_samples = self.no_samples

            new_loader.original_rows = [
                t.shape[0] for t in new_loader.feature_layer_torch
            ]
            return new_loader

        # Handle slicing
        elif isinstance(idx, slice):
            new_loader = DataLoader.__new__(DataLoader)
            new_loader.feature_layer_torch = self.feature_layer_torch[idx]
            new_loader.intensity_layer_torch = self.intensity_layer_torch[idx]

            new_loader.feature_layer = self.feature_layer[idx]
            new_loader.intensity_layer = self.intensity_layer[idx]

            new_loader.no_features = self.no_features
            new_loader.no_samples = self.no_samples

            new_loader.original_rows = [
                t.shape[0] for t in new_loader.feature_layer_torch
            ]
            return new_loader

        # Handle single index
        return self.feature_layer_torch[idx], self.intensity_layer_torch[idx]

    def __iter__(self):
        """Make the DataLoader iterable."""
        for i in range(len(self)):
            yield self.feature_layer_torch[i], self.intensity_layer_torch[i]

    def _multi_from_numpy_to_torch(self, feature_layer, intensity_layer):
        """
        Turn multiple numpy arrays into torch tensors.

        Parameters:
        ----------
            feature_layer (list): List of feature layers in numpy format.
            intensity_layer (list): List of intensity layers in numpy format

        Returns:
        ----------
            tuple: Tuple of feature layers and intensity layers in torch format
        """

        feature_layer_torch = repeater(
            feature_layer, self._single_from_numpy_to_torch, False
        )
        intensity_layer_torch = repeater(
            intensity_layer, self._single_from_numpy_to_torch, False
        )

        return feature_layer_torch, intensity_layer_torch

    def _single_from_numpy_to_torch(self, data):
        """
        Convert a single numpy array to a torch tensor.

        Parameters:
        ----------
            data (np.array): Numpy array to convert to torch tensor.

        Returns:
        ----------
            torch.Tensor: Torch tensor of the input numpy array.
        """

        return torch.from_numpy(data).float()

    def merge(self):
        """
        Concatenate each protein group's feature and intensity layers together to
        one entire feature and intensity layer. This is used for batching the data.

        Returns
        -------
        tuple of torch.Tensor
            Tuple of two tensors containing concatenated feature & intensity layers.
        """
        return torch.cat(self.feature_layer_torch), torch.cat(
            self.intensity_layer_torch
        )

    def remove(self, indices_to_remove):
        """
        Remove specified indices from the third dimension of each tensor in feature_layer_torch.
        Returns a new DataLoader instance with the modified features.

        Parameters:
        ----------
            indices_to_remove (list): List of indices to remove from the third dimension

        Returns:
        ----------
            DataLoader: Returns a new DataLoader instance with modified features

        Example:
        ----------
            If tensor shape is [213, 20, 4] and indices_to_remove = [1, 2],
            resulting tensor shape will be [213, 20, 2] keeping indices [0, 3]
        """
        # Convert indices to remove into a set for faster lookup
        indices_to_remove = set(indices_to_remove)

        # Get all possible indices for the third dimension
        all_indices = set(range(self.no_features))

        # Calculate which indices to keep
        indices_to_keep = sorted(list(all_indices - indices_to_remove))

        # Create new feature layers with removed indices
        new_feature_layers = [
            tensor[:, :, indices_to_keep] for tensor in self.feature_layer
        ]

        # Create a new DataLoader instance with modified feature layers
        # but keeping the same intensity layers
        return DataLoader(new_feature_layers, self.intensity_layer)
