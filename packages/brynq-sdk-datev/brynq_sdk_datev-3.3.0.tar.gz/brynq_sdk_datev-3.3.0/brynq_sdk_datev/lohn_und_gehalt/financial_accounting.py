import pandas as pd
import json
from typing import Optional, Tuple, Dict
from datetime import datetime

from .base import BaseResource
from .schemas import FinancialAccountingSchema
from brynq_sdk_functions import Functions


class FinancialAccounting(BaseResource):
    """Resource for interacting with the DATEV Lohn und Gehalt Financial Accounting API endpoints"""

    def __init__(self, lohn_und_gehalt):
        super().__init__(lohn_und_gehalt)
        self.endpoint = "financial-accounting"
        self.schema = FinancialAccountingSchema

    def get(self, reference_date: Optional[datetime] = None) -> Tuple[pd.DataFrame, Dict]:
        """
        Get financial accounting data.

        Args:
            reference_date: Date for which to retrieve the data

        Returns:
            DataFrame with financial accounting data and additional metadata dict
        """
        params = {}
        if reference_date:
            params["reference-date"] = reference_date.strftime("%Y-%m-%d")
        else:
            params["reference-date"] = datetime.now().strftime("%Y-%m-%d")

        # Use client_id directly from the DatevLohnUndGehalt instance
        client_id = self.datev.client_id

        if self.debug:
            print("Fetching financial accounting data")

        # Construct the endpoint
        endpoint = f"clients/{client_id}/{self.endpoint}"
        data = self._make_request(endpoint, params=params)

        # Ensure data is in a list format for DataFrame creation
        if isinstance(data, dict):
            data = [data]

        # Convert to DataFrame and validate
        df = pd.DataFrame(data)
        valid_data, invalid_data = Functions.validate_data(df, self.schema, debug=self.debug)

        return valid_data, invalid_data
