import pandera as pa
from pandera.typing import Series, DataFrame
from typing import Optional
from pydantic import BaseModel, Field
import pandas as pd
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from enum import Enum


class EmploymentType(str, Enum):
    """Employment type enum from Payroll-3.1.1.yaml"""
    HAUPTARBEITGEBER = "hauptarbeitgeber"
    NEBENARBEITGEBER = "nebenarbeitgeber"


class TaxationSchema(BrynQPanderaDataFrameModel):
    """Schema for employee taxation response"""
    id: Series[str] = pa.Field(alias="employee_id")
    tax_identification_number: Optional[Series[str]] = pa.Field(nullable=True)
    employment_type: Optional[Series[str]] = pa.Field(nullable=True)
    requested_annual_allowance: Optional[Series[float]] = pa.Field(nullable=True)
    is_two_percent_flat_rate_taxation: Optional[Series[bool]] = pa.Field(nullable=True)

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

class TaxationUpdateSchema(BaseModel):
    """Schema for validating taxation update requests"""
    id: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[str] = Field(None, description="The reference date, if not provided, the current date will be used")
    tax_identification_number: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    requested_annual_allowance: Optional[float] = None
    is_two_percent_flat_rate_taxation: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "employee_id": "00010",
                    "tax_identification_number": "12345678995",
                    "employment_type": "hauptarbeitgeber",
                    "is_two_percent_flat_rate_taxation": False
                }
            ]
        }
