import pandera as pa
import pandas as pd
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from pandera.typing import Series


class DepartmentsSchema(BrynQPanderaDataFrameModel):
    """Pandera schema for validating departments data from the DATEV API"""

    id: Series[str] = pa.Field(nullable=False, alias="department_id")
    name: Series[str] = pa.Field(nullable=False)

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["department_id"]


class DepartmentsRequest(BaseModel):
    """Request model for departments data"""

    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "Finance Department"
            }
        }
