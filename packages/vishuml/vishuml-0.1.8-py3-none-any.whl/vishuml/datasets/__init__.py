"""
Dataset loader utilities for packaged CSV datasets.

These functions use importlib.resources to load CSV files that are shipped
inside the installed package, so users don't need repo-relative paths.
"""

from __future__ import annotations

import io
import csv
from importlib import resources
from typing import Tuple

import numpy as np


def _read_text_resource(resource_name: str) -> str:
    with resources.files(__package__).joinpath(resource_name).open("rb") as f:
        return f.read().decode("utf-8")


def _load_numeric_csv(resource_name: str) -> np.ndarray:
    """Load numeric-only CSV (with header) into a 2D float array."""
    data = _read_text_resource(resource_name)
    return np.genfromtxt(io.StringIO(data), delimiter=",", skip_header=1, dtype=float)


def load_iris() -> Tuple[np.ndarray, np.ndarray]:
    """
    Load the classic Iris dataset.

    Returns:
        (X, y): Features (n_samples, 4) and integer labels (n_samples,).
    """
    text = _read_text_resource("iris.csv")
    reader = csv.reader(io.StringIO(text))
    header = next(reader, None)  # skip header
    rows = list(reader)
    X = np.array([[float(r[0]), float(r[1]), float(r[2]), float(r[3])] for r in rows], dtype=float)
    classes = {"setosa": 0, "versicolor": 1, "virginica": 2}
    y = np.array([classes[r[4]] for r in rows], dtype=int)
    return X, y


def load_housing() -> Tuple[np.ndarray, np.ndarray]:
    """
    Load the sample housing dataset.

    Returns:
        (X, y): Features (size, bedrooms, age) and target price.
    """
    arr = _load_numeric_csv("housing.csv")
    X = arr[:, :3]
    y = arr[:, 3]
    return X, y


def load_wine() -> Tuple[np.ndarray, np.ndarray]:
    """
    Load the sample wine dataset.

    Returns:
        (X, y): Features and integer quality labels.
    """
    arr = _load_numeric_csv("wine.csv")
    X = arr[:, :3]
    y = arr[:, 3].astype(int)
    return X, y


