import pandera as pa
from pandera.typing import Series, DataFrame
from typing import Optional
from pydantic import BaseModel
import pandas as pd
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class WorkingHoursSchema(BrynQPanderaDataFrameModel):
    """Schema for company working hours response"""
    id: Series[str] = pa.Field(alias="client_id")
    weekly_working_hours: Optional[Series[float]] = pa.Field(nullable=True)
    allocation_of_working_hours_monday: Optional[Series[float]] = pa.Field(nullable=True)
    allocation_of_working_hours_tuesday: Optional[Series[float]] = pa.Field(nullable=True)
    allocation_of_working_hours_wednesday: Optional[Series[float]] = pa.Field(nullable=True)
    allocation_of_working_hours_thursday: Optional[Series[float]] = pa.Field(nullable=True)
    allocation_of_working_hours_friday: Optional[Series[float]] = pa.Field(nullable=True)
    allocation_of_working_hours_saturday: Optional[Series[float]] = pa.Field(nullable=True)
    allocation_of_working_hours_sunday: Optional[Series[float]] = pa.Field(nullable=True)
    daily_working_hours: Optional[Series[float]] = pa.Field(nullable=True)
    valid_from: Optional[Series[datetime]] = pa.Field(nullable=True)
    valid_to: Optional[Series[datetime]] = pa.Field(nullable=True)

    class Config:
        coerce = True

    class _Annotation:
        foreign_keys = {
            "client_id": {
                "parent_schema": "ClientSchema",
                "parent_column": "client_id",
                "cardinality": "N:1"
            }
        }
