import pytest

from mloptimizer.domain.hyperspace import Hyperparam


@pytest.fixture
def int_param():
    return Hyperparam('int_param', 1, 10, 'int')


@pytest.fixture
def float_param():
    return Hyperparam('float_param', 1, 200, 'float', scale=100)


@pytest.fixture
def nexp_param():
    return Hyperparam('nexp_param', -2, 10, 'nexp')


@pytest.fixture
def x10_param():
    return Hyperparam('x10_param', 0, 10, 'x10')


@pytest.fixture
def list_param():
    return Hyperparam('list_param', 0, 2, 'list', values_str=['a', 'b', 'c'])


@pytest.fixture
def list_method_param():
    return Hyperparam.from_values_list('list_method_param', ['a', 'b', 'c'])


def test_int_param_correct(int_param):
    assert int_param.correct(5) == 5
    assert int_param.correct(0) == 1
    assert int_param.correct(11) == 10


def test_float_param_correct(float_param):
    assert float_param.correct(50) == 0.5
    assert float_param.correct(300) == 2.0
    assert float_param.correct(150) == 1.5


def test_nexp_param_correct(nexp_param):
    assert nexp_param.correct(-3) == 100
    assert nexp_param.correct(-1) == 10
    assert nexp_param.correct(0) == 1
    assert nexp_param.correct(10) == 0.0000000001
    assert nexp_param.correct(11) == 0.0000000001


def test_x10_param_correct(x10_param):
    assert x10_param.correct(5) == 50
    assert x10_param.correct(-1) == 0
    assert x10_param.correct(11) == 100


def test_list_param_correct(list_param):
    assert list_param.correct(-1) == 'a'
    assert list_param.correct(0.2) == 'a'
    assert list_param.correct(1) == 'b'
    assert list_param.correct(2) == 'c'
    assert list_param.correct(3) == 'c'


def test_list_method_param_correct(list_method_param):
    assert list_method_param.correct(-1) == 'a'
    assert list_method_param.correct(0.2) == 'a'
    assert list_method_param.correct(1) == 'b'
    assert list_method_param.correct(2) == 'c'
    assert list_method_param.correct(3) == 'c'


def test_str_float_param(float_param):
    float_param_str = str(float_param)
    assert float_param_str == "Hyperparam('float_param', 1, 200, 'float', 100)"


def test_str_list_param(list_param):
    list_param_str = str(list_param)
    assert list_param_str == "Hyperparam('list_param', 0, 2, 'list', ['a', 'b', 'c'])"
