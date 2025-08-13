from datetime import datetime
import requests
from .schemas.clients import ClientSchema
from brynq_sdk_functions import Functions
import pandas as pd


class Client:
    def __init__(self, datev):
        from . import DatevLohnUndGehalt
        self.datev: DatevLohnUndGehalt = datev
        self.debug = datev.debug

    def get(self, reference_date: datetime) -> tuple[pd.DataFrame, pd.DataFrame]:
        body = {
            "local_requests": [{
                "url": f"{self.datev.local_url}/clients",
                "method": "GET",
                "headers": self.datev.local_headers,
                "params": {
                    "reference-date": reference_date.strftime("%Y-%m-%d")
                }
            }]
        }
        resp = requests.post(self.datev.agent_url, headers=self.datev.headers, json=body, timeout=self.datev.timeout)
        resp.raise_for_status()
        data = resp.json()[0].get("response")
        df = pd.DataFrame(data)
        valid_data, invalid_data = Functions.validate_data(df, ClientSchema, debug=self.debug)

        return valid_data, invalid_data
