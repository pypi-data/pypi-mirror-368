import pandera as pa
import pandas as pd
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from pandera.typing import Series


class CostCentersSchema(BrynQPanderaDataFrameModel):
    """Pandera schema for validating cost centers data from the DATEV API"""

    id: Series[str] = pa.Field(nullable=False, alias="cost_center_id")
    name: Series[str] = pa.Field(nullable=False)

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["cost_center_id"]


class CostCentersUpdateSchema(BaseModel):
    """Request model for cost centers data"""

    id: str = Field(..., description="The ID of the cost center", alias="cost_center_id")
    reference_date: Optional[datetime] = Field(None, description="The reference date of the cost center, if not provided, the current date will be used")
    name: str

    class Config:
        schema_extra = {
            "examples": [
                {
                    "cost_center_id": "1",
                    "name": "Einkauff"
                }
            ]
        }
