"""
Utility functions for machine learning operations.

This module provides common helper functions used across different ML algorithms
including data splitting, evaluation metrics, and preprocessing utilities.
"""

import numpy as np
from typing import Tuple, Union, List
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def train_test_split(X: Union[np.ndarray, 'pd.DataFrame'], y: Union[np.ndarray, 'pd.Series'], 
                    test_size: float = 0.2, random_state: int = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Split arrays or DataFrames into random train and test subsets.
    
    Args:
        X (np.ndarray or pd.DataFrame): Feature matrix of shape (n_samples, n_features).
        y (np.ndarray or pd.Series): Target vector of shape (n_samples,).
        test_size (float, optional): Proportion of dataset to include in test split. 
            Defaults to 0.2.
        random_state (int, optional): Controls randomness of the split. Defaults to None.
    
    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: 
            X_train, X_test, y_train, y_test arrays.
    
    Examples:
        >>> X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
        >>> y = np.array([0, 1, 0, 1])
        >>> X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5)
        >>> print(X_train.shape, X_test.shape)
        (2, 2) (2, 2)
        
        # Works with pandas too:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'feature1': [1, 2, 3, 4], 'feature2': [5, 6, 7, 8]})
        >>> target = pd.Series([0, 1, 0, 1])
        >>> X_train, X_test, y_train, y_test = train_test_split(df, target, test_size=0.5)
    """
    # Convert to numpy arrays if needed
    X_conv, y_conv = validate_and_convert_data(X, y)
    
    if random_state is not None:
        np.random.seed(random_state)
    
    n_samples = len(X_conv)
    test_samples = int(n_samples * test_size)
    
    indices = np.random.permutation(n_samples)
    test_indices = indices[:test_samples]
    train_indices = indices[test_samples:]
    
    return X_conv[train_indices], X_conv[test_indices], y_conv[train_indices], y_conv[test_indices]


def accuracy_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate classification accuracy score.
    
    Args:
        y_true (np.ndarray): True target values.
        y_pred (np.ndarray): Predicted target values.
    
    Returns:
        float: Accuracy score between 0 and 1.
    
    Examples:
        >>> y_true = np.array([1, 0, 1, 1, 0])
        >>> y_pred = np.array([1, 0, 1, 0, 0])
        >>> accuracy_score(y_true, y_pred)
        0.8
    """
    return np.mean(y_true == y_pred)


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate R² (coefficient of determination) regression score.
    
    Args:
        y_true (np.ndarray): True target values.
        y_pred (np.ndarray): Predicted target values.
    
    Returns:
        float: R² score. Best possible score is 1.0.
    
    Examples:
        >>> y_true = np.array([3, -0.5, 2, 7])
        >>> y_pred = np.array([2.5, 0.0, 2, 8])
        >>> r2_score(y_true, y_pred)
        0.9486081370449679
    """
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot)


def mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate mean squared error regression loss.
    
    Args:
        y_true (np.ndarray): True target values.
        y_pred (np.ndarray): Predicted target values.
    
    Returns:
        float: Mean squared error.
    
    Examples:
        >>> y_true = np.array([3, -0.5, 2, 7])
        >>> y_pred = np.array([2.5, 0.0, 2, 8])
        >>> mean_squared_error(y_true, y_pred)
        0.375
    """
    return np.mean((y_true - y_pred) ** 2)


def euclidean_distance(x1: np.ndarray, x2: np.ndarray) -> float:
    """
    Calculate Euclidean distance between two points.
    
    Args:
        x1 (np.ndarray): First point.
        x2 (np.ndarray): Second point.
    
    Returns:
        float: Euclidean distance.
    
    Examples:
        >>> x1 = np.array([1, 2])
        >>> x2 = np.array([4, 6])
        >>> euclidean_distance(x1, x2)
        5.0
    """
    return np.sqrt(np.sum((x1 - x2) ** 2))


def normalize(X: np.ndarray) -> np.ndarray:
    """
    Normalize features to have zero mean and unit variance.
    
    Args:
        X (np.ndarray): Feature matrix of shape (n_samples, n_features).
    
    Returns:
        np.ndarray: Normalized feature matrix.
    
    Examples:
        >>> X = np.array([[1, 2], [3, 4], [5, 6]])
        >>> X_norm = normalize(X)
        >>> np.allclose(np.mean(X_norm, axis=0), 0)
        True
        >>> np.allclose(np.std(X_norm, axis=0), 1)
        True
    """
    return (X - np.mean(X, axis=0)) / np.std(X, axis=0)


def confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """
    Compute confusion matrix to evaluate classification accuracy.
    
    Args:
        y_true (np.ndarray): True target values.
        y_pred (np.ndarray): Predicted target values.
    
    Returns:
        np.ndarray: Confusion matrix of shape (n_classes, n_classes).
    
    Examples:
        >>> y_true = np.array([0, 1, 2, 0, 1, 2])
        >>> y_pred = np.array([0, 2, 1, 0, 0, 1])
        >>> confusion_matrix(y_true, y_pred)
        array([[2, 0, 0],
               [1, 0, 1],
               [0, 1, 1]])
    """
    labels = np.unique(np.concatenate([y_true, y_pred]))
    n_labels = len(labels)
    cm = np.zeros((n_labels, n_labels), dtype=int)
    
    for i, true_label in enumerate(labels):
        for j, pred_label in enumerate(labels):
            cm[i, j] = np.sum((y_true == true_label) & (y_pred == pred_label))
    
    return cm


def add_bias_column(X: np.ndarray) -> np.ndarray:
    """
    Add bias column (column of ones) to feature matrix.
    
    Args:
        X (np.ndarray): Feature matrix of shape (n_samples, n_features).
    
    Returns:
        np.ndarray: Feature matrix with bias column of shape (n_samples, n_features + 1).
    
    Examples:
        >>> X = np.array([[1, 2], [3, 4]])
        >>> add_bias_column(X)
        array([[1., 1., 2.],
               [1., 3., 4.]])
    """
    return np.column_stack([np.ones(X.shape[0]), X])


def _convert_to_numpy(data: Union[np.ndarray, 'pd.DataFrame', 'pd.Series']) -> np.ndarray:
    """
    Convert pandas DataFrame/Series or numpy array to numpy array.
    
    Args:
        data: Input data (pandas DataFrame/Series or numpy array).
    
    Returns:
        np.ndarray: Converted numpy array.
    
    Raises:
        ImportError: If pandas is not installed but pandas data is provided.
        ValueError: If data type is not supported.
    """
    if isinstance(data, np.ndarray):
        return data
    
    if HAS_PANDAS and isinstance(data, (pd.DataFrame, pd.Series)):
        return data.values
    
    # Check if it looks like pandas but pandas is not installed
    if hasattr(data, 'values') and hasattr(data, 'columns'):
        raise ImportError("pandas data detected but pandas is not installed. Please install pandas: pip install pandas")
    
    # Try to convert to numpy array
    try:
        return np.array(data)
    except Exception as e:
        raise ValueError(f"Could not convert data to numpy array: {e}")


def validate_and_convert_data(X: Union[np.ndarray, 'pd.DataFrame'], 
                             y: Union[np.ndarray, 'pd.Series'] = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Validate and convert input data to numpy arrays.
    
    Args:
        X: Feature data (pandas DataFrame or numpy array).
        y: Target data (pandas Series or numpy array), optional.
    
    Returns:
        Tuple[np.ndarray, np.ndarray]: Converted X and y as numpy arrays.
    
    Raises:
        ValueError: If X and y have incompatible shapes.
    """
    X_converted = _convert_to_numpy(X)
    
    # Ensure X is 2D
    if X_converted.ndim == 1:
        X_converted = X_converted.reshape(-1, 1)
    
    if y is not None:
        y_converted = _convert_to_numpy(y)
        
        # Ensure y is 1D
        if y_converted.ndim > 1:
            y_converted = y_converted.ravel()
        
        # Check shapes
        if X_converted.shape[0] != len(y_converted):
            raise ValueError(f"X and y must have the same number of samples. "
                           f"Got X: {X_converted.shape[0]}, y: {len(y_converted)}")
        
        return X_converted, y_converted
    
    return X_converted, None
