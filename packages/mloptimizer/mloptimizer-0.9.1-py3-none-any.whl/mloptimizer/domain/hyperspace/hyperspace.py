import json
from .hyperparam import Hyperparam
import os


class HyperparameterSpace:
    """
    This class represents the hyperparameter space for a scikit-learn classifier. It contains the fixed hyperparameters
    and the evolvable hyperparameters. The fixed hyperparameters are just a dictionary with the hyperparameters that
    are not going to be optimized and their value.
    The evolvable hyperparameters are a dictionary with the hyperparameters that are
    going to be optimized.
    The keys are the hyperparameter names and the values are instances of the
    :class:`~mloptimizer.hyperparams.Hyperparam` class.

    Attributes
    ----------
    fixed_hyperparams : dict
        Dictionary with the fixed hyperparameters
    evolvable_hyperparams : dict
        Dictionary with the evolvable hyperparameters of :class:`~mloptimizer.hyperparams.Hyperparam` instances
    """
    default_hyperparameter_spaces_json = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                      "..", "..", "infrastructure", "config", "hyperspace",
                                                      "default_hyperparameter_spaces.json")

    def __init__(self, fixed_hyperparams: dict, evolvable_hyperparams: dict):
        """
        Constructs all the necessary attributes for the HyperparameterSpace object.

        Parameters
        ----------
        fixed_hyperparams : dict
            Dictionary with the fixed hyperparameters
        evolvable_hyperparams : dict
            Dictionary with the evolvable hyperparameters of :class:`~mloptimizer.hyperparams.Hyperparam` instances
        """
        self.fixed_hyperparams = fixed_hyperparams
        self.evolvable_hyperparams = evolvable_hyperparams

    @classmethod
    def from_json_data(cls, json_data):
        """
        Create a HyperparameterSpace object from a dictionary (JSON data).

        Parameters
        ----------
        json_data : dict
            Dictionary containing the hyperparameter space data.

        Returns
        -------
        HyperparameterSpace
            An instance of HyperparameterSpace.
        """
        # Extract fixed hyperparameters
        fixed_hyperparams = json_data['fixed_hyperparams']

        # Extract evolvable hyperparameters
        evolvable_hyperparams_dict = json_data['evolvable_hyperparams']
        evolvable_hyperparams = {}
        for key, param_data in evolvable_hyperparams_dict.items():
            evolvable_hyperparams[key] = Hyperparam(**param_data)

        return cls(fixed_hyperparams=fixed_hyperparams, evolvable_hyperparams=evolvable_hyperparams)

    @classmethod
    def from_json(cls, file_path):
        """
        This method creates a :class:`~mloptimizer.hyperparams.HyperparameterSpace` object from a JSON file.

        Parameters
        ----------
        file_path : str
            Path to the JSON file

        Returns
        -------
        :class:`~mloptimizer.hyperparams.HyperparameterSpace`

        Raises
        ------
        FileNotFoundError
            If the file does not exist
        json.JSONDecodeError
            If the file is not a valid JSON file
        """
        try:
            # Load JSON data from the file
            with open(file_path, 'r', encoding='utf-8') as file:
                json_text = file.read()  # Read raw JSON string
                json_data = json.loads(json_text)  # Try to parse it

        except FileNotFoundError:
            raise FileNotFoundError(f"The file {file_path} does not exist")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"The file '{file_path}' is not a valid JSON file: {e.msg}",
                doc=json_text,  # The original JSON string
                pos=e.pos  # The error position
            )

        # Extract fixed hyperparams, just a dictionary
        fixed_hyperparams = json_data['fixed_hyperparams']
        # Extract evolvable hyperparams
        evolvable_hyperparams_dict = json_data['evolvable_hyperparams']
        evolvable_hyperparams = {}
        # for k in evolvable_hyperparams_dict.keys():
        #    evolvable_hyperparams[k] = Hyperparam(**evolvable_hyperparams_dict[k])
        for key, param_data in evolvable_hyperparams_dict.items():
            # Support a potential 'str_values' or 'values_str' key in the JSON
            evolvable_hyperparams[key] = Hyperparam(**param_data)

        return cls(fixed_hyperparams=fixed_hyperparams, evolvable_hyperparams=evolvable_hyperparams)

    def to_json(self, file_path, overwrite=False):
        """
        This method saves the hyperparameter space as a JSON file.

        Parameters
        ----------
        file_path : str
            Path to the JSON file
        overwrite : bool, optional (default=False)
            If True, the file will be overwritten if it exists. If False, a FileExistsError will be raised if the file
            exists

        Raises
        ------
        ValueError
            If the file path is None
        FileExistsError
            If the file exists and overwrite is False
        """
        # Verify the file path exists
        if file_path is None:
            raise ValueError("The file path must be a valid path")
        if os.path.exists(file_path) and not overwrite:
            raise FileExistsError(f"The file path {file_path} exist and overwrite is {overwrite}")
        # Create a dictionary with the fixed hyperparams and evolvable hyperparams
        hyperparams_dict = {
            'fixed_hyperparams': self.fixed_hyperparams,
            'evolvable_hyperparams': {key: value.__dict__ for key, value in self.evolvable_hyperparams.items()}
        }

        # Save the dictionary as a JSON file
        with open(file_path, 'w') as file:
            json.dump(hyperparams_dict, file, indent=4)

    @staticmethod
    def get_default_hyperparameter_space(estimator_class):
        """
        This method returns a dictionary with the default hyperparameters for the scikit-learn classifier.
        It reads the default_hyperparameter_spaces.json file and returns the hyperparameters for the classifier

        Parameters
        ----------
        estimator_class : class
            The scikit-learn classifier class

        Returns
        -------
        :class:`~mloptimizer.hyperparams.HyperparameterSpace`
            The hyperparameter space for the classifier
        """
        with open(HyperparameterSpace.default_hyperparameter_spaces_json, 'r') as file:
            default_hyperparams = json.load(file)
        if estimator_class.__name__ in default_hyperparams.keys():
            hyperspace_conf_subfolder_name = default_hyperparams[estimator_class.__name__]['folder']
            return HyperparameterSpace.from_json(
                str(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "..", "infrastructure", "config", "hyperspace",
                                 hyperspace_conf_subfolder_name,
                                 default_hyperparams[estimator_class.__name__]['file']
                                 )
                    )
            )
        else:
            raise ValueError(f"Default hyperparameter space for {estimator_class.__name__} not found")

    def get_all_params(self):
        """
        This method returns a dictionary with all the hyperparameters, fixed and evolvable.

        Returns
        -------
        dict
            Dictionary with all the hyperparameters
        """
        all_params = self.fixed_hyperparams.copy()
        all_params.update(self.evolvable_hyperparams)
        return all_params

    def __str__(self):
        return (f"HyperparameterSpace(fixed_hyperparams={self.fixed_hyperparams}, "
                f"evolvable_hyperparams={self.evolvable_hyperparams})")

    def __repr__(self):
        return (f"HyperparameterSpace(fixed_hyperparams={self.fixed_hyperparams}, "
                f"evolvable_hyperparams={self.evolvable_hyperparams})")

    def __eq__(self, other):
        return (self.fixed_hyperparams == other.fixed_hyperparams and
                self.evolvable_hyperparams == other.evolvable_hyperparams)
