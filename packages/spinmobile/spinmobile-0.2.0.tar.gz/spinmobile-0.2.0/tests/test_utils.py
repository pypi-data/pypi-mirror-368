import pytest
from spinmobile.utils import check_values


def test_check_values_exact_match():
    response = {"key1": "value1", "key2": "value2"}
    input_data = {"key1": "value1", "key2": "value2"}
    result = check_values(response, input_data)
    assert result == {"key1": True, "key2": True}


def test_check_values_case_insensitive():
    response = {"key1": "Value1", "key2": "VALUE2"}
    input_data = {"key1": "value1", "key2": "value2"}
    result = check_values(response, input_data)
    assert result == {"key1": True, "key2": True}


def test_check_values_partial_match():
    response = {"key1": "value1", "key2": "different"}
    input_data = {"key1": "value1", "key2": "value2"}
    result = check_values(response, input_data)
    assert result == {"key1": True, "key2": False}


def test_check_values_similarity():
    response = {"key1": "value1", "key2": "valeu2"}
    input_data = {"key1": "value1", "key2": "value2"}
    result = check_values(response, input_data, 0.9)
    assert result == {"key1": True, "key2": False}
