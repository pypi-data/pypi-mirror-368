from mloptimizer.domain.evaluation import kfold_stratified_score, temporal_kfold_score, \
    train_score, train_test_score, kfold_score
import pytest
from sklearn.datasets import make_classification
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score


@pytest.fixture
def classification_mock_data():
    # Create mock features and labels for classification testing
    features, labels = make_classification(n_samples=100, n_features=10, n_classes=2, random_state=42)
    return features, labels


@pytest.fixture
def metrics_dict():
    return {
        "accuracy": accuracy_score
    }


def test_kfold_stratified_score(classification_mock_data, metrics_dict):
    features, labels = classification_mock_data
    clf = DecisionTreeClassifier()
    metrics = kfold_stratified_score(features, labels, clf, metrics_dict)
    assert isinstance(metrics, dict)


def test_temporal_kfold_score(classification_mock_data, metrics_dict):
    features, labels = classification_mock_data
    clf = DecisionTreeClassifier()
    metrics = temporal_kfold_score(features, labels, clf, metrics_dict)
    assert isinstance(metrics, dict)


def test_train_score(classification_mock_data, metrics_dict):
    features, labels = classification_mock_data
    clf = DecisionTreeClassifier()
    metrics = train_score(features, labels, clf, metrics_dict)
    assert isinstance(metrics, dict)


def test_test_train_score(classification_mock_data, metrics_dict):
    features, labels = classification_mock_data
    clf = DecisionTreeClassifier()
    metrics = train_test_score(features, labels, clf, metrics_dict)
    assert isinstance(metrics, dict)


def test_kfold_score(classification_mock_data, metrics_dict):
    features, labels = classification_mock_data
    clf = DecisionTreeClassifier()
    metrics = kfold_score(features, labels, clf, metrics_dict)
    assert isinstance(metrics, dict)
