"""
Linear Regression implementation from scratch.

This module implements linear regression using ordinary least squares method
for both simple and multiple linear regression.
"""

import numpy as np
import pandas as pd
from typing import Optional, Union, List, Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.animation import FuncAnimation
import matplotlib.colors as mcolors
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
        normalize: bool = True,
        patience: int = 5,
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
            normalize (bool, optional): When using gradient descent, standardize
                features to zero-mean and unit-variance for stable convergence,
                and convert coefficients back to the original scale after fit.
                Defaults to True.
            patience (int, optional): Early-stopping patience (number of
                consecutive iterations where MSE change < tolerance before
                stopping). Defaults to 5.
        """
        self.fit_intercept = fit_intercept
        self.use_gradient_descent = use_gradient_descent
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.normalize = normalize
        self.patience = int(patience) if patience is not None else 5
        self.weights: Optional[np.ndarray] = None
        self.intercept: Optional[float] = None
        self._fit_history: list = []
        self._converged: bool = False
        self._effective_learning_rate: Optional[float] = None
    
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
            # Gradient descent solution with optional feature normalization
            n_samples, n_features = X.shape

            if self.normalize:
                x_mean = X.mean(axis=0)
                x_std = X.std(axis=0)
                x_std[x_std == 0] = 1.0
                Xs = (X - x_mean) / x_std
            else:
                Xs = X

            # Auto-tune learning rate if invalid/non-positive for stability
            lr = self.learning_rate
            if not np.isfinite(lr) or lr <= 0:
                # Spectral norm bound → safe step size for MSE GD
                # L = 2/n * s_max^2, lr < 1/L
                # Use a margin factor 1.5 for stability
                s_max = np.linalg.norm(Xs, 2)
                L = (2.0 / max(n_samples, 1)) * (s_max ** 2)
                lr = 1.0 / (L * 1.5) if L > 0 else 1e-3
            self._effective_learning_rate = float(lr)

            w_s = np.zeros(n_features)
            b_s = 0.0 if self.fit_intercept else 0.0

            previous_loss = np.inf
            stable_count = 0
            self._fit_history = []
            self._converged = False
            for it in range(self.max_iterations):
                # Predictions in scaled space
                y_pred = Xs @ w_s
                if self.fit_intercept:
                    y_pred = y_pred + b_s

                # Gradients (MSE loss)
                error = (y_pred - y)
                dw = (2.0 / n_samples) * (Xs.T @ error)
                if self.fit_intercept:
                    db = (2.0 / n_samples) * float(np.sum(error))

                # Gradient clipping to avoid explosion
                dw = np.clip(dw, -1e6, 1e6)
                if self.fit_intercept:
                    db = float(np.clip(db, -1e6, 1e6))

                # Update
                w_s = w_s - lr * dw
                if self.fit_intercept:
                    b_s = b_s - lr * db

                # Early stopping on loss improvement
                loss = float((error @ error) / n_samples)
                self._fit_history.append({'iter': it + 1, 'loss': loss})
                if abs(previous_loss - loss) < self.tolerance:
                    stable_count += 1
                    if stable_count >= max(1, self.patience):
                        self._converged = True
                        break
                else:
                    stable_count = 0
                previous_loss = loss

            # Convert scaled-space coefficients back to original feature scale
            if self.normalize:
                self.weights = w_s / x_std
                if self.fit_intercept:
                    self.intercept = b_s - float((x_mean / x_std) @ w_s)
                else:
                    self.intercept = 0.0
            else:
                self.weights = w_s
                self.intercept = b_s if self.fit_intercept else 0.0
        
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
            'patience': self.patience,
            'weights': self.weights,
            'intercept': self.intercept
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
        animation_path: str = 'lr_animation.gif'
    ) -> Dict[str, Any]:
        """
        Visualize the linear regression model's learning process with interactive plots.
        
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
        
        # For multiple features, use the first feature for visualization
        X_viz = X[:, 0].reshape(-1, 1) if X.shape[1] > 1 else X
        
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
        
        # Scatter plot with regression line evolution
        ax_scatter = fig.add_subplot(gs[0, :])
        ax_loss = fig.add_subplot(gs[1, 0])
        ax_equation = fig.add_subplot(gs[1, 1])
        
        # Plot data points
        sns.scatterplot(x=X_viz.flatten(), y=y, ax=ax_scatter, alpha=0.6)
        ax_scatter.set_title('Regression Line Evolution')
        if X.shape[1] > 1:
            ax_scatter.set_xlabel('First Feature (X₁)')
        
        # Store original parameters
        original_lr = self.learning_rate
        original_history = getattr(self, '_fit_history', [])
        
        # Fit the model if not already fitted
        if self.weights is None or not self.use_gradient_descent:
            self.use_gradient_descent = True
            self.fit(X, y)
            
        history = self._fit_history
        
        # Plot loss curve
        iterations = [h['iter'] for h in history]
        losses = [h['loss'] for h in history]
        sns.lineplot(x=iterations, y=losses, ax=ax_loss)
        ax_loss.set_title('Loss Curve')
        ax_loss.set_xlabel('Iteration')
        ax_loss.set_ylabel('MSE Loss')
        ax_loss.set_yscale('log')
        
        # Animation function for regression line
        line, = ax_scatter.plot([], [], 'r-', alpha=0.5)
        
        def init():
            line.set_data([], [])
            return line,
            
        def animate(frame):
            if frame >= len(history):
                return line,
            
            alpha = 0.3 + 0.7 * (frame / len(history))
            x_range = np.array([X_viz.min(), X_viz.max()])
            
            if frame == 0:
                w = 0.0
                b = 0.0
            else:
                # For multiple features, we'll show the evolution of the first feature's coefficient
                w = self.weights[0] * (frame / len(history))
                b = self.intercept * (frame / len(history))
                
            y_pred = x_range * w + b
            line.set_data(x_range, y_pred)
            line.set_alpha(alpha)
            
            return line,
            
        anim = FuncAnimation(
            fig, animate, init_func=init,
            frames=len(history),
            interval=animation_interval,
            blit=True
        )
        
        # Display final equation
        ax_equation.axis('off')
        if self.weights is not None and self.intercept is not None:
            if X.shape[1] > 1:
                # For multiple features, show the first feature coefficient and indicate others
                equation = f'y = {self.weights[0]:.4f}X₁ + ... + {self.intercept:.4f}\n'
                equation += f'(showing projection on X₁, total features: {X.shape[1]})'
            else:
                equation = f'y = {self.weights[0]:.4f}x + {self.intercept:.4f}'
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
                'scatter': ax_scatter,
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
        fig, (ax_lines, ax_loss) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Plot data points
        sns.scatterplot(x=X_viz.flatten(), y=y, ax=ax_lines, alpha=0.6)
        if X.shape[1] > 1:
            ax_lines.set_xlabel('First Feature (X₁)')
        
        # Colors for different learning rates
        colors = sns.color_palette('husl', n_colors=len(learning_rates))
        
        results = {}
        for lr, color in zip(learning_rates, colors):
            # Reset and fit model with current learning rate
            self.learning_rate = lr
            self.fit(X, y)
            
            # Plot final regression line
            x_range = np.array([X_viz.min(), X_viz.max()])
            # For multiple features, use only the first feature's coefficient
            w = self.weights[0] if X.shape[1] > 1 else self.weights
            y_pred = x_range * w + self.intercept
            ax_lines.plot(x_range, y_pred, color=color, 
                         label=f'lr={lr:.4f}')
            
            # Plot loss curve
            history = self._fit_history
            iterations = [h['iter'] for h in history]
            losses = [h['loss'] for h in history]
            ax_loss.plot(iterations, losses, color=color,
                        label=f'lr={lr:.4f}')
            
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
        ax_lines.set_title('Final Regression Lines')
        ax_lines.legend()
        
        ax_loss.set_title('Loss Curves')
        ax_loss.set_xlabel('Iteration')
        ax_loss.set_ylabel('MSE Loss')
        ax_loss.set_yscale('log')
        ax_loss.legend()
        
        plt.tight_layout()
        
        return {
            'figure': fig,
            'axes': {'lines': ax_lines, 'loss': ax_loss},
            'results': results
        }


def compare_methods(
    X: Union[np.ndarray, 'pd.DataFrame'],
    y: Union[np.ndarray, 'pd.Series'],
    *,
    fit_intercept: bool = True,
    learning_rate: float = 0.01,
    max_iterations: int = 1000,
    tolerance: float = 1e-8,
    normalize: bool = True,
    patience: int = 5,
    X_test: Optional[Union[np.ndarray, 'pd.DataFrame']] = None,
    y_test: Optional[Union[np.ndarray, 'pd.Series']] = None,
    return_report: bool = False,
    history_tail: int = 10,
) -> Union[dict, str]:
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
            'normal': {
                'train': {...}, 'test': {...}
            },
            'gradient_descent': {
                'train': {...}, 'test': {...}, 'history': [...],
                'delta': {
                    'weights_diff_l2', 'intercept_diff', 'r2_diff', 'mse_diff',
                    'effective_learning_rate', 'converged'
                }
            },
            'summary': {
                'train': {'r2_diff', 'mse_diff'},
                'test': {'r2_diff', 'mse_diff'} or None
            }
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
    res_ne_train = {
        'weights': model_ne.weights.copy() if model_ne.weights is not None else None,
        'intercept': float(model_ne.intercept),
        'r2': float(r2_score(yc, pred_ne)),
        'mse': float(mean_squared_error(yc, pred_ne)),
    }
    res_ne_test = None
    if X_test is not None and y_test is not None:
        Xt, yt = validate_and_convert_data(X_test, y_test)
        p = model_ne.predict(Xt)
        res_ne_test = {
            'r2': float(r2_score(yt, p)),
            'mse': float(mean_squared_error(yt, p)),
        }

    # Gradient descent
    model_gd = LinearRegression(
        fit_intercept=fit_intercept,
        use_gradient_descent=True,
        learning_rate=learning_rate,
        max_iterations=max_iterations,
        tolerance=tolerance,
        normalize=normalize,
        patience=patience,
    ).fit(Xc, yc)
    pred_gd = model_gd.predict(Xc)
    res_gd_train = {
        'weights': model_gd.weights.copy() if model_gd.weights is not None else None,
        'intercept': float(model_gd.intercept),
        'r2': float(r2_score(yc, pred_gd)),
        'mse': float(mean_squared_error(yc, pred_gd)),
    }
    res_gd_test = None
    if X_test is not None and y_test is not None:
        Xt, yt = validate_and_convert_data(X_test, y_test)
        p = model_gd.predict(Xt)
        res_gd_test = {
            'r2': float(r2_score(yt, p)),
            'mse': float(mean_squared_error(yt, p)),
        }

    # Differences summary (train)
    r2_diff_train = float(res_gd_train['r2'] - res_ne_train['r2'])
    mse_diff_train = float(res_gd_train['mse'] - res_ne_train['mse'])
    # Differences summary (test)
    if res_ne_test and res_gd_test:
        r2_diff_test = float(res_gd_test['r2'] - res_ne_test['r2'])
        mse_diff_test = float(res_gd_test['mse'] - res_ne_test['mse'])
        summary_test = {'r2_diff': r2_diff_test, 'mse_diff': mse_diff_test}
    else:
        summary_test = None

    # Parameter differences
    w_ne = res_ne_train['weights'] if res_ne_train['weights'] is not None else np.zeros_like(res_gd_train['weights'])
    w_gd = res_gd_train['weights'] if res_gd_train['weights'] is not None else np.zeros_like(w_ne)
    weights_diff_l2 = float(np.linalg.norm(w_gd - w_ne))
    intercept_diff = float(res_gd_train['intercept'] - res_ne_train['intercept'])

    result = {
        'normal': {
            'train': res_ne_train,
            'test': res_ne_test,
        },
        'gradient_descent': {
            'train': res_gd_train,
            'test': res_gd_test,
            'history': getattr(model_gd, '_fit_history', []),
            'delta': {
                'weights_diff_l2': weights_diff_l2,
                'intercept_diff': intercept_diff,
                'r2_diff': r2_diff_train,
                'mse_diff': mse_diff_train,
                'effective_learning_rate': getattr(model_gd, '_effective_learning_rate', None),
                'converged': getattr(model_gd, '_converged', False),
            }
        },
        'summary': {
            'train': {'r2_diff': r2_diff_train, 'mse_diff': mse_diff_train},
            'test': summary_test,
        }
    }

    if return_report:
        return format_comparison(result, history_tail=history_tail)
    return result


def format_comparison(comp: dict, *, history_tail: int = 10) -> str:
    """
    Build a user-friendly, multi-line comparison report for compare_methods output.

    Args:
        comp: The dict returned by compare_methods.
        history_tail: How many last GD iterations' losses to show.

    Returns:
        str: A formatted report string ready to print.
    """
    def fmtf(x):
        try:
            return f"{float(x):.4f}"
        except Exception:
            return str(x)

    lines = []
    ne_tr = comp['normal']['train']
    gd_tr = comp['gradient_descent']['train']
    ne_te = comp['normal']['test']
    gd_te = comp['gradient_descent']['test']
    delta = comp['gradient_descent'].get('delta', {})
    hist = comp['gradient_descent'].get('history', [])

    lines.append("--- Training Set Comparison ---\n")
    lines.append("Normal Method:")
    lines.append(f"  Weights: {ne_tr['weights']}")
    lines.append(f"  Intercept: {fmtf(ne_tr['intercept'])}")
    lines.append(f"  R²: {fmtf(ne_tr['r2'])}")
    lines.append(f"  MSE: {fmtf(ne_tr['mse'])}\n")

    lines.append("Gradient Descent Method:")
    lines.append(f"  Weights: {gd_tr['weights']}")
    lines.append(f"  Intercept: {fmtf(gd_tr['intercept'])}")
    lines.append(f"  R²: {fmtf(gd_tr['r2'])}")
    lines.append(f"  MSE: {fmtf(gd_tr['mse'])}\n")

    lines.append("Diffs (GD - Normal):")
    lines.append(f"  weights_diff_l2: {fmtf(delta.get('weights_diff_l2'))}")
    lines.append(f"  intercept_diff: {fmtf(delta.get('intercept_diff'))}")
    lines.append(f"  r2_diff: {fmtf(delta.get('r2_diff'))}")
    lines.append(f"  mse_diff: {fmtf(delta.get('mse_diff'))}")
    lines.append(f"  converged: {delta.get('converged')}")
    lines.append(f"  effective_lr: {delta.get('effective_learning_rate')}\n")

    lines.append("--- Test Set Comparison ---\n")
    if ne_te is not None:
        lines.append("Normal Method:")
        lines.append(f"  R²: {fmtf(ne_te['r2'])}")
        lines.append(f"  MSE: {fmtf(ne_te['mse'])}\n")
    if gd_te is not None:
        lines.append("Gradient Descent Method:")
        lines.append(f"  R²: {fmtf(gd_te['r2'])}")
        lines.append(f"  MSE: {fmtf(gd_te['mse'])}\n")

    # GD loss tail
    if hist:
        lines.append("GD Loss tail (last {} iters):".format(min(history_tail, len(hist))))
        for h in hist[-history_tail:]:
            lines.append(f"  iter={h['iter']}, loss={fmtf(h['loss'])}")

    return "\n".join(lines)
