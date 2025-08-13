import pandas as pd
import json
from typing import Optional, Tuple, Dict
from datetime import datetime

from .base import BaseResource
from .schemas import DepartmentsSchema
from brynq_sdk_functions import Functions


class Departments(BaseResource):
    """Resource for interacting with the DATEV Lohn und Gehalt Departments API endpoints"""

    def __init__(self, lohn_und_gehalt):
        super().__init__(lohn_und_gehalt)
        self.batch_endpoint = "departments"
        self.individual_endpoint = "departments/{department_id}"
        self.schema = DepartmentsSchema

    def get(self, department_id: Optional[str] = None,
            reference_date: Optional[datetime] = None) -> Tuple[pd.DataFrame, Dict]:
        """
        Get departments data.

        Args:
            department_id: Specific department ID to retrieve
            reference_date: Date for which to retrieve the data

        Returns:
            DataFrame with departments data and additional metadata dict
        """
        params = {}
        if reference_date:
            params["reference-date"] = reference_date.strftime("%Y-%m-%d")
        else:
            params["reference-date"] = datetime.now().strftime("%Y-%m-%d")

        # Use client_id directly from the DatevLohnUndGehalt instance
        client_id = self.datev.client_id

        if self.debug:
            if department_id:
                print(f"Fetching specific department {department_id}")
            else:
                print("Fetching all departments")

        # Construct the appropriate endpoint URL based on parameters
        if department_id:
            # Get specific department
            endpoint = f"clients/{client_id}/{self.individual_endpoint.format(department_id=department_id)}"
            data = self._make_request(endpoint, params=params)
            # Convert single item to list for consistency
            if isinstance(data, dict):
                data = [data]
        else:
            # Get all departments
            endpoint = f"clients/{client_id}/{self.batch_endpoint}"
            data = self._make_request(endpoint, params=params)

        # Convert to DataFrame and validate
        df = pd.DataFrame(data)
        valid_data, invalid_data = Functions.validate_data(df, self.schema, debug=self.debug)

        return valid_data, invalid_data
