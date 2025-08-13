import pandera as pa
from pandera.typing import Series
from typing import Optional
from pydantic import BaseModel, Field
import pandas as pd
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class VocationalTrainingsSchema(BrynQPanderaDataFrameModel):
    """Schema for vocational trainings response"""
    id: Optional[Series[str]] = pa.Field(nullable=True)
    personnel_number: Series[str] = pa.Field(alias="employee_id")
    start: Optional[Series[datetime]] = pa.Field(nullable=True)
    expected_end: Optional[Series[datetime]] = pa.Field(nullable=True)
    actual_end: Optional[Series[datetime]] = pa.Field(nullable=True)

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["id"]
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeeSchema",
                "parent_column": "employee_id",
                "cardinality": "N:1"
            }
        }

class VocationalTrainingsUpdateSchema(BaseModel):
    """Schema for validating vocational trainings update requests"""
    id: str = Field(..., description="The ID of the vocational training", alias="vocational_training_id")
    personnel_number: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[str] = Field(None, description="The reference date, if not provided, the current date will be used")
    start: Optional[datetime] = None
    expected_end: Optional[datetime] = None
    actual_end: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "vocational_training_id": "69800",
                    "employee_id": "00010",
                    "start": "2024-03-01",
                    "expected_end": "2024-08-31",
                    "actual_end": "2024-06-25"
                }
            ]
        }


class VocationalTrainingsCreateSchema(BaseModel):
    """Schema for validating vocational trainings creation requests (without ID)"""
    personnel_number: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[str] = Field(None, description="The reference date, if not provided, the current date will be used")
    start: Optional[datetime] = None
    expected_end: Optional[datetime] = None
    actual_end: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "employee_id": "00010",
                    "start": "2024-01-01",
                    "expected_end": "2024-08-31",
                    "actual_end": "2024-06-25"
                }
            ]
        }
