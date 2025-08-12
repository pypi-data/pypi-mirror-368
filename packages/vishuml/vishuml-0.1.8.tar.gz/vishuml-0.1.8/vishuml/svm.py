"""
Support Vector Machine implementation from scratch.

This module implements a simplified Support Vector Machine using
the Sequential Minimal Optimization (SMO) algorithm for binary classification.
"""

import numpy as np
from typing import Optional, Literal


class SupportVectorMachine:
    """
    Support Vector Machine classifier using SMO algorithm.
    
    SVM finds the optimal hyperplane that separates classes with maximum margin.
    This implementation uses a simplified version of the SMO algorithm for
    binary classification with linear and RBF kernels.
    
    Attributes:
        C (float): Regularization parameter.
        kernel (str): Kernel type - 'linear' or 'rbf'.
        gamma (float): Kernel coefficient for RBF kernel.
        max_iterations (int): Maximum number of iterations.
        tolerance (float): Tolerance for stopping criterion.
        alpha (np.ndarray): Lagrange multipliers.
        b (float): Bias term.
        X_train (np.ndarray): Training feature matrix.
        y_train (np.ndarray): Training target vector.
        support_vectors (np.ndarray): Support vectors.
        support_vector_labels (np.ndarray): Support vector labels.
    
    Examples:
        >>> from vishuml.svm import SupportVectorMachine
        >>> import numpy as np
        >>> X = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
        >>> y = np.array([-1, -1, 1, 1])
        >>> model = SupportVectorMachine(C=1.0)
        >>> model.fit(X, y)
        >>> predictions = model.predict([[2.5, 3.5]])
        >>> print(predictions)
        [1]
    """
    
    def __init__(self, C: float = 1.0, kernel: Literal['linear', 'rbf'] = 'linear',
                 gamma: float = 1.0, max_iterations: int = 1000, tolerance: float = 1e-3):
        """
        Initialize SVM model.
        
        Args:
            C (float, optional): Regularization parameter. Defaults to 1.0.
            kernel (str, optional): Kernel type - 'linear' or 'rbf'. Defaults to 'linear'.
            gamma (float, optional): Kernel coefficient for RBF. Defaults to 1.0.
            max_iterations (int, optional): Maximum iterations. Defaults to 1000.
            tolerance (float, optional): Tolerance for stopping. Defaults to 1e-3.
        """
        self.C = C
        self.kernel = kernel
        self.gamma = gamma
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        
        # Model parameters
        self.alpha: Optional[np.ndarray] = None
        self.b: float = 0.0
        self.X_train: Optional[np.ndarray] = None
        self.y_train: Optional[np.ndarray] = None
        self.support_vectors: Optional[np.ndarray] = None
        self.support_vector_labels: Optional[np.ndarray] = None
    
    def _kernel_function(self, x1: np.ndarray, x2: np.ndarray) -> float:
        """
        Compute kernel function between two vectors.
        
        Args:
            x1 (np.ndarray): First vector.
            x2 (np.ndarray): Second vector.
        
        Returns:
            float: Kernel value.
        """
        if self.kernel == 'linear':
            return np.dot(x1, x2)
        elif self.kernel == 'rbf':
            return np.exp(-self.gamma * np.linalg.norm(x1 - x2) ** 2)
        else:
            raise ValueError(f"Unknown kernel: {self.kernel}")
    
    def _compute_kernel_matrix(self, X: np.ndarray) -> np.ndarray:
        """
        Compute kernel matrix for all training samples.
        
        Args:
            X (np.ndarray): Feature matrix.
        
        Returns:
            np.ndarray: Kernel matrix.
        """
        n_samples = X.shape[0]
        K = np.zeros((n_samples, n_samples))
        
        for i in range(n_samples):
            for j in range(n_samples):
                K[i, j] = self._kernel_function(X[i], X[j])
        
        return K
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'SupportVectorMachine':
        """
        Fit SVM model to training data using simplified SMO algorithm.
        
        Args:
            X (np.ndarray): Training feature matrix of shape (n_samples, n_features).
            y (np.ndarray): Training target vector of shape (n_samples,).
                Values should be -1 or 1.
        
        Returns:
            SupportVectorMachine: Returns self for method chaining.
        
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
        
        self.X_train = X
        self.y_train = y
        n_samples = X.shape[0]
        
        # Initialize parameters
        self.alpha = np.zeros(n_samples)
        self.b = 0.0
        
        # Compute kernel matrix
        K = self._compute_kernel_matrix(X)
        
        # Simplified SMO algorithm
        for iteration in range(self.max_iterations):
            alpha_prev = np.copy(self.alpha)
            
            for i in range(n_samples):
                # Calculate prediction error
                prediction = np.sum(self.alpha * y * K[:, i]) + self.b
                E_i = prediction - y[i]
                
                # Check KKT conditions
                if (y[i] * E_i < -self.tolerance and self.alpha[i] < self.C) or \
                   (y[i] * E_i > self.tolerance and self.alpha[i] > 0):
                    
                    # Select second alpha randomly
                    j = np.random.choice([idx for idx in range(n_samples) if idx != i])
                    
                    prediction_j = np.sum(self.alpha * y * K[:, j]) + self.b
                    E_j = prediction_j - y[j]
                    
                    # Save old alphas
                    alpha_i_old = self.alpha[i]
                    alpha_j_old = self.alpha[j]
                    
                    # Compute bounds
                    if y[i] != y[j]:
                        L = max(0, self.alpha[j] - self.alpha[i])
                        H = min(self.C, self.C + self.alpha[j] - self.alpha[i])
                    else:
                        L = max(0, self.alpha[i] + self.alpha[j] - self.C)
                        H = min(self.C, self.alpha[i] + self.alpha[j])
                    
                    if L == H:
                        continue
                    
                    # Compute eta
                    eta = 2 * K[i, j] - K[i, i] - K[j, j]
                    if eta >= 0:
                        continue
                    
                    # Update alpha_j
                    self.alpha[j] -= y[j] * (E_i - E_j) / eta
                    self.alpha[j] = np.clip(self.alpha[j], L, H)
                    
                    if abs(self.alpha[j] - alpha_j_old) < 1e-5:
                        continue
                    
                    # Update alpha_i
                    self.alpha[i] += y[i] * y[j] * (alpha_j_old - self.alpha[j])
                    
                    # Update bias
                    b1 = self.b - E_i - y[i] * (self.alpha[i] - alpha_i_old) * K[i, i] - \
                         y[j] * (self.alpha[j] - alpha_j_old) * K[i, j]
                    b2 = self.b - E_j - y[i] * (self.alpha[i] - alpha_i_old) * K[i, j] - \
                         y[j] * (self.alpha[j] - alpha_j_old) * K[j, j]
                    
                    if 0 < self.alpha[i] < self.C:
                        self.b = b1
                    elif 0 < self.alpha[j] < self.C:
                        self.b = b2
                    else:
                        self.b = (b1 + b2) / 2
            
            # Check for convergence
            if np.allclose(self.alpha, alpha_prev, atol=self.tolerance):
                break
        
        # Identify support vectors
        support_vector_indices = self.alpha > 1e-5
        self.support_vectors = X[support_vector_indices]
        self.support_vector_labels = y[support_vector_indices]
        self.alpha = self.alpha[support_vector_indices]
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class labels for samples in X.
        
        Args:
            X (np.ndarray): Feature matrix of shape (n_samples, n_features).
        
        Returns:
            np.ndarray: Predicted class labels of shape (n_samples,).
        
        Raises:
            ValueError: If model hasn't been fitted yet.
        """
        if self.support_vectors is None:
            raise ValueError("Model must be fitted before making predictions")
        
        X = np.array(X)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        predictions = []
        
        for x in X:
            prediction = 0
            for i in range(len(self.support_vectors)):
                prediction += self.alpha[i] * self.support_vector_labels[i] * \
                             self._kernel_function(self.support_vectors[i], x)
            prediction += self.b
            predictions.append(1 if prediction >= 0 else -1)
        
        return np.array(predictions)
    
    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """
        Evaluate the decision function for the samples in X.
        
        Args:
            X (np.ndarray): Feature matrix of shape (n_samples, n_features).
        
        Returns:
            np.ndarray: Decision function values of shape (n_samples,).
        """
        if self.support_vectors is None:
            raise ValueError("Model must be fitted before making predictions")
        
        X = np.array(X)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        decisions = []
        
        for x in X:
            decision = 0
            for i in range(len(self.support_vectors)):
                decision += self.alpha[i] * self.support_vector_labels[i] * \
                           self._kernel_function(self.support_vectors[i], x)
            decision += self.b
            decisions.append(decision)
        
        return np.array(decisions)
    
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Return the mean accuracy on the given test data and labels.
        
        Args:
            X (np.ndarray): Test feature matrix of shape (n_samples, n_features).
            y (np.ndarray): Test target vector of shape (n_samples,).
        
        Returns:
            float: Mean accuracy.
        """
        # Convert labels to -1, 1 if they are 0, 1
        unique_labels = np.unique(y)
        if set(unique_labels) == {0, 1}:
            y = 2 * y - 1
        
        y_pred = self.predict(X)
        return np.mean(y == y_pred)
    
    def get_params(self) -> dict:
        """
        Get parameters of the model.
        
        Returns:
            dict: Dictionary containing model parameters.
        """
        return {
            'C': self.C,
            'kernel': self.kernel,
            'gamma': self.gamma,
            'max_iterations': self.max_iterations,
            'tolerance': self.tolerance
        }
