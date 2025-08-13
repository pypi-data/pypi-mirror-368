from datetime import datetime
from typing import Tuple, Optional, Dict, Any, List, Union
import pandas as pd
from .base import BaseResource
from .schemas.vocational_trainings import VocationalTrainingsSchema, VocationalTrainingsUpdateSchema, VocationalTrainingsCreateSchema
from brynq_sdk_functions import Functions

class VocationalTrainings(BaseResource):
    """
    VocationalTrainings resource for DATEV Lohn und Gehalt
    Handles vocational training details for employees
    Supports both batch operations and per-employee operations
    Find this in Datev under Mitarbeiter > Schnellerfassung > this is Tätigkeit > Angaben zum asubildungsverhältnis
    """

    def __init__(self, datev):
        super().__init__(datev)

    def get(self, reference_date: Optional[datetime] = None, employee_id: Optional[str] = None, vocational_training_id: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get vocational training data for all employees, a specific employee, or a specific vocational training

        Args:
            reference_date: Optional reference date
            employee_id: Optional employee ID to get vocational trainings for a specific employee
            vocational_training_id: Optional vocational training ID to get a specific vocational training

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
            if vocational_training_id and employee_id:
                print(f"Fetching vocational training data for training {vocational_training_id} of employee {employee_id}")
            elif employee_id:
                print(f"Fetching vocational training data for employee {employee_id}")
            else:
                print("Fetching vocational training data for all employees")

        # Construct the appropriate endpoint URL based on parameters
        if vocational_training_id and employee_id:
            endpoint = f"clients/{client_id}/employees/{employee_id}/vocational-trainings/{vocational_training_id}"
        elif employee_id:
            endpoint = f"clients/{client_id}/employees/{employee_id}/vocational-trainings"
        else:
            endpoint = f"clients/{client_id}/vocational-trainings"

        data = self._make_request(endpoint, params=params)

        # Convert single object to a list for DataFrame if necessary
        if isinstance(data, dict):
            data = [data]

        df = pd.DataFrame(data)
        valid_data, invalid_data = Functions.validate_data(df, VocationalTrainingsSchema, debug=self.debug)

        return valid_data, invalid_data

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create vocational training data for an employee

        Args:
            data: Vocational training data, including employee_id and reference_date

        Returns:
            Created vocational training data
        """
        # Validate and format using our generic method
        validated_data = self._validate_request_data(
            data=data,
            schema_class=VocationalTrainingsCreateSchema
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
            print(f"Creating vocational training data for employee {employee_id}")

        # POST request returns created object
        return self._make_request(f"clients/{client_id}/employees/{employee_id}/vocational-trainings",
                                method="POST",
                                json_data=validated_data,
                                params=params)

    def update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update vocational training data for an employee

        Args:
            data: Updated vocational training data, including vocational_training_id, employee_id, and reference_date

        Returns:
            Updated vocational training data
        """
        # Validate and format using our generic method
        validated_data = self._validate_request_data(
            data=data,
            schema_class=VocationalTrainingsUpdateSchema
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
        vocational_training_id = validated_data.get("id")

        if self.debug:
            print(f"Updating vocational training {vocational_training_id} for employee {employee_id}")

        # PUT request returns 204 No Content on success
        return self._make_request(f"clients/{client_id}/employees/{employee_id}/vocational-trainings/{vocational_training_id}",
                                method="PUT",
                                json_data=validated_data,
                                params=params)

    def delete(self, employee_id: str, vocational_training_id: str, reference_date: Optional[datetime] = None) -> None:
        """
        Delete a vocational training for a specific employee

        Args:
            employee_id: Employee ID for the employee
            vocational_training_id: ID of the vocational training to delete
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

        endpoint = f"clients/{client_id}/employees/{employee_id}/vocational-trainings/{vocational_training_id}"

        if self.debug:
            print(f"Deleting vocational training {vocational_training_id} for employee {employee_id}")

        # DELETE request returns 204 No Content on success
        self._make_request(endpoint, method="DELETE", params=params)
        return None
