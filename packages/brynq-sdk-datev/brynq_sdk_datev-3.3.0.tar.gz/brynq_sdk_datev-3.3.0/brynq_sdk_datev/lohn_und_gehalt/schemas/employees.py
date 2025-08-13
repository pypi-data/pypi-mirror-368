import pandera as pa
from pandera.typing import Series, DataFrame
from datetime import datetime
from typing import Optional, Dict, Any
import pydantic
from pydantic import BaseModel, Field
from brynq_sdk_functions import BrynQPanderaDataFrameModel


# Response schema for DataFrame validation
class EmployeeSchema(BrynQPanderaDataFrameModel):
    """Schema for employee data response"""
    id: Series[str] = pa.Field(alias="employee_id")
    surname: Series[str] = pa.Field()
    first_name: Series[str] = pa.Field()
    company_personnel_number: Optional[Series[str]] = pa.Field(nullable=True)
    date_of_commencement_of_employment: Series[datetime] = pa.Field()
    first_accounting_month: Optional[Series[datetime]] = pa.Field(nullable=True)
    # Add any additional fields from the API response

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["id"]

# Request validation schemas using pydantic
class EmployeeCreateSchema(BaseModel):
    """Schema for validating employee creation data"""
    id: Optional[str] = None
    reference_date: Optional[datetime] = Field(None, description="The reference date of the employee, if not provided, the current date will be used")
    surname: str
    first_name: str
    company_personnel_number: Optional[str] = None
    date_of_commencement_of_employment: datetime
    first_accounting_month: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "employee_id": "00010",
                    "surname": "Mustermann",
                    "first_name": "Max",
                    "company_personnel_number": "00010",
                    "date_of_commencement_of_employment": "2024-01-01"
                }
            ]
        }

class EmployeeUpdateSchema(BaseModel):
    """Schema for validating employee update data"""
    id: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[datetime] = Field(None, description="The reference date of the employee, if not provided, the current date will be used")
    surname: Optional[str] = None
    first_name: Optional[str] = None
    company_personnel_number: Optional[str] = None
    date_of_commencement_of_employment: Optional[datetime] = None
    first_accounting_month: Optional[datetime] = None
