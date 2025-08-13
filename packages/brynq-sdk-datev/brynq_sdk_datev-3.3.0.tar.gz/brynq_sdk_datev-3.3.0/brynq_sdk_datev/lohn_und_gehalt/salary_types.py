import pandas as pd
import json
from typing import Optional, Tuple, Dict
from datetime import datetime

from .base import BaseResource
from .schemas import SalaryTypeSchema
from brynq_sdk_functions import Functions


class SalaryTypes(BaseResource):
    """Resource for interacting with the DATEV Lohn und Gehalt Salary Types API endpoints"""

    def __init__(self, lohn_und_gehalt):
        super().__init__(lohn_und_gehalt)
        self.batch_endpoint = "salary-types"
        self.individual_endpoint = "salary-types/{salary_type_id}"
        self.schema = SalaryTypeSchema

    def get(self, salary_type_id: Optional[str] = None,
            reference_date: Optional[datetime] = None) -> Tuple[pd.DataFrame, Dict]:
        """
        Get salary type data.

        Args:
            salary_type_id: Specific salary type ID to retrieve
            reference_date: Date for which to retrieve the data

        Returns:
            DataFrame with salary type data and additional metadata dict
        """
        params = {}
        if reference_date:
            params["reference-date"] = reference_date.strftime("%Y-%m-%d")
        else:
            params["reference-date"] = datetime.now().strftime("%Y-%m-%d")

        # Use client_id directly from the DatevLohnUndGehalt instance
        client_id = self.datev.client_id

        if self.debug:
            if salary_type_id:
                print(f"Fetching specific salary type {salary_type_id}")
            else:
                print("Fetching all salary types")

        # Construct the appropriate endpoint URL based on parameters
        if salary_type_id:
            # Get specific salary type
            endpoint = f"clients/{client_id}/{self.individual_endpoint.format(salary_type_id=salary_type_id)}"
            data = self._make_request(endpoint, params=params)
            # Convert single item to list for consistency
            if isinstance(data, dict):
                data = [data]
        else:
            # Get all salary types
            endpoint = f"clients/{client_id}/{self.batch_endpoint}"
            data = self._make_request(endpoint, params=params)

        # Convert to DataFrame and validate
        df = pd.DataFrame(data)
        valid_data, invalid_data = Functions.validate_data(df, self.schema, debug=self.debug)

        return valid_data, invalid_data
