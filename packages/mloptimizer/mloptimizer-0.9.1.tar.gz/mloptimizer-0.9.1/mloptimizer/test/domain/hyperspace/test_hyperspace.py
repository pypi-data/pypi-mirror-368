import pytest
import json
import os
from mloptimizer.domain.hyperspace import HyperparameterSpace, Hyperparam
import tempfile


@pytest.fixture
def hyperparam_space():
    fixed_hyperparams = {'fixed_param_1': 1, 'fixed_param_2': 2}
    evolvable_hyperparams = {
        'evolvable_param_1': Hyperparam(name='evolvable_param_1', min_value=1, max_value=2, hyperparam_type='int'),
        'evolvable_param_2': Hyperparam(name='evolvable_param_2', min_value=2, max_value=8, hyperparam_type='int')
    }
    return HyperparameterSpace(fixed_hyperparams, evolvable_hyperparams)


@pytest.fixture
def json_file_path(tmpdir):
    return tmpdir.join("test_hyperparameter_space.json")


def test_from_json(hyperparam_space, json_file_path):
    # Save data to file
    hyperparam_space.to_json(str(json_file_path), overwrite=True)

    # Load from file
    loaded_hyperparam_space = HyperparameterSpace.from_json(str(json_file_path))

    # Assertions
    assert isinstance(loaded_hyperparam_space, HyperparameterSpace)
    assert loaded_hyperparam_space.fixed_hyperparams == hyperparam_space.fixed_hyperparams
    assert loaded_hyperparam_space.evolvable_hyperparams.keys() == hyperparam_space.evolvable_hyperparams.keys()


def test_to_json(hyperparam_space, json_file_path):
    # Test if the method correctly writes the instance to a JSON file
    hyperparam_space.to_json(str(json_file_path), overwrite=True)

    # Check if the file was correctly written
    with open(str(json_file_path), 'r') as file:
        data = json.load(file)

    assert 'fixed_hyperparams' in data
    assert data['fixed_hyperparams'] == hyperparam_space.fixed_hyperparams
    assert 'evolvable_hyperparams' in data
    assert (data['evolvable_hyperparams'] ==
            {key: value.__dict__ for key, value in hyperparam_space.evolvable_hyperparams.items()})

    # Test that FileExistsError is raised if overwrite=False
    with pytest.raises(FileExistsError):
        hyperparam_space.to_json(str(json_file_path), overwrite=False)


def test_load_json_file_not_found():
    """Test that loading a non-existent file raises FileNotFoundError"""
    with pytest.raises(FileNotFoundError):
        HyperparameterSpace.from_json("non_existent_file.json")


def test_load_json_file_invalid_json():
    """Test that loading a malformed JSON file raises JSONDecodeError"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        tmp.write("{ invalid_json: True,, }")  # Malformed JSON
        tmp_path = tmp.name

    try:
        with pytest.raises(json.JSONDecodeError):
            HyperparameterSpace.from_json(tmp_path)
    finally:
        os.remove(tmp_path)

def test_to_json_raises_value_error_when_filepath_is_none():
    """Test that to_json raises ValueError if file_path is None"""
    space = HyperparameterSpace(fixed_hyperparams={}, evolvable_hyperparams={})
    with pytest.raises(ValueError, match="The file path must be a valid path"):
        space.to_json(None)

class FakeEstimator:
    pass  # No need to override __name__

def test_get_default_hyperparameter_space_invalid_estimator():
    """Test that get_default_hyperparameter_space raises ValueError for unknown estimator"""
    with pytest.raises(ValueError, match="Default hyperparameter space for FakeEstimator not found"):
        HyperparameterSpace.get_default_hyperparameter_space(FakeEstimator)

def test_hyperparameter_space_str():
    """Test the string representation of HyperparameterSpace (__str__)"""
    space = HyperparameterSpace(
        fixed_hyperparams={"max_depth": 3},
        evolvable_hyperparams={
            "evolvable_param_1": Hyperparam(
                name="evolvable_param_1",
                min_value=1,
                max_value=2,
                hyperparam_type="int"
            )
        }
    )
    result = str(space)

    # Match the actual format returned by __str__/__repr__
    assert "HyperparameterSpace(fixed_hyperparams={'max_depth': 3}" in result
    assert "'evolvable_param_1': Hyperparam(" in result
    assert "'evolvable_param_1', 1, 2, 'int'" in result

def test_hyperparameter_space_repr():
    """Test the repr of HyperparameterSpace (__repr__)"""
    space = HyperparameterSpace(
        fixed_hyperparams={"n_estimators": 100},
        evolvable_hyperparams={
            "evolvable_param_1": Hyperparam(
                name="evolvable_param_1",
                min_value=1,
                max_value=2,
                hyperparam_type="int"
            )
        }
    )
    result = repr(space)

    # Match the actual format returned by __repr__
    assert "HyperparameterSpace(fixed_hyperparams={'n_estimators': 100}" in result
    assert "'evolvable_param_1': Hyperparam(" in result
    assert "'evolvable_param_1', 1, 2, 'int'" in result
