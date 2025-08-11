from typing import Dict, Any
from difflib import SequenceMatcher


def check_values(
    response: Dict[str, Any], input_data: Dict[str, Any], threshold: float = 0.8
) -> Dict[str, bool]:
    """
    Compare values in the response with those passed during the function call.

    Args:
        response (Dict[str, Any]): The response data from the API.
        input_data (Dict[str, Any]): The input data passed to the function.

    Returns:
        Dict[str, bool]: A dictionary indicating whether each input value matches or is similar to the corresponding response value.
    """
    comparison_results = {}

    for key, input_value in input_data.items():
        response_value = response.get(key)
        if isinstance(input_value, str) and isinstance(response_value, str):
            # Perform a case-insensitive comparison for strings
            similarity = SequenceMatcher(
                None, input_value.strip().lower(), response_value.strip().lower()
            ).ratio()
            comparison_results[key] = similarity > threshold
        else:
            # Perform a direct comparison for other types
            comparison_results[key] = input_value == response_value

    return comparison_results
