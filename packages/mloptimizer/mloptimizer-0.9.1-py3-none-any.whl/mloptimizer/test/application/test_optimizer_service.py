import pytest
import time
import warnings
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.datasets import load_iris, load_breast_cancer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from mloptimizer.application.optimizer_service import OptimizerService
from mloptimizer.domain.hyperspace import HyperparameterSpace, Hyperparam
from mloptimizer.domain.evaluation import kfold_score, train_score, train_test_score

@pytest.fixture
def default_metrics_dict():
    return {
        "accuracy": accuracy_score,
    }

@pytest.mark.parametrize('estimator_class',
                         [DecisionTreeClassifier, RandomForestClassifier, ExtraTreesClassifier,
                          GradientBoostingClassifier, XGBClassifier, SVC])
def test_optimizer_service_with_estimators(estimator_class, default_metrics_dict, tmp_path):
    x, y = load_iris(return_X_y=True)
    if estimator_class == SVC:
        scaler = StandardScaler()
        x = scaler.fit_transform(x)
    hyperparam_space = HyperparameterSpace.get_default_hyperparameter_space(estimator_class)
    optimizer_service = OptimizerService(
        estimator_class=estimator_class,
        hyperparam_space=hyperparam_space,
        genetic_params={"generations": 5, "population_size": 5},
        metrics=default_metrics_dict,
        seed=42,
        use_parallel=False
    )
    best_model = optimizer_service.optimize(x, y)
    assert best_model is not None

@pytest.mark.parametrize('estimator_class',
                         [DecisionTreeClassifier, RandomForestClassifier, ExtraTreesClassifier,
                          GradientBoostingClassifier, XGBClassifier, SVC])
@pytest.mark.parametrize('dataset',
                         [load_breast_cancer, load_iris])
def test_optimizer_service_with_datasets(estimator_class, dataset, default_metrics_dict, tmp_path):
    x, y = dataset(return_X_y=True)
    if estimator_class == SVC:
        scaler = StandardScaler()
        x = scaler.fit_transform(x)
    hyperparam_space = HyperparameterSpace.get_default_hyperparameter_space(estimator_class)
    optimizer_service = OptimizerService(
        estimator_class=estimator_class,
        hyperparam_space=hyperparam_space,
        genetic_params={"generations": 5, "population_size": 5},
        metrics=default_metrics_dict,
        seed=42,
        use_parallel=False
    )
    best_model = optimizer_service.optimize(x, y)
    assert best_model is not None

@pytest.mark.parametrize('estimator_class',
                         [DecisionTreeClassifier, RandomForestClassifier, ExtraTreesClassifier,
                          GradientBoostingClassifier, SVC])
@pytest.mark.parametrize('dataset',
                         [load_breast_cancer, load_iris])
def test_optimizer_service_parallel_speedup(estimator_class, dataset, default_metrics_dict, tmp_path):
    x, y = dataset(return_X_y=True)
    if estimator_class == SVC:
        scaler = StandardScaler()
        x = scaler.fit_transform(x)
    hyperparam_space = HyperparameterSpace.get_default_hyperparameter_space(estimator_class)
    seed = 42
    generations = 20
    population_size = 10
    optimizer_service_parallel = OptimizerService(
        estimator_class=estimator_class,
        hyperparam_space=hyperparam_space,
        genetic_params={"generations": generations, "population_size": population_size},
        metrics=default_metrics_dict,
        seed=seed,
        use_parallel=True
    )
    start_time_parallel = time.time()
    best_model_parallel = optimizer_service_parallel.optimize(x, y)
    end_time_parallel = time.time()
    elapsed_time_parallel = end_time_parallel - start_time_parallel

    optimizer_service = OptimizerService(
        estimator_class=estimator_class,
        hyperparam_space=hyperparam_space,
        genetic_params={"generations": generations, "population_size": population_size},
        metrics=default_metrics_dict,
        seed=seed,
        use_parallel=False
    )
    start_time = time.time()
    best_model = optimizer_service.optimize(x, y)
    end_time = time.time()
    elapsed_time = end_time - start_time

    assert str(best_model) == str(best_model_parallel)
    print(f"Elapsed time with parallel: {elapsed_time_parallel}")
    print(f"Elapsed time without parallel: {elapsed_time}")
    if elapsed_time_parallel < elapsed_time:
        warnings.warn(
            f"Sequential execution time ({elapsed_time:.2f}s) is greater than or equal "
            f"to parallel execution time ({elapsed_time_parallel:.2f}s)."
        )

@pytest.mark.parametrize('estimator_class',
                         [DecisionTreeClassifier, RandomForestClassifier, ExtraTreesClassifier,
                          GradientBoostingClassifier, XGBClassifier, SVC])
@pytest.mark.parametrize('eval_function', [kfold_score, train_score, train_test_score])
def test_optimizer_service_reproducibility(estimator_class, default_metrics_dict,
                                           eval_function, tmp_path):
    x, y = load_iris(return_X_y=True)
    if estimator_class == SVC:
        scaler = StandardScaler()
        x = scaler.fit_transform(x)
    hyperparam_space = HyperparameterSpace.get_default_hyperparameter_space(estimator_class)
    seed = 42
    distinct_seed = 43
    generations = 2
    population_size = 5
    optimizer_service_1 = OptimizerService(
        estimator_class=estimator_class,
        hyperparam_space=hyperparam_space,
        genetic_params={"generations": generations, "population_size": population_size},
        metrics=default_metrics_dict,
        eval_function=eval_function,
        seed=seed,
        use_parallel=False
    )
    best_model_1 = optimizer_service_1.optimize(x, y)
    optimizer_service_2 = OptimizerService(
        estimator_class=estimator_class,
        hyperparam_space=hyperparam_space,
        genetic_params={"generations": generations, "population_size": population_size},
        metrics=default_metrics_dict,
        eval_function=eval_function,
        seed=seed,
        use_parallel=False
    )
    best_model_2 = optimizer_service_2.optimize(x, y)
    optimizer_service_3 = OptimizerService(
        estimator_class=estimator_class,
        hyperparam_space=hyperparam_space,
        genetic_params={"generations": generations, "population_size": population_size},
        metrics=default_metrics_dict,
        eval_function=eval_function,
        seed=distinct_seed,
        use_parallel=False
    )
    best_model_3 = optimizer_service_3.optimize(x, y)
    assert str(best_model_1) == str(best_model_2)
    assert str(best_model_1) != str(best_model_3)

def test_optimizer_service_set_evaluator(tmp_path, default_metrics_dict):
    x, y = load_iris(return_X_y=True)
    hyperparam_space = HyperparameterSpace.get_default_hyperparameter_space(DecisionTreeClassifier)
    optimizer_service = OptimizerService(
        estimator_class=DecisionTreeClassifier,
        hyperparam_space=hyperparam_space,
        genetic_params={"generations": 5, "population_size": 5},
        metrics=default_metrics_dict,
        seed=42,
        use_parallel=False
    )
    new_eval_function = train_test_score
    optimizer_service.set_eval_function(new_eval_function)
    assert optimizer_service.eval_function == new_eval_function
    best_model = optimizer_service.optimize(x, y)
    assert best_model is not None

def test_optimizer_service_set_hyperparameter_space(tmp_path):
    x, y = load_iris(return_X_y=True)
    initial_hyperparam_space = HyperparameterSpace.get_default_hyperparameter_space(DecisionTreeClassifier)
    optimizer_service = OptimizerService(
        estimator_class=DecisionTreeClassifier,
        hyperparam_space=initial_hyperparam_space,
        genetic_params={"generations": 5, "population_size": 5},
        eval_function=train_test_score,
        seed=42,
        use_parallel=False
    )
    new_hyperparam_space = HyperparameterSpace(
        evolvable_hyperparams={
            "max_depth": Hyperparam("max_depth", 1, 5, 'int'),
            "min_samples_split": Hyperparam("min_samples_split", 2, 10, 'int'),
        },
        fixed_hyperparams={}
    )
    optimizer_service.set_hyperparameter_space(new_hyperparam_space)
    assert optimizer_service.hyperparam_space == new_hyperparam_space
    best_model = optimizer_service.optimize(x, y)
    assert best_model is not None

def test_optimizer_service_invalid_hyperparameter_space(tmp_path):
    x, y = load_iris(return_X_y=True)
    invalid_hyperparam_space = HyperparameterSpace(
        evolvable_hyperparams={
            "invalid_param": Hyperparam("invalid_param", 0, 10, 'int')
        },
        fixed_hyperparams={}
    )
    optimizer_service = OptimizerService(
        estimator_class=DecisionTreeClassifier,
        hyperparam_space=invalid_hyperparam_space,
        genetic_params={"generations": 5, "population_size": 5},
        eval_function=accuracy_score,
        seed=42,
        use_parallel=False
    )
    with pytest.raises(ValueError,
                       match="Parameters {'invalid_param'} are not parameters of DecisionTreeClassifier"):
        optimizer_service.optimize(x, y)

def test_optimizer_service_hyperparameter_space_none(tmp_path):
    x, y = load_iris(return_X_y=True)
    optimizer_service = OptimizerService(
        estimator_class=DecisionTreeClassifier,
        hyperparam_space=None,
        genetic_params={"generations": 5, "population_size": 5},
        eval_function=accuracy_score,
        seed=42,
        use_parallel=False
    )
    with pytest.raises(ValueError, match="hyperparam_space is None"):
        optimizer_service.optimize(x, y)

def test_optimizer_service_custom_svc(tmp_path):
    x, y = load_breast_cancer(return_X_y=True)
    scaler = StandardScaler()
    x = scaler.fit_transform(x)
    custom_svc_evolvable_hyperparams = {
        "C": Hyperparam("C", -2, 2, 'nexp'),
        "kernel": Hyperparam("kernel", 0, 3, 'list', values_str=['linear', 'poly', 'rbf', 'sigmoid']),
        "degree": Hyperparam("degree", 0, 6, 'int'),
        "gamma": Hyperparam("gamma", -3, 3, 'nexp'),
        "max_iter": Hyperparam("max_iter", 1000, 10000, 'int')
    }
    hyperparam_space = HyperparameterSpace(
        evolvable_hyperparams=custom_svc_evolvable_hyperparams,
        fixed_hyperparams={}
    )
    optimizer_service = OptimizerService(
        estimator_class=SVC,
        hyperparam_space=hyperparam_space,
        genetic_params={"generations": 5, "population_size": 5},
        eval_function=train_test_score,
        seed=42,
        use_parallel=False
    )
    best_model = optimizer_service.optimize(x, y)
    assert best_model is not None
