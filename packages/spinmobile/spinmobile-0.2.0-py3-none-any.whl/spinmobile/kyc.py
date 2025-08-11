"""KYC operations.

This module provides services for verifying user identity using the Spinmobile API.
"""

from typing import Dict, Any
from spinmobile.client import SpinmobileClient
from spinmobile.utils import check_values


class KYCService:
    """
    Service for handling Know Your Customer (KYC) operations.

    Attributes:
        client (SpinmobileClient): The client used to interact with the Spinmobile API.
    """

    def __init__(self, client: SpinmobileClient):
        """
        Initialize the KYCService.

        Args:
            client (SpinmobileClient): The client used to interact with the Spinmobile API.
        """
        self.client = client

    async def verify_identity(
        self, id_number: str, first_name: str, last_name: str
    ) -> Dict[str, Any]:
        """
        Verify the identity of a user.

        Args:
            id_number (str): The user's national ID number.
            first_name (str): The user's first name.
            last_name (str): The user's last name.

        Returns:
            Dict[str, Any]: The response from the API containing verification details.

        Raises:
            ValueError: If the verification fails due to mismatched details.
        """
        payload = {"search_type": "identity", "identifier": id_number}
        response = await self.client.post("/api/analytics/account/iprs", json=payload)

        # Validate the response
        response_data = response.get("data", {})
        input_values = {"id_number": id_number, "name": f"{first_name} {last_name}"}
        response_values = {
            "id_number": response_data.get("id_number"),
            "name": f"{response_data.get('first_name', '')} {response_data.get('last_name', '')} {response_data.get('surname', '')}",
        }

        validation_results = check_values(response_values, input_values)

        # Ensure all validation results are True
        if not all(validation_results.values()):
            raise ValueError(
                "Identity verification failed: Mismatch in provided details."
            )

        return response
