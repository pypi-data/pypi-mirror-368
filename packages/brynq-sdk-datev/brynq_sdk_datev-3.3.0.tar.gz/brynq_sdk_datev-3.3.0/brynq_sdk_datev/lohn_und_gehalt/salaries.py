import pandas as pd
import json
from typing import Optional, Tuple, Dict, List, Any
from datetime import datetime

from .base import BaseResource
from .schemas import (
    SalarySchema,
    SalaryCreateSchema
)
from brynq_sdk_functions import Functions


class Salaries(BaseResource):
    """Resource for interacting with the DATEV Lohn und Gehalt Salaries API endpoints"""

    def __init__(self, lohn_und_gehalt):
        super().__init__(lohn_und_gehalt)
        self.batch_endpoint = "salaries"
        self.employee_endpoint = "employees/{employee_id}/salaries"
        self.individual_endpoint = "employees/{employee_id}/salaries/{salary_id}"
        self.schema = SalarySchema

    def get(self, employee_id: Optional[str] = None,
            salary_id: Optional[str] = None,
            reference_date: Optional[datetime] = None) -> Tuple[pd.DataFrame, Dict]:
        """
        Get salary data.

        Args:
            employee_id: Employee ID to get salary data for
            salary_id: Specific salary ID to retrieve
            reference_date: Date for which to retrieve the data

        Returns:
            DataFrame with salary data and additional metadata dict
        """
        params = {}
        if reference_date:
            params["reference-date"] = reference_date.strftime("%Y-%m-%d")
        else:
            params["reference-date"] = datetime.now().strftime("%Y-%m-%d")

        # Use client_id directly from the DatevLohnUndGehalt instance
        client_id = self.datev.client_id

        if self.debug:
            if employee_id and salary_id:
                print(f"Fetching specific salary {salary_id} for employee {employee_id}")
            elif employee_id:
                print(f"Fetching all salaries for employee {employee_id}")
            else:
                print("Fetching all salaries for all employees")

        # Construct the appropriate endpoint URL based on parameters
        if employee_id and salary_id:
            # Get specific salary for specific employee
            endpoint = f"clients/{client_id}/{self.individual_endpoint.format(employee_id=employee_id, salary_id=salary_id)}"
            data = self._make_request(endpoint, params=params)
            # Convert single item to list for consistency
            if isinstance(data, dict):
                data = [data]
        elif employee_id:
            # Get all salaries for specific employee
            endpoint = f"clients/{client_id}/{self.employee_endpoint.format(employee_id=employee_id)}"
            data = self._make_request(endpoint, params=params)
        else:
            # Get all salaries for all employees
            endpoint = f"clients/{client_id}/{self.batch_endpoint}"
            data = self._make_request(endpoint, params=params)

        # Convert to DataFrame and validate
        df = pd.DataFrame(data)
        valid_data, invalid_data = Functions.validate_data(df, self.schema, debug=self.debug)

        return valid_data, invalid_data

    def create(self, data: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict]:
        """
        Create new salary entries for an employee.

        Args:
            data: Dictionary with salary data, including employee_id and reference_date

        Returns:
            DataFrame with created salary data and additional metadata dict
        """
        # Validate and format using our generic method
        validated_data = self._validate_request_data(
            data=data,
            schema_class=SalaryCreateSchema
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

        # Construct the endpoint
        endpoint = f"clients/{client_id}/{self.employee_endpoint.format(employee_id=employee_id)}"

        if self.debug:
            print(f"Creating new salary for employee {employee_id}")

        # Make the POST request
        response = self._make_request(endpoint, method="POST", json_data=validated_data, params=params)

        # Return the created data
        created_data, _ = self.get(employee_id=employee_id, reference_date=validated_data.get("reference_date"))
        return created_data, response

    def delete(self, employee_id: str,
               salary_id: str,
               reference_date: Optional[datetime] = None) -> Dict:
        """
        Delete a specific salary entry.

        Args:
            employee_id: Employee ID to delete salary data for
            salary_id: Specific salary ID to delete
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
        endpoint = f"clients/{client_id}/{self.individual_endpoint.format(employee_id=employee_id, salary_id=salary_id)}"

        if self.debug:
            print(f"Deleting salary {salary_id} for employee {employee_id}")

        # Make the DELETE request
        return self._make_request(endpoint, method="DELETE", params=params)
