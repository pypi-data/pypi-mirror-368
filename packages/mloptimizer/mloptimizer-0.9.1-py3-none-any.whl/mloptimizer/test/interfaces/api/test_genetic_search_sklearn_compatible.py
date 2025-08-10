import pytest
from sklearn.utils.estimator_checks import check_estimator
from mloptimizer.interfaces.api import GeneticSearch  # Adjust if the path differs
from sklearn.tree import DecisionTreeClassifier
from mloptimizer.domain.hyperspace import HyperparameterSpace


# Wrap in a function for pytest
def test_geneticsearch_sklearn_compatibility():
    estimator = GeneticSearch(
        estimator_class=DecisionTreeClassifier,
        hyperparam_space=HyperparameterSpace.get_default_hyperparameter_space(DecisionTreeClassifier),
        **{"generations": 1, "population_size": 2},  # Keep it fast
        seed=42
    )
    check_estimator(estimator)
