from datetime import datetime
from typing import Tuple, Optional, Dict, Any
import pandas as pd
from .base import BaseResource
from .schemas.account import AccountSchema, AccountUpdateSchema
from brynq_sdk_functions import Functions

class Account(BaseResource):
    """
    Account resource for DATEV Lohn und Gehalt
    Handles bank account details for employees
    Find this in UI: Schnellerfassung > Bank
    """

    def __init__(self, datev):
        super().__init__(datev)

    def get(self, employee_id: Optional[str] = None, reference_date: Optional[datetime] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get bank account data for employees

        Args:
            employee_id: Optional ID of a specific employee. If not provided, bank account data for all employees is returned.
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

        # Determine the endpoint based on whether employee_id is provided
        if employee_id:
            if self.debug:
                print(f"Fetching bank account data for employee {employee_id}")
            endpoint = f"clients/{client_id}/employees/{employee_id}/account"
        else:
            if self.debug:
                print("Fetching bank account data for all employees")
            endpoint = f"clients/{client_id}/account"

        data = self._make_request(endpoint, params=params)

        # Convert single object to a list for DataFrame if necessary
        if isinstance(data, dict):
            data = [data]

        df = pd.DataFrame(data)
        valid_data, invalid_data = Functions.validate_data(df, AccountSchema, debug=self.debug)

        return valid_data, invalid_data

    def update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update bank account data for an employee

        Args:
            account_data: Updated bank account data

        Returns:
            Updated bank account data
        """
        # Validate and format using our generic method
        validated_data = self._validate_request_data(
            data=data,
            schema_class=AccountUpdateSchema
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
            print(f"Updating bank account data for employee {employee_id}")

        # PUT request returns 204 No Content on success
        resp =self._make_request(f"clients/{client_id}/employees/{employee_id}/account",
                         method="PUT",
                         json_data=validated_data,
                         params=params)

        return resp
