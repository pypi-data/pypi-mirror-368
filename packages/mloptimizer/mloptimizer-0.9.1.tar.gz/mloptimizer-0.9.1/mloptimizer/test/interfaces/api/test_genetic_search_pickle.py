import pytest
import pickle
from io import BytesIO
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier
from mloptimizer.domain.hyperspace import HyperparameterSpace
import pandas as pd
from mloptimizer.interfaces.api import GeneticSearch, HyperparameterSpaceBuilder


@pytest.fixture
def iris_data():
    """Fixture to load the Iris dataset."""
    data = load_iris()
    return data.data, data.target


@pytest.fixture
def hyperparam_space_dt():
    """Fixture to create a hyperparameter space for DecisionTreeClassifier."""
    builder = HyperparameterSpaceBuilder()
    hyperspace_dt = (builder.add_int_param("min_samples_split", 2, 20)
                     .add_int_param("max_depth", 2, 20)
                     .build())
    return hyperspace_dt


@pytest.fixture
def fitted_genetic_optimizer_dt(hyperparam_space_dt, iris_data):
    """Fixture to create and fit a GeneticOptimizerAPI instance for DecisionTreeClassifier."""
    X, y = iris_data
    optimizer = GeneticSearch(
        estimator_class=DecisionTreeClassifier,
        hyperparam_space=hyperparam_space_dt,
        **{"generations": 2, "population_size": 3},
        eval_function=None,
        seed=42,
        use_parallel=False,
        cv=3  # Use a small number of folds for testing
    )
    optimizer.fit(X, y)
    return optimizer


def test_pickle_unfitted_optimizer(hyperparam_space_dt):
    """Test that an unfitted GeneticSearch can be pickled and unpickled."""
    optimizer = GeneticSearch(
        estimator_class=DecisionTreeClassifier,
        hyperparam_space=hyperparam_space_dt,
        **{"generations": 2, "population_size": 3},
        eval_function=None,
        seed=42,
        use_parallel=False
    )

    # Pickle and unpickle
    buff = BytesIO()
    pickle.dump(optimizer, buff)
    buff.seek(0)
    restored = pickle.load(buff)

    # Verify basic attributes
    assert restored.estimator_class == DecisionTreeClassifier
    assert restored.seed == 42
    assert restored.generations == 2
    assert not hasattr(restored, 'best_estimator_'), \
        "Unfitted estimator shouldn't have best_estimator_"


def test_pickle_fitted_optimizer(fitted_genetic_optimizer_dt):
    """Test that a fitted GeneticSearch can be pickled and preserves all important attributes."""
    original = fitted_genetic_optimizer_dt

    # Store original attributes for comparison
    original_attrs = {
        'best_estimator_': original.best_estimator_,
        'best_params_': original.best_params_,
        'cv_results_': original.cv_results_,
        'logbook_': original.logbook_,
    }

    # Special handling for populations_ DataFrame
    original_populations = original.populations_.copy() if hasattr(original, 'populations_') else None

    # Pickle and unpickle
    buff = BytesIO()
    pickle.dump(original, buff)
    buff.seek(0)
    restored = pickle.load(buff)

    # Verify all important attributes exist and match
    for attr_name, original_value in original_attrs.items():
        assert hasattr(restored, attr_name), \
            f"Restored estimator is missing attribute: {attr_name}"

        restored_value = getattr(restored, attr_name)

        # Special handling for the estimator object
        if attr_name == 'best_estimator_':
            assert isinstance(restored_value, DecisionTreeClassifier), \
                "Restored best_estimator_ is not the correct type"
            assert restored_value.get_params() == original_value.get_params(), \
                "Restored best_estimator_ has different parameters"
        else:
            assert restored_value == original_value, \
                f"Restored {attr_name} does not match original"

    # Special comparison for populations DataFrame
    if original_populations is not None:
        assert hasattr(restored, 'populations_'), "Restored estimator is missing populations_"
        pd.testing.assert_frame_equal(
            restored.populations_,
            original_populations,
            check_dtype=False,
            check_exact=False,
            rtol=1e-3
        )


def test_pickled_optimizer_functionality(fitted_genetic_optimizer_dt, iris_data):
    """Test that a pickled-then-unpickled GeneticSearch remains functional."""
    X, y = iris_data

    # Pickle and unpickle
    buff = BytesIO()
    pickle.dump(fitted_genetic_optimizer_dt, buff)
    buff.seek(0)
    restored = pickle.load(buff)

    # Test prediction functionality
    predictions = restored.predict(X)
    assert len(predictions) == len(y)

    # Test scoring functionality
    score = restored.score(X, y)
    assert 0 <= score <= 1  # Accuracy should be between 0 and 1


def test_pickle_with_custom_eval_function(hyperparam_space_dt, iris_data):
    """Test pickling with a custom evaluation function."""
    X, y = iris_data

    # Use one of the existing evaluation functions
    from mloptimizer.domain.evaluation import train_score

    optimizer = GeneticSearch(
        estimator_class=DecisionTreeClassifier,
        hyperparam_space=hyperparam_space_dt,
        **{"generations": 2, "population_size": 3},
        eval_function=train_score,
        seed=42
    )

    # Test that it can be pickled and unpickled
    buff = BytesIO()
    pickle.dump(optimizer, buff)
    buff.seek(0)
    restored = pickle.load(buff)

    # Verify the eval function was preserved
    assert callable(restored._eval_function)
    assert restored._eval_function.__name__ == 'train_score'

    # Test that the restored optimizer works
    restored.fit(X, y)
    assert hasattr(restored, 'best_estimator_')
