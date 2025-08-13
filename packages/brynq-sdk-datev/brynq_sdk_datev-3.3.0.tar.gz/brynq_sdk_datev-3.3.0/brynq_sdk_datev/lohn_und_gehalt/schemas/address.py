import pandera as pa
from pandera.typing import Series, DataFrame
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class AddressSchema(BrynQPanderaDataFrameModel):
    """Schema for employee address response"""
    id: Series[str] = pa.Field(alias="employee_id")
    street: Series[str] = pa.Field(nullable=True)
    house_number: Series[str] = pa.Field(nullable=True)
    city: Series[str] = pa.Field(nullable=True)
    postal_code: Series[str] = pa.Field(nullable=True)
    country: Series[str] = pa.Field(nullable=True)
    address_affix: Series[str] = pa.Field(nullable=True)

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


class AddressUpdateSchema(BaseModel):
    """Schema for validating address update requests"""
    id: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[datetime] = Field(None, description="The reference date of the address, if not provided, the current date will be used")
    street: Optional[str] = None
    house_number: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    address_affix: Optional[str] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "employee_id": "00010",
                    "street": "Fürther Str.",
                    "house_number": "5a",
                    "city": "Nürnberg",
                    "postal_code": "90329",
                    "country": "D",
                    "address_affix": "2. OG"
                }
            ]
        }
