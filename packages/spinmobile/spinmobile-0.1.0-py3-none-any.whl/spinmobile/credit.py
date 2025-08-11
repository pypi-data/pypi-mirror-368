"""Credit bureau scoring operations.

This module provides services for retrieving credit scores using the Spinmobile API.
"""

from typing import Dict, Any
from .client import SpinmobileClient
from .utils import check_values


class CreditService:
    """
    Service for handling credit score operations.

    Attributes:
        client (SpinmobileClient): The client used to interact with the Spinmobile API.
    """

    def __init__(self, client: SpinmobileClient):
        """
        Initialize the CreditService.

        Args:
            client (SpinmobileClient): The client used to interact with the Spinmobile API.
        """
        self.client = client

    async def get_credit_score(self, id_number: str) -> Dict[str, Any]:
        """
        Retrieve the credit score for a user.

        Args:
            id_number (str): The user's national ID number.

        Returns:
            Dict[str, Any]: The response from the API containing credit score details.

        Raises:
            ValueError: If the credit score verification fails due to mismatched details.
        """
        payload = {"search_type": "Metropol", "identifier": id_number}
        response = await self.client.post("/api/analytics/account/metropol", json=payload)

        # Validate the response
        input_data = {"id_no": id_number}
        validation_results = check_values(
            response.get("data", {}).get("id_no"), input_data
        )

        if not validation_results.get("id_no"):
            raise ValueError("Credit score verification failed: ID number mismatch.")

        return response
