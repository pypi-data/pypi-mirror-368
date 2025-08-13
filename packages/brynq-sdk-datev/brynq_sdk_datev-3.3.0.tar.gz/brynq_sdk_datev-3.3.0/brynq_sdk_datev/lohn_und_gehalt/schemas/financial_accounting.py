import pandera as pa
import pandas as pd
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from pandera.typing import Series


class FinancialAccountingSchema(BrynQPanderaDataFrameModel):
    """Pandera schema for validating financial accounting data from the DATEV API"""

    id: Series[str] = pa.Field(nullable=False, alias="client_id")
    different_consultant_number: Series[pd.Int64Dtype] = pa.Field(nullable=True)
    different_client_number: Series[pd.Int64Dtype] = pa.Field(nullable=True)

    class Config:
        coerce = True

    class _Annotation:
        foreign_keys = {
            "client_id": {
                "parent_schema": "ClientSchema",
                "parent_column": "client_id",
                "cardinality": "N:1"
            }
        }

class FinancialAccountingRequest(BaseModel):
    """Request model for financial accounting data"""

    different_consultant_number: Optional[int] = None
    different_client_number: Optional[int] = None

    class Config:
        schema_extra = {
            "example": {
                "different_consultant_number": 1234567,
                "different_client_number": 12345
            }
        }
