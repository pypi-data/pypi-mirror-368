from datetime import datetime
from typing import Tuple, Optional, Dict, Any, List, Union
import pandas as pd
from .base import BaseResource
from .schemas.month_records import MonthRecordsSchema, MonthRecordsUpdateSchema, MonthRecordsCreateSchema
from brynq_sdk_functions import Functions

class MonthRecords(BaseResource):
    """
    MonthRecords resource for DATEV Lohn und Gehalt
    Handles monthly record details for employees
    Supports both batch operations and per-employee operations
    """

    def __init__(self, datev):
        super().__init__(datev)

    def get(self, reference_date: Optional[datetime] = None, employee_id: Optional[str] = None, month_record_id: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get month records data for all employees, a specific employee, or a specific month record

        Args:
            reference_date: Optional reference date (affects the allocated month)
            employee_id: Optional employee ID to get month records for a specific employee
            month_record_id: Optional month record ID to get a specific month record

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
            if month_record_id:
                print(f"Fetching month record data for record {month_record_id}")
            elif employee_id:
                print(f"Fetching month records data for employee {employee_id}")
            else:
                print("Fetching month records data for all employees")

        # Construct the appropriate endpoint URL based on parameters
        if month_record_id and employee_id:
            endpoint = f"clients/{client_id}/employees/{employee_id}/month-records/{month_record_id}"
        elif month_record_id:
            endpoint = f"clients/{client_id}/month-records/{month_record_id}"
        elif employee_id:
            endpoint = f"clients/{client_id}/employees/{employee_id}/month-records"
        else:
            endpoint = f"clients/{client_id}/month-records"

        data = self._make_request(endpoint, params=params)

        # Convert single object to a list for DataFrame if necessary
        if isinstance(data, dict):
            data = [data]

        df = pd.DataFrame(data)
        valid_data, invalid_data = Functions.validate_data(df, MonthRecordsSchema, debug=self.debug)

        return valid_data, invalid_data

    def update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update month records data

        Args:
            data: Updated month records data, including employee_id, month_record_id, and reference_date

        Returns:
            Updated month records data
        """
        # Validate and format using our generic method
        validated_data = self._validate_request_data(
            data=data,
            schema_class=MonthRecordsUpdateSchema
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
        month_record_id = validated_data.get("id")

        if self.debug:
            print(f"Updating month record {month_record_id} for employee {employee_id}")

        # Update a specific month record for a specific employee
        endpoint = f"clients/{client_id}/employees/{employee_id}/month-records/{month_record_id}"

        # PUT request returns 204 No Content on success
        return self._make_request(endpoint,
                              method="PUT",
                              json_data=validated_data,
                              params=params)

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new month record

        Args:
            data: Month record data to create, including employee_id and reference_date

        Returns:
            Created month record data
        """
        # Validate and format using our generic method
        validated_data = self._validate_request_data(
            data=data,
            schema_class=MonthRecordsCreateSchema
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
            print(f"Creating month record for employee {employee_id}")

        # Create a month record for a specific employee
        endpoint = f"clients/{client_id}/employees/{employee_id}/month-records"

        # POST request returns 201 Created on success
        return self._make_request(endpoint,
                              method="POST",
                              json_data=validated_data,
                              params=params)

    def delete(self, month_record_id: str, reference_date: Optional[datetime] = None, employee_id: Optional[str] = None) -> None:
        """
        Delete a month record

        Args:
            month_record_id: ID of the month record to delete
            reference_date: Optional reference date
            employee_id: Optional employee ID if deleting for a specific employee

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

        if employee_id:
            endpoint = f"clients/{client_id}/employees/{employee_id}/month-records/{month_record_id}"
            if self.debug:
                print(f"Deleting month record {month_record_id} for employee {employee_id}")
        else:
            endpoint = f"clients/{client_id}/month-records/{month_record_id}"
            if self.debug:
                print(f"Deleting month record {month_record_id}")

        # DELETE request returns 204 No Content on success
        self._make_request(endpoint, method="DELETE", params=params)
        return None
