import pytest
from sklearn.datasets import load_iris
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from mloptimizer.interfaces.api import GeneticSearch, HyperparameterSpaceBuilder


@pytest.fixture
def iris_data():
    """Fixture to load the Iris dataset."""
    data = load_iris()
    return data.data, data.target


@pytest.fixture
def hyperparam_space_rf_cv():
    """Fixture with at least two evolvable params to avoid DEAP cx errors."""
    builder = HyperparameterSpaceBuilder()
    return (builder.add_int_param("n_estimators", 10, 50)
                  .add_int_param("max_depth", 3, 10)
                  .build())


def test_genetic_search_cv_int_casts_to_stratifiedkfold(iris_data, hyperparam_space_rf_cv):
    """Test that passing an int as cv defaults to StratifiedKFold and works end-to-end."""
    X, y = iris_data

    search = GeneticSearch(
        estimator_class=RandomForestClassifier,
        hyperparam_space=hyperparam_space_rf_cv,
        cv=3,  # should be interpreted as StratifiedKFold
        **{"generations": 3, "population_size": 4},
        seed=42,
        use_parallel=False
    )

    search.fit(X, y)

    assert isinstance(search.cv, StratifiedKFold)
    assert search.best_estimator_ is not None
    assert search.best_params_ is not None
    assert search.cv_results_ is not None

def test_genetic_search_explicit_kfold(iris_data, hyperparam_space_rf_cv):
    """Test that passing an explicit KFold object works correctly."""
    X, y = iris_data

    custom_cv = KFold(n_splits=4, shuffle=True, random_state=42)

    search = GeneticSearch(
        estimator_class=RandomForestClassifier,
        hyperparam_space=hyperparam_space_rf_cv,
        cv=custom_cv,
        **{"generations": 3, "population_size": 4},
        seed=42,
        use_parallel=False
    )

    search.fit(X, y)

    assert isinstance(search.cv, KFold)
    assert search.cv.n_splits == 4
    assert search.best_estimator_ is not None
    assert search.best_params_ is not None
