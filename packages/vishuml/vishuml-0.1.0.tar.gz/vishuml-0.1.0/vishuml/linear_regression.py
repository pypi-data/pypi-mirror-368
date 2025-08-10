"""
Linear Regression implementation from scratch.

This module implements linear regression using ordinary least squares method
for both simple and multiple linear regression.
"""

import numpy as np
from typing import Optional, Union
from .utils import validate_and_convert_data


class LinearRegression:
    """
    Linear Regression using Ordinary Least Squares.
    
    Linear regression fits a linear model with coefficients w = (w1, ..., wp)
    to minimize the residual sum of squares between the observed targets in
    the dataset, and the targets predicted by the linear approximation.
    
    Attributes:
        fit_intercept (bool): Whether to fit intercept term.
        weights (np.ndarray): Coefficients of the linear model.
        intercept (float): Independent term in the linear model.
    
    Examples:
        >>> from vishuml.linear_regression import LinearRegression
        >>> import numpy as np
        >>> X = np.array([[1], [2], [3], [4]])
        >>> y = np.array([2, 4, 6, 8])
        >>> model = LinearRegression()
        >>> model.fit(X, y)
        >>> predictions = model.predict(X)
        >>> print(predictions)
        [2. 4. 6. 8.]
    """
    
    def __init__(self, fit_intercept: bool = True):
        """
        Initialize Linear Regression model.
        
        Args:
            fit_intercept (bool, optional): Whether to calculate the intercept.
                Defaults to True.
        """
        self.fit_intercept = fit_intercept
        self.weights: Optional[np.ndarray] = None
        self.intercept: Optional[float] = None
    
    def fit(self, X: Union[np.ndarray, 'pd.DataFrame'], y: Union[np.ndarray, 'pd.Series']) -> 'LinearRegression':
        """
        Fit linear model to training data.
        
        Args:
            X (np.ndarray or pd.DataFrame): Training feature matrix of shape (n_samples, n_features).
            y (np.ndarray or pd.Series): Training target vector of shape (n_samples,).
        
        Returns:
            LinearRegression: Returns self for method chaining.
        
        Raises:
            ValueError: If X and y have incompatible shapes.
        
        Examples:
            Using pandas DataFrame:
            >>> import pandas as pd
            >>> df = pd.read_csv('data.csv')
            >>> X = df[['feature1', 'feature2']]
            >>> y = df['target']
            >>> model = LinearRegression()
            >>> model.fit(X, y)
        """
        # Convert and validate input data
        X, y = validate_and_convert_data(X, y)
        
        if self.fit_intercept:
            # Add bias column
            X_with_bias = np.column_stack([np.ones(X.shape[0]), X])
            # Solve normal equation: (X^T X)^-1 X^T y with regularization for numerical stability
            XTX = X_with_bias.T @ X_with_bias
            # Add small regularization term to diagonal for numerical stability
            XTX += 1e-8 * np.eye(XTX.shape[0])
            coefficients = np.linalg.inv(XTX) @ X_with_bias.T @ y
            self.intercept = coefficients[0]
            self.weights = coefficients[1:]
        else:
            # No intercept case
            XTX = X.T @ X
            # Add small regularization term to diagonal for numerical stability
            XTX += 1e-8 * np.eye(XTX.shape[0])
            self.weights = np.linalg.inv(XTX) @ X.T @ y
            self.intercept = 0.0
        
        return self
    
    def predict(self, X: Union[np.ndarray, 'pd.DataFrame']) -> np.ndarray:
        """
        Predict using the linear model.
        
        Args:
            X (np.ndarray or pd.DataFrame): Feature matrix of shape (n_samples, n_features).
        
        Returns:
            np.ndarray: Predicted values of shape (n_samples,).
        
        Raises:
            ValueError: If model hasn't been fitted yet.
        """
        if self.weights is None:
            raise ValueError("Model must be fitted before making predictions")
        
        # Convert and validate input data
        X, _ = validate_and_convert_data(X)
        
        return X @ self.weights + self.intercept
    
    def score(self, X: Union[np.ndarray, 'pd.DataFrame'], y: Union[np.ndarray, 'pd.Series']) -> float:
        """
        Return the coefficient of determination R² of the prediction.
        
        Args:
            X (np.ndarray or pd.DataFrame): Test feature matrix of shape (n_samples, n_features).
            y (np.ndarray or pd.Series): Test target vector of shape (n_samples,).
        
        Returns:
            float: R² score.
        """
        # Convert and validate input data
        X, y = validate_and_convert_data(X, y)
        
        y_pred = self.predict(X)
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
            'fit_intercept': self.fit_intercept,
            'weights': self.weights,
            'intercept': self.intercept
        }
