import pytest
import numpy as np
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import balanced_accuracy_score

from mloptimizer.interfaces.api import GeneticSearch, HyperparameterSpaceBuilder
from mloptimizer.domain.evaluation import kfold_stratified_score


@pytest.fixture
def iris_data():
    data = load_iris()
    return data.data, data.target


@pytest.fixture
def hyperparam_space_rf():
    builder = HyperparameterSpaceBuilder()
    return (builder
            .add_int_param("n_estimators", 50, 50)
            .add_int_param("max_depth", 6, 6)
            .build())


def test_eval_function_vs_cv_equivalence(iris_data, hyperparam_space_rf):
    X, y = iris_data
    seed = 123
    n_splits = 4

    # --- First GeneticSearch using eval_function ---
    search_eval = GeneticSearch(
        estimator_class=RandomForestClassifier,
        hyperparam_space=hyperparam_space_rf,
        generations=5,
        population_size=5,
        eval_function=lambda features, labels, clf, metrics, random_state=None:
            kfold_stratified_score(features, labels, clf, metrics,
                                   n_splits=n_splits, random_state=random_state),
        seed=seed,
        use_parallel=False,
        scoring='balanced_accuracy'
    )
    search_eval.fit(X, y)
    result_eval_fn = search_eval.cv_results_

    # --- Second GeneticSearch using cv=StratifiedKFold ---
    from sklearn.model_selection import StratifiedKFold

    class LoggingStratifiedKFold(StratifiedKFold):
        def split(self, X, y, groups=None):
            print(
                f"[CVWrapper] Called split: n_splits={self.n_splits}, shuffle={self.shuffle}, random_state={self.random_state}")
            print(f"[CVWrapper] Dataset shape: X={X.shape}, y={y.shape}")
            for i, (train_idx, test_idx) in enumerate(super().split(X, y, groups)):
                print(f"[CVWrapper] Fold {i + 1}")
                print(f"  → Train indices: ({len(train_idx)},), Test indices: ({len(test_idx)},)")
                yield train_idx, test_idx

    stratified_cv = LoggingStratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)

    search_cv = GeneticSearch(
        estimator_class=RandomForestClassifier,
        hyperparam_space=hyperparam_space_rf,
        generations=5,
        population_size=5,
        cv=stratified_cv,
        seed=seed,
        use_parallel=False,
        scoring='balanced_accuracy'
    )
    search_cv.fit(X, y)
    result_cv_obj = search_cv.cv_results_

    # --- Comparison ---
    for ind_eval, ind_cv in zip(result_eval_fn, result_cv_obj):
        print(f"\n[METRICS eval]: {ind_eval}")
        print(f"[METRICS cv]:   {ind_cv}")

        assert ind_eval['gen'] == ind_cv['gen']
        assert ind_eval['nevals'] == ind_cv['nevals']

        for key in ['avg', 'min', 'max']:
            assert key in ind_eval and key in ind_cv
            diff = abs(ind_eval[key] - ind_cv[key])
            print(f"→ {key}: eval={ind_eval[key]:.6f} | cv={ind_cv[key]:.6f} | Δ={diff:.6f}")
            assert np.isclose(ind_eval[key], ind_cv[key], atol=1e-4), \
                f"Mismatch in {key}: {ind_eval[key]} != {ind_cv[key]}"

    # --- Manual check of best estimator performance ---
    if hasattr(search_eval, 'best_estimator_') and hasattr(search_cv, 'best_estimator_'):
        best_eval = search_eval.best_estimator_
        best_cv = search_cv.best_estimator_

        assert isinstance(best_eval, RandomForestClassifier)
        assert isinstance(best_cv, RandomForestClassifier)
        assert best_eval.get_params() == best_cv.get_params()

        pred_eval = best_eval.predict(X)
        pred_cv = best_cv.predict(X)
        score_eval = balanced_accuracy_score(y, pred_eval)
        score_cv = balanced_accuracy_score(y, pred_cv)

        print(f"\n[Manual balanced_accuracy_score]")
        print(f"→ Best from eval_function: {score_eval:.6f}")
        print(f"→ Best from cv object:     {score_cv:.6f}")

        assert np.isclose(score_eval, score_cv, atol=1e-4), \
            f"Mismatch in final score: {score_eval} != {score_cv}"

    else:
        print("Warning: best_estimator_ not available; skipping final prediction comparison.")
