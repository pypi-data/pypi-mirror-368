"""
VishuML - A basic machine learning library implementing algorithms from scratch.

This package provides implementations of fundamental machine learning algorithms
that are built from the ground up without using external ML libraries.
"""

from .linear_regression import LinearRegression
from .logistic_regression import LogisticRegression
from .knn import KNearestNeighbors
from .svm import SupportVectorMachine
from .decision_tree import DecisionTree
from .naive_bayes import NaiveBayes
from .perceptron import Perceptron
from .kmeans import KMeans
from . import utils
from . import datasets as datasets

__version__ = "0.1.1"
__author__ = "Vishu pratap"
__email__ = "vishurizz0@gmail.com"

__all__ = [
    "LinearRegression",
    "LogisticRegression", 
    "KNearestNeighbors",
    "SupportVectorMachine",
    "DecisionTree",
    "NaiveBayes",
    "Perceptron",
    "KMeans",
    "utils"
]
