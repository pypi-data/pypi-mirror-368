import pytest
import numpy as np
from sklearn.model_selection import StratifiedKFold, KFold, TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from mloptimizer.interfaces.api import GeneticSearch, HyperparameterSpaceBuilder
from sklearn.base import is_classifier, is_regressor


@pytest.fixture
def dummy_hyperparam_space():
    builder = HyperparameterSpaceBuilder()
    return builder.add_int_param("n_estimators", 10, 50).build()


@pytest.fixture
def iris_data():
    from sklearn.datasets import load_iris
    data = load_iris()
    return data.data, data.target


def test_cv_as_integer_classifier(dummy_hyperparam_space):
    optimizer = GeneticSearch(
        estimator_class=RandomForestClassifier,
        hyperparam_space=dummy_hyperparam_space,
        cv=4,
        seed=123
    )
    assert isinstance(optimizer.cv, StratifiedKFold)
    assert optimizer.cv.n_splits == 4
    assert optimizer.cv.shuffle
    assert optimizer.cv.random_state == 123


def test_cv_as_integer_regressor(dummy_hyperparam_space):
    optimizer = GeneticSearch(
        estimator_class=LinearRegression,
        hyperparam_space=dummy_hyperparam_space,
        cv=3,
        seed=456
    )
    assert isinstance(optimizer.cv, KFold)
    assert optimizer.cv.n_splits == 3
    assert optimizer.cv.shuffle
    assert optimizer.cv.random_state == 456


def test_cv_as_splitter_object(dummy_hyperparam_space):
    cv_obj = TimeSeriesSplit(n_splits=5)
    optimizer = GeneticSearch(
        estimator_class=RandomForestClassifier,
        hyperparam_space=dummy_hyperparam_space,
        cv=cv_obj
    )
    assert optimizer.cv is cv_obj


def test_cv_invalid_type_raises(dummy_hyperparam_space):
    with pytest.raises(TypeError, match="`cv` must be an integer, a scikit-learn CV splitter"):
        GeneticSearch(
            estimator_class=RandomForestClassifier,
            hyperparam_space=dummy_hyperparam_space,
            cv="stratified"
        )


def test_cv_integer_less_than_2_raises(dummy_hyperparam_space):
    with pytest.raises(ValueError, match="cv must be >= 2 when given as an integer."):
        GeneticSearch(
            estimator_class=RandomForestClassifier,
            hyperparam_space=dummy_hyperparam_space,
            cv=1
        )
