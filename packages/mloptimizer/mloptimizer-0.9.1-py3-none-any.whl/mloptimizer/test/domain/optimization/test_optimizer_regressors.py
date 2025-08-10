import pytest
from mloptimizer.domain.optimization import Optimizer
from mloptimizer.domain.hyperspace import HyperparameterSpace
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor
from sklearn.datasets import load_diabetes
from xgboost import XGBRegressor
from sklearn.svm import SVR

from sklearn.metrics import mean_squared_error, root_mean_squared_error


def test_regression_optimizer(tmp_path):
    x, y = load_diabetes(return_X_y=True)
    regression_metrics = {
        "mse": mean_squared_error,
        "rmse": root_mean_squared_error
    }
    evolvable_hyperparams = HyperparameterSpace.get_default_hyperparameter_space(RandomForestRegressor)

    mlopt = Optimizer(estimator_class=RandomForestRegressor,
                      hyperparam_space=evolvable_hyperparams,
                      fitness_score='rmse', metrics=regression_metrics,
                      features=x, labels=y, folder=tmp_path)
    mlopt.optimize_clf(5, 5)
    assert mlopt is not None


@pytest.mark.parametrize('estimator_class',
                         (DecisionTreeRegressor, RandomForestRegressor, ExtraTreesRegressor,
                          GradientBoostingRegressor, XGBRegressor, SVR))
def test_sklearn_optimizer(estimator_class, tmp_path):
    x, y = load_diabetes(return_X_y=True)
    evolvable_hyperparams = HyperparameterSpace.get_default_hyperparameter_space(estimator_class)
    mlopt = Optimizer(estimator_class=estimator_class,
                      hyperparam_space=evolvable_hyperparams,
                      features=x, labels=y, folder=tmp_path)
    mlopt.optimize_clf(5, 5)
    assert mlopt is not None


@pytest.mark.parametrize('use_mlflow', [True, False])
def test_mloptimizer(use_mlflow, tmp_path):
    x, y = load_diabetes(return_X_y=True)
    mlopt = Optimizer(estimator_class=XGBRegressor,
                      hyperparam_space=HyperparameterSpace.get_default_hyperparameter_space(XGBRegressor),
                      genetic_params={"population_size": 5, "generations": 5},
                      features=x, labels=y, use_mlflow=use_mlflow, folder=tmp_path)
    mlopt.optimize_clf(5, 5)
    assert mlopt is not None
