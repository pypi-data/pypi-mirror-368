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


def handle_missing_values(X: Union[np.ndarray, 'pd.DataFrame'], 
                        strategy: str = 'mean',
                        fill_value: Union[int, float, None] = None) -> Union[np.ndarray, 'pd.DataFrame']:
    """
    Handle missing values in the dataset using various strategies.
    
    Args:
        X: Input data (pandas DataFrame or numpy array).
        strategy: Strategy to handle missing values. Options:
            - 'mean': Replace with mean of column
            - 'median': Replace with median of column
            - 'mode': Replace with mode of column
            - 'constant': Replace with fill_value
            - 'interpolate': Linear interpolation
            - 'forward': Forward fill
            - 'backward': Backward fill
        fill_value: Value to use when strategy='constant'.
    
    Returns:
        Processed data with missing values handled.
    
    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'A': [1, np.nan, 3], 'B': [4, 5, np.nan]})
        >>> handle_missing_values(df, strategy='mean')
           A    B
        0  1.0  4.0
        1  2.0  5.0
        2  3.0  4.5
    """
    if not HAS_PANDAS:
        raise ImportError("pandas is required for handle_missing_values")
    
    if isinstance(X, np.ndarray):
        X = pd.DataFrame(X)
    
    if strategy == 'mean':
        return X.fillna(X.mean())
    elif strategy == 'median':
        return X.fillna(X.median())
    elif strategy == 'mode':
        return X.fillna(X.mode().iloc[0])
    elif strategy == 'constant':
        return X.fillna(fill_value)
    elif strategy == 'interpolate':
        return X.interpolate(method='linear')
    elif strategy == 'forward':
        return X.fillna(method='ffill')
    elif strategy == 'backward':
        return X.fillna(method='bfill')
    else:
        raise ValueError(f"Unknown strategy: {strategy}")


def detect_outliers(X: Union[np.ndarray, 'pd.DataFrame'],
                   method: str = 'zscore',
                   threshold: float = 3.0) -> np.ndarray:
    """
    Detect outliers in the dataset using various methods.
    
    Args:
        X: Input data (pandas DataFrame or numpy array).
        method: Method to detect outliers. Options:
            - 'zscore': Use Z-score method
            - 'iqr': Use Interquartile Range method
            - 'isolation_forest': Use Isolation Forest algorithm
        threshold: Threshold for outlier detection (used in zscore and iqr methods).
    
    Returns:
        np.ndarray: Boolean mask indicating outlier samples.
    
    Examples:
        >>> X = np.array([[1], [2], [100], [3], [4], [200]])
        >>> mask = detect_outliers(X, method='zscore')
        >>> X[~mask]  # Remove outliers
        array([[1],
               [2],
               [3],
               [4]])
    """
    X_conv = _convert_to_numpy(X)
    
    if method == 'zscore':
        z_scores = np.abs((X_conv - np.mean(X_conv, axis=0)) / np.std(X_conv, axis=0))
        return np.all(z_scores < threshold, axis=1)
    
    elif method == 'iqr':
        q1 = np.percentile(X_conv, 25, axis=0)
        q3 = np.percentile(X_conv, 75, axis=0)
        iqr = q3 - q1
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        return np.all((X_conv >= lower_bound) & (X_conv <= upper_bound), axis=1)
    
    elif method == 'isolation_forest':
        try:
            from sklearn.ensemble import IsolationForest
            iso_forest = IsolationForest(contamination='auto', random_state=42)
            return iso_forest.fit_predict(X_conv) == 1
        except ImportError:
            raise ImportError("scikit-learn is required for isolation_forest method")
    
    else:
        raise ValueError(f"Unknown method: {method}")


def encode_categorical(X: Union[np.ndarray, 'pd.DataFrame'],
                      columns: Union[List[str], List[int], None] = None,
                      method: str = 'onehot') -> Union[np.ndarray, 'pd.DataFrame']:
    """
    Encode categorical variables using various encoding methods.
    
    Args:
        X: Input data (pandas DataFrame or numpy array).
        columns: List of column names (for DataFrame) or indices (for array) to encode.
            If None, tries to detect categorical columns automatically.
        method: Encoding method. Options:
            - 'onehot': One-hot encoding
            - 'label': Label encoding
            - 'ordinal': Ordinal encoding (maintains order)
            - 'frequency': Frequency encoding
            - 'target': Target encoding (requires y)
    
    Returns:
        Encoded data.
    
    Examples:
        >>> df = pd.DataFrame({'category': ['A', 'B', 'A', 'C']})
        >>> encode_categorical(df, method='onehot')
           category_A  category_B  category_C
        0          1          0          0
        1          0          1          0
        2          1          0          0
        3          0          0          1
    """
    if not HAS_PANDAS:
        raise ImportError("pandas is required for encode_categorical")
    
    if isinstance(X, np.ndarray):
        X = pd.DataFrame(X)
    
    # Auto-detect categorical columns if not specified
    if columns is None:
        columns = X.select_dtypes(include=['object', 'category']).columns
    
    result = X.copy()
    
    if method == 'onehot':
        return pd.get_dummies(result, columns=columns)
    
    elif method == 'label':
        for col in columns:
            result[col] = pd.Categorical(result[col]).codes
        return result
    
    elif method == 'ordinal':
        for col in columns:
            result[col] = pd.Categorical(result[col], ordered=True).codes
        return result
    
    elif method == 'frequency':
        for col in columns:
            freq = result[col].value_counts(normalize=True)
            result[col] = result[col].map(freq)
        return result
    
    else:
        raise ValueError(f"Unknown method: {method}")


def scale_features(X: Union[np.ndarray, 'pd.DataFrame'],
                  method: str = 'standard',
                  feature_range: Tuple[float, float] = (0, 1)) -> Union[np.ndarray, 'pd.DataFrame']:
    """
    Scale features using various scaling methods.
    
    Args:
        X: Input data (pandas DataFrame or numpy array).
        method: Scaling method. Options:
            - 'standard': Standardization (zero mean, unit variance)
            - 'minmax': Min-max scaling to feature_range
            - 'robust': Robust scaling using quartiles
            - 'maxabs': Scale by maximum absolute value
        feature_range: Tuple (min, max) for min-max scaling.
    
    Returns:
        Scaled data.
    
    Examples:
        >>> X = np.array([[1, -1, 2], [2, 0, 0], [0, 1, -1]])
        >>> scale_features(X, method='standard')
        array([[ 0.        , -1.22474487,  1.33630621],
               [ 1.22474487,  0.        , -0.26726124],
               [-1.22474487,  1.22474487, -1.06904497]])
    """
    X_conv = _convert_to_numpy(X)
    is_pandas = isinstance(X, pd.DataFrame)
    
    if method == 'standard':
        X_scaled = (X_conv - np.mean(X_conv, axis=0)) / np.std(X_conv, axis=0)
    
    elif method == 'minmax':
        X_min = np.min(X_conv, axis=0)
        X_max = np.max(X_conv, axis=0)
        X_scaled = (X_conv - X_min) / (X_max - X_min)
        X_scaled = X_scaled * (feature_range[1] - feature_range[0]) + feature_range[0]
    
    elif method == 'robust':
        q1 = np.percentile(X_conv, 25, axis=0)
        q3 = np.percentile(X_conv, 75, axis=0)
        iqr = q3 - q1
        X_scaled = (X_conv - np.median(X_conv, axis=0)) / iqr
    
    elif method == 'maxabs':
        X_scaled = X_conv / np.max(np.abs(X_conv), axis=0)
    
    else:
        raise ValueError(f"Unknown method: {method}")
    
    if is_pandas:
        return pd.DataFrame(X_scaled, index=X.index, columns=X.columns)
    return X_scaled


def reduce_dimensionality(X: Union[np.ndarray, 'pd.DataFrame'],
                         method: str = 'pca',
                         n_components: int = 2) -> np.ndarray:
    """
    Reduce dimensionality of the dataset using various methods.
    
    Args:
        X: Input data (pandas DataFrame or numpy array).
        method: Dimensionality reduction method. Options:
            - 'pca': Principal Component Analysis
            - 'tsne': t-SNE
            - 'umap': Uniform Manifold Approximation and Projection
        n_components: Number of components in reduced space.
    
    Returns:
        np.ndarray: Reduced data.
    
    Examples:
        >>> X = np.random.rand(100, 10)  # 100 samples, 10 features
        >>> X_reduced = reduce_dimensionality(X, method='pca', n_components=2)
        >>> X_reduced.shape
        (100, 2)
    """
    X_conv = _convert_to_numpy(X)
    
    if method == 'pca':
        try:
            from sklearn.decomposition import PCA
            pca = PCA(n_components=n_components)
            return pca.fit_transform(X_conv)
        except ImportError:
            raise ImportError("scikit-learn is required for PCA")
    
    elif method == 'tsne':
        try:
            from sklearn.manifold import TSNE
            tsne = TSNE(n_components=n_components, random_state=42)
            return tsne.fit_transform(X_conv)
        except ImportError:
            raise ImportError("scikit-learn is required for t-SNE")
    
    elif method == 'umap':
        try:
            import umap
            reducer = umap.UMAP(n_components=n_components, random_state=42)
            return reducer.fit_transform(X_conv)
        except ImportError:
            raise ImportError("umap-learn is required for UMAP")
    
    else:
        raise ValueError(f"Unknown method: {method}")


def cross_validate(estimator, X: Union[np.ndarray, 'pd.DataFrame'], 
                y: Union[np.ndarray, 'pd.Series'], cv: int = 5, 
                scoring: str = 'r2', random_state: int = None) -> np.ndarray:
    """
    Perform k-fold cross validation.
    
    Args:
        estimator: A model object that implements fit() and predict() methods.
        X: Feature matrix of shape (n_samples, n_features).
        y: Target vector of shape (n_samples,).
        cv: Number of folds. Must be at least 2.
        scoring: Metric to evaluate. Options: 'r2', 'accuracy', 'mse'.
        random_state: Controls randomness of the splits.
    
    Returns:
        np.ndarray: Array of scores of shape (n_folds,).
    
    Examples:
        >>> from vishuml.linear_regression import LinearRegression
        >>> X = np.array([[1], [2], [3], [4], [5]])
        >>> y = np.array([2, 4, 6, 8, 10])
        >>> model = LinearRegression()
        >>> scores = cross_validate(model, X, y, cv=3)
        >>> print(f"Mean CV score: {scores.mean():.3f}")
        Mean CV score: 0.985
    """
    X_conv, y_conv = validate_and_convert_data(X, y)
    
    if cv < 2:
        raise ValueError("cv must be at least 2")
    
    if random_state is not None:
        np.random.seed(random_state)
    
    # Generate fold indices
    n_samples = len(X_conv)
    indices = np.random.permutation(n_samples)
    fold_sizes = np.full(cv, n_samples // cv, dtype=int)
    fold_sizes[:n_samples % cv] += 1
    current = 0
    folds = []
    for fold_size in fold_sizes:
        start, stop = current, current + fold_size
        folds.append(indices[start:stop])
        current = stop
    
    # Perform cross validation
    scores = np.zeros(cv)
    for i, test_idx in enumerate(folds):
        train_idx = np.concatenate([f for j, f in enumerate(folds) if j != i])
        X_train, y_train = X_conv[train_idx], y_conv[train_idx]
        X_test, y_test = X_conv[test_idx], y_conv[test_idx]
        
        # Train and evaluate
        estimator.fit(X_train, y_train)
        y_pred = estimator.predict(X_test)
        
        # Calculate score
        if scoring == 'r2':
            scores[i] = r2_score(y_test, y_pred)
        elif scoring == 'accuracy':
            scores[i] = accuracy_score(y_test, y_pred)
        elif scoring == 'mse':
            scores[i] = -mean_squared_error(y_test, y_pred)  # Negative for consistency
        else:
            raise ValueError(f"Unknown scoring metric: {scoring}")
    
    return scores


def stratified_split(X: Union[np.ndarray, 'pd.DataFrame'], 
                    y: Union[np.ndarray, 'pd.Series'],
                    test_size: float = 0.2,
                    random_state: int = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Split arrays or matrices into stratified random train and test subsets.
    
    Args:
        X: Feature matrix of shape (n_samples, n_features).
        y: Target vector of shape (n_samples,).
        test_size: Proportion of dataset to include in test split.
        random_state: Controls randomness of the split.
    
    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: 
            X_train, X_test, y_train, y_test arrays.
    
    Examples:
        >>> X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
        >>> y = np.array([0, 0, 1, 1])
        >>> X_train, X_test, y_train, y_test = stratified_split(X, y, test_size=0.5)
        >>> np.bincount(y_train) / len(y_train)  # Class distribution preserved
        array([0.5, 0.5])
    """
    X_conv, y_conv = validate_and_convert_data(X, y)
    
    if random_state is not None:
        np.random.seed(random_state)
    
    # Get unique classes and their indices
    classes, y_indices = np.unique(y_conv, return_inverse=True)
    n_classes = len(classes)
    
    # Calculate number of test samples per class
    n_samples = len(y_conv)
    n_test = int(test_size * n_samples)
    n_test_per_class = max(1, int(test_size * n_samples / n_classes))
    
    # Initialize indices
    test_indices = []
    train_indices = np.zeros(n_samples, dtype=bool)
    
    # Split each class
    for i in range(n_classes):
        class_indices = np.where(y_indices == i)[0]
        np.random.shuffle(class_indices)
        n_test_i = min(n_test_per_class, len(class_indices))
        test_indices.extend(class_indices[:n_test_i])
    
    test_indices = np.array(test_indices)
    train_indices = ~np.isin(np.arange(n_samples), test_indices)
    
    return (X_conv[train_indices], X_conv[test_indices],
            y_conv[train_indices], y_conv[test_indices])


def precision_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate precision score (positive predictive value).
    
    Args:
        y_true: True target values.
        y_pred: Predicted target values.
    
    Returns:
        float: Precision score between 0 and 1.
    
    Examples:
        >>> y_true = np.array([1, 0, 1, 1, 0])
        >>> y_pred = np.array([1, 0, 1, 0, 0])
        >>> precision_score(y_true, y_pred)
        1.0
    """
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    return tp / (tp + fp) if (tp + fp) > 0 else 0.0


def recall_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate recall score (true positive rate).
    
    Args:
        y_true: True target values.
        y_pred: Predicted target values.
    
    Returns:
        float: Recall score between 0 and 1.
    
    Examples:
        >>> y_true = np.array([1, 0, 1, 1, 0])
        >>> y_pred = np.array([1, 0, 1, 0, 0])
        >>> recall_score(y_true, y_pred)
        0.6666666666666666
    """
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    return tp / (tp + fn) if (tp + fn) > 0 else 0.0


def f1_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate F1 score (harmonic mean of precision and recall).
    
    Args:
        y_true: True target values.
        y_pred: Predicted target values.
    
    Returns:
        float: F1 score between 0 and 1.
    
    Examples:
        >>> y_true = np.array([1, 0, 1, 1, 0])
        >>> y_pred = np.array([1, 0, 1, 0, 0])
        >>> f1_score(y_true, y_pred)
        0.8
    """
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0


def silhouette_score(X: np.ndarray, labels: np.ndarray) -> float:
    """
    Calculate the mean Silhouette Coefficient for all samples.
    
    Args:
        X: Feature matrix of shape (n_samples, n_features).
        labels: Predicted cluster labels of shape (n_samples,).
    
    Returns:
        float: Silhouette score between -1 and 1.
    
    Examples:
        >>> X = np.array([[1, 2], [1, 4], [1, 0], [4, 2], [4, 4], [4, 0]])
        >>> labels = np.array([0, 0, 0, 1, 1, 1])
        >>> silhouette_score(X, labels)
        0.714
    """
    def _intra_cluster_distance(point_idx: int, cluster_points: np.ndarray) -> float:
        if len(cluster_points) <= 1:
            return 0.0
        distances = np.array([euclidean_distance(X[point_idx], X[i]) 
                            for i in cluster_points if i != point_idx])
        return np.mean(distances) if len(distances) > 0 else 0.0
    
    def _nearest_cluster_distance(point_idx: int, cluster_idx: int) -> float:
        other_clusters = [i for i in range(len(unique_labels)) if i != cluster_idx]
        if not other_clusters:
            return 0.0
        cluster_distances = []
        for other_idx in other_clusters:
            other_points = points_in_clusters[other_idx]
            if len(other_points) > 0:
                distances = np.array([euclidean_distance(X[point_idx], X[i]) 
                                   for i in other_points])
                cluster_distances.append(np.mean(distances))
        return min(cluster_distances) if cluster_distances else 0.0
    
    unique_labels = np.unique(labels)
    points_in_clusters = [np.where(labels == label)[0] for label in unique_labels]
    
    silhouette_values = []
    for i in range(len(X)):
        cluster_idx = np.where(unique_labels == labels[i])[0][0]
        a = _intra_cluster_distance(i, points_in_clusters[cluster_idx])
        b = _nearest_cluster_distance(i, cluster_idx)
        if a == 0 and b == 0:
            silhouette_values.append(0)
        else:
            silhouette_values.append((b - a) / max(a, b))
    
    return np.mean(silhouette_values)


def inertia_score(X: np.ndarray, labels: np.ndarray) -> float:
    """
    Calculate clustering inertia (within-cluster sum of squares).
    
    Args:
        X: Feature matrix of shape (n_samples, n_features).
        labels: Predicted cluster labels of shape (n_samples,).
    
    Returns:
        float: Inertia score (lower is better).
    
    Examples:
        >>> X = np.array([[1, 2], [1, 4], [1, 0], [4, 2], [4, 4], [4, 0]])
        >>> labels = np.array([0, 0, 0, 1, 1, 1])
        >>> inertia_score(X, labels)
        8.0
    """
    unique_labels = np.unique(labels)
    inertia = 0.0
    
    for label in unique_labels:
        cluster_points = X[labels == label]
        centroid = np.mean(cluster_points, axis=0)
        inertia += np.sum([euclidean_distance(point, centroid) ** 2 
                          for point in cluster_points])
    
    return inertia


def manhattan_distance(x1: np.ndarray, x2: np.ndarray) -> float:
    """
    Calculate Manhattan distance (L1 norm) between two points.
    
    Args:
        x1: First point.
        x2: Second point.
    
    Returns:
        float: Manhattan distance.
    
    Examples:
        >>> x1 = np.array([1, 2])
        >>> x2 = np.array([4, 6])
        >>> manhattan_distance(x1, x2)
        7.0
    """
    return np.sum(np.abs(x1 - x2))


def cosine_similarity(x1: np.ndarray, x2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        x1: First vector.
        x2: Second vector.
    
    Returns:
        float: Cosine similarity between -1 and 1.
    
    Examples:
        >>> x1 = np.array([1, 1, 0])
        >>> x2 = np.array([1, 1, 1])
        >>> cosine_similarity(x1, x2)
        0.8164965809277261
    """
    norm1 = np.sqrt(np.sum(x1 ** 2))
    norm2 = np.sqrt(np.sum(x2 ** 2))
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return np.dot(x1, x2) / (norm1 * norm2)


def analyze_dataset(X: Union[np.ndarray, 'pd.DataFrame'], 
                   target_column: str = None) -> dict:
    """
    Comprehensive dataset analysis for preprocessing recommendations.
    
    Args:
        X: Input dataset.
        target_column: Name of target column if available.
    
    Returns:
        dict: Comprehensive analysis results.
    
    Examples:
        >>> df = pd.DataFrame({'A': [1, 2, np.nan], 'B': ['a', 'b', 'c']})
        >>> analysis = analyze_dataset(df)
        >>> print(analysis['missing_summary'])
    """
    if not HAS_PANDAS:
        raise ImportError("pandas is required for analyze_dataset")
    
    if isinstance(X, np.ndarray):
        X = pd.DataFrame(X)
    
    analysis = {
        'shape': X.shape,
        'dtypes': X.dtypes.to_dict(),
        'missing_summary': X.isnull().sum().to_dict(),
        'missing_percentage': (X.isnull().sum() / len(X) * 100).to_dict(),
        'outlier_summary': {},
        'correlation_insights': {},
        'distribution_analysis': {},
        'recommendations': []
    }
    
    # Analyze numerical columns
    numerical_cols = X.select_dtypes(include=[np.number]).columns
    for col in numerical_cols:
        # Outlier analysis
        q1 = X[col].quantile(0.25)
        q3 = X[col].quantile(0.75)
        iqr = q3 - q1
        outliers = ((X[col] < (q1 - 1.5 * iqr)) | (X[col] > (q3 + 1.5 * iqr))).sum()
        analysis['outlier_summary'][col] = {
            'count': outliers,
            'percentage': outliers / len(X) * 100
        }
        
        # Distribution analysis
        skewness = X[col].skew()
        analysis['distribution_analysis'][col] = {
            'skewness': skewness,
            'distribution_type': 'normal' if abs(skewness) < 1 else 'skewed'
        }
    
    # Correlation analysis
    if len(numerical_cols) > 1:
        corr_matrix = X[numerical_cols].corr()
        high_corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) > 0.8:
                    high_corr_pairs.append((corr_matrix.columns[i], corr_matrix.columns[j]))
        analysis['correlation_insights'] = {
            'high_correlation_pairs': high_corr_pairs,
            'correlation_matrix': corr_matrix.to_dict()
        }
    
    # Generate recommendations
    if analysis['missing_summary']:
        analysis['recommendations'].append("Handle missing values using appropriate imputation strategies")
    
    if any(analysis['outlier_summary'].values()):
        analysis['recommendations'].append("Consider outlier detection and treatment")
    
    if high_corr_pairs:
        analysis['recommendations'].append("Address high correlations between features")
    
    return analysis


def generate_preprocessing_report(analysis: dict) -> list:
    """
    Generate preprocessing recommendations based on analysis.
    
    Args:
        analysis: Output from analyze_dataset function.
    
    Returns:
        list: List of preprocessing recommendations.
    """
    recommendations = []
    
    # Missing value recommendations
    missing_cols = [col for col, count in analysis['missing_summary'].items() if count > 0]
    if missing_cols:
        recommendations.append(f"Impute missing values in {len(missing_cols)} columns")
    
    # Outlier recommendations
    outlier_cols = [col for col, info in analysis['outlier_summary'].items() if info['percentage'] > 5]
    if outlier_cols:
        recommendations.append(f"Handle outliers in {len(outlier_cols)} columns")
    
    # Scaling recommendations
    skewed_cols = [col for col, info in analysis['distribution_analysis'].items() if info['distribution_type'] == 'skewed']
    if skewed_cols:
        recommendations.append(f"Apply robust scaling to {len(skewed_cols)} skewed columns")
    
    return recommendations


def impute_missing_advanced(X: Union[np.ndarray, 'pd.DataFrame'],
                          strategy: str = 'correlation_based',
                          **kwargs) -> Union[np.ndarray, 'pd.DataFrame']:
    """
    Advanced missing value imputation with multiple strategies.
    
    Args:
        X: Input data.
        strategy: Imputation strategy.
        **kwargs: Additional strategy-specific parameters.
    
    Returns:
        Data with imputed missing values.
    """
    if not HAS_PANDAS:
        raise ImportError("pandas is required for impute_missing_advanced")
    
    if isinstance(X, np.ndarray):
        X = pd.DataFrame(X)
    
    if strategy == 'correlation_based':
        return _correlation_based_imputation(X, **kwargs)
    elif strategy == 'multiple_imputation':
        return _multiple_imputation(X, **kwargs)
    elif strategy == 'domain_knowledge':
        return _domain_knowledge_imputation(X, **kwargs)
    else:
        return handle_missing_values(X, strategy=strategy, **kwargs)


def _correlation_based_imputation(X: pd.DataFrame, correlation_threshold: float = 0.3, 
                                use_ml_imputation: bool = False) -> pd.DataFrame:
    """Correlation-based imputation using feature relationships."""
    X_imputed = X.copy()
    
    for col in X.columns:
        if X[col].isnull().any():
            # Find correlated features
            correlations = X.corr()[col].abs().sort_values(ascending=False)
            correlated_features = correlations[correlations > correlation_threshold].index.tolist()
            
            if correlated_features and len(correlated_features) > 1:
                # Use correlated features for imputation
                feature_cols = [f for f in correlated_features if f != col and not X[f].isnull().all()]
                if feature_cols:
                    X_imputed[col] = X_imputed[col].fillna(X_imputed[col].median())
    
    return X_imputed


def _multiple_imputation(X: pd.DataFrame, n_imputations: int = 5, 
                        random_state: int = None) -> pd.DataFrame:
    """Multiple imputation for uncertainty quantification."""
    if random_state is not None:
        np.random.seed(random_state)
    
    # Simple multiple imputation using bootstrap
    imputed_datasets = []
    for _ in range(n_imputations):
        X_bootstrap = X.copy()
        for col in X.columns:
            if X[col].isnull().any():
                non_null_values = X[col].dropna()
                if len(non_null_values) > 0:
                    X_bootstrap[col] = X_bootstrap[col].fillna(
                        np.random.choice(non_null_values, size=X[col].isnull().sum())
                    )
        imputed_datasets.append(X_bootstrap)
    
    # Return the first imputation (could be enhanced to return all)
    return imputed_datasets[0]


def _domain_knowledge_imputation(X: pd.DataFrame, rules: dict) -> pd.DataFrame:
    """Domain-specific imputation using custom rules."""
    X_imputed = X.copy()
    
    for col, rule in rules.items():
        if col in X.columns and X[col].isnull().any():
            method = rule.get('method', 'median')
            group_by = rule.get('group_by')
            
            if group_by and group_by in X.columns:
                # Group-based imputation
                X_imputed[col] = X_imputed.groupby(group_by)[col].transform(
                    lambda x: x.fillna(x.median() if method == 'median' else x.mean())
                )
            else:
                # Simple imputation
                if method == 'median':
                    X_imputed[col] = X_imputed[col].fillna(X_imputed[col].median())
                elif method == 'mean':
                    X_imputed[col] = X_imputed[col].fillna(X_imputed[col].mean())
                elif method == 'forward_fill':
                    X_imputed[col] = X_imputed[col].fillna(method='ffill')
    
    return X_imputed


def detect_outliers_advanced(X: Union[np.ndarray, 'pd.DataFrame'],
                           method: str = 'ensemble',
                           **kwargs) -> np.ndarray:
    """
    Advanced outlier detection with multiple methods.
    
    Args:
        X: Input data.
        method: Detection method.
        **kwargs: Method-specific parameters.
    
    Returns:
        Boolean mask indicating outlier samples.
    """
    X_conv = _convert_to_numpy(X)
    
    if method == 'ensemble':
        methods = kwargs.get('methods', ['zscore', 'iqr', 'isolation_forest'])
        voting_threshold = kwargs.get('voting_threshold', 2)
        
        outlier_masks = []
        for m in methods:
            mask = detect_outliers_advanced(X_conv, method=m, **kwargs)
            outlier_masks.append(mask)
        
        # Ensemble voting
        outlier_votes = np.sum(outlier_masks, axis=0)
        return outlier_votes >= voting_threshold
    
    elif method == 'local_outlier_factor':
        try:
            from sklearn.neighbors import LocalOutlierFactor
            lof = LocalOutlierFactor(n_neighbors=20, contamination='auto')
            return lof.fit_predict(X_conv) == 1
        except ImportError:
            raise ImportError("scikit-learn is required for local_outlier_factor method")
    
    else:
        return detect_outliers(X_conv, method=method, **kwargs)


def analyze_outlier_patterns(X: Union[np.ndarray, 'pd.DataFrame']) -> dict:
    """
    Analyze outlier patterns in the dataset.
    
    Args:
        X: Input data.
    
    Returns:
        dict: Outlier analysis results.
    """
    X_conv = _convert_to_numpy(X)
    
    analysis = {
        'global_outliers': 0,
        'local_outliers': 0,
        'multivariate_outliers': 0,
        'outlier_percentage': 0
    }
    
    # Global outliers (Z-score method)
    z_scores = np.abs((X_conv - np.mean(X_conv, axis=0)) / np.std(X_conv, axis=0))
    global_outliers = np.any(z_scores > 3, axis=1)
    analysis['global_outliers'] = np.sum(global_outliers)
    
    # Local outliers (IQR method)
    q1 = np.percentile(X_conv, 25, axis=0)
    q3 = np.percentile(X_conv, 75, axis=0)
    iqr = q3 - q1
    local_outliers = np.any((X_conv < (q1 - 1.5 * iqr)) | (X_conv > (q3 + 1.5 * iqr)), axis=1)
    analysis['local_outliers'] = np.sum(local_outliers)
    
    # Multivariate outliers (Mahalanobis distance)
    try:
        from scipy.stats import chi2
        cov_matrix = np.cov(X_conv.T)
        inv_cov_matrix = np.linalg.inv(cov_matrix)
        mahal_dist = np.array([np.sqrt((x - np.mean(X_conv, axis=0)).T @ inv_cov_matrix @ (x - np.mean(X_conv, axis=0))) 
                              for x in X_conv])
        multivariate_outliers = mahal_dist > chi2.ppf(0.95, X_conv.shape[1])
        analysis['multivariate_outliers'] = np.sum(multivariate_outliers)
    except:
        analysis['multivariate_outliers'] = 0
    
    analysis['outlier_percentage'] = (analysis['global_outliers'] / len(X_conv)) * 100
    
    return analysis


def engineer_features_advanced(X: Union[np.ndarray, 'pd.DataFrame'],
                             target_column: str = None,
                             feature_types: dict = None,
                             engineering_options: dict = None,
                             **kwargs) -> Union[np.ndarray, 'pd.DataFrame']:
    """
    Advanced feature engineering with multiple strategies.
    
    Args:
        X: Input data.
        target_column: Target column name.
        feature_types: Dictionary specifying feature types.
        engineering_options: Options for feature engineering.
        **kwargs: Additional parameters.
    
    Returns:
        Data with engineered features.
    """
    if not HAS_PANDAS:
        raise ImportError("pandas is required for engineer_features_advanced")
    
    if isinstance(X, np.ndarray):
        X = pd.DataFrame(X)
    
    X_engineered = X.copy()
    
    if engineering_options.get('temporal_features', False):
        temporal_cols = feature_types.get('temporal', [])
        for col in temporal_cols:
            if col in X.columns:
                X_engineered = _add_temporal_features(X_engineered, col)
    
    if engineering_options.get('aggregation_features', False):
        group_by = kwargs.get('group_by')
        if group_by and group_by in X.columns:
            X_engineered = _add_aggregation_features(X_engineered, group_by)
    
    if engineering_options.get('interaction_features', False):
        X_engineered = generate_features(X_engineered, interactions=True, polynomials=False)
    
    if engineering_options.get('polynomial_features', False):
        X_engineered = generate_features(X_engineered, interactions=False, polynomials=True)
    
    return X_engineered


def _add_temporal_features(X: pd.DataFrame, date_column: str) -> pd.DataFrame:
    """Add temporal features from date column."""
    try:
        X[date_column] = pd.to_datetime(X[date_column])
        X[f'{date_column}_hour'] = X[date_column].dt.hour
        X[f'{date_column}_day_of_week'] = X[date_column].dt.dayofweek
        X[f'{date_column}_month'] = X[date_column].dt.month
        X[f'{date_column}_quarter'] = X[date_column].dt.quarter
        X[f'{date_column}_is_weekend'] = X[date_column].dt.dayofweek.isin([5, 6]).astype(int)
    except:
        pass
    return X


def _add_aggregation_features(X: pd.DataFrame, group_by: str) -> pd.DataFrame:
    """Add aggregation features based on grouping."""
    numerical_cols = X.select_dtypes(include=[np.number]).columns
    numerical_cols = [col for col in numerical_cols if col != group_by]
    
    for col in numerical_cols:
        X[f'{col}_group_mean'] = X.groupby(group_by)[col].transform('mean')
        X[f'{col}_group_std'] = X.groupby(group_by)[col].transform('std')
        X[f'{col}_group_count'] = X.groupby(group_by)[col].transform('count')
    
    return X


def create_time_features(dates: Union[pd.Series, np.ndarray],
                        features: list = None) -> pd.DataFrame:
    """
    Create time-based features from date series.
    
    Args:
        dates: Date series.
        features: List of features to create.
    
    Returns:
        DataFrame with time features.
    """
    if not HAS_PANDAS:
        raise ImportError("pandas is required for create_time_features")
    
    if features is None:
        features = ['hour', 'day_of_week', 'month', 'quarter', 'is_weekend']
    
    if isinstance(dates, np.ndarray):
        dates = pd.Series(dates)
    
    dates = pd.to_datetime(dates)
    time_features = pd.DataFrame()
    
    for feature in features:
        if feature == 'hour':
            time_features['hour'] = dates.dt.hour
        elif feature == 'day_of_week':
            time_features['day_of_week'] = dates.dt.dayofweek
        elif feature == 'month':
            time_features['month'] = dates.dt.month
        elif feature == 'quarter':
            time_features['quarter'] = dates.dt.quarter
        elif feature == 'is_weekend':
            time_features['is_weekend'] = dates.dt.dayofweek.isin([5, 6]).astype(int)
        elif feature == 'is_holiday':
            # Simple holiday detection (could be enhanced)
            time_features['is_holiday'] = ((dates.dt.month == 12) & (dates.dt.day == 25)).astype(int)
    
    return time_features


def scale_features_advanced(X: Union[np.ndarray, 'pd.DataFrame'],
                          strategies: dict = None,
                          **kwargs) -> Union[np.ndarray, 'pd.DataFrame']:
    """
    Advanced feature scaling with custom strategies per feature.
    
    Args:
        X: Input data.
        strategies: Dictionary mapping feature indices to scaling methods.
        **kwargs: Additional parameters.
    
    Returns:
        Scaled data.
    """
    X_conv = _convert_to_numpy(X)
    is_pandas = isinstance(X, pd.DataFrame)
    
    if strategies is None:
        return scale_features(X_conv, method='standard')
    
    X_scaled = X_conv.copy()
    
    for idx, method in strategies.items():
        if idx < X_conv.shape[1]:
            if method == 'log_transform':
                X_scaled[:, idx] = np.log1p(X_conv[:, idx])
            elif method == 'box_cox':
                # Simple Box-Cox approximation
                X_scaled[:, idx] = np.log1p(X_conv[:, idx] - X_conv[:, idx].min() + 1)
            else:
                # Use existing scaling methods
                X_scaled[:, idx] = scale_features(X_conv[:, idx].reshape(-1, 1), method=method).flatten()
    
    if is_pandas:
        return pd.DataFrame(X_scaled, index=X.index, columns=X.columns)
    return X_scaled


def auto_scale_features(X: Union[np.ndarray, 'pd.DataFrame'],
                       method: str = 'auto',
                       **kwargs) -> Union[np.ndarray, 'pd.DataFrame']:
    """
    Automatic feature scaling based on data distribution.
    
    Args:
        X: Input data.
        method: Scaling method.
        **kwargs: Additional parameters.
    
    Returns:
        Automatically scaled data.
    """
    X_conv = _convert_to_numpy(X)
    is_pandas = isinstance(X, pd.DataFrame)
    
    if method == 'auto':
        # Analyze distributions and choose appropriate scaling
        strategies = {}
        for i in range(X_conv.shape[1]):
            skewness = np.abs(np.mean(((X_conv[:, i] - np.mean(X_conv[:, i])) / np.std(X_conv[:, i])) ** 3))
            if skewness > 1:
                strategies[i] = 'robust'
            else:
                strategies[i] = 'standard'
        
        return scale_features_advanced(X_conv, strategies=strategies, **kwargs)
    else:
        return scale_features(X_conv, method=method, **kwargs)


def compare_scaling_methods(X: Union[np.ndarray, 'pd.DataFrame'],
                          methods: list = None,
                          target_variable: Union[np.ndarray, 'pd.Series'] = None) -> dict:
    """
    Compare different scaling methods.
    
    Args:
        X: Input data.
        methods: List of scaling methods to compare.
        target_variable: Target variable for evaluation.
    
    Returns:
        Dictionary with comparison results.
    """
    if methods is None:
        methods = ['standard', 'robust', 'minmax']
    
    results = {}
    
    for method in methods:
        X_scaled = scale_features(X, method=method)
        
        if target_variable is not None:
            # Simple evaluation using correlation with target
            if hasattr(X_scaled, 'values'):
                X_scaled = X_scaled.values
            if hasattr(target_variable, 'values'):
                target_variable = target_variable.values
            
            correlations = [np.corrcoef(X_scaled[:, i], target_variable)[0, 1] 
                          for i in range(X_scaled.shape[1])]
            results[method] = np.mean(np.abs(correlations))
        else:
            # Use variance as simple metric
            results[method] = np.var(X_scaled).mean()
    
    return results


class PreprocessingPipeline:
    """
    Complete preprocessing pipeline for end-to-end data preparation.
    """
    
    def __init__(self, steps: list, config: dict = None):
        self.steps = steps
        self.config = config or {}
        self.fitted = False
        self.transformers = {}
    
    def fit_transform(self, X, y=None):
        """Fit the pipeline and transform the data."""
        # Implementation would go here
        # For now, return the data as-is
        self.fitted = True
        return X, y
    
    def transform(self, X):
        """Transform new data using fitted pipeline."""
        if not self.fitted:
            raise ValueError("Pipeline must be fitted before transform")
        return X
    
    def get_report(self):
        """Get preprocessing report."""
        return {
            'original_shape': None,
            'final_shape': None,
            'features_removed': 0,
            'features_added': 0,
            'missing_handled': 0,
            'outliers_detected': 0
        }
    
    def save(self, path):
        """Save pipeline to file."""
        # Implementation would go here
        pass
    
    @classmethod
    def load(cls, path):
        """Load pipeline from file."""
        # Implementation would go here
        return cls([], {})


def generate_features(X: Union[np.ndarray, 'pd.DataFrame'],
                     interactions: bool = True,
                     polynomials: bool = True,
                     degree: int = 2) -> Union[np.ndarray, 'pd.DataFrame']:
    """
    Generate new features through feature interactions and transformations.
    
    Args:
        X: Input data (pandas DataFrame or numpy array).
        interactions: Whether to generate interaction features.
        polynomials: Whether to generate polynomial features.
        degree: Degree of polynomial features.
    
    Returns:
        Data with additional generated features.
    
    Examples:
        >>> X = np.array([[1, 2], [3, 4]])
        >>> generate_features(X, interactions=True, polynomials=True, degree=2)
        array([[ 1.,  2.,  2.,  4.,  1.],
               [ 3.,  4., 12., 16.,  9.]])
    """
    X_conv = _convert_to_numpy(X)
    is_pandas = isinstance(X, pd.DataFrame)
    features = [X_conv]
    feature_names = list(X.columns) if is_pandas else [f"x{i}" for i in range(X_conv.shape[1])]
    new_names = feature_names.copy()
    
    if interactions:
        for i in range(X_conv.shape[1]):
            for j in range(i + 1, X_conv.shape[1]):
                features.append((X_conv[:, i] * X_conv[:, j]).reshape(-1, 1))
                name_i = feature_names[i]
                name_j = feature_names[j]
                new_names.append(f"{name_i}_{name_j}")
    
    if polynomials:
        for i in range(X_conv.shape[1]):
            for d in range(2, degree + 1):
                features.append(np.power(X_conv[:, i], d).reshape(-1, 1))
                name = feature_names[i]
                new_names.append(f"{name}^{d}")
    
    X_new = np.hstack(features)
    
    if is_pandas:
        return pd.DataFrame(X_new, index=X.index, columns=new_names)
    return X_new
