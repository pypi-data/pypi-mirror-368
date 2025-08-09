import numpy as np
from scipy import sparse


def train_test_split(
    *arrays,
    test_size=None,
    train_size=None,
    random_state=None,
    shuffle=True,
    stratify=None,
):
    """Splits arrays or matrices into random train and test subsets.

    Args:
        *arrays: (sequence of arrays) - Allowed inputs are lists, numpy arrays,
            scipy-sparse matrices, or pandas DataFrames.
        test_size: (float or int), optional - If float, should be between 0.0 and 1.0
            and represent the proportion of the dataset to include in the test split.
            If int, represents the absolute number of test samples (default is None).
        train_size: (float or int), optional - If float, should be between 0.0 and 1.0
            and represent the proportion of the dataset to include in the train split.
            If int, represents the absolute number of train samples. If None, the value
            is automatically computed as the complement of the test size (default is None).
        random_state: (int, RandomState instance, or None), optional - Controls the shuffling
            applied to the data before applying the split. Pass an int for reproducible output
            across multiple function calls (default is None).
        shuffle: (bool), optional - Whether or not to shuffle the data before splitting.
            If shuffle=False, then stratify must be None (default is True).
        stratify: (array-like), optional - If not None, data is split in a stratified fashion,
            using this as the class labels (default is None).

    Returns:
        splitting: (list) - A list containing the train-test split of inputs, with length
            equal to 2 * len(arrays).
    """
    # Initialize random number generator
    if random_state is not None:
        np.random.seed(random_state)

    # Input validation
    if len(arrays) == 0:
        raise ValueError("At least one array required as input")

    # Get number of samples
    first_array = arrays[0]
    if sparse.issparse(first_array) or hasattr(first_array, "shape"):
        n_samples = first_array.shape[0]
    else:
        n_samples = len(first_array)

    # Validate array lengths
    for array in arrays:
        if sparse.issparse(array) or hasattr(array, "shape"):
            if array.shape[0] != n_samples:
                raise ValueError("Arrays must have the same length")
        elif len(array) != n_samples:
            raise ValueError("Arrays must have the same length")

    # Handle stratification
    if stratify is not None:
        if not shuffle:
            raise ValueError(
                "Stratified train/test split is not implemented for shuffle=False"
            )

        stratify = np.asarray(stratify)
        if stratify.shape[0] != n_samples:
            raise ValueError("Stratify labels must have the same length as the arrays")

        classes, stratify_indices = np.unique(stratify, return_inverse=True)
        n_classes = len(classes)

        if n_classes < 2:
            raise ValueError(
                "Stratify labels array must have at least two unique values"
            )

    # Set default test_size if both test_size and train_size are None
    if test_size is None and train_size is None:
        test_size = 0.25

    # Calculate train and test sizes
    if train_size is None:
        if isinstance(test_size, float):
            if test_size < 0 or test_size > 1:
                raise ValueError("test_size must be between 0 and 1")
            n_test = int(np.ceil(test_size * n_samples))
        else:  # test_size is an integer
            if test_size < 0 or test_size > n_samples:
                raise ValueError(f"test_size must be between 0 and {n_samples}")
            n_test = test_size
        n_train = n_samples - n_test
    else:
        if isinstance(train_size, float):
            if train_size < 0 or train_size > 1:
                raise ValueError("train_size must be between 0 and 1")
            n_train = int(np.floor(train_size * n_samples))
        else:  # train_size is an integer
            if train_size < 0 or train_size > n_samples:
                raise ValueError(f"train_size must be between 0 and {n_samples}")
            n_train = train_size

        if test_size is None:
            n_test = n_samples - n_train
        else:
            if isinstance(test_size, float):
                n_test = int(np.ceil(test_size * n_samples))
            else:
                n_test = test_size

            if n_train + n_test > n_samples:
                raise ValueError(
                    "The sum of train_size and test_size cannot exceed the number of samples"
                )

    # Determine indices for the split
    if shuffle:
        if stratify is None:
            # Simple random shuffling
            indices = np.random.permutation(n_samples)
            train_indices = indices[:n_train]
            test_indices = indices[n_train : n_train + n_test]
        else:
            # Stratified shuffle splitting using proportional allocation
            train_indices = []
            test_indices = []
            unique_classes = np.unique(stratify)
            # Calculate per-class allocation for train set
            base_train_counts = {}
            remainders = {}
            class_counts = {}
            for cls in unique_classes:
                cls_idx = np.where(stratify == cls)[0]
                class_counts[cls] = len(cls_idx)
                desired = n_train * len(cls_idx) / n_samples
                base = int(np.floor(desired))
                base_train_counts[cls] = base
                remainders[cls] = desired - base

            sum_base = sum(base_train_counts.values())
            extra = n_train - sum_base
            extra_alloc = dict.fromkeys(unique_classes, 0)
            # Distribute extra samples based on remainders
            for cls in sorted(
                unique_classes, key=lambda x: remainders[x], reverse=True
            ):
                if extra <= 0:
                    break
                if base_train_counts[cls] + extra_alloc[cls] < class_counts[cls]:
                    extra_alloc[cls] += 1
                    extra -= 1

            # Now assign indices for each class
            for cls in unique_classes:
                cls_idx = np.where(stratify == cls)[0]
                np.random.shuffle(cls_idx)
                n_train_cls = base_train_counts[cls] + extra_alloc[cls]
                # Ensure at least one sample goes to the test set if possible
                if class_counts[cls] > 1 and (class_counts[cls] - n_train_cls) < 1:
                    n_train_cls = class_counts[cls] - 1
                _n_test_cls = class_counts[cls] - n_train_cls
                train_indices.extend(cls_idx[:n_train_cls])
                test_indices.extend(cls_idx[n_train_cls:])

            train_indices = np.array(train_indices)
            test_indices = np.array(test_indices)
            # If numbers don't match exactly due to rounding, adjust randomly
            if len(train_indices) != n_train:
                np.random.shuffle(train_indices)
                train_indices = train_indices[:n_train]
            if len(test_indices) != n_test:
                np.random.shuffle(test_indices)
                test_indices = test_indices[:n_test]
    else:
        indices = np.arange(n_samples)
        train_indices = indices[:n_train]
        test_indices = indices[n_train : n_train + n_test]

    # Split the arrays while preserving their type (especially for numpy arrays)
    result = []
    for array in arrays:
        if sparse.issparse(array):
            train = array[train_indices]
            test = array[test_indices]
        elif hasattr(array, "iloc"):  # pandas DataFrame or Series
            train = array.iloc[train_indices]
            test = array.iloc[test_indices]
        elif isinstance(
            array, np.ndarray
        ):  # handles 1D and multi-dimensional NumPy arrays
            train = array[train_indices]
            test = array[test_indices]
        else:  # list or other sequence
            train = [array[i] for i in train_indices]
            test = [array[i] for i in test_indices]

        result.append(train)
        result.append(test)

    return result


class PCA:
    """Principal Component Analysis (PCA) implementation."""

    def __init__(self, n_components):
        """Initializes the PCA model.

        Args:
            n_components: (int) - Number of principal components to keep.
        """
        self.n_components = n_components
        self.components = None
        self.mean_ = None

    def fit(self, X):
        """Fits the PCA model to the data.

        Args:
            X: (np.ndarray) - Input data of shape (n_samples, n_features).

        Raises:
            ValueError: If input data is not a 2D numpy array or if n_components exceeds the number of features.
        """
        if not isinstance(X, np.ndarray):
            raise ValueError("Input data must be a numpy array.")
        if X.ndim != 2:
            raise ValueError("Input data must be a 2D array.")
        if self.n_components > X.shape[1]:
            raise ValueError(
                "Number of components cannot be greater than the number of features."
            )

        # Mean centering
        self.mean_ = np.mean(X, axis=0)
        X = X - self.mean_

        # Covariance matrix
        cov = np.cov(X.T)

        # Eigenvalues and eigenvectors
        eigenvalues, eigenvectors = np.linalg.eig(cov)

        # Sort eigenvectors by eigenvalues in descending order
        eigenvectors = eigenvectors[:, np.argsort(eigenvalues)[::-1]]

        # Select the top n_components eigenvectors
        self.components_ = eigenvectors[:, : self.n_components]
        self.explained_variance_ratio_ = eigenvalues[: self.n_components] / np.sum(
            eigenvalues
        )

    def transform(self, X):
        """Applies dimensionality reduction on the input data.

        Args:
            X: (np.ndarray) - Input data of shape (n_samples, n_features).

        Returns:
            X_transformed: (np.ndarray) - Data transformed into the principal component space of shape (n_samples, n_components).

        Raises:
            ValueError: If input data is not a 2D numpy array or if its dimensions do not match the fitted data.
        """
        if not isinstance(X, np.ndarray):
            raise ValueError("Input data must be a numpy array.")
        if X.ndim != 2:
            raise ValueError("Input data must be a 2D array.")
        if X.shape[1] != self.mean_.shape[0]:
            raise ValueError(
                "Input data must have the same number of features as the data used to fit the model."
            )

        # Project data to the principal component space
        X = X - self.mean_
        return np.dot(X, self.components_)

    def fit_transform(self, X):
        """Fits the PCA model and applies dimensionality reduction on the input data.

        Args:
            X: (np.ndarray) - Input data of shape (n_samples, n_features).

        Returns:
            X_transformed: (np.ndarray) - Data transformed into the principal component space of shape (n_samples, n_components).
        """
        self.fit(X)
        return self.transform(X)

    def get_explained_variance_ratio(self):
        """Retrieves the explained variance ratio.

        Returns:
            explained_variance_ratio_: (np.ndarray) - Array of explained variance ratios for each principal component.
        """
        return self.explained_variance_ratio_

    def get_components(self):
        """Retrieves the principal components.

        Returns:
            components_: (np.ndarray) - Array of principal components of shape (n_features, n_components).
        """
        return self.components_

    def inverse_transform(self, X_reduced):
        """Reconstructs the original data from the reduced data.

        Args:
            X_reduced: (np.ndarray) - Reduced data of shape (n_samples, n_components).

        Returns:
            X_original: (np.ndarray) - Reconstructed data of shape (n_samples, n_features).

        Raises:
            ValueError: If input data is not a 2D numpy array.
        """
        if not isinstance(X_reduced, np.ndarray):
            raise ValueError("Input data must be a numpy array.")
        if X_reduced.ndim != 2:
            raise ValueError("Input data must be a 2D array.")
        return np.dot(X_reduced, self.components_.T) + self.mean_
