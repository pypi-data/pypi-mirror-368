from datetime import datetime
from typing import Tuple, Optional, Dict, Any, List, Union
import pandas as pd
from .base import BaseResource
from .schemas.gross_payments import GrossPaymentsSchema, GrossPaymentsUpdateSchema, GrossPaymentsCreateSchema
from brynq_sdk_functions import Functions

class GrossPayments(BaseResource):
    """
    GrossPayments resource for DATEV Lohn und Gehalt
    Handles gross payment details for employees
    Supports both batch operations and per-employee operations
    """

    def __init__(self, datev):
        super().__init__(datev)

    def get(self, reference_date: Optional[datetime] = None, employee_id: Optional[str] = None, gross_payment_id: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get gross payments data for all employees, a specific employee, or a specific gross payment

        Args:
            reference_date: Optional reference date
            employee_id: Optional employee ID to get gross payments for a specific employee
            gross_payment_id: Optional gross payment ID to get a specific gross payment

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
            if gross_payment_id:
                print(f"Fetching gross payment data for payment {gross_payment_id}")
            elif employee_id:
                print(f"Fetching gross payments data for employee {employee_id}")
            else:
                print("Fetching gross payments data for all employees")

        # Construct the appropriate endpoint URL based on parameters
        if gross_payment_id and employee_id:
            endpoint = f"clients/{client_id}/employees/{employee_id}/gross-payments/{gross_payment_id}"
        elif employee_id:
            endpoint = f"clients/{client_id}/employees/{employee_id}/gross-payments"
        else:
            endpoint = f"clients/{client_id}/gross-payments"

        data = self._make_request(endpoint, params=params)

        # Convert single object to a list for DataFrame if necessary
        if isinstance(data, dict):
            data = [data]

        df = pd.DataFrame(data)
        valid_data, invalid_data = Functions.validate_data(df, GrossPaymentsSchema, debug=self.debug)

        return valid_data, invalid_data

    def update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update gross payments data

        Args:
            data: Updated gross payments data, including employee_id, gross_payment_id, and reference_date

        Returns:
            Updated gross payments data
        """
        # Validate and format using our generic method
        validated_data = self._validate_request_data(
            data=data,
            schema_class=GrossPaymentsUpdateSchema
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
        gross_payment_id = validated_data.get("id")

        if self.debug:
            print(f"Updating gross payment {gross_payment_id} for employee {employee_id}")

        # Update a specific gross payment for a specific employee
        endpoint = f"clients/{client_id}/employees/{employee_id}/gross-payments/{gross_payment_id}"

        # PUT request returns 204 No Content on success
        return self._make_request(endpoint,
                              method="PUT",
                              json_data=validated_data,
                              params=params)

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new gross payment for a specific employee

        Args:
            data: Gross payment data to create, including employee_id and reference_date

        Returns:
            Created gross payment data
        """
        # Validate and format using our generic method
        validated_data = self._validate_request_data(
            data=data,
            schema_class=GrossPaymentsCreateSchema
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
            print(f"Creating gross payment for employee {employee_id}")

        endpoint = f"clients/{client_id}/employees/{employee_id}/gross-payments"

        # POST request returns 201 Created on success
        return self._make_request(endpoint,
                              method="POST",
                              json_data=validated_data,
                              params=params)
