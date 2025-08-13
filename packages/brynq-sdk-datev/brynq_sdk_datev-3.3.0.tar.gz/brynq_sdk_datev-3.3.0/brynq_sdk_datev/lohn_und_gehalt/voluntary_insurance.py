from datetime import datetime
from typing import Tuple, Optional, Dict, Any, List, Union
import pandas as pd
from .base import BaseResource
from .schemas.voluntary_insurance import VoluntaryInsuranceSchema, VoluntaryInsuranceUpdateSchema
from brynq_sdk_functions import Functions

class VoluntaryInsurance(BaseResource):
    """
    VoluntaryInsurance resource for DATEV Lohn und Gehalt
    Handles voluntary insurance details for employees
    Supports both batch operations and per-employee operations
    Find this in UI under Mitarbeiter > Stammdaten > Sozialversicherung > Gesetzliche Krankenkasse
    """

    def __init__(self, datev):
        super().__init__(datev)

    def get(self, reference_date: Optional[datetime] = None, employee_id: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get voluntary insurance data for all employees or a specific employee

        Args:
            reference_date: Optional reference date
            employee_id: Optional employee ID to get voluntary insurance for a specific employee

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
            if employee_id:
                print(f"Fetching voluntary insurance data for employee {employee_id}")
            else:
                print("Fetching voluntary insurance data for all employees")

        # Construct the appropriate endpoint URL based on parameters
        if employee_id:
            endpoint = f"clients/{client_id}/employees/{employee_id}/voluntary-insurance"
        else:
            endpoint = f"clients/{client_id}/voluntary-insurance"

        data = self._make_request(endpoint, params=params)

        # Convert single object to a list for DataFrame if necessary
        if isinstance(data, dict):
            data = [data]

        df = pd.DataFrame(data)
        valid_data, invalid_data = Functions.validate_data(df, VoluntaryInsuranceSchema, debug=self.debug)

        return valid_data, invalid_data

    def update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update voluntary insurance data for an employee

        Args:
            data: Updated voluntary insurance data, including employee_id and reference_date

        Returns:
            Updated voluntary insurance data
        """
        # Validate and format using our generic method
        validated_data = self._validate_request_data(
            data=data,
            schema_class=VoluntaryInsuranceUpdateSchema
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
            print(f"Updating voluntary insurance data for employee {employee_id}")

        # Construct the endpoint for the specific employee
        endpoint = f"clients/{client_id}/employees/{employee_id}/voluntary-insurance"

        # PUT request returns 204 No Content on success
        return self._make_request(endpoint,
                                method="PUT",
                                json_data=validated_data,
                                params=params)
