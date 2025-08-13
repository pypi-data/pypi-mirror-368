import pandas as pd
import json
from typing import Optional, Tuple, Dict
from datetime import datetime

from .base import BaseResource
from .schemas import ReasonsForAbsenceSchema
from brynq_sdk_functions import Functions


class ReasonsForAbsence(BaseResource):
    """Resource for interacting with the DATEV Lohn und Gehalt Reasons for Absence API endpoints"""

    def __init__(self, lohn_und_gehalt):
        super().__init__(lohn_und_gehalt)
        self.batch_endpoint = "reasons-for-absence"
        self.individual_endpoint = "reasons-for-absence/{reason_id}"
        self.schema = ReasonsForAbsenceSchema

    def get(self, reason_id: Optional[str] = None,
            reference_date: Optional[datetime] = None) -> Tuple[pd.DataFrame, Dict]:
        """
        Get reasons for absence data.

        Args:
            reason_id: Specific reason ID to retrieve
            reference_date: Date for which to retrieve the data

        Returns:
            DataFrame with reasons for absence data and additional metadata dict
        """
        params = {}
        if reference_date:
            params["reference-date"] = reference_date.strftime("%Y-%m-%d")
        else:
            params["reference-date"] = datetime.now().strftime("%Y-%m-%d")

        # Use client_id directly from the DatevLohnUndGehalt instance
        client_id = self.datev.client_id

        if self.debug:
            if reason_id:
                print(f"Fetching specific reason for absence {reason_id}")
            else:
                print("Fetching all reasons for absence")

        # Construct the appropriate endpoint URL based on parameters
        if reason_id:
            # Get specific reason for absence
            endpoint = f"clients/{client_id}/{self.individual_endpoint.format(reason_id=reason_id)}"
            data = self._make_request(endpoint, params=params)
            # Convert single item to list for consistency
            if isinstance(data, dict):
                data = [data]
        else:
            # Get all reasons for absence
            endpoint = f"clients/{client_id}/{self.batch_endpoint}"
            data = self._make_request(endpoint, params=params)

        # Convert to DataFrame and validate
        df = pd.DataFrame(data)
        valid_data, invalid_data = Functions.validate_data(df, self.schema, debug=self.debug)

        return valid_data, invalid_data
