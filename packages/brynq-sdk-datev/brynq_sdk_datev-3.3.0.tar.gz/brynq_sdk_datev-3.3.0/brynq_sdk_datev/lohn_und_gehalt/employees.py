from datetime import datetime
from typing import Tuple, Optional, Dict, Any, List
import pandas as pd
from .base import BaseResource
from .schemas.employees import EmployeeSchema, EmployeeCreateSchema, EmployeeUpdateSchema
from brynq_sdk_functions import Functions

class Employee(BaseResource):
    """
    Employee resource for DATEV Lohn und Gehalt
    """

    def __init__(self, datev):
        super().__init__(datev)

    def get(self, employee_id: Optional[str] = None, reference_date: Optional[datetime] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get employee data

        Args:
            employee_id: Optional ID of a specific employee. If not provided, all employees are returned.
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
                print(f"Fetching employee {employee_id}")
            endpoint = f"clients/{client_id}/employees/{employee_id}"
        else:
            if self.debug:
                print("Fetching all employees")
            endpoint = f"clients/{client_id}/employees"

        data = self._make_request(endpoint, params=params)

        # Convert single object to a list for DataFrame if necessary
        if isinstance(data, dict):
            data = [data]

        df = pd.DataFrame(data)
        valid_data, invalid_data = Functions.validate_data(df, EmployeeSchema, debug=self.debug)

        return valid_data, invalid_data

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new employee

        Args:
            data: Data for the new employee, including reference_date if needed

        Returns:
            Created employee data
        """
        # Validate and format using our generic method
        validated_data = self._validate_request_data(
            data=data,
            schema_class=EmployeeCreateSchema
        )

        params = {}
        if validated_data.get("reference_date"):
            params["reference-date"] = validated_data["reference_date"]
            validated_data.pop("reference_date")
        else:
            params["reference-date"] = datetime.now().strftime("%Y-%m-%d")

        # Use client_id directly from the DatevLohnUndGehalt instance
        client_id = self.datev.client_id

        if self.debug:
            print("Creating new employee")

        # POST request returns the created object
        return self._make_request(f"clients/{client_id}/employees",
                              method="POST",
                              json_data=validated_data,
                              params=params)

    def update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an employee

        Args:
            data: Updated employee data, including employee_id and reference_date

        Returns:
            Updated employee data
        """
        # Validate and format using our generic method
        validated_data = self._validate_request_data(
            data=data,
            schema_class=EmployeeUpdateSchema
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
            print(f"Updating employee {employee_id}")

        # PUT request returns 204 No Content on success
        return self._make_request(f"clients/{client_id}/employees/{employee_id}",
                              method="PUT",
                              json_data=validated_data,
                              params=params)
