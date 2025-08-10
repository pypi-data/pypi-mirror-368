from mloptimizer.interfaces.api import GeneticSearch
from mloptimizer.domain.hyperspace import HyperparameterSpace
from mloptimizer.domain.evaluation import kfold_score, train_score, train_test_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (RandomForestClassifier,
                              ExtraTreesClassifier,
                              GradientBoostingClassifier)
from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
import pytest
import warnings

@pytest.mark.parametrize('estimator_class',
                         (DecisionTreeClassifier, RandomForestClassifier, ExtraTreesClassifier,
                          GradientBoostingClassifier, XGBClassifier, SVC))
@pytest.mark.parametrize('target_score', (kfold_score, train_score, train_test_score))
def test_reproducibility(estimator_class, target_score):
    x, y = load_iris(return_X_y=True)
    if estimator_class == SVC:
        scaler = StandardScaler()
        x = scaler.fit_transform(x)
    evolvable_hyperparams = HyperparameterSpace.get_default_hyperparameter_space(estimator_class)
    genetic_params = {
        "generations": 2,
        "population_size": 2,
        'cxpb':  0.5, 'mutpb': 0.5,
        'n_elites': 10, 'tournsize': 3, 'indpb': 0.05
    }
    seed = 25
    distinct_seed = 23414134
    optimizer1 = GeneticSearch(estimator_class=estimator_class,
                               hyperparam_space=evolvable_hyperparams,
                               eval_function=target_score,
                               **genetic_params,
                               seed=seed,
                               scoring="accuracy",
                               use_parallel=False,
                               use_mlflow=False
                               )

    optimizer1.fit(x, y)
    result1 = optimizer1.best_params_
    population_df_1 = optimizer1._optimizer_service.optimizer.genetic_algorithm.population_2_df()
    best_row_1 = population_df_1.sort_values(by="fitness", ascending=False).iloc[0]
    best_score_1 = float(best_row_1['fitness'])

    optimizer2 = GeneticSearch(estimator_class=estimator_class,
                               hyperparam_space=evolvable_hyperparams,
                               eval_function=target_score,
                               **genetic_params,
                               seed=seed,
                               scoring="accuracy",
                               use_parallel=False,
                               use_mlflow=False
                               )

    optimizer2.fit(x, y)
    result2 = optimizer2.best_params_
    population_df_2 = optimizer2._optimizer_service.optimizer.genetic_algorithm.population_2_df()
    best_row_2 = population_df_2.sort_values(by="fitness", ascending=False).iloc[0]
    best_score_2 = float(best_row_2['fitness'])

    optimizer3 = GeneticSearch(estimator_class=estimator_class,
                               hyperparam_space=evolvable_hyperparams,
                               eval_function=target_score,
                               **genetic_params,
                               seed=distinct_seed,
                               scoring="accuracy",
                               use_parallel=False,
                               use_mlflow=False
                               )

    optimizer3.fit(x, y)
    result3 = optimizer3.best_params_
    population_df_3 = optimizer3._optimizer_service.optimizer.genetic_algorithm.population_2_df()
    best_row_3 = population_df_3.sort_values(by="fitness", ascending=False).iloc[0]
    best_score_3 = float(best_row_3['fitness'])

    assert str(result1) == str(result2)
    # assert best_score_1 == best_score_2
    assert str(result1) != str(result3)
    # Warnings for soft checks
    if str(result1) == str(result3):
        warnings.warn("result1 == result3: This might be by chance and could be unexpected.")

    if best_score_1 == best_score_3:
        warnings.warn("best_score_1 == best_score_3: This could be coincidental.")