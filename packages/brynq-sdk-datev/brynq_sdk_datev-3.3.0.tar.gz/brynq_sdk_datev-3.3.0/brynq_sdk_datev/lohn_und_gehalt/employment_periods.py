from datetime import datetime
from typing import Tuple, Optional, Dict, Any, List
import pandas as pd
from .base import BaseResource
from .schemas.employment_periods import EmploymentPeriodsSchema, EmploymentPeriodsUpdateSchema, EmploymentPeriodsCreateSchema
from brynq_sdk_functions import Functions

class EmploymentPeriods(BaseResource):
    """
    EmploymentPeriods resource for DATEV Lohn und Gehalt
    Handles employment period details for employees
    Supports both batch operations and per-employee operations
    """

    def __init__(self, datev):
        super().__init__(datev)

    def get(self, reference_date: Optional[datetime] = None, employee_id: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get employment periods data for all employees or a specific employee

        Args:
            reference_date: Optional reference date
            employee_id: Optional employee ID to get employment periods for a specific employee

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
                print(f"Fetching employment periods data for employee {employee_id}")
            else:
                print("Fetching employment periods data for all employees")

        if employee_id:
            endpoint = f"clients/{client_id}/employees/{employee_id}/employment-periods"
        else:
            endpoint = f"clients/{client_id}/employment-periods"

        data = self._make_request(endpoint, params=params)

        # Convert single object to a list for DataFrame if necessary
        if isinstance(data, dict):
            data = [data]

        df = pd.DataFrame(data)
        valid_data, invalid_data = Functions.validate_data(df, EmploymentPeriodsSchema, debug=self.debug)

        return valid_data, invalid_data

    def update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing employment period for a specific employee

        Args:
            data: Updated employment periods data, including employee_id, employment_period_id, and reference_date

        Returns:
            Updated employment period data
        """
        # Validate and format using our generic method
        validated_data = self._validate_request_data(
            data=data,
            schema_class=EmploymentPeriodsUpdateSchema
        )

        params = {}
        if validated_data.get("reference_date"):
            params["reference-date"] = validated_data["reference_date"]
            validated_data.pop("reference_date")
        else:
            params["reference-date"] = datetime.now().strftime("%Y-%m-%d")

        # Use client_id directly from the DatevLohnUndGehalt instance
        client_id = self.datev.client_id
        employment_period_id = validated_data.get("id")
        employee_id = validated_data.get("personnel_number")

        if self.debug:
            print(f"Updating employment period {employment_period_id} for employee {employee_id}")

        # According to the API spec, PUT requires the specific employment period ID
        endpoint = f"clients/{client_id}/employees/{employee_id}/employment-periods/{employment_period_id}"

        # PUT request returns 204 No Content on success
        return self._make_request(endpoint,
                               method="PUT",
                               json_data=validated_data,
                               params=params)

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new employment period for a specific employee

        Args:
            data: Employment periods data to create, including employee_id and reference_date

        Returns:
            Newly created employment period data
        """
        # Validate and format using our generic method
        validated_data = self._validate_request_data(
            data=data,
            schema_class=EmploymentPeriodsCreateSchema
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

        if self.debug:
            print(f"Creating employment period for employee {employee_id}")

        endpoint = f"clients/{client_id}/employees/{employee_id}/employment-periods"

        # POST request returns 201 Created on success
        return self._make_request(endpoint,
                              method="POST",
                              json_data=validated_data,
                              params=params)

    def delete(self, employee_id: str, employment_period_id: str, reference_date: Optional[datetime] = None) -> None:
        """
        Delete an employment period for a specific employee

        Args:
            employee_id: Employee ID for the employee
            employment_period_id: ID of the employment period to delete
            reference_date: Optional reference date

        Returns:
            None
        """
        params = {}
        if reference_date:
            params["reference-date"] = reference_date.strftime("%Y-%m-%d")
        else:
            params["reference-date"] = datetime.now().strftime("%Y-%m-%d")

        # Use client_id directly from the DatevLohnUndGehalt instance
        client_id = self.datev.client_id

        if self.debug:
            print(f"Deleting employment period {employment_period_id} for employee {employee_id}")

        endpoint = f"clients/{client_id}/employees/{employee_id}/employment-periods/{employment_period_id}"

        # DELETE request returns 204 No Content on success
        self._make_request(endpoint, method="DELETE", params=params)
        return None
