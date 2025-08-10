from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, root_mean_squared_error
from mloptimizer.infrastructure.tracking import Tracker
import numpy as np
import warnings

from sklearn.base import is_regressor, is_classifier


def _default_classification_metrics():
    return {
        "accuracy": accuracy_score,
        "balanced_accuracy": balanced_accuracy_score
    }


def _default_regression_metrics():
    return {
        "mae": mean_absolute_error,
        "mse": mean_squared_error,
        "rmse": root_mean_squared_error
    }


class Evaluator:
    """
    Evaluator class to evaluate the performance of a classifier

    Parameters
    ----------
    features : array-like
        The features to use to evaluate the classifier
    labels : array-like
        The labels to use to evaluate the classifier
    eval_function : function
        The evaluation function to use to evaluate the performance of the classifier
    fitness_score : str
        The fitness score to use to evaluate the performance of the classifier
    metrics : dict
        The metrics to use to evaluate the performance of the classifier
        Dictionary of the form {"metric_name": metric_function}
    tracker : Tracker
        The tracker to use to log the evaluations
    individual_utils : IndividualUtils
        The individual utils to use to get the classifier from the individual
    seed : int
        The random seed to use for reproducibility
    """

    def __init__(self, estimator_class, features: np.array, labels: np.array, eval_function, fitness_score=None,
                 metrics=None, tracker: Tracker = None, individual_utils=None, seed: int = 0):

        self.estimator_class = estimator_class
        if not is_classifier(self.estimator_class) and not is_regressor(self.estimator_class):
            raise ValueError(f"The estimator class {self.estimator_class} must be a classifier or a regressor")

        self.eval_function = eval_function
        self.fitness_score = fitness_score
        self.tracker = tracker
        self.features = features
        self.labels = labels
        self.individual_utils = individual_utils
        self.seed = seed

        if metrics is None:
            if is_classifier(self.estimator_class):
                self.metrics = _default_classification_metrics()
                if fitness_score is None:
                    self.fitness_score = "accuracy"
                else:
                    self.fitness_score = fitness_score
            elif is_regressor(self.estimator_class):
                self.metrics = _default_regression_metrics()
                if fitness_score is None:
                    self.fitness_score = "rmse"
                else:
                    self.fitness_score = fitness_score
        else:
            self.metrics = metrics

    def evaluate(self, clf, features, labels):
        """
        Evaluate the performance of a classifier

        Parameters
        ----------
        clf : object
            The classifier to evaluate
        features : array-like
            The features to use to evaluate the classifier
        labels : array-like
            The labels to use to evaluate the classifier

        Returns
        -------
        metrics : dict
            Dictionary of the form {"metric_name": metric_value}
        """
        import inspect
        sig = inspect.signature(self.eval_function)
        param_names = list(sig.parameters)

        # Match old-style: features, labels, clf, metrics
        if param_names[:4] == ["features", "labels", "clf", "metrics"]:
            if "random_state" in param_names:
                return self.eval_function(features, labels, clf, self.metrics, random_state=self.seed)
            else:
                return self.eval_function(features, labels, clf, self.metrics)

        # Match new-style: clf, X, y, metrics
        elif param_names[:4] == ["estimator", "X", "y", "metrics"]:
            if "random_state" in param_names:
                return self.eval_function(clf, features, labels, self.metrics, random_state=self.seed)
            else:
                return self.eval_function(clf, features, labels, self.metrics)


        # Fallback for partial matches
        else:
            raise TypeError(
                f"The evaluation function `{self.eval_function.__name__}` does not match expected signatures.\n"
                "It should be either:\n"
                "  (features, labels, clf, metrics[, random_state]) [OLD STYLE], or\n"
                "  (clf, X, y, metrics[, random_state]) [NEW STYLE].\n"
                f"Found parameters: {param_names}"
            )

    def evaluate_individual(self, individual):
        clf = self.individual_utils.get_clf(individual)
        metrics = self.evaluate(clf=clf, features=self.features, labels=self.labels)
        self.tracker.log_evaluation(clf, metrics,
                                    fitness_score=metrics[self.fitness_score],
                                    greater_is_better=is_classifier(clf))
        return (metrics[self.fitness_score],)
