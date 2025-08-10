import json
import os


class HyperparameterSpaceRepository:
    """
    Repository for loading and saving hyperparameter spaces to/from JSON files.
    """

    @staticmethod
    def load_json(file_path):
        """
        Load a hyperparameter space from a JSON file.

        Parameters
        ----------
        file_path : str
            Path to the JSON file.

        Returns
        -------
        dict
            The hyperparameter space as a dictionary.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        json.JSONDecodeError
            If the file is not a valid JSON.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist")

        with open(file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def save_json(data, file_path, overwrite=False):
        """
        Save a hyperparameter space to a JSON file.

        Parameters
        ----------
        data : dict
            Hyperparameter space data to save.
        file_path : str
            Path to the JSON file.
        overwrite : bool, optional
            Whether to overwrite the file if it exists (default=False).

        Raises
        ------
        FileExistsError
            If the file exists and overwrite is False.
        """
        if os.path.exists(file_path) and not overwrite:
            raise FileExistsError(f"The file {file_path} already exists.")

        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
