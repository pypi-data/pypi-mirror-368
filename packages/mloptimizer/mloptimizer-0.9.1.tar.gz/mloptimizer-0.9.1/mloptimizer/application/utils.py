from sklearn.base import is_classifier, is_regressor


def get_default_fitness_score(estimator_class, provided_fitness_score=None):
    """
    Returns a default fitness score based on the type of the estimator class.

    If the estimator_class is a classifier, the default is 'accuracy'.
    If it is a regressor, the default is 'rmse'.
    If a fitness_score is provided, it is used instead.

    Parameters:
    ----------
    estimator_class : class
        The machine learning model class (e.g., RandomForestClassifier, SVC).

    provided_fitness_score : str, optional
        The fitness score provided by the user. If None, defaults are applied.

    Returns:
    --------
    str : The fitness score to be used.
    """
    if provided_fitness_score is not None:
        return provided_fitness_score

    if is_classifier(estimator_class):
        return 'accuracy'
    elif is_regressor(estimator_class):
        return 'rmse'
    else:
        raise ValueError("The provided estimator_class is neither a classifier nor a regressor.")
