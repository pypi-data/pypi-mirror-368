from datetime import datetime
from typing import Tuple, Optional, Dict, Any
import pandas as pd
from .base import BaseResource
from .schemas.working_hours import WorkingHoursSchema
from brynq_sdk_functions import Functions

class WorkingHours(BaseResource):
    """
    WorkingHours resource for DATEV Lohn und Gehalt
    Handles working hours details for employees
    Note: Only supports batch operations, no per-employee endpoint
    """

    def __init__(self, datev):
        super().__init__(datev)

    def get(self, reference_date: Optional[datetime] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get working hours data for all employees

        Args:
            reference_date: Optional reference date

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
            print("Fetching working hours data for all employees")
        endpoint = f"clients/{client_id}/working-hours"

        data = self._make_request(endpoint, params=params)

        # Convert single object to a list for DataFrame if necessary
        if isinstance(data, dict):
            data = [data]

        df = pd.DataFrame(data)
        valid_data, invalid_data = Functions.validate_data(df, WorkingHoursSchema, debug=self.debug)

        return valid_data, invalid_data
