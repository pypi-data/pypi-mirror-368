import pandera as pa
from pandera.typing import Series
from typing import Optional
from pydantic import BaseModel, Field
import pandas as pd
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from enum import Enum


class Reduction(str, Enum):
    """Reduction enum for gross payments"""
    TEILMONAT_KUERZEN_AUSFALLMONAT_KUERZEN = "teilmonat_kuerzen_ausfallmonat_kuerzen"
    TEILMONAT_NICHT_KUERZEN_AUSFALLMONAT_NICHT_KUERZEN = "teilmonat_nicht_kuerzen_ausfallmonat_nicht_kuerzen"
    TEILMONAT_NICHT_KUERZEN_AUSFALLMONAT_KUERZEN = "teilmonat_nicht_kuerzen_ausfallmonat_kuerzen"


class PaymentInterval(str, Enum):
    """Payment interval enum for gross payments"""
    MONTHLY = "monthly"
    SEMIANNUALLY = "semiannually"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


class GrossPaymentsSchema(BrynQPanderaDataFrameModel):
    """Schema for gross payments response"""
    id: Optional[Series[str]] = pa.Field(nullable=True)
    personnel_number: Series[str] = pa.Field(alias="employee_id")
    amount: Optional[Series[float]] = pa.Field(nullable=True)
    salary_type_id: Optional[Series[pd.Int64Dtype]] = pa.Field(nullable=True)
    reduction: Optional[Series[str]] = pa.Field(nullable=True)
    cost_center_allocation_id: Optional[Series[str]] = pa.Field(nullable=True)
    cost_unit_allocation_id: Optional[Series[str]] = pa.Field(nullable=True)
    payment_interval: Optional[Series[str]] = pa.Field(nullable=True)
    reference_date: Optional[Series[str]] = pa.Field(nullable=True)  # Format: YYYY-MM

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["id"]
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeeSchema",
                "parent_column": "employee_id",
                "cardinality": "N:1"
            },
            "salary_type_id": {
                "parent_schema": "SalaryTypeSchema",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "cost_center_allocation_id": {
                "parent_schema": "CostCenterSchema",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "cost_unit_allocation_id": {
                "parent_schema": "CostUnitSchema",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }


class GrossPaymentsUpdateSchema(BaseModel):
    """Schema for validating gross payments update requests"""
    id: str = Field(..., description="The ID of the gross payment", alias="gross_payment_id")
    personnel_number: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[str] = Field(None, description="The reference date of the gross payment (format: YYYY-MM), if not provided, the current date will be used")
    amount: float
    salary_type_id: int
    reduction: Optional[Reduction] = None
    cost_center_allocation_id: Optional[str] = None
    cost_unit_allocation_id: Optional[str] = None
    payment_interval: Optional[PaymentInterval] = None


class GrossPaymentsCreateSchema(BaseModel):
    """Schema for validating gross payments creation requests (without ID)"""
    personnel_number: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[str] = Field(None, description="The reference date of the gross payment (format: YYYY-MM), if not provided, the current date will be used")
    amount: float
    salary_type_id: int
    reduction: Optional[Reduction] = None
    cost_center_allocation_id: Optional[str] = None
    cost_unit_allocation_id: Optional[str] = None
    payment_interval: Optional[PaymentInterval] = None
