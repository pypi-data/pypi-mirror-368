import pandera as pa
import pandas as pd
from pydantic import BaseModel, Field
from pandera.typing import Series
from typing import Optional
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class CostUnitsSchema(BrynQPanderaDataFrameModel):
    """Pandera schema for validating cost units data from the DATEV API"""

    id:Series[str] = pa.Field(nullable=False)
    name: Series[str] = pa.Field(nullable=False)

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["id"]


class CostUnitsUpdateSchema(BaseModel):
    """Request model for cost units data"""

    id: str = Field(..., description="The ID of the cost unit", alias="cost_unit_id")
    reference_date: Optional[datetime] = Field(None, description="The reference date of the cost unit, if not provided, the current date will be used")
    name: str

    class Config:
        schema_extra = {
            "examples": [
                {
                    "cost_unit_id": "1",
                    "name": "XT 14"
                }
            ]
        }
