"""
Decision Tree implementation from scratch.

This module implements a decision tree classifier using the CART algorithm
with information gain (entropy) for splitting criteria.
"""

import numpy as np
from typing import Optional, Union, Dict, Any
from collections import Counter


class DecisionTreeNode:
    """
    Node class for Decision Tree.
    
    Attributes:
        feature_index (int): Index of feature used for splitting.
        threshold (float): Threshold value for splitting.
        left (DecisionTreeNode): Left child node.
        right (DecisionTreeNode): Right child node.
        value (Any): Value for leaf nodes (class label or regression value).
        is_leaf (bool): Whether this node is a leaf.
    """
    
    def __init__(self, feature_index: Optional[int] = None, threshold: Optional[float] = None,
                 left: Optional['DecisionTreeNode'] = None, right: Optional['DecisionTreeNode'] = None,
                 value: Optional[Any] = None):
        """
        Initialize DecisionTreeNode.
        
        Args:
            feature_index (int, optional): Feature index for splitting.
            threshold (float, optional): Threshold for splitting.
            left (DecisionTreeNode, optional): Left child.
            right (DecisionTreeNode, optional): Right child.
            value (Any, optional): Value for leaf nodes.
        """
        self.feature_index = feature_index
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value
        self.is_leaf = value is not None


class DecisionTree:
    """
    Decision Tree classifier using CART algorithm.
    
    Decision tree builds a tree-like model of decisions by recursively splitting
    the dataset based on feature values that maximize information gain.
    
    Attributes:
        max_depth (int): Maximum depth of the tree.
        min_samples_split (int): Minimum samples required to split a node.
        min_samples_leaf (int): Minimum samples required at a leaf node.
        max_features (int): Maximum features to consider for splitting.
        root (DecisionTreeNode): Root node of the tree.
    
    Examples:
        >>> from vishuml.decision_tree import DecisionTree
        >>> import numpy as np
        >>> X = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
        >>> y = np.array([0, 0, 1, 1])
        >>> model = DecisionTree(max_depth=3)
        >>> model.fit(X, y)
        >>> predictions = model.predict([[2.5, 3.5]])
        >>> print(predictions)
        [1]
    """
    
    def __init__(self, max_depth: int = 10, min_samples_split: int = 2,
                 min_samples_leaf: int = 1, max_features: Optional[int] = None):
        """
        Initialize Decision Tree model.
        
        Args:
            max_depth (int, optional): Maximum depth of tree. Defaults to 10.
            min_samples_split (int, optional): Minimum samples to split. Defaults to 2.
            min_samples_leaf (int, optional): Minimum samples in leaf. Defaults to 1.
            max_features (int, optional): Maximum features to consider. Defaults to None (all features).
        """
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.max_features = max_features
        self.root: Optional[DecisionTreeNode] = None
    
    def _entropy(self, y: np.ndarray) -> float:
        """
        Calculate entropy of target variable.
        
        Args:
            y (np.ndarray): Target variable.
        
        Returns:
            float: Entropy value.
        """
        if len(y) == 0:
            return 0
        
        proportions = np.bincount(y) / len(y)
        entropy = -np.sum([p * np.log2(p) for p in proportions if p > 0])
        return entropy
    
    def _information_gain(self, y: np.ndarray, left_y: np.ndarray, right_y: np.ndarray) -> float:
        """
        Calculate information gain from a split.
        
        Args:
            y (np.ndarray): Original target variable.
            left_y (np.ndarray): Left split target variable.
            right_y (np.ndarray): Right split target variable.
        
        Returns:
            float: Information gain.
        """
        n = len(y)
        n_left = len(left_y)
        n_right = len(right_y)
        
        if n_left == 0 or n_right == 0:
            return 0
        
        entropy_parent = self._entropy(y)
        entropy_left = self._entropy(left_y)
        entropy_right = self._entropy(right_y)
        
        weighted_entropy = (n_left / n) * entropy_left + (n_right / n) * entropy_right
        information_gain = entropy_parent - weighted_entropy
        
        return information_gain
    
    def _best_split(self, X: np.ndarray, y: np.ndarray) -> tuple:
        """
        Find the best feature and threshold for splitting.
        
        Args:
            X (np.ndarray): Feature matrix.
            y (np.ndarray): Target variable.
        
        Returns:
            tuple: (best_feature_index, best_threshold, best_gain).
        """
        n_samples, n_features = X.shape
        
        if self.max_features is not None:
            feature_indices = np.random.choice(n_features, 
                                             min(self.max_features, n_features), 
                                             replace=False)
        else:
            feature_indices = range(n_features)
        
        best_gain = -1
        best_feature_index = None
        best_threshold = None
        
        for feature_index in feature_indices:
            feature_values = X[:, feature_index]
            thresholds = np.unique(feature_values)
            
            for threshold in thresholds:
                left_mask = feature_values <= threshold
                right_mask = ~left_mask
                
                if np.sum(left_mask) < self.min_samples_leaf or \
                   np.sum(right_mask) < self.min_samples_leaf:
                    continue
                
                left_y = y[left_mask]
                right_y = y[right_mask]
                
                gain = self._information_gain(y, left_y, right_y)
                
                if gain > best_gain:
                    best_gain = gain
                    best_feature_index = feature_index
                    best_threshold = threshold
        
        return best_feature_index, best_threshold, best_gain
    
    def _build_tree(self, X: np.ndarray, y: np.ndarray, depth: int = 0) -> DecisionTreeNode:
        """
        Recursively build the decision tree.
        
        Args:
            X (np.ndarray): Feature matrix.
            y (np.ndarray): Target variable.
            depth (int, optional): Current depth. Defaults to 0.
        
        Returns:
            DecisionTreeNode: Root node of the subtree.
        """
        n_samples = len(y)
        n_classes = len(np.unique(y))
        
        # Stopping criteria
        if (depth >= self.max_depth or 
            n_samples < self.min_samples_split or 
            n_classes == 1):
            # Create leaf node
            most_common_class = Counter(y).most_common(1)[0][0]
            return DecisionTreeNode(value=most_common_class)
        
        # Find best split
        feature_index, threshold, gain = self._best_split(X, y)
        
        if feature_index is None or gain <= 0:
            # Create leaf node if no good split found
            most_common_class = Counter(y).most_common(1)[0][0]
            return DecisionTreeNode(value=most_common_class)
        
        # Split data
        left_mask = X[:, feature_index] <= threshold
        right_mask = ~left_mask
        
        # Recursively build left and right subtrees
        left_subtree = self._build_tree(X[left_mask], y[left_mask], depth + 1)
        right_subtree = self._build_tree(X[right_mask], y[right_mask], depth + 1)
        
        return DecisionTreeNode(feature_index, threshold, left_subtree, right_subtree)
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'DecisionTree':
        """
        Fit decision tree to training data.
        
        Args:
            X (np.ndarray): Training feature matrix of shape (n_samples, n_features).
            y (np.ndarray): Training target vector of shape (n_samples,).
        
        Returns:
            DecisionTree: Returns self for method chaining.
        
        Raises:
            ValueError: If X and y have incompatible shapes.
        """
        X = np.array(X)
        y = np.array(y)
        
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        if X.shape[0] != len(y):
            raise ValueError("X and y must have the same number of samples")
        
        # Convert string labels to integers if necessary
        if y.dtype == object or y.dtype.kind in 'SU':
            unique_labels = np.unique(y)
            label_to_int = {label: i for i, label in enumerate(unique_labels)}
            y = np.array([label_to_int[label] for label in y])
            self._label_mapping = {i: label for label, i in label_to_int.items()}
        else:
            self._label_mapping = None
        
        self.root = self._build_tree(X, y)
        return self
    
    def _predict_sample(self, x: np.ndarray, node: DecisionTreeNode) -> Any:
        """
        Predict single sample using the tree.
        
        Args:
            x (np.ndarray): Single sample.
            node (DecisionTreeNode): Current node.
        
        Returns:
            Any: Predicted class label.
        """
        if node.is_leaf:
            if self._label_mapping is not None:
                return self._label_mapping[node.value]
            return node.value
        
        if x[node.feature_index] <= node.threshold:
            return self._predict_sample(x, node.left)
        else:
            return self._predict_sample(x, node.right)
    
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
        if self.root is None:
            raise ValueError("Model must be fitted before making predictions")
        
        X = np.array(X)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        predictions = [self._predict_sample(x, self.root) for x in X]
        return np.array(predictions)
    
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
            'max_depth': self.max_depth,
            'min_samples_split': self.min_samples_split,
            'min_samples_leaf': self.min_samples_leaf,
            'max_features': self.max_features
        }
