import pandera as pa
import pandas as pd
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from pandera.typing import Series


class ReasonsForAbsenceSchema(BrynQPanderaDataFrameModel):
    """Pandera schema for validating reasons for absence data from the DATEV API"""

    id: Series[str] = pa.Field(nullable=False, alias="reason_for_absence_id")
    name: Series[str] = pa.Field(nullable=False)

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["reason_for_absence_id"]

class ReasonsForAbsenceRequest(BaseModel):
    """Request model for reasons for absence data"""

    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "Sick Leave"
            }
        }
