import pandera as pa
from pandera.typing import Series
from typing import Optional
from pydantic import BaseModel, Field
import pandas as pd
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class IndividualDataSchema(BrynQPanderaDataFrameModel):
    """Schema for individual data response"""
    id: Series[str] = pa.Field(alias="employee_id")
    long_field_name: Optional[Series[str]] = pa.Field(nullable=True)
    short_field_name: Optional[Series[str]] = pa.Field(nullable=True)
    date: Optional[Series[datetime]] = pa.Field(nullable=True)
    amount: Optional[Series[float]] = pa.Field(nullable=True)
    long_field_name2: Optional[Series[str]] = pa.Field(nullable=True)
    short_field_name2: Optional[Series[str]] = pa.Field(nullable=True)
    date2: Optional[Series[datetime]] = pa.Field(nullable=True)
    amount2: Optional[Series[float]] = pa.Field(nullable=True)
    long_field_name3: Optional[Series[str]] = pa.Field(nullable=True)
    short_field_name3: Optional[Series[str]] = pa.Field(nullable=True)
    date3: Optional[Series[datetime]] = pa.Field(nullable=True)
    amount3: Optional[Series[float]] = pa.Field(nullable=True)
    long_field_name4: Optional[Series[str]] = pa.Field(nullable=True)
    short_field_name4: Optional[Series[str]] = pa.Field(nullable=True)
    date4: Optional[Series[datetime]] = pa.Field(nullable=True)
    amount4: Optional[Series[float]] = pa.Field(nullable=True)
    long_field_name5: Optional[Series[str]] = pa.Field(nullable=True)
    short_field_name5: Optional[Series[str]] = pa.Field(nullable=True)
    date5: Optional[Series[datetime]] = pa.Field(nullable=True)
    amount5: Optional[Series[float]] = pa.Field(nullable=True)
    long_field_name6: Optional[Series[str]] = pa.Field(nullable=True)
    short_field_name6: Optional[Series[str]] = pa.Field(nullable=True)
    date6: Optional[Series[datetime]] = pa.Field(nullable=True)
    amount6: Optional[Series[float]] = pa.Field(nullable=True)
    long_field_name7: Optional[Series[str]] = pa.Field(nullable=True)
    short_field_name7: Optional[Series[str]] = pa.Field(nullable=True)
    date7: Optional[Series[datetime]] = pa.Field(nullable=True)
    amount7: Optional[Series[float]] = pa.Field(nullable=True)
    long_field_name8: Optional[Series[str]] = pa.Field(nullable=True)
    short_field_name8: Optional[Series[str]] = pa.Field(nullable=True)
    date8: Optional[Series[datetime]] = pa.Field(nullable=True)
    amount8: Optional[Series[float]] = pa.Field(nullable=True)

    class Config:
        coerce = True

    class _Annotation:
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeeSchema",
                "parent_column": "employee_id",
                "cardinality": "N:1"
            }
        }
