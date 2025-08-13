import pandera as pa
import pandas as pd
from pandera.typing import Series
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class AccountableEmployeesSchema(BrynQPanderaDataFrameModel):
    """Pandera schema for validating accountable employees data from the DATEV API"""

    id: Series[str] = pa.Field(nullable=False, alias="employee_id")
    surname: Series[str] = pa.Field(nullable=False)
    first_name: Series[str] = pa.Field(nullable=True)
    company_personnel_number: Series[str] = pa.Field(nullable=True)
    date_of_commencement_of_employment: Series[str] = pa.Field(nullable=True)
    date_of_termination_of_employment: Series[str] = pa.Field(nullable=True)

    class Config:
        coerce = True

    class _Annotation:
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeeSchema",
                "parent_column": "employee_id",
                "cardinality": "1:1"
            }
        }


class AccountableEmployeesRequest(BaseModel):
    """Request model for accountable employees data"""

    surname: str
    first_name: Optional[str] = None
    company_personnel_number: Optional[str] = None
    date_of_commencement_of_employment: Optional[str] = None
    date_of_termination_of_employment: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "surname": "Mustermann",
                "first_name": "Max",
                "company_personnel_number": "1",
                "date_of_commencement_of_employment": "2023-01-01"
            }
        }
