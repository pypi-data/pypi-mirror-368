import pandera as pa
from pandera.typing import Series, DataFrame
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from enum import Enum


class MaritalStatus(str, Enum):
    """Marital status enum from Payroll-3.1.1.yaml"""
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"
    PERMANENTLY_SEPERATED = "permanently_seperated"
    CIVIL_UNION = "civil_union"
    ABROGATED_CIVIL_UNION = "abrogated_civil_union"


class Sex(str, Enum):
    """Sex enum from Payroll-3.1.1.yaml"""
    FEMALE = "female"
    MALE = "male"
    NON_BINARY = "non_binary"
    INDETERMINATE = "indeterminate"


class PersonalDataSchema(BrynQPanderaDataFrameModel):
    """Schema for employee personal data response"""
    id: Series[str] = pa.Field(alias="employee_id")
    first_name: Series[str] = pa.Field()
    surname: Series[str] = pa.Field()
    academic_title: Optional[Series[str]] = pa.Field(nullable=True)
    name_affix: Optional[Series[str]] = pa.Field(nullable=True)
    name_prefix: Optional[Series[str]] = pa.Field(nullable=True)
    birth_name: Optional[Series[str]] = pa.Field(nullable=True)
    birth_name_affix: Optional[Series[str]] = pa.Field(nullable=True)
    birth_name_prefix: Optional[Series[str]] = pa.Field(nullable=True)
    date_of_birth: Series[datetime] = pa.Field()
    place_of_birth: Optional[Series[str]] = pa.Field(nullable=True)
    country_of_birth: Optional[Series[str]] = pa.Field(nullable=True)
    nationality: Optional[Series[str]] = pa.Field(nullable=True)
    marital_status: Optional[Series[str]] = pa.Field(nullable=True)
    sex: Optional[Series[str]] = pa.Field(nullable=True)
    social_security_number: Optional[Series[str]] = pa.Field(nullable=True)
    initial_day_of_entrance: Optional[Series[datetime]] = pa.Field(nullable=True)

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

class PersonalDataUpdateSchema(BaseModel):
    """Schema for validating personal data update requests"""
    id: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[str] = Field(None, description="The reference date of the personal data, if not provided, the current date will be used")
    first_name: Optional[str] = None
    surname: Optional[str] = None
    academic_title: Optional[str] = None
    name_affix: Optional[str] = None
    name_prefix: Optional[str] = None
    birth_name: Optional[str] = None
    birth_name_affix: Optional[str] = None
    birth_name_prefix: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    place_of_birth: Optional[str] = None
    country_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    marital_status: Optional[MaritalStatus] = None
    sex: Optional[Sex] = None
    social_security_number: Optional[str] = None
    initial_day_of_entrance: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "employee_id": "00010",
                    "first_name": "Maria",
                    "surname": "Schmidt",
                    "academic_title": "Dr.",
                    "name_affix": "Baron",
                    "name_prefix": "von zu",
                    "birth_name": "Müller",
                    "birth_name_affix": "Baron",
                    "birth_name_prefix": "von zu",
                    "date_of_birth": "1990-05-15",
                    "place_of_birth": "Berlin",
                    "country_of_birth": "D",
                    "nationality": "000",
                    "marital_status": "married",
                    "sex": "female",
                    "social_security_number": "09050355S095",
                    "initial_day_of_entrance": "2023-03-01"
                }
            ]
        }

class PersonalDataCreateSchema(BaseModel):
    """Schema for validating personal data creation requests"""
    personnel_number: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[str] = Field(None, description="The reference date of the personal data, if not provided, the current date will be used")
    first_name: str
    surname: str
    academic_title: Optional[str] = None
    name_affix: Optional[str] = None
    name_prefix: Optional[str] = None
    birth_name: Optional[str] = None
    birth_name_affix: Optional[str] = None
    birth_name_prefix: Optional[str] = None
    date_of_birth: datetime
    place_of_birth: Optional[str] = None
    country_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    marital_status: Optional[MaritalStatus] = None
    sex: Optional[Sex] = None
    social_security_number: Optional[str] = None
    initial_day_of_entrance: Optional[datetime] = None
