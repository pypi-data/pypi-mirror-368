import pandas as pd
import json
from typing import Any, Optional, Tuple, Dict
from datetime import datetime

from .base import BaseResource
from .schemas import CostUnitsSchema, CostUnitsUpdateSchema
from brynq_sdk_functions import Functions


class CostUnits(BaseResource):
    """Resource for interacting with the DATEV Lohn und Gehalt Cost Units API endpoints"""

    def __init__(self, lohn_und_gehalt):
        super().__init__(lohn_und_gehalt)
        self.batch_endpoint = "cost-units"
        self.individual_endpoint = "cost-units/{cost_unit_id}"
        self.schema = CostUnitsSchema

    def get(self, cost_unit_id: Optional[str] = None,
            reference_date: Optional[datetime] = None) -> Tuple[pd.DataFrame, Dict]:
        """
        Get cost units data.

        Args:
            cost_unit_id: Specific cost unit ID to retrieve
            reference_date: Date for which to retrieve the data

        Returns:
            DataFrame with cost units data and additional metadata dict
        """
        params = {}
        if reference_date:
            params["reference-date"] = reference_date.strftime("%Y-%m-%d")
        else:
            params["reference-date"] = datetime.now().strftime("%Y-%m-%d")

        # Use client_id directly from the DatevLohnUndGehalt instance
        client_id = self.datev.client_id

        if self.debug:
            if cost_unit_id:
                print(f"Fetching specific cost unit {cost_unit_id}")
            else:
                print("Fetching all cost units")

        # Construct the appropriate endpoint URL based on parameters
        if cost_unit_id:
            # Get specific cost unit
            endpoint = f"clients/{client_id}/{self.individual_endpoint.format(cost_unit_id=cost_unit_id)}"
            data = self._make_request(endpoint, params=params)
            # Convert single item to list for consistency
            if isinstance(data, dict):
                data = [data]
        else:
            # Get all cost units
            endpoint = f"clients/{client_id}/{self.batch_endpoint}"
            data = self._make_request(endpoint, params=params)

        # Convert to DataFrame and validate
        df = pd.DataFrame(data)
        valid_data, invalid_data = Functions.validate_data(df, self.schema, debug=self.debug)

        return valid_data, invalid_data

    def update(self, data: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict]:
        """
        Update an existing cost unit. Adding a new one should work according to the Datev docs by passing a non existing costunit ID but in practice, this does not work.

        Args:
            data: Dictionary with cost unit data, including cost_unit_id and reference_date

        Returns:
            DataFrame with updated cost center data and additional metadata dict
        """
        # Validate request data
        validated_data = self._validate_request_data(
            data=data,
            schema_class=CostUnitsUpdateSchema
        )

        params = {}
        if validated_data.get("reference_date"):
            params["reference-date"] = validated_data["reference_date"]
            validated_data.pop("reference_date")
        else:
            params["reference-date"] = datetime.now().strftime("%Y-%m-%d")

        # Use client_id directly from the DatevLohnUndGehalt instance
        client_id = self.datev.client_id
        cost_unit_id = validated_data.get("id")

        # Construct the endpoint
        endpoint = f"clients/{client_id}/{self.individual_endpoint.format(cost_unit_id=cost_unit_id)}"

        if self.debug:
            print(f"Updating cost unit {cost_unit_id}")

        # PUT request returns 204 No Content on success
        return self._make_request(endpoint,
                                method="PUT",
                                json_data=validated_data,
                                params=params)

    def delete(self, cost_unit_id: str,
               reference_date: Optional[datetime] = None) -> Dict:
        """
        Delete a specific cost unit.

        Args:
            cost_unit_id: Cost unit ID to delete
            reference_date: Reference date

        Returns:
            Response metadata
        """
        params = {}
        if reference_date:
            params["reference-date"] = reference_date.strftime("%Y-%m-%d")
        else:
            params["reference-date"] = datetime.now().strftime("%Y-%m-%d")

        # Use client_id directly from the DatevLohnUndGehalt instance
        client_id = self.datev.client_id

        # Construct the endpoint
        endpoint = f"clients/{client_id}/{self.individual_endpoint.format(cost_unit_id=cost_unit_id)}"

        if self.debug:
            print(f"Deleting cost unit {cost_unit_id}")

        # Make the DELETE request
        return self._make_request(endpoint, method="DELETE", params=params)
