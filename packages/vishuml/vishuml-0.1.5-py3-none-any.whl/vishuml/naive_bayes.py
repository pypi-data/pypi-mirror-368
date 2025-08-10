"""
Naive Bayes implementation from scratch.

This module implements Gaussian Naive Bayes classifier for continuous features
and assumes that features follow a normal distribution.
"""

import numpy as np
from typing import Dict, Any


class NaiveBayes:
    """
    Gaussian Naive Bayes classifier.
    
    Naive Bayes classifiers are based on applying Bayes' theorem with the
    "naive" assumption of conditional independence between every pair of features.
    This implementation assumes that the likelihood of the features is Gaussian.
    
    Attributes:
        class_priors (dict): Prior probabilities for each class.
        feature_means (dict): Mean values for each feature per class.
        feature_vars (dict): Variance values for each feature per class.
        classes (np.ndarray): Unique class labels.
    
    Examples:
        >>> from vishuml.naive_bayes import NaiveBayes
        >>> import numpy as np
        >>> X = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
        >>> y = np.array([0, 0, 1, 1])
        >>> model = NaiveBayes()
        >>> model.fit(X, y)
        >>> predictions = model.predict([[2.5, 3.5]])
        >>> print(predictions)
        [1]
    """
    
    def __init__(self):
        """Initialize Naive Bayes model."""
        self.class_priors: Dict[Any, float] = {}
        self.feature_means: Dict[Any, np.ndarray] = {}
        self.feature_vars: Dict[Any, np.ndarray] = {}
        self.classes: np.ndarray = None
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'NaiveBayes':
        """
        Fit Naive Bayes model to training data.
        
        Args:
            X (np.ndarray): Training feature matrix of shape (n_samples, n_features).
            y (np.ndarray): Training target vector of shape (n_samples,).
        
        Returns:
            NaiveBayes: Returns self for method chaining.
        
        Raises:
            ValueError: If X and y have incompatible shapes.
        """
        X = np.array(X)
        y = np.array(y)
        
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        if X.shape[0] != len(y):
            raise ValueError("X and y must have the same number of samples")
        
        self.classes = np.unique(y)
        n_samples = len(y)
        
        # Calculate class priors and feature statistics
        for class_label in self.classes:
            # Get samples for this class
            class_mask = (y == class_label)
            X_class = X[class_mask]
            
            # Calculate prior probability
            self.class_priors[class_label] = np.sum(class_mask) / n_samples
            
            # Calculate mean and variance for each feature
            self.feature_means[class_label] = np.mean(X_class, axis=0)
            self.feature_vars[class_label] = np.var(X_class, axis=0)
            
            # Add small epsilon to avoid division by zero
            self.feature_vars[class_label] += 1e-9
        
        return self
    
    def _gaussian_probability(self, x: float, mean: float, var: float) -> float:
        """
        Calculate Gaussian probability density function.
        
        Args:
            x (float): Input value.
            mean (float): Mean of the distribution.
            var (float): Variance of the distribution.
        
        Returns:
            float: Probability density.
        """
        numerator = np.exp(-0.5 * ((x - mean) ** 2) / var)
        denominator = np.sqrt(2 * np.pi * var)
        return numerator / denominator
    
    def _calculate_class_probability(self, x: np.ndarray, class_label: Any) -> float:
        """
        Calculate probability of a sample belonging to a specific class.
        
        Args:
            x (np.ndarray): Feature vector.
            class_label (Any): Class label.
        
        Returns:
            float: Log probability of the sample belonging to the class.
        """
        # Start with log prior
        log_prob = np.log(self.class_priors[class_label])
        
        # Add log likelihood for each feature (assuming independence)
        feature_means = self.feature_means[class_label]
        feature_vars = self.feature_vars[class_label]
        
        for i, feature_value in enumerate(x):
            # Use log probability to avoid numerical underflow
            prob = self._gaussian_probability(feature_value, feature_means[i], feature_vars[i])
            log_prob += np.log(prob + 1e-10)  # Add small epsilon to avoid log(0)
        
        return log_prob
    
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
        if self.classes is None:
            raise ValueError("Model must be fitted before making predictions")
        
        X = np.array(X)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        predictions = []
        
        for x in X:
            # Calculate probability for each class
            class_probabilities = {}
            for class_label in self.classes:
                class_probabilities[class_label] = self._calculate_class_probability(x, class_label)
            
            # Predict class with highest probability
            predicted_class = max(class_probabilities, key=class_probabilities.get)
            predictions.append(predicted_class)
        
        return np.array(predictions)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities for samples in X.
        
        Args:
            X (np.ndarray): Feature matrix of shape (n_samples, n_features).
        
        Returns:
            np.ndarray: Predicted probabilities of shape (n_samples, n_classes).
        
        Raises:
            ValueError: If model hasn't been fitted yet.
        """
        if self.classes is None:
            raise ValueError("Model must be fitted before making predictions")
        
        X = np.array(X)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        probabilities = []
        
        for x in X:
            # Calculate log probabilities for each class
            log_probs = []
            for class_label in self.classes:
                log_prob = self._calculate_class_probability(x, class_label)
                log_probs.append(log_prob)
            
            # Convert log probabilities to probabilities using softmax
            log_probs = np.array(log_probs)
            # Subtract max for numerical stability
            log_probs = log_probs - np.max(log_probs)
            probs = np.exp(log_probs)
            probs = probs / np.sum(probs)
            
            probabilities.append(probs)
        
        return np.array(probabilities)
    
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
        return np.mean(y == y_pred)
    
    def get_params(self) -> dict:
        """
        Get parameters of the model.
        
        Returns:
            dict: Dictionary containing model parameters.
        """
        return {
            'class_priors': self.class_priors,
            'feature_means': self.feature_means,
            'feature_vars': self.feature_vars,
            'classes': self.classes
        }
