"""Financial statement file analysis operations.

This module provides services for submitting and analyzing financial statements using the Spinmobile API.
"""

from typing import Dict, Any
from .client import SpinmobileClient


class FileAnalysisService:
    """
    Service for handling financial statement file analysis operations.

    Attributes:
        client (SpinmobileClient): The client used to interact with the Spinmobile API.
    """

    def __init__(self, client: SpinmobileClient):
        """
        Initialize the FileAnalysisService.

        Args:
            client (SpinmobileClient): The client used to interact with the Spinmobile API.
        """
        self.client = client

    async def submit_statement(
        self, file_paths: list, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit documents for combined analysis.

        Supports only MPESA and BANK statements.

        Args:
            file_paths (list): A list of file paths to be submitted.
            payload (Dict[str, Any]): The payload containing metadata for the submission.

        Returns:
            Dict[str, Any]: The response from the submission endpoint.

        Raises:
            ValueError: If the document type is not supported.
        """
        # Validate document type
        supported_types = ["MPESA", "BANK"]
        document_type = payload.get("document_type")
        if document_type not in supported_types:
            raise ValueError(
                f"Unsupported document type: {document_type}. Supported types are: {supported_types}"
            )

        # Prepare files for submission
        files = {
            f"file_{i+1}": open(file_path, "rb")
            for i, file_path in enumerate(file_paths)
        }

        try:
            return await self.client.post(
                "/api/analytics/combined-statement/", json=payload, files=files
            )
        finally:
            # Ensure all files are closed
            for file in files.values():
                file.close()

    async def check_analysis_status(self, request_id: str) -> Dict[str, Any]:
        """
        Check the status of a combined analysis request.

        Args:
            request_id (str): The unique identifier for the request.

        Returns:
            Dict[str, Any]: The response from the status query endpoint.
        """
        payload = {"score_type": "COMBINED", "unique_identifier": request_id}
        return await self.client.post("/api/analytics/status-query/", json=payload)

    async def get_analysis_result(self, request_id: str) -> Dict[str, Any]:
        """
        Get the result of a combined analysis request.

        Args:
            request_id (str): The unique identifier for the request.

        Returns:
            Dict[str, Any]: The response from the analysis query endpoint.
        """
        payload = {"score_type": "COMBINED", "unique_identifier": request_id}
        return await self.client.post("/api/analytics/analysis-query/", json=payload)
