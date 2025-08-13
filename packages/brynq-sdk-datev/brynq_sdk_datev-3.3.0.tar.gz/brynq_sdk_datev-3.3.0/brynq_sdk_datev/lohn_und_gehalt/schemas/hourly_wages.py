import pandera as pa
from pandera.typing import Series
from typing import Optional
from pydantic import BaseModel, Field
import pandas as pd
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class HourlyWagesSchema(BrynQPanderaDataFrameModel):
    """Schema for hourly wages response"""
    id: Series[str] = pa.Field(alias="hourly_wage_id")
    personnel_number: Series[str] = pa.Field(alias="employee_id")
    amount: Optional[Series[float]] = pa.Field(nullable=True)

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["hourly_wage_id"]
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeeSchema",
                "parent_column": "employee_id",
                "cardinality": "N:1"
            }
        }

class HourlyWagesUpdateSchema(BaseModel):
    """Schema for validating hourly wages update requests"""
    id: str = Field(..., description="The ID of the hourly wage, value between 1 and 5", alias="hourly_wage_id")
    personnel_number: str = Field(..., description="The personnel number of the employee", alias="employee_id")
    reference_date: Optional[datetime] = Field(None, description="The reference date of the hourly wage, if not provided, the current date will be used")
    amount: float

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "hourly_wage_id": "1",
                    "employee_id": "00010",
                    "amount": 40.00
                }
            ]
        }
