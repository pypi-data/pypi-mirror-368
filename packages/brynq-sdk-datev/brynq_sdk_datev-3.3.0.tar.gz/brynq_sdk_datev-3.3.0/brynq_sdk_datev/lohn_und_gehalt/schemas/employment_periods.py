import pandera as pa
from pandera.typing import Series
from typing import Optional
from pydantic import BaseModel, Field
import pandas as pd
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class EmploymentPeriodsSchema(BrynQPanderaDataFrameModel):
    """Schema for employee employment periods response"""
    personnel_number: Series[str] = pa.Field(alias="employee_id")
    id: Optional[Series[str]] = pa.Field(nullable=True, alias="employment_period_id")
    date_of_commencement_of_employment: Optional[Series[datetime]] = pa.Field(nullable=True)
    date_of_termination_of_employment: Optional[Series[datetime]] = pa.Field(nullable=True)
    date_of_death: Optional[Series[datetime]] = pa.Field(nullable=True)

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["employment_period_id"]
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeeSchema",
                "parent_column": "employee_id",
                "cardinality": "N:1"
            }
        }

class EmploymentPeriodsUpdateSchema(BaseModel):
    """Schema for validating employment periods update requests"""
    id: str = Field(..., description="The ID of the employment period", alias="employment_period_id")
    personnel_number: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[datetime] = Field(None, description="The reference date of the employment period, if not provided, the current date will be used")
    date_of_commencement_of_employment: Optional[datetime] = None
    date_of_termination_of_employment: Optional[datetime] = None
    date_of_death: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "employment_period_id": "68946",
                    "employee_id": "00010",
                    "date_of_termination_of_employment": "2025-12-31"
                }
            ]
        }

class EmploymentPeriodsCreateSchema(BaseModel):
    """Schema for validating employment periods creation requests (without ID)"""
    personnel_number: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[datetime] = Field(None, description="The reference date of the employment period, if not provided, the current date will be used")
    date_of_commencement_of_employment: Optional[datetime] = None
    date_of_termination_of_employment: Optional[datetime] = None
    date_of_death: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "employee_id": "00010",
                    "date_of_commencement_of_employment": "2026-01-01",
                    "reference_date": "2025-05-01"
                }
            ]
        }
