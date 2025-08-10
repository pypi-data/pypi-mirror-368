import numpy as np
import xgboost as xgb
from sklearn.base import BaseEstimator
from sklearn.utils import check_array


class CustomXGBClassifier(BaseEstimator):
    """
    A class to wrap the xgboost classifier.


    Attributes
    ----------
    base_score : float, optional (default=0.5)
        The initial prediction score of all instances, global bias.
    booster : string, optional (default="gbtree")
        Which booster to use, can be gbtree, gblinear or dart;
        gbtree and dart use tree based models while gblinear uses linear functions.
    eval_metric : string, optional (default="auc")
        Evaluation metrics for validation data, a default metric will be assigned according to objective
        (rmse for regression, and error for classification, mean average precision for ranking).
    eta : float, optional (default=0.077)
        Step size shrinkage used in update to prevent overfitting.
    gamma : float, optional (default=18)
        Minimum loss reduction required to make a further partition on a leaf node of the tree.
    subsample : float, optional (default=0.728)
        Subsample ratio of the training instance.
    colsample_bylevel : float, optional (default=1)
        Subsample ratio of columns for each split, in each level.
    colsample_bytree : float, optional (default=0.46)
        Subsample ratio of columns when constructing each tree.
    max_delta_step : int, optional (default=0)
        Maximum delta step we allow each tree's weight estimation to be.
    max_depth : int, optional (default=7)
        Maximum depth of a tree.
    min_child_weight : int, optional (default=1)
        Minimum sum of instance weight(hessian) needed in a child.
    seed : int, optional (default=1)
        Random number seed.
    alpha : float, optional (default=0)
        L1 regularization term on weights.
    reg_lambda : float, optional (default=1)
        L2 regularization term on weights.
    scale_pos_weight : float, optional (default=4.43)
        Balancing of positive and negative weights.
    obj : callable, optional (default=None)
        Customized objective function.
    feval : callable, optional (default=None)
        Customized evaluation function.
    num_boost_round : int, optional (default=50)
        Number of boosting iterations.
    """
    def __init__(self, base_score=0.5, booster="gbtree", eval_metric="auc",
                 eta=0.077, gamma=18, subsample=0.728, colsample_bylevel=1,
                 colsample_bytree=0.46, max_delta_step=0, max_depth=7,
                 min_child_weight=1, seed=1, alpha=0, reg_lambda=1, scale_pos_weight=4.43,
                 obj=None, feval=None, num_boost_round=50):
        """
        Constructs all the necessary attributes for the CustomXGBClassifier object.

        Parameters
        ----------
        base_score : float, optional (default=0.5)
            The initial prediction score of all instances, global bias.
        booster : string, optional (default="gbtree")
            Which booster to use, can be gbtree, gblinear or dart;
            gbtree and dart use tree based models while gblinear uses linear functions.
        eval_metric : string, optional (default="auc")
            Evaluation metrics for validation data, a default metric will be assigned according to objective
            (rmse for regression, and error for classification, mean average precision for ranking).
        eta : float, optional (default=0.077)
            Step size shrinkage used in update to prevent overfitting.
        gamma : float, optional (default=18)
            Minimum loss reduction required to make a further partition on a leaf node of the tree.
        subsample : float, optional (default=0.728)
            Subsample ratio of the training instance.
        colsample_bylevel : float, optional (default=1)
            Subsample ratio of columns for each split, in each level.
        colsample_bytree : float, optional (default=0.46)
            Subsample ratio of columns when constructing each tree.
        max_delta_step : int, optional (default=0)
            Maximum delta step we allow each tree's weight estimation to be.
        max_depth : int, optional (default=7)
            Maximum depth of a tree.
        min_child_weight : int, optional (default=1)
            Minimum sum of instance weight(hessian) needed in a child.
        seed : int, optional (default=1)
            Random number seed.
        alpha : float, optional (default=0)
            L1 regularization term on weights.
        reg_lambda : float, optional (default=1)
            L2 regularization term on weights.
        scale_pos_weight : float, optional (default=4.43)
            Balancing of positive and negative weights.
        obj : callable, optional (default=None)
            Customized objective function.
        feval : callable, optional (default=None)
            Customized evaluation function.
        num_boost_round : int, optional (default=50)
            Number of boosting iterations.
        """
        self._xclf = None
        self.base_score = base_score
        self.booster = booster
        self.eval_metric = eval_metric
        self.eta = eta
        self.gamma = gamma
        self.reg_lambda = reg_lambda
        self.subsample = subsample
        self.colsample_bylevel = colsample_bylevel
        self.colsample_bytree = colsample_bytree
        self.max_delta_step = max_delta_step
        self.max_depth = max_depth
        self.min_child_weight = min_child_weight
        self.seed = seed
        self.alpha = alpha
        self.scale_pos_weight = round(1/scale_pos_weight, 3)
        self.obj = obj
        self.feval = feval
        #self.tree_method = "gpu_hist"
        self.num_boost_round= num_boost_round

    def fit(self, x, y):
        """
        Fit the model according to the given training data.

        Parameters
        ----------
        x : array-like of shape (n_samples, n_features)
            The training input samples.
        y : array-like of shape (n_samples,)
            The target values (class labels in classification, real numbers in regression).

        Returns
        -------
        self : object
            Returns self.
        """
        check_array(x)
        check_array(y, ensure_2d=False)
        dtrain = xgb.DMatrix(x, y)
        params = self.get_params()
        # Workaround: lambda is a reserved word in Python
        params['lambda'] = params.pop("reg_lambda")
        n_boost_round = params.pop("num_boost_round")
        # Extract params for obj and feval
        if self.obj is not None:
            obj = params.pop('obj')
            feval = params.pop('feval')
            self._xclf = xgb.train(params, dtrain, num_boost_round=n_boost_round, obj=obj, feval=feval)
        else:
            params['objective'] = "binary:logistic"
            self._xclf = xgb.train(params, dtrain, num_boost_round=n_boost_round)

        return self

    def predict(self, x):
        """
        Predict class labels for samples in X.

        Parameters
        ----------
        x : array-like of shape (n_samples, n_features)
            The input samples.

        Returns
        -------
        preds : array-like of shape (n_samples,)
            The predicted classes.
        """
        #check_array(X)
        #dtest = xgb.DMatrix(X)
        #preds = np.array(self._xclf.predict(dtest, ntree_limit=self._xclf.best_iteration))
        p = self.predict_proba(x)
        preds = p > 0.5
        preds = preds.astype(int)
        return preds

    def predict_proba(self, x):
        """
        Predict class probabilities for samples in X.

        Parameters
        ----------
        x : array-like of shape (n_samples, n_features)
            The input samples.

        Returns
        -------
        p : array-like of shape (n_samples,)
            The predicted probabilities.
        """
        if self.obj is None:
            p = self.predict_z(x)
        else:
            zs = self.predict_z(x)
            p = 1.0 / (1.0 + np.exp(-zs))
        return p

    def predict_z(self, x):
        """
        Predict z values for samples in X.

        Parameters
        ----------
        x : array-like of shape (n_samples, n_features)
            The input samples.

        Returns
        -------
        zs : array-like of shape (n_samples,)
            The predicted z values.
        """
        check_array(x)
        dtest = xgb.DMatrix(x)
        preds = np.array(self._xclf.predict(dtest))
        preds = preds > 0.5
        preds = preds.astype(int)
        return preds


def generate_model(learning_rate=0.01, layer_1=100, layer_2=50,
                   dropout_rate_1=0, dropout_rate_2=0):
    try:
        from keras.optimizers import Adam
        from keras.layers import Dense, Dropout
        from keras.models import Sequential
    except ImportError as e:
        print(f"{e}: Keras is not installed. Please install it to use this function.")
        return None

    model = Sequential()
    model.add(Dense(layer_1, activation="relu", input_shape=(30,)))  # Specify input shape for the first layer
    model.add(Dropout(dropout_rate_1))
    model.add(Dense(layer_2, activation="relu"))
    model.add(Dropout(dropout_rate_2))
    model.add(Dense(1, activation="sigmoid"))

    opt = Adam(learning_rate=learning_rate)
    model.compile(loss='binary_crossentropy', optimizer=opt, metrics=['accuracy'])
    return model
