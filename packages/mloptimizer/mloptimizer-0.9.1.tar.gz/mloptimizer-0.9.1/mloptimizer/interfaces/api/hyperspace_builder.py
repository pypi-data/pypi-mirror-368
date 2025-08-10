"""
HyperparameterSpaceBuilder
==========================

Class for building and managing a hyperparameter space. This class allows 
the creation of both fixed and evolvable hyperparameters, supporting various 
data types such as integers, floats, and categorical parameters. The resulting 
hyperparameter space can then be used in machine learning optimization tasks.

Attributes
----------
fixed_hyperparams : dict
    A dictionary of hyperparameters that have fixed values.
evolvable_hyperparams : dict
    A dictionary of hyperparameters that can be tuned or evolved during optimization.
service : HyperparameterSpaceService
    A service class to interact with the underlying hyperparameter space operations.

Methods
-------
add_int_param(name, min_value, max_value)
    Adds an integer parameter to the evolvable hyperparameters.
add_float_param(name, min_value, max_value, scale=100)
    Adds a float parameter to the evolvable hyperparameters with optional scaling.
add_categorical_param(name, values)
    Adds a categorical parameter to the evolvable hyperparameters.
set_fixed_param(name, value)
    Sets a fixed parameter with a given name and value.
set_fixed_params(fixed_params)
    Sets multiple fixed parameters using a dictionary.
build()
    Builds and returns the hyperparameter space.
load_default_space(estimator_class)
    Loads a default hyperparameter space for the specified estimator.
get_default_space(estimator_class)
    Returns a default hyperparameter space for the specified estimator.
save_space(hyperparam_space, file_path, overwrite=False)
    Saves the hyperparameter space to a file.

Examples
--------
>>> builder = HyperparameterSpaceBuilder()
>>> builder.add_int_param("n_estimators", 50, 200)
>>> builder.add_float_param("learning_rate", 0.01, 0.1, scale=100)
>>> builder.add_categorical_param("boosting_type", ["gbdt", "dart"])
>>> space = builder.build()

"""

from mloptimizer.domain.hyperspace import HyperparameterSpace
from mloptimizer.domain.hyperspace import Hyperparam
from mloptimizer.application import HyperparameterSpaceService


class HyperparameterSpaceBuilder:
    """
    A builder class for constructing hyperparameter spaces.

    This class is responsible for defining both fixed and evolvable
    hyperparameters, allowing for the construction of a 
    `HyperparameterSpace` object used in optimization tasks.
    """

    def __init__(self):
        """
        Initializes the builder with empty dictionaries for both fixed and evolvable
        hyperparameters. Also initializes an instance of `HyperparameterSpaceService`
        to manage space-related operations.
        """
        self.fixed_hyperparams = {}
        self.evolvable_hyperparams = {}
        self.service = HyperparameterSpaceService()

    def add_int_param(self, name: str, min_value: int, max_value: int):
        """
        Adds an integer parameter to the evolvable hyperparameters.

        Parameters
        ----------
        name : str
            The name of the hyperparameter.
        min_value : int
            The minimum value the parameter can take.
        max_value : int
            The maximum value the parameter can take.

        Returns
        -------
        self : HyperparameterSpaceBuilder
            The builder instance, allowing for method chaining.
        """
        param = Hyperparam(name=name, min_value=min_value, max_value=max_value, hyperparam_type='int')
        self.evolvable_hyperparams[name] = param
        return self

    def add_float_param(self, name: str, min_value: int, max_value: int, scale=100):
        """
        Adds a float parameter to the evolvable hyperparameters.

        Parameters
        ----------
        name : str
            The name of the hyperparameter.
        min_value : int
            The minimum value the parameter can take.
        max_value : int
            The maximum value the parameter can take.
        scale : int, optional
            Scaling factor for the float parameter (default is 100).

        Returns
        -------
        self : HyperparameterSpaceBuilder
            The builder instance, allowing for method chaining.
        """
        param = Hyperparam(name=name, min_value=min_value, max_value=max_value, hyperparam_type='float', scale=scale)
        self.evolvable_hyperparams[name] = param
        return self

    def add_categorical_param(self, name: str, values: list):
        """
        Adds a categorical parameter to the evolvable hyperparameters.

        Parameters
        ----------
        name : str
            The name of the hyperparameter.
        values : list
            A list of categorical values that the parameter can take.

        Returns
        -------
        self : HyperparameterSpaceBuilder
            The builder instance, allowing for method chaining.
        """
        param = Hyperparam.from_values_list(name=name, values_str=values)
        self.evolvable_hyperparams[name] = param
        return self

    def set_fixed_param(self, name: str, value):
        """
        Sets a fixed parameter with the given name and value.

        Parameters
        ----------
        name : str
            The name of the parameter.
        value : any
            The fixed value to assign to the parameter.

        Returns
        -------
        self : HyperparameterSpaceBuilder
            The builder instance, allowing for method chaining.
        """
        self.fixed_hyperparams[name] = value
        return self

    def set_fixed_params(self, fixed_params: dict):
        """
        Sets multiple fixed parameters using a dictionary.

        Parameters
        ----------
        fixed_params : dict
            A dictionary where keys are parameter names and values are their fixed values.

        Returns
        -------
        self : HyperparameterSpaceBuilder
            The builder instance, allowing for method chaining.
        """
        self.fixed_hyperparams = fixed_params
        return self

    def build(self):
        """
        Builds the `HyperparameterSpace` object using the current configuration.

        Returns
        -------
        HyperparameterSpace
            The constructed hyperparameter space containing both fixed and evolvable parameters.
        """
        return HyperparameterSpace(fixed_hyperparams=self.fixed_hyperparams,
                                   evolvable_hyperparams=self.evolvable_hyperparams)

    def load_default_space(self, estimator_class):
        """
        Load a default hyperparameter space using the `HyperparameterSpaceService`.

        Parameters
        ----------
        estimator_class : class
            The estimator class for which the default hyperparameter space should be loaded.

        Returns
        -------
        HyperparameterSpace
            A default hyperparameter space for the given estimator class.
        """
        return self.service.load_default_hyperparameter_space(estimator_class)

    @staticmethod
    def get_default_space(estimator_class):
        """
        Returns a default hyperparameter space using the `HyperparameterSpaceService`.

        Parameters
        ----------
        estimator_class : class
            The estimator class for which the default hyperparameter space should be retrieved.

        Returns
        -------
        HyperparameterSpace
            A default hyperparameter space for the given estimator class.
        """
        tmp_service = HyperparameterSpaceService()
        return tmp_service.load_default_hyperparameter_space(estimator_class=estimator_class)

    def save_space(self, hyperparam_space, file_path, overwrite=False):
        """
        Save the hyperparameter space using the `HyperparameterSpaceService`.

        Parameters
        ----------
        hyperparam_space : HyperparameterSpace
            The hyperparameter space to be saved.
        file_path : str
            The file path where the hyperparameter space should be saved.
        overwrite : bool, optional
            Whether to overwrite an existing file (default is False).

        Returns
        -------
        None
        """
        self.service.save_hyperparameter_space(hyperparam_space, file_path, overwrite)

    def load_space(self, hyperparam_space_json_path):
        """
        Load a hyperparameter space from a JSON file using the `HyperparameterSpaceService`.

        Parameters
        ----------
        hyperparam_space_json_path : str
            The path to the JSON file containing the hyperparameter space.

        Returns
        -------
        HyperparameterSpace
            The loaded hyperparameter space.
        """
        return self.service.load_hyperparameter_space(hyperparam_space_json_path)
