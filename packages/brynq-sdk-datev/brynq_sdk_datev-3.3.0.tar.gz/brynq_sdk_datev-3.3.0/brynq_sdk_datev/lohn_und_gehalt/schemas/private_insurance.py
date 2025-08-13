import pandera as pa
from pandera.typing import Series
from typing import Optional
from pydantic import BaseModel, Field
import pandas as pd
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class PrivateInsuranceSchema(BrynQPanderaDataFrameModel):
    """Schema for private insurance response"""
    id: Series[str] = pa.Field(alias="employee_id")
    is_private_health_insured: Optional[Series[bool]] = pa.Field(nullable=True)
    is_private_nursing_insured: Optional[Series[bool]] = pa.Field(nullable=True)
    monthly_premium_for_private_health_insurance: Optional[Series[float]] = pa.Field(nullable=True)
    monthly_premium_for_private_nursing_insurance: Optional[Series[float]] = pa.Field(nullable=True)
    monthly_contribution_to_basic_health_insurance: Optional[Series[float]] = pa.Field(nullable=True)

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

class PrivateInsuranceUpdateSchema(BaseModel):
    """Schema for validating private insurance update requests"""
    id: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[str] = Field(None, description="The reference date, if not provided, the current date will be used")
    is_private_health_insured: Optional[bool] = None
    is_private_nursing_insured: Optional[bool] = None
    monthly_premium_for_private_health_insurance: Optional[float] = None
    monthly_premium_for_private_nursing_insurance: Optional[float] = None
    monthly_contribution_to_basic_health_insurance: Optional[float] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "employee_id": "00010",
                    "is_private_health_insured": True,
                    "is_private_nursing_insured": True,
                    "monthly_premium_for_private_health_insurance": 549.33,
                    "monthly_premium_for_private_nursing_insurance": 149.33,
                    "monthly_contribution_to_basic_health_insurance": 49.33
                }
            ]
        }
