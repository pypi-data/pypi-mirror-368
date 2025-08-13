import pandas as pd
from typing import Optional, Tuple, Dict
from datetime import datetime

from .base import BaseResource
from .schemas import AccountableEmployeesSchema
from brynq_sdk_functions import Functions


class AccountableEmployees(BaseResource):
    """Resource for interacting with the DATEV Lohn und Gehalt Accountable Employees API endpoints"""

    def __init__(self, lohn_und_gehalt):
        super().__init__(lohn_und_gehalt)
        self.batch_endpoint = "accountable-employees"
        self.individual_endpoint = "accountable-employees/{accountable_employee_id}"
        self.schema = AccountableEmployeesSchema

    def get(self, accountable_employee_id: Optional[str] = None,
            reference_date: Optional[datetime] = None) -> Tuple[pd.DataFrame, Dict]:
        """
        Get accountable employees data.

        Args:
            accountable_employee_id: Specific accountable employee ID to retrieve
            reference_date: Date for which to retrieve the data

        Returns:
            DataFrame with accountable employees data and additional metadata dict
        """
        params = {}
        if reference_date:
            params["reference-date"] = reference_date.strftime("%Y-%m-%d")
        else:
            params["reference-date"] = datetime.now().strftime("%Y-%m-%d")

        # Use client_id directly from the DatevLohnUndGehalt instance
        client_id = self.datev.client_id

        if self.debug:
            if accountable_employee_id:
                print(f"Fetching specific accountable employee {accountable_employee_id}")
            else:
                print("Fetching all accountable employees")

        # Construct the appropriate endpoint URL based on parameters
        if accountable_employee_id:
            # Get specific accountable employee
            endpoint = f"clients/{client_id}/{self.individual_endpoint.format(accountable_employee_id=accountable_employee_id)}"
            data = self._make_request(endpoint, params=params)
            # Convert single item to list for consistency
            if isinstance(data, dict):
                data = [data]
        else:
            # Get all accountable employees
            endpoint = f"clients/{client_id}/{self.batch_endpoint}"
            data = self._make_request(endpoint, params=params)

        # Convert to DataFrame and validate
        df = pd.DataFrame(data)
        valid_data, invalid_data = Functions.validate_data(df, self.schema, debug=self.debug)

        return valid_data, invalid_data
