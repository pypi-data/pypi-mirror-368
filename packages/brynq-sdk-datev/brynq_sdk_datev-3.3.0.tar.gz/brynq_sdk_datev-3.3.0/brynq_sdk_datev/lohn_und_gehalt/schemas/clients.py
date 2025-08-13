from typing import List, Optional
from uuid import UUID
import pandas as pd
import pandera as pa
from pandera.typing import Series, DataFrame
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class ClientSchema(BrynQPanderaDataFrameModel):
    """
    Pandera schema for validating client data.
    """
    id: Series[str] = pa.Field(alias="client_id")
    number: Series[pd.Int64Dtype] = pa.Field()
    consultant_number: Series[pd.Int64Dtype] = pa.Field()
    name: Series[str] = pa.Field()

    class Config:
        coerce = True

    class _Annotation:
        primary_keys = ["client_id"]
