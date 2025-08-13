import pandera as pa
from pandera.typing import Series
from typing import Optional, Literal
from pydantic import BaseModel, Field
import pandas as pd
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from enum import Enum


class MaximalPremiumHealthInsurance(str, Enum):
    """Maximal premium for voluntary health insurance enum"""
    ALLGEMEIN = "allgemein"
    ERHOEHT = "erhoeht"
    ERMAESSIGT = "ermaessigt"


class MaximalPremiumNursingInsurance(str, Enum):
    """Maximal premium for voluntary nursing insurance enum"""
    AUTOMATISCH_BERECHNET = "automatisch_berechnet"
    AUTOMATISCH_MIT_ZUSCHUSS_AUF_ENTGELT = "automatisch_mit_zuschuss_auf_entgelt"
    MANUELL_MIT_BETRAGSANGABE = "manuell_mit_betragsangabe"


class VoluntaryInsuranceSchema(BrynQPanderaDataFrameModel):
    """Schema for voluntary insurance response"""
    id: Series[str] = pa.Field(alias="employee_id")
    maximal_premium_for_voluntary_health_insurance: Optional[Series[str]] = pa.Field(nullable=True)
    maximal_premium_for_voluntary_nursing_insurance: Optional[Series[str]] = pa.Field(nullable=True)

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

class VoluntaryInsuranceUpdateSchema(BaseModel):
    """Schema for validating voluntary insurance update requests"""
    id: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[str] = Field(None, description="Reference date for the update (YYYY-MM-DD format)")
    maximal_premium_for_voluntary_health_insurance: Optional[MaximalPremiumHealthInsurance] = None
    maximal_premium_for_voluntary_nursing_insurance: Optional[MaximalPremiumNursingInsurance] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "employee_id": "00010",
                    "maximal_premium_for_voluntary_health_insurance": "allgemein",
                    "maximal_premium_for_voluntary_nursing_insurance": "automatisch_berechnet"
                }
            ]
        }
