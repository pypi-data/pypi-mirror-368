import pandera as pa
import pandas as pd
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class SalarySchema(BrynQPanderaDataFrameModel):
    """Pandera schema for validating salary data from the DATEV API"""

    id: Series[str] = pa.Field(nullable=False, alias="salary_id")
    personnel_number: Series[str] = pa.Field(nullable=False, alias="employee_id")
    date_of_emergence: Series[str] = pa.Field(nullable=False)
    current_gross_payment: Series[float] = pa.Field(nullable=True)
    current_gross_tax: Series[float] = pa.Field(nullable=True)
    current_net_payment: Series[float] = pa.Field(nullable=True)
    current_church_tax: Series[float] = pa.Field(nullable=True)
    current_solidarity_tax: Series[float] = pa.Field(nullable=True)
    current_health_insurance: Series[float] = pa.Field(nullable=True)
    current_nursing_care_insurance: Series[float] = pa.Field(nullable=True)
    current_pension_insurance: Series[float] = pa.Field(nullable=True)
    current_unemployment_insurance: Series[float] = pa.Field(nullable=True)
    current_health_insurance_employer_contribution: Series[float] = pa.Field(nullable=True)
    current_nursing_care_insurance_employer_contribution: Series[float] = pa.Field(nullable=True)
    current_pension_insurance_employer_contribution: Series[float] = pa.Field(nullable=True)
    current_unemployment_insurance_employer_contribution: Series[float] = pa.Field(nullable=True)
    current_accident_insurance_employer_contribution: Series[float] = pa.Field(nullable=True)
    current_flat_rate_tax: Series[float] = pa.Field(nullable=True)
    current_flat_rate_social_security: Series[float] = pa.Field(nullable=True)
    current_flat_rate_church_tax: Series[float] = pa.Field(nullable=True)
    current_insolvency_money_contribution: Series[float] = pa.Field(nullable=True)
    current_levy_for_severely_disabled: Series[float] = pa.Field(nullable=True)
    current_sick_pay_contribution: Series[float] = pa.Field(nullable=True)
    flat_rate_tax_temporary_employed: Series[float] = pa.Field(nullable=True)
    flat_rate_social_security_temporary_employed: Series[float] = pa.Field(nullable=True)
    flat_rate_church_tax_temporary_employed: Series[float] = pa.Field(nullable=True)
    flat_rate_church_tax_agriculture_and_forestry_temporary_employed: Series[float] = pa.Field(nullable=True)
    flat_rate_church_tax_part_time_employed: Series[float] = pa.Field(nullable=True)

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["salary_id"]
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeeSchema",
                "parent_column": "employee_id",
                "cardinality": "N:1"
            }
        }


class SalaryCreateSchema(BaseModel):
    """Request model for salary data"""

    personnel_number: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[str] = Field(None, description="The reference date, if not provided, the current date will be used")
    date_of_emergence: datetime
    current_gross_payment: Optional[float] = None
    current_gross_tax: Optional[float] = None
    current_net_payment: Optional[float] = None
    current_church_tax: Optional[float] = None
    current_solidarity_tax: Optional[float] = None
    current_health_insurance: Optional[float] = None
    current_nursing_care_insurance: Optional[float] = None
    current_pension_insurance: Optional[float] = None
    current_unemployment_insurance: Optional[float] = None
    current_health_insurance_employer_contribution: Optional[float] = None
    current_nursing_care_insurance_employer_contribution: Optional[float] = None
    current_pension_insurance_employer_contribution: Optional[float] = None
    current_unemployment_insurance_employer_contribution: Optional[float] = None
    current_accident_insurance_employer_contribution: Optional[float] = None
    current_flat_rate_tax: Optional[float] = None
    current_flat_rate_social_security: Optional[float] = None
    current_flat_rate_church_tax: Optional[float] = None
    current_insolvency_money_contribution: Optional[float] = None
    current_levy_for_severely_disabled: Optional[float] = None
    current_sick_pay_contribution: Optional[float] = None
    flat_rate_tax_temporary_employed: Optional[float] = None
    flat_rate_social_security_temporary_employed: Optional[float] = None
    flat_rate_church_tax_temporary_employed: Optional[float] = None
    flat_rate_church_tax_agriculture_and_forestry_temporary_employed: Optional[float] = None
    flat_rate_church_tax_part_time_employed: Optional[float] = None

    class Config:
        schema_extra = {
            "example": {
                "employee_id": "00001",
                "date_of_emergence": "2023-01-30",
                "current_gross_payment": 3000.00,
                "current_net_payment": 2100.00
            }
        }


class SalaryTypeSchema(BrynQPanderaDataFrameModel):
    """Pandera schema for validating salary type data from the DATEV API"""

    id: Series[int] = pa.Field(nullable=False, alias="salary_type_id")
    name: Series[str] = pa.Field(nullable=False)
    core: Series[str] = pa.Field(nullable=True)

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["salary_type_id"]


class SalaryTypeRequest(BaseModel):
    """Request model for salary type data"""

    name: str
    core: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Stundenlohn",
                "core": "LFS01"
            }
        }
