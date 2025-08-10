# VishuML

A comprehensive machine learning library implementing fundamental algorithms from scratch in Python. This library provides educational implementations of popular ML algorithms without relying on external ML frameworks like scikit-learn.

## Features

**🎯 sklearn-compatible API** - Works seamlessly with pandas DataFrames and CSV data!

VishuML implements the following machine learning algorithms:

### Supervised Learning

- **Linear Regression** - For continuous target prediction
- **Logistic Regression** - For binary classification
- **K-Nearest Neighbors (KNN)** - For classification and regression
- **Support Vector Machine (SVM)** - For binary classification with linear and RBF kernels
- **Decision Tree** - For classification using CART algorithm
- **Naive Bayes** - Gaussian Naive Bayes for classification
- **Perceptron** - Linear binary classifier

### Unsupervised Learning

- **K-Means Clustering** - For data clustering

### Utilities

- Data splitting (train/test split)
- Evaluation metrics (accuracy, R², MSE)
- Distance functions
- Data normalization
- Confusion matrix

## Installation

### From PyPI (when published)

```bash
pip install vishuml
```

### From Source

```bash
git clone https://github.com/vishuRizz/vishuml.git
cd vishuml
pip install -e .
```

## Quick Start

### 🚀 Works with pandas DataFrames (Just like sklearn!)

```python
import pandas as pd
from vishuml import LinearRegression, LogisticRegression
from vishuml.utils import train_test_split, r2_score, accuracy_score

# Load your CSV data (just like sklearn!)
df = pd.read_csv('your_data.csv')
X = df[['feature1', 'feature2', 'feature3']]  # Select features
y = df['target']                               # Select target

# Train-test split (works with DataFrames!)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model (accepts DataFrames!)
model = LinearRegression()
model.fit(X_train, y_train)  # DataFrame input!

# Make predictions (works with DataFrames!)
predictions = model.predict(X_test)
score = model.score(X_test, y_test)
print(f"R² Score: {score:.4f}")

# Classification Example with real data
from vishuml import datasets as ds
X, y = ds.load_iris()

# Convert to DataFrame for realistic workflow
iris_df = pd.DataFrame(X, columns=['sepal_length', 'sepal_width', 'petal_length', 'petal_width'])
iris_df['species'] = y

# sklearn-like feature selection
features = iris_df[['sepal_length', 'sepal_width', 'petal_length', 'petal_width']]
target = (iris_df['species'] == 0).astype(int)  # Binary classification

X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.3)

classifier = LogisticRegression()
classifier.fit(X_train, y_train)  # DataFrame input!
accuracy = classifier.score(X_test, y_test)
print(f"Accuracy: {accuracy:.4f}")
```

### Traditional NumPy Arrays

```python
import numpy as np
from vishuml import LinearRegression, KMeans

# NumPy arrays also work (backward compatibility)
X = np.array([[1], [2], [3], [4], [5]])
y = np.array([2, 4, 6, 8, 10])

model = LinearRegression()
model.fit(X, y)
predictions = model.predict([[6], [7]])
print(f"Predictions: {predictions}")  # Should be close to [12, 14]

# Clustering Example
X = np.array([[1, 2], [1, 4], [1, 0], [10, 2], [10, 4], [10, 0]])
kmeans = KMeans(k=2, random_state=42)
clusters = kmeans.fit_predict(X)
print(f"Cluster labels: {clusters}")
```

## Algorithm Documentation

### Linear Regression

```python
from vishuml import LinearRegression

# Create and train model
model = LinearRegression(fit_intercept=True)
model.fit(X_train, y_train)

# Make predictions
predictions = model.predict(X_test)

# Get R² score
score = model.score(X_test, y_test)
```

### Logistic Regression

```python
from vishuml import LogisticRegression

# Create and train model
model = LogisticRegression(learning_rate=0.01, max_iterations=1000)
model.fit(X_train, y_train)

# Make predictions
predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)

# Get accuracy
accuracy = model.score(X_test, y_test)
```

### K-Nearest Neighbors

```python
from vishuml import KNearestNeighbors

# For classification
knn_clf = KNearestNeighbors(k=3, task_type='classification')
knn_clf.fit(X_train, y_train)
predictions = knn_clf.predict(X_test)

# For regression
knn_reg = KNearestNeighbors(k=5, task_type='regression')
knn_reg.fit(X_train, y_train)
predictions = knn_reg.predict(X_test)
```

### Support Vector Machine

```python
from vishuml import SupportVectorMachine

# Linear SVM
svm_linear = SupportVectorMachine(C=1.0, kernel='linear')
svm_linear.fit(X_train, y_train)

# RBF SVM
svm_rbf = SupportVectorMachine(C=1.0, kernel='rbf', gamma=1.0)
svm_rbf.fit(X_train, y_train)

predictions = svm_rbf.predict(X_test)
decision_scores = svm_rbf.decision_function(X_test)
```

### Decision Tree

```python
from vishuml import DecisionTree

# Create and train model
tree = DecisionTree(max_depth=5, min_samples_split=2, min_samples_leaf=1)
tree.fit(X_train, y_train)

# Make predictions
predictions = tree.predict(X_test)
accuracy = tree.score(X_test, y_test)
```

### Naive Bayes

```python
from vishuml import NaiveBayes

# Create and train model
nb = NaiveBayes()
nb.fit(X_train, y_train)

# Make predictions
predictions = nb.predict(X_test)
probabilities = nb.predict_proba(X_test)
```

### Perceptron

```python
from vishuml import Perceptron

# Create and train model
perceptron = Perceptron(learning_rate=0.01, max_iterations=1000)
perceptron.fit(X_train, y_train)

# Make predictions
predictions = perceptron.predict(X_test)
decision_scores = perceptron.decision_function(X_test)
```

### K-Means Clustering

```python
from vishuml import KMeans

# Create and train model
kmeans = KMeans(k=3, init='k-means++', random_state=42)
kmeans.fit(X)

# Get cluster labels
labels = kmeans.labels
# Or predict for new data
new_labels = kmeans.predict(X_new)

# Transform to distance space
distances = kmeans.transform(X)
```

## Utility Functions

```python
from vishuml.utils import (
    train_test_split, accuracy_score, r2_score,
    mean_squared_error, euclidean_distance,
    normalize, confusion_matrix
)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Evaluate predictions
accuracy = accuracy_score(y_true, y_pred)
r2 = r2_score(y_true, y_pred)
mse = mean_squared_error(y_true, y_pred)

# Normalize features
X_normalized = normalize(X)

# Confusion matrix
cm = confusion_matrix(y_true, y_pred)
```

## Sample Datasets

The library includes sample datasets in CSV format:

- `datasets/iris.csv` - Classic iris flower classification dataset
- `datasets/housing.csv` - Housing price regression dataset
- `datasets/wine.csv` - Wine quality classification dataset

```python
import pandas as pd
import os

# Load sample datasets
iris_data = pd.read_csv('datasets/iris.csv')
housing_data = pd.read_csv('datasets/housing.csv')
wine_data = pd.read_csv('datasets/wine.csv')
```

## Examples

Check out the `examples/` directory for Jupyter notebook tutorials demonstrating each algorithm:

- `examples/linear_regression_example.ipynb`
- `examples/logistic_regression_example.ipynb`
- `examples/knn_example.ipynb`
- `examples/svm_example.ipynb`
- `examples/decision_tree_example.ipynb`
- `examples/naive_bayes_example.ipynb`
- `examples/perceptron_example.ipynb`
- `examples/kmeans_example.ipynb`

## Development

### Setup Development Environment

```bash
git clone https://github.com/vishuRizz/vishuml.git
cd vishuml
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/ -v --cov=vishuml
```

### Code Formatting

```bash
black vishuml/
flake8 vishuml/
```

## Requirements

- Python >= 3.7
- NumPy >= 1.19.0

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Educational Purpose

This library is designed for educational purposes to help understand how machine learning algorithms work under the hood. For production use, consider using mature libraries like scikit-learn, which are more optimized and feature-complete.

## Author

**Vishu** - [GitHub Profile](https://github.com/vishuRizz)

## Acknowledgments

- Inspired by scikit-learn's API design
- Algorithms implemented based on standard textbook descriptions
- Built for educational and learning purposes

