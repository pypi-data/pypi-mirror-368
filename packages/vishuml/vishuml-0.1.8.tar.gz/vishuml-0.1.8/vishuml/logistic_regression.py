"""
Logistic Regression implementation from scratch.

This module implements binary logistic regression using gradient descent
for classification tasks, with advanced visualization and comparison capabilities.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.animation import FuncAnimation
from typing import Optional, Union, List, Dict, Any, Tuple
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
        tolerance (float): Early stopping tolerance.
        normalize (bool): Whether to normalize features.
        patience (int): Early stopping patience.
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
    
    def __init__(
        self,
        learning_rate: float = 0.01,
        max_iterations: int = 1000,
        fit_intercept: bool = True,
        tolerance: float = 1e-8,
        normalize: bool = True,
        patience: int = 5
    ):
        """
        Initialize Logistic Regression model.
        
        Args:
            learning_rate (float, optional): Learning rate for gradient descent.
                Defaults to 0.01.
            max_iterations (int, optional): Maximum number of iterations.
                Defaults to 1000.
            fit_intercept (bool, optional): Whether to calculate the intercept.
                Defaults to True.
            tolerance (float, optional): Early stopping tolerance.
                Defaults to 1e-8.
            normalize (bool, optional): Whether to normalize features.
                Defaults to True.
            patience (int, optional): Early stopping patience.
                Defaults to 5.
        """
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.fit_intercept = fit_intercept
        self.tolerance = tolerance
        self.normalize = normalize
        self.patience = patience
        self.weights: Optional[np.ndarray] = None
        self.intercept: Optional[float] = None
        self._fit_history: List[Dict[str, float]] = []
        self._converged: bool = False
        self._effective_learning_rate: Optional[float] = None
        self._feature_means: Optional[np.ndarray] = None
        self._feature_stds: Optional[np.ndarray] = None
    
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
    
    def _normalize_features(self, X: np.ndarray, fit: bool = True) -> np.ndarray:
        """
        Normalize features to zero mean and unit variance.
        
        Args:
            X (np.ndarray): Feature matrix.
            fit (bool): Whether to compute means and stds (True) or use stored values (False).
        
        Returns:
            np.ndarray: Normalized features.
        """
        if fit:
            self._feature_means = np.mean(X, axis=0)
            self._feature_stds = np.std(X, axis=0)
            self._feature_stds[self._feature_stds == 0] = 1.0
        
        return (X - self._feature_means) / self._feature_stds
    
    def _compute_cost(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Compute binary cross-entropy loss.
        
        Args:
            y_true (np.ndarray): True labels.
            y_pred (np.ndarray): Predicted probabilities.
        
        Returns:
            float: Loss value.
        """
        epsilon = 1e-15
        y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
        return -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))
    
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
        """
        # Convert and validate input data
        X, y = validate_and_convert_data(X, y)
        n_samples, n_features = X.shape
        
        # Normalize features if requested
        if self.normalize:
            X = self._normalize_features(X, fit=True)
        
        # Initialize weights and intercept
        self.weights = np.zeros(n_features)
        self.intercept = 0.0 if self.fit_intercept else None
        
        # Auto-tune learning rate if needed
        lr = self.learning_rate
        if not np.isfinite(lr) or lr <= 0:
            s_max = np.linalg.norm(X, 2)
            L = (0.25 / max(n_samples, 1)) * (s_max ** 2)
            lr = 1.0 / (L * 1.5) if L > 0 else 1e-3
        self._effective_learning_rate = float(lr)
        
        # Initialize history
        self._fit_history = []
        self._converged = False
        previous_loss = np.inf
        stable_count = 0
        
        # Gradient descent
        for it in range(self.max_iterations):
            # Forward pass
            linear_pred = X @ self.weights
            if self.fit_intercept:
                linear_pred += self.intercept
            
            predictions = self._sigmoid(linear_pred)
            
            # Compute loss
            loss = self._compute_cost(y, predictions)
            self._fit_history.append({'iter': it + 1, 'loss': loss})
            
            # Early stopping check
            if abs(previous_loss - loss) < self.tolerance:
                stable_count += 1
                if stable_count >= max(1, self.patience):
                    self._converged = True
                    break
            else:
                stable_count = 0
            previous_loss = loss
            
            # Compute gradients
            error = predictions - y
            dw = (1 / n_samples) * X.T @ error
            if self.fit_intercept:
                db = (1 / n_samples) * np.sum(error)
            
            # Gradient clipping
            dw = np.clip(dw, -1e6, 1e6)
            if self.fit_intercept:
                db = float(np.clip(db, -1e6, 1e6))
            
            # Update parameters
            self.weights -= lr * dw
            if self.fit_intercept:
                self.intercept -= lr * db
        
        # Convert weights back to original scale if normalized
        if self.normalize:
            self.weights = self.weights / self._feature_stds
            if self.fit_intercept:
                self.intercept = self.intercept - float((self._feature_means / self._feature_stds) @ self.weights)
        
        return self
    
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
        
        # Normalize if needed
        if self.normalize:
            X = (X - self._feature_means) / self._feature_stds
        
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
            'tolerance': self.tolerance,
            'normalize': self.normalize,
            'patience': self.patience,
            'weights': self.weights,
            'intercept': self.intercept,
            'converged': self._converged,
            'effective_learning_rate': self._effective_learning_rate
        }
    
    def visualize_lr(
        self,
        X: Union[np.ndarray, 'pd.DataFrame'],
        y: Union[np.ndarray, 'pd.Series'],
        *,
        compare_lr: bool = False,
        learning_rates: Optional[List[float]] = None,
        animation_interval: int = 200,
        n_iterations_display: int = 5,
        figsize: tuple = (15, 10),
        style: str = 'whitegrid',
        palette: str = 'husl',
        save_animation: bool = False,
        animation_path: str = 'logistic_animation.gif'
    ) -> Dict[str, Any]:
        """
        Visualize the logistic regression model's learning process with interactive plots.
        
        Args:
            X: Features matrix
            y: Target vector
            compare_lr: If True, compares different learning rates
            learning_rates: List of learning rates to compare when compare_lr=True
            animation_interval: Interval between animation frames in milliseconds
            n_iterations_display: Number of iterations to display in evolution plot
            figsize: Figure size for the plots
            style: Seaborn style for plots
            palette: Color palette for plots
            save_animation: Whether to save the animation as a GIF
            animation_path: Path to save the animation if save_animation=True
            
        Returns:
            dict: Dictionary containing plot objects and animation if created
        """
        # Convert and validate input data
        X, y = validate_and_convert_data(X, y)
        
        # For multiple features, use the first two features for visualization
        if X.shape[1] > 2:
            X_viz = X[:, :2]
            print("Note: Using first two features for visualization")
        else:
            X_viz = X
        
        # Set the style
        sns.set_style(style)
        plt.rcParams['figure.figsize'] = figsize
        
        if compare_lr:
            if learning_rates is None:
                learning_rates = [0.001, 0.01, 0.1, 0.5]
            return self._compare_learning_rates(X, y, X_viz, learning_rates)
        
        # Create figure with subplots
        fig = plt.figure(figsize=figsize)
        gs = plt.GridSpec(2, 2)
        
        # Decision boundary plot
        ax_boundary = fig.add_subplot(gs[0, :])
        ax_loss = fig.add_subplot(gs[1, 0])
        ax_equation = fig.add_subplot(gs[1, 1])
        
        # Plot data points
        scatter = ax_boundary.scatter(X_viz[:, 0], X_viz[:, 1], c=y, cmap='coolwarm', alpha=0.6)
        ax_boundary.set_title('Decision Boundary Evolution')
        
        # Store original parameters
        original_lr = self.learning_rate
        original_history = getattr(self, '_fit_history', [])
        
        # Fit the model if not already fitted
        if self.weights is None:
            self.fit(X, y)
        
        history = self._fit_history
        
        # Plot loss curve
        iterations = [h['iter'] for h in history]
        losses = [h['loss'] for h in history]
        sns.lineplot(x=iterations, y=losses, ax=ax_loss)
        ax_loss.set_title('Loss Curve')
        ax_loss.set_xlabel('Iteration')
        ax_loss.set_ylabel('Binary Cross-Entropy Loss')
        ax_loss.set_yscale('log')
        
        # Create mesh grid for decision boundary
        x_min, x_max = X_viz[:, 0].min() - 1, X_viz[:, 0].max() + 1
        y_min, y_max = X_viz[:, 1].min() - 1, X_viz[:, 1].max() + 1
        xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100),
                           np.linspace(y_min, y_max, 100))
        
        # Animation function for decision boundary
        boundary = None
        
        def init():
            nonlocal boundary
            if boundary is not None:
                boundary.remove()
            return []
        
        def animate(frame):
            nonlocal boundary
            if frame >= len(history):
                return []
            
            if boundary is not None:
                boundary.remove()
            
            # For animation, interpolate weights
            progress = frame / len(history)
            current_weights = self.weights[:2] * progress
            current_intercept = self.intercept * progress if self.intercept is not None else 0
            
            # Create mesh grid points
            mesh_points = np.c_[xx.ravel(), yy.ravel()]
            if X.shape[1] > 2:
                # Add mean values for other features
                extra_features = np.tile(X[:, 2:].mean(axis=0), (mesh_points.shape[0], 1))
                mesh_points = np.hstack([mesh_points, extra_features])
            
            # Compute decision boundary
            Z = self._sigmoid(mesh_points @ self.weights + self.intercept)
            Z = Z.reshape(xx.shape)
            
            # Plot decision boundary
            boundary = ax_boundary.contourf(xx, yy, Z, alpha=0.3, levels=np.linspace(0, 1, 11),
                                         cmap='coolwarm')
            
            return [boundary]
        
        anim = FuncAnimation(
            fig, animate, init_func=init,
            frames=len(history),
            interval=animation_interval,
            blit=True
        )
        
        # Display final equation
        ax_equation.axis('off')
        if self.weights is not None and self.intercept is not None:
            if X.shape[1] > 2:
                equation = f'logit(p) = {self.weights[0]:.4f}X₁ + {self.weights[1]:.4f}X₂ + ... + {self.intercept:.4f}'
                equation += f'\n(showing projection on X₁,X₂, total features: {X.shape[1]})'
            else:
                equation = f'logit(p) = {self.weights[0]:.4f}X₁ + {self.weights[1]:.4f}X₂ + {self.intercept:.4f}'
            ax_equation.text(0.5, 0.5, equation,
                          horizontalalignment='center',
                          verticalalignment='center',
                          fontsize=12,
                          bbox=dict(facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        if save_animation:
            anim.save(animation_path, writer='pillow')
        
        return {
            'figure': fig,
            'animation': anim,
            'axes': {
                'boundary': ax_boundary,
                'loss': ax_loss,
                'equation': ax_equation
            }
        }
    
    def _compare_learning_rates(
        self,
        X: np.ndarray,
        y: np.ndarray,
        X_viz: np.ndarray,
        learning_rates: List[float]
    ) -> Dict[str, Any]:
        """
        Compare different learning rates and visualize their effects.
        """
        # Store original parameters
        original_lr = self.learning_rate
        original_history = getattr(self, '_fit_history', [])
        
        # Create figure
        fig, (ax_boundary, ax_loss) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Plot data points
        scatter = ax_boundary.scatter(X_viz[:, 0], X_viz[:, 1], c=y, cmap='coolwarm', alpha=0.6)
        if X.shape[1] > 2:
            ax_boundary.set_xlabel('First Feature (X₁)')
            ax_boundary.set_ylabel('Second Feature (X₂)')
        
        # Colors for different learning rates
        colors = sns.color_palette('husl', n_colors=len(learning_rates))
        
        # Create mesh grid for decision boundary
        x_min, x_max = X_viz[:, 0].min() - 1, X_viz[:, 0].max() + 1
        y_min, y_max = X_viz[:, 1].min() - 1, X_viz[:, 1].max() + 1
        xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100),
                           np.linspace(y_min, y_max, 100))
        
        results = {}
        for lr, color in zip(learning_rates, colors):
            # Reset and fit model with current learning rate
            self.learning_rate = lr
            self.fit(X, y)
            
            # Plot decision boundary
            mesh_points = np.c_[xx.ravel(), yy.ravel()]
            if X.shape[1] > 2:
                extra_features = np.tile(X[:, 2:].mean(axis=0), (mesh_points.shape[0], 1))
                mesh_points = np.hstack([mesh_points, extra_features])
            
            Z = self._sigmoid(mesh_points @ self.weights + self.intercept)
            Z = Z.reshape(xx.shape)
            ax_boundary.contour(xx, yy, Z, levels=[0.5], colors=[color],
                              label=f'lr={lr:.4f}')
            
            # Plot loss curve
            history = self._fit_history
            iterations = [h['iter'] for h in history]
            losses = [h['loss'] for h in history]
            ax_loss.plot(iterations, losses, color=color, label=f'lr={lr:.4f}')
            
            results[lr] = {
                'weights': self.weights.copy(),
                'intercept': self.intercept,
                'history': history.copy(),
                'converged': self._converged
            }
        
        # Restore original parameters
        self.learning_rate = original_lr
        self._fit_history = original_history
        
        # Customize plots
        ax_boundary.set_title('Decision Boundaries')
        ax_boundary.legend()
        
        ax_loss.set_title('Loss Curves')
        ax_loss.set_xlabel('Iteration')
        ax_loss.set_ylabel('Binary Cross-Entropy Loss')
        ax_loss.set_yscale('log')
        ax_loss.legend()
        
        plt.tight_layout()
        
        return {
            'figure': fig,
            'axes': {'boundary': ax_boundary, 'loss': ax_loss},
            'results': results
        }


def compare_methods(
    X: Union[np.ndarray, 'pd.DataFrame'],
    y: Union[np.ndarray, 'pd.Series'],
    *,
    models: List[Dict[str, Any]] = None,
    X_test: Optional[Union[np.ndarray, 'pd.DataFrame']] = None,
    y_test: Optional[Union[np.ndarray, 'pd.Series']] = None,
    return_report: bool = False
) -> Union[dict, str]:
    """
    Compare different logistic regression configurations.
    
    Args:
        X: Features as numpy array or pandas DataFrame.
        y: Target as numpy array or pandas Series.
        models: List of model configurations to compare.
        X_test: Optional test features.
        y_test: Optional test targets.
        return_report: Whether to return formatted report string.
    
    Returns:
        dict or str: Comparison results or formatted report.
    """
    if models is None:
        models = [
            {'name': 'Default', 'params': {}},
            {'name': 'High LR', 'params': {'learning_rate': 0.1}},
            {'name': 'Low LR', 'params': {'learning_rate': 0.001}},
            {'name': 'No Intercept', 'params': {'fit_intercept': False}},
            {'name': 'No Normalization', 'params': {'normalize': False}}
        ]
    
    X_conv, y_conv = validate_and_convert_data(X, y)
    results = {}
    
    for model_config in models:
        name = model_config['name']
        params = model_config['params']
        
        # Train model
        model = LogisticRegression(**params)
        model.fit(X_conv, y_conv)
        
        # Evaluate
        train_pred = model.predict(X_conv)
        train_proba = model.predict_proba(X_conv)
        train_results = {
            'accuracy': float(np.mean(y_conv == train_pred)),
            'loss': float(model._compute_cost(y_conv, train_proba)),
            'params': model.get_params()
        }
        
        # Test set evaluation
        test_results = None
        if X_test is not None and y_test is not None:
            X_test_conv, y_test_conv = validate_and_convert_data(X_test, y_test)
            test_pred = model.predict(X_test_conv)
            test_proba = model.predict_proba(X_test_conv)
            test_results = {
                'accuracy': float(np.mean(y_test_conv == test_pred)),
                'loss': float(model._compute_cost(y_test_conv, test_proba))
            }
        
        results[name] = {
            'train': train_results,
            'test': test_results,
            'history': model._fit_history
        }
    
    if return_report:
        return format_comparison(results)
    return results


def format_comparison(results: dict) -> str:
    """
    Format comparison results into a readable report.
    
    Args:
        results: Dictionary of comparison results.
    
    Returns:
        str: Formatted report string.
    """
    def fmtf(x):
        try:
            return f"{float(x):.4f}"
        except Exception:
            return str(x)
    
    lines = []
    lines.append("=== Logistic Regression Model Comparison ===\n")
    
    for name, result in results.items():
        lines.append(f"Model: {name}")
        train_results = result['train']
        test_results = result['test']
        
        lines.append("\nTraining Results:")
        lines.append(f"  Accuracy: {fmtf(train_results['accuracy'])}")
        lines.append(f"  Loss: {fmtf(train_results['loss'])}")
        
        params = train_results['params']
        lines.append("\nParameters:")
        lines.append(f"  Learning Rate: {fmtf(params['learning_rate'])}")
        lines.append(f"  Converged: {params['converged']}")
        lines.append(f"  Effective LR: {fmtf(params['effective_learning_rate'])}")
        lines.append(f"  Iterations: {len(result['history'])}")
        
        if test_results:
            lines.append("\nTest Results:")
            lines.append(f"  Accuracy: {fmtf(test_results['accuracy'])}")
            lines.append(f"  Loss: {fmtf(test_results['loss'])}")
        
        lines.append("\n" + "="*50 + "\n")
    
    return "\n".join(lines)