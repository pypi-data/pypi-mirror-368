import json
import requests
from typing import Dict, Any, Optional, Tuple, Union, List, Type
import pandas as pd
from datetime import datetime
from pydantic import BaseModel

class BaseResource:
    """Base class for all DATEV Lohn und Gehalt resources"""

    def __init__(self, datev):
        from . import DatevLohnUndGehalt
        self.datev: DatevLohnUndGehalt = datev
        self.debug = datev.debug

    def _make_request(
        self,
        endpoint_path: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Make a request to the DATEV API via the agent

        Args:
            endpoint_path: The endpoint path to call
            method: HTTP method (GET, POST, PUT, DELETE)
            params: Query parameters
            json_data: JSON body for POST/PUT requests
            files: Files for multipart/form-data requests

        Returns:
            API response data
        """
        request = {
            "url": f"{self.datev.local_url}/{endpoint_path}",
            "method": method,
            "headers": self.datev.local_headers
        }

        if params:
            request["params"] = params

        if json_data:
            request["body"] = json_data

        if files:
            # Handle multipart form data
            request["files"] = files

        body = {
            "local_requests": [request]
        }

        if self.debug:
            print(f"Making {method} request to {endpoint_path}")
            print(f"Request body: {json.dumps(body, indent=2, default=str)}")

        resp = requests.post(self.datev.agent_url,
                             headers=self.datev.headers,
                             json=body,
                             timeout=self.datev.timeout)

        if self.debug:
            print(f"Response status: {resp.status_code}")
            print(f"Response headers: {resp.headers}")
            try:
                print(f"Response body: {json.dumps(resp.json(), indent=2)}")
            except:
                print(f"Response body could not be parsed as JSON: {resp.text[:200]}...")

        resp.raise_for_status()
        return resp.json()[0].get("response")

    def _validate_request_data(
        self,
        data: Dict[str, Any],
        schema_class: Type[BaseModel]
    ) -> Dict[str, Any]:
        """
        Validate request data against a pydantic schema and format dates

        Args:
            data: The data to validate
            schema_class: The pydantic schema class to use for validation

        Returns:
            Validated and formatted data dictionary
        """
        try:
            # Validate against schema
            validated = schema_class(**data)
            validated_data = validated.dict(exclude_none=True)

            # Show what fields were dropped if in debug mode
            if self.debug:
                dropped_fields = {k: v for k, v in data.items() if k not in validated_data}
                if dropped_fields:
                    print(f"Dropped fields: {dropped_fields}")

            # Format dates automatically
            validated_data = self._format_date_fields(validated_data)

            # Show final data if in debug mode
            if self.debug:
                print(f"Validated data: {validated_data}")

            return validated_data

        except Exception as e:
            if self.debug:
                print(f"Validation error: {str(e)}")
            raise ValueError(f"Invalid data: {str(e)}")

    def _format_date_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically format all datetime objects to YYYY-MM-DD string format

        Args:
            data: The data dictionary

        Returns:
            Data dictionary with formatted date fields
        """
        formatted_data = {}

        for key, value in data.items():
            if isinstance(value, datetime):
                formatted_data[key] = value.strftime("%Y-%m-%d")
            elif isinstance(value, dict):
                # Handle nested dictionaries
                formatted_data[key] = self._format_date_fields(value)
            elif isinstance(value, list):
                # Handle lists of items
                formatted_data[key] = [
                    self._format_date_fields(item) if isinstance(item, dict)
                    else (item.strftime("%Y-%m-%d") if isinstance(item, datetime) else item)
                    for item in value
                ]
            else:
                formatted_data[key] = value

        return formatted_data
