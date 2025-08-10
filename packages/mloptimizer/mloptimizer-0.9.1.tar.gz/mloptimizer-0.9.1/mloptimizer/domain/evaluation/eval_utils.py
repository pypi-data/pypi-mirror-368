import numpy as np
from sklearn.base import clone
from mloptimizer.domain.evaluation.model_evaluation import score_metrics

def make_crossval_eval(cv):
    def eval_fn(estimator, X, y, metrics: dict):
        metric_results = {k: [] for k in metrics}
        for train_idx, test_idx in cv.split(X, y):
            model = clone(estimator)
            model.fit(X[train_idx], y[train_idx])
            preds = model.predict(X[test_idx])
            fold_metrics = score_metrics(y[test_idx], preds, metrics)
            for k in metric_results:
                metric_results[k].append(fold_metrics[k])
        return {k: np.mean(metric_results[k]) for k in metric_results}
    return eval_fn
