# mloptimizer/test/interfaces/api/test_hyperparameter_space_builder.py
import os.path
import pytest
from sklearn.tree import DecisionTreeClassifier

from mloptimizer.domain.hyperspace import HyperparameterSpace
from mloptimizer.interfaces.api import HyperparameterSpaceBuilder
from mloptimizer.infrastructure.repositories import HyperparameterSpaceRepository


@pytest.fixture
def mock_service(mocker):
    return mocker.patch('mloptimizer.application.HyperparameterSpaceService')


def test_add_int_param(mock_service):
    builder = HyperparameterSpaceBuilder()
    builder.add_int_param("param1", 1, 10)
    assert "param1" in builder.evolvable_hyperparams


def test_add_float_param(mock_service):
    builder = HyperparameterSpaceBuilder()
    builder.add_float_param("param2", 10, 100)
    assert "param2" in builder.evolvable_hyperparams


def test_add_categorical_param(mock_service):
    builder = HyperparameterSpaceBuilder()
    builder.add_categorical_param("param3", ["a", "b", "c"])
    assert "param3" in builder.evolvable_hyperparams


def test_set_fixed_param(mock_service):
    builder = HyperparameterSpaceBuilder()
    builder.set_fixed_param("fixed_param1", 5)
    assert "fixed_param1" in builder.fixed_hyperparams

def test_set_fixed_params(mock_service):
    builder = HyperparameterSpaceBuilder()
    builder.set_fixed_params({"fixed_param1": 5, "fixed_param2": 10})
    assert "fixed_param1" in builder.fixed_hyperparams
    assert "fixed_param2" in builder.fixed_hyperparams

def test_build(mock_service):
    builder = HyperparameterSpaceBuilder()
    builder.add_int_param("param1", 1, 10)
    builder.set_fixed_param("fixed_param1", 5)
    space = builder.build()

    assert isinstance(space, HyperparameterSpace)
    assert space.fixed_hyperparams["fixed_param1"] == 5
    assert space.evolvable_hyperparams["param1"].name == "param1"


def test_load_default_space(mock_service, mocker):
    mock_service.load_hyperparameter_space.return_value = HyperparameterSpace({}, {})
    mocker.patch('mloptimizer.infrastructure.repositories.HyperparameterSpaceRepository.load_json', return_value={
        'fixed_hyperparams': {},
        'evolvable_hyperparams': {}
    })

    builder = HyperparameterSpaceBuilder()
    result = builder.load_default_space(estimator_class=DecisionTreeClassifier)

    assert isinstance(result, HyperparameterSpace)


def test_save_space(mock_service, mocker, tmp_path):
    space = HyperparameterSpace({}, {})
    mocker.patch('mloptimizer.infrastructure.repositories.HyperparameterSpaceRepository.save_json')

    builder = HyperparameterSpaceBuilder()
    builder.save_space(space, os.path.join(tmp_path, "hyperspace.json"), overwrite=True)

    HyperparameterSpaceRepository.save_json.assert_called_once()

def test_load_space_from_file(mock_service, mocker, tmp_path):
    import json
    mocker.patch('mloptimizer.infrastructure.repositories.HyperparameterSpaceRepository.load_json')
    builder = HyperparameterSpaceBuilder()
    file_path = os.path.join(tmp_path, "hyperspace.json")

    # Write dummy content to file
    with open(file_path, 'w') as f:
        f.write(json.dumps({
            'fixed_hyperparams': {'prueba': 1},
            'evolvable_hyperparams': {
                "min_samples_split": {
                    "name": "min_samples_split",
                    "min_value": 2,
                    "max_value": 50,
                    "hyperparam_type": "int"
                }
            }
        }))

    result = builder.load_space(file_path)

    assert isinstance(result, HyperparameterSpace)
    HyperparameterSpaceRepository.load_json.assert_called_once_with(file_path)