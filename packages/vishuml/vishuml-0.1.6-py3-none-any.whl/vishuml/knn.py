"""
K-Nearest Neighbors implementation from scratch.

This module implements the K-Nearest Neighbors algorithm for both
classification and regression tasks.
"""

import numpy as np
from typing import Union, Literal
from collections import Counter


class KNearestNeighbors:
    """
    K-Nearest Neighbors classifier and regressor.
    
    KNN is a lazy learning algorithm that stores all training data and makes
    predictions based on the k closest training examples in the feature space.
    
    Attributes:
        k (int): Number of neighbors to consider.
        task_type (str): Type of task - 'classification' or 'regression'.
        X_train (np.ndarray): Training feature matrix.
        y_train (np.ndarray): Training target vector.
    
    Examples:
        >>> from vishuml.knn import KNearestNeighbors
        >>> import numpy as np
        >>> X = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
        >>> y = np.array([0, 0, 1, 1])
        >>> model = KNearestNeighbors(k=3, task_type='classification')
        >>> model.fit(X, y)
        >>> predictions = model.predict([[2.5, 3.5]])
        >>> print(predictions)
        [1]
    """
    
    def __init__(self, k: int = 3, task_type: Literal['classification', 'regression'] = 'classification'):
        """
        Initialize KNN model.
        
        Args:
            k (int, optional): Number of neighbors to consider. Defaults to 3.
            task_type (str, optional): Type of task - 'classification' or 'regression'.
                Defaults to 'classification'.
        
        Raises:
            ValueError: If k is not positive or task_type is invalid.
        """
        if k <= 0:
            raise ValueError("k must be a positive integer")
        
        if task_type not in ['classification', 'regression']:
            raise ValueError("task_type must be 'classification' or 'regression'")
        
        self.k = k
        self.task_type = task_type
        self.X_train = None
        self.y_train = None
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'KNearestNeighbors':
        """
        Fit the KNN model to training data.
        
        Args:
            X (np.ndarray): Training feature matrix of shape (n_samples, n_features).
            y (np.ndarray): Training target vector of shape (n_samples,).
        
        Returns:
            KNearestNeighbors: Returns self for method chaining.
        
        Raises:
            ValueError: If X and y have incompatible shapes.
        """
        X = np.array(X)
        y = np.array(y)
        
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        if X.shape[0] != len(y):
            raise ValueError("X and y must have the same number of samples")
        
        if self.k > len(y):
            raise ValueError(f"k ({self.k}) cannot be greater than number of training samples ({len(y)})")
        
        self.X_train = X
        self.y_train = y
        
        return self
    
    def _euclidean_distance(self, x1: np.ndarray, x2: np.ndarray) -> float:
        """
        Calculate Euclidean distance between two points.
        
        Args:
            x1 (np.ndarray): First point.
            x2 (np.ndarray): Second point.
        
        Returns:
            float: Euclidean distance.
        """
        return np.sqrt(np.sum((x1 - x2) ** 2))
    
    def _get_neighbors(self, x: np.ndarray) -> np.ndarray:
        """
        Get k nearest neighbors for a given point.
        
        Args:
            x (np.ndarray): Query point.
        
        Returns:
            np.ndarray: Indices of k nearest neighbors.
        """
        distances = [self._euclidean_distance(x, x_train) for x_train in self.X_train]
        k_indices = np.argsort(distances)[:self.k]
        return k_indices
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict labels for test data.
        
        Args:
            X (np.ndarray): Test feature matrix of shape (n_samples, n_features).
        
        Returns:
            np.ndarray: Predicted labels of shape (n_samples,).
        
        Raises:
            ValueError: If model hasn't been fitted yet.
        """
        if self.X_train is None:
            raise ValueError("Model must be fitted before making predictions")
        
        X = np.array(X)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        predictions = []
        
        for x in X:
            neighbor_indices = self._get_neighbors(x)
            neighbor_labels = self.y_train[neighbor_indices]
            
            if self.task_type == 'classification':
                # Majority vote for classification
                prediction = Counter(neighbor_labels).most_common(1)[0][0]
            else:
                # Mean for regression
                prediction = np.mean(neighbor_labels)
            
            predictions.append(prediction)
        
        return np.array(predictions)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities for test data (classification only).
        
        Args:
            X (np.ndarray): Test feature matrix of shape (n_samples, n_features).
        
        Returns:
            np.ndarray: Predicted probabilities of shape (n_samples, n_classes).
        
        Raises:
            ValueError: If model hasn't been fitted yet or task is regression.
        """
        if self.task_type != 'classification':
            raise ValueError("predict_proba is only available for classification tasks")
        
        if self.X_train is None:
            raise ValueError("Model must be fitted before making predictions")
        
        X = np.array(X)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        unique_classes = np.unique(self.y_train)
        n_classes = len(unique_classes)
        probabilities = []
        
        for x in X:
            neighbor_indices = self._get_neighbors(x)
            neighbor_labels = self.y_train[neighbor_indices]
            
            # Calculate class probabilities
            class_counts = Counter(neighbor_labels)
            class_probs = []
            
            for class_label in unique_classes:
                prob = class_counts.get(class_label, 0) / self.k
                class_probs.append(prob)
            
            probabilities.append(class_probs)
        
        return np.array(probabilities)
    
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Return the accuracy score (classification) or R² score (regression).
        
        Args:
            X (np.ndarray): Test feature matrix of shape (n_samples, n_features).
            y (np.ndarray): Test target vector of shape (n_samples,).
        
        Returns:
            float: Accuracy score for classification or R² score for regression.
        """
        y_pred = self.predict(X)
        
        if self.task_type == 'classification':
            return np.mean(y == y_pred)
        else:
            # R² score for regression
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            return 1 - (ss_res / ss_tot)
    
    def get_params(self) -> dict:
        """
        Get parameters of the model.
        
        Returns:
            dict: Dictionary containing model parameters.
        """
        return {
            'k': self.k,
            'task_type': self.task_type
        }
