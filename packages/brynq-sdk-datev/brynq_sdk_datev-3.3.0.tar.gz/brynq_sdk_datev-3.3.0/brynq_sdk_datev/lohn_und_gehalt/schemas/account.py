from datetime import datetime
import pandera as pa
from pandera.typing import Series, DataFrame
from typing import Optional
from pydantic import BaseModel, Field
import pandas as pd
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class AccountSchema(BrynQPanderaDataFrameModel):
    """Schema for employee bank account response"""
    id: Series[str] = pa.Field(alias="employee_id", description="The ID of the employee")
    iban: Optional[Series[str]] = pa.Field(nullable=True)
    bic: Optional[Series[str]] = pa.Field(nullable=True)
    differing_account_holder: Optional[Series[str]] = pa.Field(nullable=True)

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



class AccountUpdateSchema(BaseModel):
    """Schema for validating account update requests"""
    id: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[datetime] = Field(None, description="The reference date of the account, if not provided, the current date will be used")
    iban: Optional[str] = None
    bic: Optional[str] = None
    differing_account_holder: Optional[str] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "employee_id": "00010",
                    "iban": "DE02501108000000010400",
                    "bic": "CHASDEFXXXX",
                    "differing_account_holder": "Max Mustermann"
                }
            ]
        }
