"""
Perceptron implementation from scratch.

This module implements the basic perceptron algorithm for binary classification
using online learning with gradient descent.
"""

import numpy as np
from typing import Optional


class Perceptron:
    """
    Perceptron classifier using online learning.
    
    The perceptron is a linear classifier that finds a separating hyperplane
    in the feature space. It uses online learning where weights are updated
    for each misclassified sample.
    
    Attributes:
        learning_rate (float): Learning rate for weight updates.
        max_iterations (int): Maximum number of training iterations.
        fit_intercept (bool): Whether to fit intercept term.
        weights (np.ndarray): Weight vector.
        bias (float): Bias term.
        converged (bool): Whether the algorithm converged.
    
    Examples:
        >>> from vishuml.perceptron import Perceptron
        >>> import numpy as np
        >>> X = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
        >>> y = np.array([0, 0, 1, 1])
        >>> model = Perceptron(learning_rate=0.1)
        >>> model.fit(X, y)
        >>> predictions = model.predict([[2.5, 3.5]])
        >>> print(predictions)
        [1]
    """
    
    def __init__(self, learning_rate: float = 0.01, max_iterations: int = 1000, 
                 fit_intercept: bool = True):
        """
        Initialize Perceptron model.
        
        Args:
            learning_rate (float, optional): Learning rate for updates. Defaults to 0.01.
            max_iterations (int, optional): Maximum training iterations. Defaults to 1000.
            fit_intercept (bool, optional): Whether to fit bias term. Defaults to True.
        """
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.fit_intercept = fit_intercept
        self.weights: Optional[np.ndarray] = None
        self.bias: float = 0.0
        self.converged: bool = False
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'Perceptron':
        """
        Fit perceptron model to training data.
        
        Args:
            X (np.ndarray): Training feature matrix of shape (n_samples, n_features).
            y (np.ndarray): Training target vector of shape (n_samples,).
                Values should be 0 and 1, or -1 and 1.
        
        Returns:
            Perceptron: Returns self for method chaining.
        
        Raises:
            ValueError: If X and y have incompatible shapes or y contains invalid values.
        """
        X = np.array(X)
        y = np.array(y)
        
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        if X.shape[0] != len(y):
            raise ValueError("X and y must have the same number of samples")
        
        # Convert labels to -1, 1 if they are 0, 1
        unique_labels = np.unique(y)
        if set(unique_labels) == {0, 1}:
            y = 2 * y - 1
        elif not set(unique_labels).issubset({-1, 1}):
            raise ValueError("Labels must be binary: either {0, 1} or {-1, 1}")
        
        n_samples, n_features = X.shape
        
        # Initialize weights and bias
        self.weights = np.zeros(n_features)
        self.bias = 0.0
        self.converged = False
        
        # Training loop
        for iteration in range(self.max_iterations):
            errors = 0
            
            # Go through each sample
            for i in range(n_samples):
                # Calculate prediction
                linear_output = np.dot(X[i], self.weights)
                if self.fit_intercept:
                    linear_output += self.bias
                
                # Apply activation function (sign function)
                prediction = 1 if linear_output >= 0 else -1
                
                # Update weights if prediction is wrong
                if prediction != y[i]:
                    errors += 1
                    # Update weights: w = w + eta * (y - y_pred) * x
                    update = self.learning_rate * y[i]
                    self.weights += update * X[i]
                    if self.fit_intercept:
                        self.bias += update
            
            # Check for convergence (no errors)
            if errors == 0:
                self.converged = True
                break
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class labels for samples in X.
        
        Args:
            X (np.ndarray): Feature matrix of shape (n_samples, n_features).
        
        Returns:
            np.ndarray: Predicted class labels of shape (n_samples,).
                Returns values in {0, 1} format.
        
        Raises:
            ValueError: If model hasn't been fitted yet.
        """
        if self.weights is None:
            raise ValueError("Model must be fitted before making predictions")
        
        X = np.array(X)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        # Calculate linear output
        linear_output = X @ self.weights
        if self.fit_intercept:
            linear_output += self.bias
        
        # Apply activation function and convert to 0/1
        predictions = np.where(linear_output >= 0, 1, -1)
        # Convert from {-1, 1} to {0, 1}
        predictions = (predictions + 1) // 2
        
        return predictions
    
    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """
        Compute the decision function for samples in X.
        
        Args:
            X (np.ndarray): Feature matrix of shape (n_samples, n_features).
        
        Returns:
            np.ndarray: Decision function values of shape (n_samples,).
        
        Raises:
            ValueError: If model hasn't been fitted yet.
        """
        if self.weights is None:
            raise ValueError("Model must be fitted before making predictions")
        
        X = np.array(X)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        # Calculate linear output
        linear_output = X @ self.weights
        if self.fit_intercept:
            linear_output += self.bias
        
        return linear_output
    
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Return the mean accuracy on the given test data and labels.
        
        Args:
            X (np.ndarray): Test feature matrix of shape (n_samples, n_features).
            y (np.ndarray): Test target vector of shape (n_samples,).
        
        Returns:
            float: Mean accuracy.
        """
        y_pred = self.predict(X)
        
        # Convert y to 0/1 format if it's in -1/1 format
        unique_labels = np.unique(y)
        if set(unique_labels).issubset({-1, 1}):
            y = (y + 1) // 2
        
        return np.mean(y == y_pred)
    
    def get_params(self) -> dict:
        """
        Get parameters of the model.
        
        Returns:
            dict: Dictionary containing model parameters.
        """
        return {
            'learning_rate': self.learning_rate,
            'max_iterations': self.max_iterations,
            'fit_intercept': self.fit_intercept,
            'weights': self.weights,
            'bias': self.bias,
            'converged': self.converged
        }
