from mloptimizer.infrastructure.repositories import HyperparameterSpaceRepository
import pytest
import json
import os

@pytest.fixture
def sample_data():
    return {
        'fixed_hyperparams': {'param1': 1},
        'evolvable_hyperparams': {
            'param2': {'name': 'param2', 'min_value': 0, 'max_value': 10, 'hyperparam_type': 'int'},
            'param3': {'name': 'param3', 'min_value': 0.01, 'max_value': 1.0, 'hyperparam_type': 'float', 'scale': 100},
            'param4': {'name': 'param4', 'min_value': 0, 'max_value': 3, 'hyperparam_type': 'list', 'values_str': ["a", "b", "c"]}
        }
    }

def test_load_json_success(sample_data, mocker):
    # Mock os.path.exists to return True (file exists)
    mocker.patch("os.path.exists", return_value=True)
    # Mock open and json.load to return the sample data
    mocker.patch("builtins.open", mocker.mock_open(read_data=json.dumps(sample_data)))
    result = HyperparameterSpaceRepository.load_json("test.json")
    assert result == sample_data

def test_load_json_file_not_found(mocker):
    # Mock os.path.exists to return False (file does not exist)
    mocker.patch("os.path.exists", return_value=False)
    with pytest.raises(FileNotFoundError):
        HyperparameterSpaceRepository.load_json("nonexistent.json")

def test_load_json_invalid_json(mocker):
    # Mock os.path.exists to return True (file exists)
    mocker.patch("os.path.exists", return_value=True)
    # Mock open to simulate invalid JSON content
    mocker.patch("builtins.open", mocker.mock_open(read_data="invalid json"))
    with pytest.raises(json.JSONDecodeError):
        HyperparameterSpaceRepository.load_json("test.json")

def test_save_and_load_json_success(sample_data, mocker, tmpdir):
    # Use tmpdir for a temporary file
    file_path = tmpdir.join("test.json")

    # Save the sample data
    HyperparameterSpaceRepository.save_json(sample_data, str(file_path))

    # Load the data back
    loaded_data = HyperparameterSpaceRepository.load_json(str(file_path))

    # Assert that the saved and loaded data are the same
    assert loaded_data == sample_data


def test_save_json_file_exists(sample_data, mocker):
    # Mock os.path.exists to return True (file exists)
    mocker.patch("os.path.exists", return_value=True)
    with pytest.raises(FileExistsError):
        HyperparameterSpaceRepository.save_json(sample_data, "test.json", overwrite=False)

def test_save_json_overwrite_success(sample_data, tmpdir):
    # Use tmpdir for a temporary file
    file_path = tmpdir.join("test.json")

    # First, save the sample data
    HyperparameterSpaceRepository.save_json(sample_data, str(file_path))

    # Ensure the file exists now
    assert os.path.exists(file_path)

    # Overwrite the existing file with the same sample data
    HyperparameterSpaceRepository.save_json(sample_data, str(file_path), overwrite=True)

    # Load the data back to verify
    loaded_data = HyperparameterSpaceRepository.load_json(str(file_path))

    # Assert that the saved and loaded data are the same
    assert loaded_data == sample_data

