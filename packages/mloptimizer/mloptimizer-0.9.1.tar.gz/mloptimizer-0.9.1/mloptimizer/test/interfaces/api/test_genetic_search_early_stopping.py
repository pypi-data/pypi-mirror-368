import pytest
from sklearn.datasets import make_classification
from sklearn.tree import DecisionTreeClassifier
from mloptimizer.interfaces.api import GeneticSearch, HyperparameterSpaceBuilder


@pytest.fixture
def noisy_dataset():
    """Low-signal dataset to simulate minimal fitness improvement."""
    X, y = make_classification(
        n_samples=100,
        n_features=5,
        n_informative=2,   # FIXED: was 1, now 2
        n_redundant=0,
        n_repeated=0,
        n_classes=2,
        n_clusters_per_class=2,  # default
        flip_y=0.4,
        class_sep=0.5,
        random_state=42
    )
    return X, y

def test_early_stopping_triggers(noisy_dataset):
    X, y = noisy_dataset

    genetic_optimizer = GeneticSearch(
        estimator_class=DecisionTreeClassifier,
        hyperparam_space=HyperparameterSpaceBuilder.get_default_space(DecisionTreeClassifier),
        **{
            "generations": 100,
            "population_size": 50,
            "cxpb": 0.5,
            "mutpb": 0.2,
            "tournsize": 3,
            "indpb": 0.5,
            "n_elites": 1,
        },
        seed=42,
        use_parallel=False,
        early_stopping=True,
        patience=10,
        min_delta=0.01
    )

    genetic_optimizer.fit(X, y)

    optimizer = genetic_optimizer._optimizer_service.optimizer
    ga = optimizer.genetic_algorithm

    assert hasattr(ga, "generations_run_")
    assert ga.generations_run_ < 100, f"Expected early stopping (patience={genetic_optimizer.patience}) before reaching 100 generations, but ran {ga.generations_run_}"
    assert getattr(ga, "stopped_early_", False) is True

