import pandera as pa
from pandera.typing import Series, DataFrame
from typing import Optional
from pydantic import BaseModel, Field
import pandas as pd
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class DisabilitySchema(BrynQPanderaDataFrameModel):
    """Schema for employee disability response"""
    id: Series[str] = pa.Field(alias="employee_id")
    valid_from: Optional[Series[datetime]] = pa.Field(nullable=True)
    valid_to: Optional[Series[datetime]] = pa.Field(nullable=True)
    degree_of_disability: Optional[Series[float]] = pa.Field(nullable=True)
    issuing_authority: Optional[Series[str]] = pa.Field(nullable=True)
    disability_group: Optional[Series[str]] = pa.Field(nullable=True)

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

class DisabilityUpdateSchema(BaseModel):
    """Schema for validating disability update requests"""
    id: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[datetime] = Field(None, description="The reference date of the disability, if not provided, the current date will be used")
    valid_from: Optional[datetime] = Field(None, description="The start date of the disability, has to match reference-date (otherwise Datev will throw an error)")
    valid_to: Optional[datetime] = None
    degree_of_disability: Optional[float] = None
    issuing_authority: Optional[str] = None
    disability_group: Optional[str] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "employee_id": "00010",
                    "valid_from": "2025-04-17",
                    "valid_to": "2025-12-02",
                    "degree_of_disability": 0.5,
                    "issuing_authority": "integrationsamt",
                    "disability_group": "schwerbehinderter_1_anrechnung"
                }
            ]
        }
