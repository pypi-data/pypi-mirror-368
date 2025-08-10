"""
Logistic Regression implementation from scratch.

This module implements binary logistic regression using gradient descent
for classification tasks.
"""

import numpy as np
from typing import Optional, Union
from .utils import validate_and_convert_data


class LogisticRegression:
    """
    Logistic Regression classifier using gradient descent.
    
    Logistic regression uses the logistic function to model the probability
    of binary classification. It uses gradient descent to minimize the
    log-likelihood function.
    
    Attributes:
        learning_rate (float): Step size for gradient descent.
        max_iterations (int): Maximum number of iterations.
        fit_intercept (bool): Whether to fit intercept term.
        weights (np.ndarray): Coefficients of the logistic model.
        intercept (float): Independent term in the logistic model.
    
    Examples:
        >>> from vishuml.logistic_regression import LogisticRegression
        >>> import numpy as np
        >>> X = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
        >>> y = np.array([0, 0, 1, 1])
        >>> model = LogisticRegression()
        >>> model.fit(X, y)
        >>> predictions = model.predict(X)
        >>> print(predictions)
        [0 0 1 1]
    """
    
    def __init__(self, learning_rate: float = 0.01, max_iterations: int = 1000, 
                 fit_intercept: bool = True):
        """
        Initialize Logistic Regression model.
        
        Args:
            learning_rate (float, optional): Learning rate for gradient descent.
                Defaults to 0.01.
            max_iterations (int, optional): Maximum number of iterations.
                Defaults to 1000.
            fit_intercept (bool, optional): Whether to calculate the intercept.
                Defaults to True.
        """
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.fit_intercept = fit_intercept
        self.weights: Optional[np.ndarray] = None
        self.intercept: Optional[float] = None
    
    def _sigmoid(self, z: np.ndarray) -> np.ndarray:
        """
        Sigmoid activation function.
        
        Args:
            z (np.ndarray): Input array.
        
        Returns:
            np.ndarray: Sigmoid output.
        """
        # Clip z to prevent overflow
        z = np.clip(z, -500, 500)
        return 1 / (1 + np.exp(-z))
    
    def fit(self, X: Union[np.ndarray, 'pd.DataFrame'], y: Union[np.ndarray, 'pd.Series']) -> 'LogisticRegression':
        """
        Fit logistic regression model to training data.
        
        Args:
            X (np.ndarray or pd.DataFrame): Training feature matrix of shape (n_samples, n_features).
            y (np.ndarray or pd.Series): Training target vector of shape (n_samples,).
        
        Returns:
            LogisticRegression: Returns self for method chaining.
        
        Raises:
            ValueError: If X and y have incompatible shapes.
        
        Examples:
            Using pandas DataFrame:
            >>> import pandas as pd
            >>> df = pd.read_csv('data.csv')
            >>> X = df[['feature1', 'feature2']]
            >>> y = df['target']
            >>> model = LogisticRegression()
            >>> model.fit(X, y)
        """
        # Convert and validate input data
        X, y = validate_and_convert_data(X, y)
        
        n_samples, n_features = X.shape
        
        # Initialize weights and intercept
        self.weights = np.zeros(n_features)
        self.intercept = 0.0 if self.fit_intercept else None
        
        # Gradient descent
        for _ in range(self.max_iterations):
            # Forward pass
            linear_pred = X @ self.weights
            if self.fit_intercept:
                linear_pred += self.intercept
            
            predictions = self._sigmoid(linear_pred)
            
            # Compute cost (log-likelihood)
            cost = self._compute_cost(y, predictions)
            
            # Compute gradients
            dw = (1 / n_samples) * X.T @ (predictions - y)
            if self.fit_intercept:
                db = (1 / n_samples) * np.sum(predictions - y)
            
            # Update parameters
            self.weights -= self.learning_rate * dw
            if self.fit_intercept:
                self.intercept -= self.learning_rate * db
        
        return self
    
    def _compute_cost(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Compute logistic regression cost function.
        
        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted probabilities.
        
        Returns:
            float: Cost value.
        """
        # Avoid log(0) by adding small epsilon
        epsilon = 1e-15
        y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
        
        cost = -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))
        return cost
    
    def predict(self, X: Union[np.ndarray, 'pd.DataFrame']) -> np.ndarray:
        """
        Predict class labels for samples in X.
        
        Args:
            X (np.ndarray or pd.DataFrame): Feature matrix of shape (n_samples, n_features).
        
        Returns:
            np.ndarray: Predicted class labels of shape (n_samples,).
        
        Raises:
            ValueError: If model hasn't been fitted yet.
        """
        return (self.predict_proba(X) >= 0.5).astype(int)
    
    def predict_proba(self, X: Union[np.ndarray, 'pd.DataFrame']) -> np.ndarray:
        """
        Predict class probabilities for samples in X.
        
        Args:
            X (np.ndarray or pd.DataFrame): Feature matrix of shape (n_samples, n_features).
        
        Returns:
            np.ndarray: Predicted probabilities of shape (n_samples,).
        
        Raises:
            ValueError: If model hasn't been fitted yet.
        """
        if self.weights is None:
            raise ValueError("Model must be fitted before making predictions")
        
        # Convert and validate input data
        X, _ = validate_and_convert_data(X)
        
        linear_pred = X @ self.weights
        if self.fit_intercept:
            linear_pred += self.intercept
        
        return self._sigmoid(linear_pred)
    
    def score(self, X: Union[np.ndarray, 'pd.DataFrame'], y: Union[np.ndarray, 'pd.Series']) -> float:
        """
        Return the mean accuracy on the given test data and labels.
        
        Args:
            X (np.ndarray or pd.DataFrame): Test feature matrix of shape (n_samples, n_features).
            y (np.ndarray or pd.Series): Test target vector of shape (n_samples,).
        
        Returns:
            float: Mean accuracy.
        """
        # Convert and validate input data
        _, y = validate_and_convert_data(X, y)
        
        y_pred = self.predict(X)
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
            'intercept': self.intercept
        }
