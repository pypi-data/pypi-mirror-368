from datetime import datetime
from typing import Tuple, Optional, Dict, Any
import pandas as pd
from .base import BaseResource
from .schemas.individual_data import IndividualDataSchema
from brynq_sdk_functions import Functions

class IndividualData(BaseResource):
    """
    IndividualData resource for DATEV Lohn und Gehalt
    Handles individual data details for employees
    Supports both batch operations and per-employee operations
    """

    def __init__(self, datev):
        super().__init__(datev)

    def get(self, reference_date: Optional[datetime] = None, employee_id: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get individual data for all employees or a specific employee

        Args:
            reference_date: Optional reference date
            employee_id: Optional employee ID to get individual data for a specific employee

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
                print(f"Fetching individual data for employee {employee_id}")
            else:
                print("Fetching individual data for all employees")

        # Construct the appropriate endpoint URL based on parameters
        if employee_id:
            endpoint = f"clients/{client_id}/employees/{employee_id}/individual-data"
        else:
            endpoint = f"clients/{client_id}/individual-data"

        data = self._make_request(endpoint, params=params)

        # Convert single object to a list for DataFrame if necessary
        if isinstance(data, dict):
            data = [data]

        df = pd.DataFrame(data)
        valid_data, invalid_data = Functions.validate_data(df, IndividualDataSchema, debug=self.debug)

        return valid_data, invalid_data
