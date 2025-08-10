import warnings
from mloptimizer.domain.evaluation import train_score
from mloptimizer.application import OptimizerService, HyperparameterSpaceService
import random
from sklearn.model_selection import StratifiedKFold, KFold, BaseCrossValidator
from mloptimizer.domain.evaluation import make_crossval_eval
from sklearn.base import is_classifier
from sklearn.base import BaseEstimator, MetaEstimatorMixin
from copy import deepcopy
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
import numpy as np





class GeneticSearch(MetaEstimatorMixin, BaseEstimator):
    """
    Genetic algorithm-based optimization for hyperparameter tuning.

    The `GeneticOptimizer` provides an interface for optimizing an estimator's hyperparameters
    using a genetic algorithm. It supports cross-validation and parallel computation.

    Parameters
    ----------
    estimator_class : class
        The class of the estimator to be optimized.

    hyperparam_space : dict or HyperparameterSpace
        The hyperparameter search space as a dictionary or a `HyperparameterSpace` object.

    eval_function : callable, optional
        [DEPRECATED] Will be removed in v1.0.
        Use ``cv`` parameter instead for cross-validation configuration.

        .. deprecated:: 0.5
           The eval_function parameter is deprecated.

    seed : int, optional (default=None)
        Random seed for reproducibility. If None, a random seed is generated.

    scoring : str or callable, optional (default=None)
        Scoring method to evaluate the estimator's performance. If None, the estimator’s default score method is used.

    use_parallel : bool, optional (default=False)
        Whether to run the optimization in parallel. If True, parallel processing is enabled.

    cv : int, sklearn.model_selection.BaseCrossValidator, or None
        Cross-validation strategy:
        - int: number of splits (StratifiedKFold if classifier, else KFold)
        - CV splitter object: e.g., StratifiedKFold, KFold, TimeSeriesSplit
        - None: default behavior inside the optimizer service (train_score function).
        Cannot be set simultaneously with `eval_function`.

    use_mlflow : bool, optional (default=False)
        If True, the optimization process will be tracked using MLFlow. Default is False.

    early_stopping : bool, optional (default=False)
        If True, the optimization will stop early if no improvement is observed in the fitness score.

    patience : int, optional (default=5)
        Number of generations to wait before stopping if no improvement is observed.

    min_delta : float, optional (default=0.01)
        Minimum change in the fitness score to qualify as an improvement.

    generations : int, optional (default=20)
        Number of generations to run in the genetic algorithm.

    population_size : int, optional (default=15)
        Size of the population in each generation.

    cxpb : float, optional (default=0.5)
        Crossover probability, the probability of mating two individuals to produce offspring.

    mutpb : float, optional (default=0.5)
        Mutation probability, the probability of mutating an individual.

    n_elites : int, optional (default=10)
        Number of elite individuals to carry over to the next generation without mutation.

    tournsize : int, optional (default=3)
        Tournament size for selection, the number of individuals to compete in each tournament.

    indpb : float, optional (default=0.05)
        Independent probability for each attribute to be mutated, used in mutation operations.

    Attributes
    ----------
    best_estimator_ : estimator
        The estimator with the best found hyperparameters after fitting.

    best_params_ : dict
        The hyperparameters that produced the best performance during the optimization.

    cv_results_ : list of dicts
        A log of the optimization progress, containing details such as fitness scores and hyperparameters
        evaluated during each generation.
    """
    _required_parameters = ["estimator_class"]

    def __init__(self, estimator_class, hyperparam_space, eval_function: callable = None,
                 seed=None, scoring=None, use_parallel=False,
                 cv=None, use_mlflow=False, early_stopping=False, patience=5, min_delta=0.01,
                 generations=20, population_size=15, cxpb=0.5, mutpb=0.5,
                 n_elites=10, tournsize=3, indpb=0.05):
        """Initialize the GeneticOptimizer with the necessary components."""
        # Set the genetic algorithm parameters
        # If hyperparam_space not provided, use default for the estimator_class
        if hyperparam_space is None:
            self.hyperparam_space = HyperparameterSpaceService.load_default_hyperparameter_space(
                estimator_class)
        else:
            self.hyperparam_space = hyperparam_space

        self.estimator_class = estimator_class
        self.scoring = scoring
        self.use_parallel = use_parallel
        self.use_mlflow = use_mlflow

        self.generations = generations
        self.population_size = population_size
        self.cxpb = cxpb
        self.mutpb = mutpb
        self.n_elites = n_elites
        self.tournsize = tournsize
        self.indpb = indpb

        if eval_function is not None:
            warnings.warn(
                "'eval_function' was deprecated in version 0.5 and will be "
                "removed in 1.0. Use the 'cv' parameter instead.",
                FutureWarning,  # More visible than DeprecationWarning
                stacklevel=2  # Points to user's code, not your internals
            )
        self._eval_function = eval_function  # Store privately

        # Random seed for reproducibility
        if seed is None:
            seed = random.randint(0, 1000000)
        elif not isinstance(seed, int):
            raise ValueError("Seed must be an integer.")
        elif seed < 0:
            raise ValueError("Seed must be a non-negative integer.")
        self.seed = seed

        # cv - Cross-validation handling
        if isinstance(cv, int):
            if cv < 2:
                raise ValueError("cv must be >= 2 when given as an integer.")
            if is_classifier(estimator_class()):
                self.cv = StratifiedKFold(n_splits=cv, shuffle=True, random_state=self.seed)
            else:
                self.cv = KFold(n_splits=cv, shuffle=True, random_state=self.seed)
        elif isinstance(cv, BaseCrossValidator):
            self.cv = cv
        elif cv is None:
            self.cv = None
        else:
            raise TypeError(
                "`cv` must be an integer, a scikit-learn CV splitter (e.g., KFold), or None."
            )

        # Build eval_function
        if eval_function is None:
            if self.cv is not None:
                self._eval_function = make_crossval_eval(self.cv)
            else:
                self._eval_function = train_score
        else:
            if not callable(eval_function):
                raise TypeError("eval_function must be a callable function.")
            self._eval_function = eval_function

        # Early stopping parameters
        if not isinstance(early_stopping, bool):
            raise TypeError("early_stopping must be a boolean value.")
        self.early_stopping = early_stopping

        if not isinstance(patience, int) or patience < 1:
            raise ValueError("patience must be a positive integer.")
        self.patience = patience

        if not isinstance(min_delta, (int, float)):
            raise TypeError("min_delta must be a numeric value (int or float).")
        self.min_delta = min_delta


    def fit(self, X, y):
        """
        Run the genetic algorithm optimization to fit the best model.

        Parameters
        ----------
        X : np.array
            Feature set for the optimization process.

        y : np.array
            Label set for the optimization process.

        Returns
        -------
        self : object
            Fitted `GeneticOptimizer` object.
        """
        if X is None or y is None or len(X) == 0 or len(y) == 0:
            raise ValueError("Features and labels must not be empty.")
        # Validate inputs
        X, y = check_X_y(X, y, force_all_finite=True, dtype="numeric")
        # Convert object dtype to numeric if needed
        if y.dtype == object:
            try:
                y = y.astype(float)
            except ValueError as e:
                raise ValueError("Unknown label type") from e

        self.n_features_in_ = X.shape[1]  # Add this line

        # Initialize the optimizer service
        self._optimizer_service = OptimizerService(
            estimator_class=self.estimator_class,
            hyperparam_space=self.hyperparam_space,
            genetic_params=self.get_genetic_params(),
            eval_function=self._eval_function,
            scoring=self.scoring,
            seed=self.seed,
            use_parallel=self.use_parallel,
            use_mlflow=self.use_mlflow,
            early_stopping=self.early_stopping,
            patience=self.patience,
            min_delta=self.min_delta
        )

        # Perform optimization via the optimizer service
        estimator_with_best_params = self._optimizer_service.optimize(X, y)
        self.best_estimator_ = estimator_with_best_params.fit(X, y)

        # Extract best hyperparameters from the optimizer service
        self.best_params_ = self.best_estimator_.get_params()

        # Store the detailed cross-validation or genetic algorithm results TODO
        self.cv_results_ = self._optimizer_service.optimizer.genetic_algorithm.logbook

        # Store logbook
        self.logbook_ = self._optimizer_service.optimizer.genetic_algorithm.logbook

        # Store population df
        self.populations_ = self._optimizer_service.optimizer.genetic_algorithm.population_2_df()

        return self

    def predict(self, X):
        """
        Make predictions using the best estimator found by the optimization process.

        Parameters
        ----------
        X : np.array
            Input features to predict labels.

        Returns
        -------
        y_pred : np.array
            Predicted labels.
        """
        check_is_fitted(self, attributes=["best_estimator_"])
        X = check_array(X, force_all_finite=True, dtype="numeric")
        return self.best_estimator_.predict(X)

    def score(self, X, y):
        """
        Return the score of the best estimator on the given test data and labels.

        Parameters
        ----------
        X : np.array
            Test feature set.

        y : np.array
            True labels for scoring.

        Returns
        -------
        score : float
            Score of the best estimator on the test data.
        """
        if self.best_estimator_ is None:
            raise ValueError("The model must be fitted before scoring.")
        return self.best_estimator_.score(X, y)

    def set_hyperparameter_space(self, hyperparam_space):
        """
        Set or update the hyperparameter space for the optimization process.

        Parameters
        ----------
        hyperparam_space : HyperparameterSpace
            The hyperparameter space object to be used for optimization.
        """
        self._optimizer_service.set_hyperparameter_space(hyperparam_space)

    def get_evolvable_hyperparams(self):
        """
        Get the evolvable hyperparameters from the hyperparameter space.

        Returns
        -------
        evolvable_hyperparams : dict
            Dictionary of evolvable hyperparameters.
        """
        return self._optimizer_service.hyperparam_space.evolvable_hyperparams

    def set_eval_function(self, eval_function: callable):
        """
        Set or update the evaluator function for the optimization process.

        Parameters
        ----------
        eval_function : callable
            A new evaluation function for the optimization process.
        """
        self._optimizer_service.set_eval_function(eval_function)

    def load_default_hyperparameter_space(self, estimator_class):
        """
        Load a default hyperparameter space for the given estimator using the HyperparameterSpaceService.

        Parameters
        ----------
        estimator_class : class
            The estimator class for which to load the default hyperparameter space.

        Returns
        -------
        HyperparameterSpace
            The loaded hyperparameter space object.
        """
        return HyperparameterSpaceService().load_default_hyperparameter_space(estimator_class)

    def load_hyperparameter_space(self, file_path):
        """
        Load a hyperparameter space from a file using the HyperparameterSpaceService.

        Parameters
        ----------
        file_path : str
            The path to the file containing the hyperparameter space.

        Returns
        -------
        HyperparameterSpace
            The loaded hyperparameter space object.
        """
        return HyperparameterSpaceService.load_hyperparameter_space(file_path)

    def save_hyperparameter_space(self, file_path, overwrite=False):
        """
        Save the current hyperparameter space to a file using the HyperparameterSpaceService.

        Parameters
        ----------
        file_path : str
            The path to the file where the hyperparameter space will be saved.
        overwrite : bool, optional (default=False)
            Whether to overwrite the existing file if it exists.
        """
        if self._optimizer_service.hyperparam_space is None:
            raise ValueError("No hyperparameter space is set for saving.")
        HyperparameterSpaceService.save_hyperparameter_space(
            self._optimizer_service.hyperparam_space, file_path, overwrite)

    def get_params(self, deep=True):
        """
        Get parameters for this optimizer.

        Returns
        -------
        params : dict
            Parameter names mapped to their values.
        """
        return {
            "estimator_class": self.estimator_class,
            "hyperparam_space": self.hyperparam_space,
            # "eval_function": self._eval_function,
            "seed": self.seed,
            "scoring": self.scoring,
            "use_parallel": self.use_parallel,
            "cv": self.cv,
            "use_mlflow": self.use_mlflow,
            "early_stopping": self.early_stopping,
            "patience": self.patience,
            "min_delta": self.min_delta,
            ** self.get_genetic_params()
        }

    def set_params(self, **params):
        """
        Set the parameters of this optimizer.

        Parameters
        ----------
        **params : dict
            Estimator parameters to update.

        Returns
        -------
        self : object
            Updated `GeneticOptimizer` object.
        """
        for param, value in params.items():
            setattr(self, param, value)
        return self

    def get_genetic_params(self):
        """
        Get the genetic algorithm parameters.

        Returns
        -------
        genetic_params : dict
            Genetic algorithm parameters.
        """
        return {"generations": self.generations,
                "population_size": self.population_size,
                "cxpb": self.cxpb, "mutpb": self.mutpb,
                "n_elites": self.n_elites, "tournsize": self.tournsize,
                "indpb": self.indpb
        }

    def set_genetic_params(self, **params):
        self.genetic_params = deepcopy(params) if params else None

        self._internal_genetic_params = self.default_genetic_params.copy()
        if self.genetic_params:
            self._internal_genetic_params.update(self.genetic_params)

        return self

    def get_feature_names_out(self, input_features=None):
        """Get output feature names for transformation.

        Parameters
        ----------
        input_features : array-like of str or None, default=None
            Input features.

        Returns
        -------
        feature_names_out : ndarray of str objects
            Transformed feature names.
        """
        if not hasattr(self, 'n_features_in_'):
            raise ValueError("Estimator has not been fitted yet")
        return np.asarray(input_features, dtype=object)

    def __reduce__(self):
        """Proper pickle reduction implementation"""
        # Store all initialization parameters
        init_kwargs = {
            'estimator_class': self.estimator_class,
            'hyperparam_space': self.hyperparam_space,
            'eval_function': None,
            'seed': self.seed,
            'scoring': self.scoring,
            'use_parallel': self.use_parallel,
            'cv': self.cv,
            'use_mlflow': self.use_mlflow,
            'early_stopping': self.early_stopping,
            'patience': self.patience,
            'min_delta': self.min_delta,
            'generations': self.generations,
            'population_size': self.population_size,
            'cxpb': self.cxpb,
            'mutpb': self.mutpb,
            'n_elites': self.n_elites,
            'tournsize': self.tournsize,
            'indpb': self.indpb
        }

        # Remove None values to reduce pickle size
        init_kwargs = {k: v for k, v in init_kwargs.items() if v is not None}

        # Store fitted state if available
        fitted_state = {}
        if hasattr(self, 'best_estimator_'):
            fitted_state = {
                'best_estimator_': self.best_estimator_,
                'best_params_': self.best_params_,
                'cv_results_': self.cv_results_,
                'logbook_': self.logbook_,
                'populations_': self.populations_,
                'n_features_in_': self.n_features_in_,
            }

        return (
            self.__class__,
            (self.estimator_class, self.hyperparam_space),  # Required positional args
            {
                'init_kwargs': init_kwargs,
                'fitted_state': fitted_state
            }
        )

    def __setstate__(self, state):
        """Restore state from pickle"""
        if isinstance(state, dict):
            # First handle the required positional args
            estimator_class = state.get('init_kwargs', {}).pop('estimator_class', None)
            hyperparam_space = state.get('init_kwargs', {}).pop('hyperparam_space', None)

            # Initialize with required args and remaining kwargs
            self.__init__(estimator_class, hyperparam_space, **state['init_kwargs'])

            # Restore fitted state if it exists
            if 'fitted_state' in state:
                for key, value in state['fitted_state'].items():
                    setattr(self, key, value)

            # Explicitly handle cv to ensure proper _eval_function reconstruction
            if 'cv' in state['init_kwargs']:
                self.cv = state['init_kwargs']['cv']
                if self.cv is not None:
                    self._eval_function = make_crossval_eval(self.cv)
                else:
                    self._eval_function = train_score

            if 'n_features_in_' in state:
                self.n_features_in_ = state['n_features_in_']
        else:
            # Fallback for older versions
            self.__dict__.update(state)
