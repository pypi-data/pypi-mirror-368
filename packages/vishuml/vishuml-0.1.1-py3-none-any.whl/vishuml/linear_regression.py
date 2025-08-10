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
    
    def __init__(
        self,
        fit_intercept: bool = True,
        use_gradient_descent: bool = False,
        learning_rate: float = 0.01,
        max_iterations: int = 1000,
        tolerance: float = 1e-8,
    ):
        """
        Initialize Linear Regression model.
        
        Args:
            fit_intercept (bool, optional): Whether to calculate the intercept.
                Defaults to True.
            use_gradient_descent (bool, optional): When True, fits the model using
                gradient descent; when False, uses the closed-form normal equation.
                Defaults to False.
            learning_rate (float, optional): Learning rate for gradient descent.
                Defaults to 0.01.
            max_iterations (int, optional): Maximum gradient descent iterations.
                Defaults to 1000.
            tolerance (float, optional): Early-stopping tolerance for gradient descent.
                Defaults to 1e-8.
        """
        self.fit_intercept = fit_intercept
        self.use_gradient_descent = use_gradient_descent
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.tolerance = tolerance
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
        
        if not self.use_gradient_descent:
            # Closed-form solution via normal equation
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
        else:
            # Gradient descent solution
            n_samples, n_features = X.shape
            self.weights = np.zeros(n_features)
            self.intercept = 0.0 if self.fit_intercept else 0.0

            previous_loss = np.inf
            for _ in range(self.max_iterations):
                # Predictions
                y_pred = X @ self.weights
                if self.fit_intercept:
                    y_pred = y_pred + self.intercept

                # Gradients (MSE loss)
                error = (y_pred - y)
                dw = (2.0 / n_samples) * (X.T @ error)
                if self.fit_intercept:
                    db = (2.0 / n_samples) * np.sum(error)

                # Update
                self.weights = self.weights - self.learning_rate * dw
                if self.fit_intercept:
                    self.intercept = self.intercept - self.learning_rate * db

                # Early stopping on loss improvement
                loss = (error @ error) / n_samples
                if abs(previous_loss - loss) < self.tolerance:
                    break
                previous_loss = loss
        
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
            'use_gradient_descent': self.use_gradient_descent,
            'learning_rate': self.learning_rate,
            'max_iterations': self.max_iterations,
            'tolerance': self.tolerance,
            'weights': self.weights,
            'intercept': self.intercept
        }


def compare_methods(
    X: Union[np.ndarray, 'pd.DataFrame'],
    y: Union[np.ndarray, 'pd.Series'],
    *,
    fit_intercept: bool = True,
    learning_rate: float = 0.01,
    max_iterations: int = 1000,
    tolerance: float = 1e-8,
) -> dict:
    """
    Train LinearRegression with both normal equation and gradient descent
    and return a comparison of parameters and scores.

    Args:
        X: Features as numpy array or pandas DataFrame.
        y: Target as numpy array or pandas Series.
        fit_intercept: Whether to fit intercept.
        learning_rate: Learning rate for gradient descent.
        max_iterations: Max iterations for gradient descent.
        tolerance: Early-stopping tolerance for gradient descent.

    Returns:
        dict: {
            'normal': {'weights', 'intercept', 'r2', 'mse'},
            'gradient_descent': {'weights', 'intercept', 'r2', 'mse'}
        }
    """
    from .utils import r2_score, mean_squared_error, validate_and_convert_data

    Xc, yc = validate_and_convert_data(X, y)

    # Normal equation
    model_ne = LinearRegression(
        fit_intercept=fit_intercept,
        use_gradient_descent=False,
    ).fit(Xc, yc)
    pred_ne = model_ne.predict(Xc)
    res_ne = {
        'weights': model_ne.weights.copy() if model_ne.weights is not None else None,
        'intercept': float(model_ne.intercept),
        'r2': float(r2_score(yc, pred_ne)),
        'mse': float(mean_squared_error(yc, pred_ne)),
    }

    # Gradient descent
    model_gd = LinearRegression(
        fit_intercept=fit_intercept,
        use_gradient_descent=True,
        learning_rate=learning_rate,
        max_iterations=max_iterations,
        tolerance=tolerance,
    ).fit(Xc, yc)
    pred_gd = model_gd.predict(Xc)
    res_gd = {
        'weights': model_gd.weights.copy() if model_gd.weights is not None else None,
        'intercept': float(model_gd.intercept),
        'r2': float(r2_score(yc, pred_gd)),
        'mse': float(mean_squared_error(yc, pred_gd)),
    }

    return {'normal': res_ne, 'gradient_descent': res_gd}
