from mloptimizer.domain.model.alg_wrapper import generate_model
from mloptimizer.domain.optimization import Optimizer
from mloptimizer.domain.hyperspace import Hyperparam
from mloptimizer.domain.population import IndividualUtils


class KerasClassifierOptimizer(Optimizer):
    """
    Class for the optimization of a gradient boosting classifier from keras.wrappers.scikit_learn.KerasClassifier.
    It inherits from BaseOptimizer.
    """

    @staticmethod
    def get_default_hyperparams():
        default_hyperparams = {
            'epochs': Hyperparam("epochs", 1, 10, "x10"),
            'batch_size': Hyperparam("batch_size", 1, 5, "x10"),
            'learning_rate': Hyperparam("learning_rate", 1, 20, 'float', 1000),
            'layer_1': Hyperparam("layer_1", 10, 50, "x10"),
            'layer_2': Hyperparam("layer_2", 5, 20, "x10"),
            'dropout_rate_1': Hyperparam("dropout_rate_1", 0, 5, 'float', 10),
            'dropout_rate_2': Hyperparam("dropout_rate_2", 0, 5, 'float', 10),
        }
        return default_hyperparams

    def get_clf(self, individual):
        try:
            from keras.wrappers.scikit_learn import KerasClassifier
        except ImportError as e:
            print(f"{e}: Keras is not installed. Please install it to use this function.")
            return None
        individual_dict = IndividualUtils(hyperparam_space=self.hyperparam_space).individual2dict(individual)
        print(individual_dict)
        clf = KerasClassifier(build_fn=generate_model,
                              **individual_dict)
        return clf
