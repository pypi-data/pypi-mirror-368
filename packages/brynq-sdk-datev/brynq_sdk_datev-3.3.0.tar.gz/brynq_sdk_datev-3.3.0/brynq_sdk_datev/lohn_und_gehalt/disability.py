from datetime import datetime
from typing import Tuple, Optional, Dict, Any
import pandas as pd
from .base import BaseResource
from .schemas.disability import DisabilitySchema, DisabilityUpdateSchema
from brynq_sdk_functions import Functions

class Disability(BaseResource):
    """
    Disability resource for DATEV Lohn und Gehalt
    Handles disability details for employees
    """

    def __init__(self, datev):
        super().__init__(datev)

    def get(self, reference_date: Optional[datetime] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get disability data for all employees

        Args:
            reference_date: Optional reference date

        Returns:
            Tuple of (valid_data, invalid_data) DataFrames
        """
        params = {}
        if reference_date:
            params["reference-date"] = reference_date.strftime("%Y-%m-%d")
        else:
            params["reference-date"] = datetime.now().strftime("%Y-%m-%d")

        # Use client_id directly from the DatevLohnUndGehalt instance
        client_id = self.datev.client_id

        if self.debug:
            print("Fetching disability data for all employees")
        endpoint = f"clients/{client_id}/disability"

        data = self._make_request(endpoint, params=params)

        # Convert single object to a list for DataFrame if necessary
        if isinstance(data, dict):
            data = [data]

        df = pd.DataFrame(data)
        valid_data, invalid_data = Functions.validate_data(df, DisabilitySchema, debug=self.debug)

        return valid_data, invalid_data

    def update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update disability data

        Args:
            data: Updated disability data, including employee_id and reference_date

        Returns:
            Updated disability data
        """
        # Validate and format using our generic method
        validated_data = self._validate_request_data(
            data=data,
            schema_class=DisabilityUpdateSchema
        )

        params = {}
        if validated_data.get("reference_date"):
            params["reference-date"] = validated_data["reference_date"]
            validated_data.pop("reference_date")
        else:
            params["reference-date"] = datetime.now().strftime("%Y-%m-%d")

        # Use client_id directly from the DatevLohnUndGehalt instance
        client_id = self.datev.client_id
        employee_id = validated_data.get("id")

        if self.debug:
            print("Updating disability data")

        # PUT request returns 204 No Content on success
        return self._make_request(f"clients/{client_id}/employees/{employee_id}/disability",
                              method="PUT",
                              json_data=validated_data,
                              params=params)
