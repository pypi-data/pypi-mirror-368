from datetime import datetime
from typing import Tuple, Optional, Dict, Any, List, Union
import pandas as pd
from .base import BaseResource
from .schemas.hourly_wages import HourlyWagesSchema, HourlyWagesUpdateSchema
from brynq_sdk_functions import Functions

class HourlyWages(BaseResource):
    """
    HourlyWages resource for DATEV Lohn und Gehalt
    Handles hourly wage details for employees
    Supports both batch operations and per-employee operations
    Find this in UI under Mitarbeiter > Stammdaten > Entlohnung > Stunden/ Tagelöhne OR Schnellerfassung > Entlohnung > Stunden/ Tagelöhne
    """

    def __init__(self, datev):
        super().__init__(datev)

    def get(self, reference_date: Optional[datetime] = None, employee_id: Optional[str] = None, hourly_wage_id: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get hourly wages data for all employees, a specific employee, or a specific hourly wage

        Args:
            reference_date: Optional reference date
            employee_id: Optional employee ID to get hourly wages for a specific employee
            hourly_wage_id: Optional hourly wage ID to get a specific hourly wage

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
            if hourly_wage_id and employee_id:
                print(f"Fetching hourly wage data for wage {hourly_wage_id} of employee {employee_id}")
            elif employee_id:
                print(f"Fetching hourly wages data for employee {employee_id}")
            else:
                print("Fetching hourly wages data for all employees")

        # Construct the appropriate endpoint URL based on parameters
        if hourly_wage_id and employee_id:
            endpoint = f"clients/{client_id}/employees/{employee_id}/hourly-wages/{hourly_wage_id}"
        elif employee_id:
            endpoint = f"clients/{client_id}/employees/{employee_id}/hourly-wages"
        else:
            endpoint = f"clients/{client_id}/hourly-wages"

        data = self._make_request(endpoint, params=params)

        # Convert single object to a list for DataFrame if necessary
        if isinstance(data, dict):
            data = [data]

        df = pd.DataFrame(data)
        valid_data, invalid_data = Functions.validate_data(df, HourlyWagesSchema, debug=self.debug)

        return valid_data, invalid_data

    def update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update hourly wages data

        Args:
            data: Updated hourly wages data, including employee_id, hourly_wage_id, and reference_date

        Returns:
            Updated hourly wages data
        """
        # Validate and format using our generic method
        validated_data = self._validate_request_data(
            data=data,
            schema_class=HourlyWagesUpdateSchema
        )

        params = {}
        if validated_data.get("reference_date"):
            params["reference-date"] = validated_data["reference_date"]
            validated_data.pop("reference_date")
        else:
            params["reference-date"] = datetime.now().strftime("%Y-%m-%d")

        # Use client_id directly from the DatevLohnUndGehalt instance
        client_id = self.datev.client_id
        employee_id = validated_data.get("personnel_number")
        hourly_wage_id = validated_data.get("id")

        if self.debug:
            print(f"Updating hourly wage {hourly_wage_id} for employee {employee_id}")

        # Update a specific hourly wage for a specific employee
        endpoint = f"clients/{client_id}/employees/{employee_id}/hourly-wages/{hourly_wage_id}"

        # PUT request returns 204 No Content on success
        return self._make_request(endpoint,
                               method="PUT",
                               json_data=validated_data,
                               params=params)
