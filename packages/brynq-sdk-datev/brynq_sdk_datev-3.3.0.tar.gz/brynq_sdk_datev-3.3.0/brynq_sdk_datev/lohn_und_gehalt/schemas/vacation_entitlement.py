import pandera as pa
from pandera.typing import Series
from typing import Optional
from pydantic import BaseModel, Field
import pandas as pd
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class VacationEntitlementSchema(BrynQPanderaDataFrameModel):
    """Schema for vacation entitlement response"""
    id: Series[str] = pa.Field(alias="employee_id")
    basic_vacation_entitlement: Optional[Series[float]] = pa.Field(nullable=True)
    current_year_vacation_entitlement: Optional[Series[float]] = pa.Field(nullable=True)
    remaining_days_of_vacation_previous_year: Optional[Series[float]] = pa.Field(nullable=True)

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

class VacationEntitlementUpdateSchema(BaseModel):
    """Schema for validating vacation entitlement update requests"""
    id: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[str] = Field(None, description="The reference date, if not provided, the current date will be used")
    basic_vacation_entitlement: Optional[float] = None
    current_year_vacation_entitlement: Optional[float] = None
    remaining_days_of_vacation_previous_year: Optional[float] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "employee_id": "00010",
                    "basic_vacation_entitlement": 28.8,
                    "current_year_vacation_entitlement": 5.3,
                    "remaining_days_of_vacation_previous_year": 4.2
                }
            ]
        }
