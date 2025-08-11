"""
K-Means Clustering implementation from scratch.

This module implements the K-Means clustering algorithm for unsupervised learning
using Lloyd's algorithm with multiple initialization strategies.
"""

import numpy as np
from typing import Optional, Literal


class KMeans:
    """
    K-Means clustering algorithm.
    
    K-Means clustering partitions data into k clusters by minimizing the
    within-cluster sum of squares. It uses an iterative algorithm that
    alternates between assigning points to clusters and updating centroids.
    
    Attributes:
        k (int): Number of clusters.
        max_iterations (int): Maximum number of iterations.
        tolerance (float): Tolerance for convergence.
        init (str): Initialization method.
        random_state (int): Random seed for reproducibility.
        centroids (np.ndarray): Cluster centroids.
        labels (np.ndarray): Cluster labels for training data.
        inertia (float): Sum of squared distances to centroids.
        n_iterations (int): Number of iterations performed.
    
    Examples:
        >>> from vishuml.kmeans import KMeans
        >>> import numpy as np
        >>> X = np.array([[1, 2], [2, 3], [8, 9], [9, 10]])
        >>> model = KMeans(k=2, random_state=42)
        >>> model.fit(X)
        >>> predictions = model.predict([[5, 6]])
        >>> print(predictions)
        [0]
    """
    
    def __init__(self, k: int = 8, max_iterations: int = 300, tolerance: float = 1e-4,
                 init: Literal['random', 'k-means++'] = 'k-means++', random_state: Optional[int] = None):
        """
        Initialize K-Means model.
        
        Args:
            k (int, optional): Number of clusters. Defaults to 8.
            max_iterations (int, optional): Maximum iterations. Defaults to 300.
            tolerance (float, optional): Tolerance for convergence. Defaults to 1e-4.
            init (str, optional): Initialization method. Defaults to 'k-means++'.
            random_state (int, optional): Random seed. Defaults to None.
        
        Raises:
            ValueError: If k is not positive or init method is invalid.
        """
        if k <= 0:
            raise ValueError("k must be a positive integer")
        
        if init not in ['random', 'k-means++']:
            raise ValueError("init must be 'random' or 'k-means++'")
        
        self.k = k
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.init = init
        self.random_state = random_state
        
        # Model attributes
        self.centroids: Optional[np.ndarray] = None
        self.labels: Optional[np.ndarray] = None
        self.inertia: Optional[float] = None
        self.n_iterations: int = 0
    
    def _initialize_centroids(self, X: np.ndarray) -> np.ndarray:
        """
        Initialize cluster centroids.
        
        Args:
            X (np.ndarray): Feature matrix.
        
        Returns:
            np.ndarray: Initial centroids.
        """
        if self.random_state is not None:
            np.random.seed(self.random_state)
        
        n_samples, n_features = X.shape
        
        if self.init == 'random':
            # Random initialization
            centroids = np.random.uniform(
                low=X.min(axis=0),
                high=X.max(axis=0),
                size=(self.k, n_features)
            )
        elif self.init == 'k-means++':
            # K-means++ initialization
            centroids = np.zeros((self.k, n_features))
            
            # Choose first centroid randomly
            centroids[0] = X[np.random.randint(n_samples)]
            
            # Choose remaining centroids
            for i in range(1, self.k):
                # Calculate distances to nearest centroid
                distances = np.array([
                    min([np.linalg.norm(x - c) ** 2 for c in centroids[:i]])
                    for x in X
                ])
                
                # Choose next centroid with probability proportional to distance²
                probabilities = distances / distances.sum()
                cumulative_probabilities = probabilities.cumsum()
                r = np.random.random()
                
                for j, p in enumerate(cumulative_probabilities):
                    if r < p:
                        centroids[i] = X[j]
                        break
        
        return centroids
    
    def _assign_clusters(self, X: np.ndarray, centroids: np.ndarray) -> np.ndarray:
        """
        Assign each point to the nearest cluster.
        
        Args:
            X (np.ndarray): Feature matrix.
            centroids (np.ndarray): Current centroids.
        
        Returns:
            np.ndarray: Cluster assignments.
        """
        distances = np.sqrt(((X - centroids[:, np.newaxis]) ** 2).sum(axis=2))
        return np.argmin(distances, axis=0)
    
    def _update_centroids(self, X: np.ndarray, labels: np.ndarray) -> np.ndarray:
        """
        Update centroids based on current cluster assignments.
        
        Args:
            X (np.ndarray): Feature matrix.
            labels (np.ndarray): Current cluster assignments.
        
        Returns:
            np.ndarray: Updated centroids.
        """
        centroids = np.zeros((self.k, X.shape[1]))
        
        for i in range(self.k):
            if np.sum(labels == i) > 0:
                centroids[i] = X[labels == i].mean(axis=0)
            else:
                # If cluster is empty, reinitialize randomly
                centroids[i] = X[np.random.randint(len(X))]
        
        return centroids
    
    def _calculate_inertia(self, X: np.ndarray, labels: np.ndarray, centroids: np.ndarray) -> float:
        """
        Calculate within-cluster sum of squares (inertia).
        
        Args:
            X (np.ndarray): Feature matrix.
            labels (np.ndarray): Cluster assignments.
            centroids (np.ndarray): Centroids.
        
        Returns:
            float: Inertia value.
        """
        inertia = 0.0
        for i in range(self.k):
            cluster_points = X[labels == i]
            if len(cluster_points) > 0:
                inertia += np.sum((cluster_points - centroids[i]) ** 2)
        return inertia
    
    def fit(self, X: np.ndarray) -> 'KMeans':
        """
        Fit K-Means model to data.
        
        Args:
            X (np.ndarray): Feature matrix of shape (n_samples, n_features).
        
        Returns:
            KMeans: Returns self for method chaining.
        
        Raises:
            ValueError: If k is greater than number of samples.
        """
        X = np.array(X)
        
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        n_samples, n_features = X.shape
        
        if self.k > n_samples:
            raise ValueError(f"k ({self.k}) cannot be greater than number of samples ({n_samples})")
        
        # Initialize centroids
        self.centroids = self._initialize_centroids(X)
        
        # Main K-means loop
        for iteration in range(self.max_iterations):
            # Assign points to clusters
            new_labels = self._assign_clusters(X, self.centroids)
            
            # Update centroids
            new_centroids = self._update_centroids(X, new_labels)
            
            # Check for convergence
            if np.allclose(self.centroids, new_centroids, atol=self.tolerance):
                break
            
            self.centroids = new_centroids
            self.labels = new_labels
            self.n_iterations = iteration + 1
        
        # Final assignment and calculate inertia
        self.labels = self._assign_clusters(X, self.centroids)
        self.inertia = self._calculate_inertia(X, self.labels, self.centroids)
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict cluster labels for new data.
        
        Args:
            X (np.ndarray): Feature matrix of shape (n_samples, n_features).
        
        Returns:
            np.ndarray: Predicted cluster labels of shape (n_samples,).
        
        Raises:
            ValueError: If model hasn't been fitted yet.
        """
        if self.centroids is None:
            raise ValueError("Model must be fitted before making predictions")
        
        X = np.array(X)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        return self._assign_clusters(X, self.centroids)
    
    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        """
        Fit model and predict cluster labels for X.
        
        Args:
            X (np.ndarray): Feature matrix of shape (n_samples, n_features).
        
        Returns:
            np.ndarray: Predicted cluster labels of shape (n_samples,).
        """
        self.fit(X)
        return self.labels
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform X to cluster-distance space.
        
        Args:
            X (np.ndarray): Feature matrix of shape (n_samples, n_features).
        
        Returns:
            np.ndarray: Distances to each cluster center of shape (n_samples, k).
        
        Raises:
            ValueError: If model hasn't been fitted yet.
        """
        if self.centroids is None:
            raise ValueError("Model must be fitted before transforming")
        
        X = np.array(X)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        distances = np.sqrt(((X - self.centroids[:, np.newaxis]) ** 2).sum(axis=2))
        return distances.T
    
    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """
        Fit model and transform X to cluster-distance space.
        
        Args:
            X (np.ndarray): Feature matrix of shape (n_samples, n_features).
        
        Returns:
            np.ndarray: Distances to each cluster center of shape (n_samples, k).
        """
        self.fit(X)
        return self.transform(X)
    
    def get_params(self) -> dict:
        """
        Get parameters of the model.
        
        Returns:
            dict: Dictionary containing model parameters.
        """
        return {
            'k': self.k,
            'max_iterations': self.max_iterations,
            'tolerance': self.tolerance,
            'init': self.init,
            'random_state': self.random_state,
            'centroids': self.centroids,
            'inertia': self.inertia,
            'n_iterations': self.n_iterations
        }
