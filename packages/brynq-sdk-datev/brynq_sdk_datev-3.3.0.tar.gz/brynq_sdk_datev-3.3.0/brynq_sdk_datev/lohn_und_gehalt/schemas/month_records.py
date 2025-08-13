import pandera as pa
from pandera.typing import Series
from typing import Optional
from pydantic import BaseModel, Field
import pandas as pd
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class MonthRecordsSchema(BrynQPanderaDataFrameModel):
    """Schema for monthly records response"""
    id: Optional[Series[str]] = pa.Field(nullable=True, alias="month_record_id")
    personnel_number: Series[str] = pa.Field(alias="employee_id")
    month_of_emergence: Series[str] = pa.Field()  # Format: YYYY-MM
    salary_type_id: Series[pd.Int64Dtype] = pa.Field(nullable=True)
    cost_center_id: Optional[Series[str]] = pa.Field(nullable=True)
    cost_unit_id: Optional[Series[str]] = pa.Field(nullable=True)
    value: Optional[Series[float]] = pa.Field(nullable=True)
    differing_factor: Optional[Series[float]] = pa.Field(nullable=True)
    differing_pay_change: Optional[Series[float]] = pa.Field(nullable=True)
    origin: Optional[Series[str]] = pa.Field(nullable=True)
    accounting_month: Optional[Series[str]] = pa.Field(nullable=True)  # Format: YYYY-MM

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["month_record_id"]
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeeSchema",
                "parent_column": "employee_id",
                "cardinality": "N:1"
            },
            "salary_type_id": {
                "parent_schema": "SalaryTypeSchema",
                "parent_column": "salary_type_id",
                "cardinality": "N:1"
            },
            "cost_center_id": {
                "parent_schema": "CostCenterSchema",
                "parent_column": "cost_center_id",
                "cardinality": "N:1"
            },
            "cost_unit_id": {
                "parent_schema": "CostUnitSchema",
                "parent_column": "cost_unit_id",
                "cardinality": "N:1"
            }
        }

class MonthRecordsUpdateSchema(BaseModel):
    """Schema for validating month records update requests"""
    id: str = Field(..., description="The ID of the month record", alias="month_record_id")
    personnel_number: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[str] = Field(None, description="The reference date of the month record, if not provided, the current date will be used")
    month_of_emergence: str  # Format: YYYY-MM
    salary_type_id: int
    cost_center_id: Optional[str] = None
    cost_unit_id: Optional[str] = None
    value: Optional[float] = None
    differing_factor: Optional[float] = None
    differing_pay_change: Optional[float] = None



class MonthRecordsCreateSchema(BaseModel):
    """Schema for validating month records creation requests (without ID)"""
    personnel_number: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[str] = Field(None, description="The reference date of the month record, if not provided, the current date will be used")
    month_of_emergence: str  # Format: YYYY-MM
    salary_type_id: int
    cost_center_id: Optional[str] = None
    cost_unit_id: Optional[str] = None
    value: Optional[float] = None
    differing_factor: Optional[float] = None
    differing_pay_change: Optional[float] = None
