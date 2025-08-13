import pandera as pa
from pandera.typing import Series, DataFrame
from typing import Optional
from pydantic import BaseModel, Field
import pandas as pd
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from enum import Enum


class Denomination(str, Enum):
    """Religious denomination enum from Payroll-3.1.1.yaml"""
    AK_ALTKATHOLISCHE_KIRCHENSTEUER = "ak_altkatholische_kirchensteuer"
    LT_EVANGELISCH_LUTHERISCH_BIS_12_2015 = "lt_evangelisch_lutherisch_bis_12_2015"
    RF_EVANGELISCH_REFORMIERT_BIS_12_2015 = "rf_evangelisch_reformiert_bis_12_2015"
    EV_EVANGELISCHE_KIRCHENSTEUER = "ev_evangelische_kirchensteuer"
    FR_FRANZOESISCH_REFORMIERT_BIS_12_2015 = "fr_franzoesisch_reformiert_bis_12_2015"
    FA_FREIE_RELIGIONSGEMEINSCHAFT_ALZEY = "fa_freie_religionsgemeinschaft_alzey"
    FM_FREIRELIGIOESE_GEMEINDE_MAINZ = "fm_freireligioese_gemeinde_mainz"
    FO_FREIRELIGIOESE_GEMEINDE_OFFENBACH_MAIN = "fo_freireligioese_gemeinde_offenbach_main"
    FS_FREIRELIGIOESE_GEMEINDE_OFFENBACH_MAIN = "fs_freireligioese_gemeinde_offenbach_main"
    FB_FREIRELIGIOESE_LANDESGEMEINDE_BADEN = "fb_freireligioese_landesgemeinde_baden"
    FP_FREIRELIGIOESE_LANDESGEMEINDE_PFALZ = "fp_freireligioese_landesgemeinde_pfalz"
    FG_FREIRELIGIOESE_LANDESGEMEINDE_PFALZ = "fg_freireligioese_landesgemeinde_pfalz"
    IS_ISRAELITISCHE_JUEDISCHE_KULTUSSTEUER = "is_israelitische_juedische_kultussteuer"
    IL_ISRAELITISCHE_KULTUSSTEUER_DER_KULTUSBERECHTIGTEN_GEMEINDEN = "il_israelitische_kultussteuer_der_kultusberechtigten_gemeinden"
    IF_ISRAELITISCHE_KULTUSSTEUER_FRANKFURT = "if_israelitische_kultussteuer_frankfurt"
    IB_ISRAELITISCHE_RELIGIONSGEMEINSCHAFT_BADEN = "ib_israelitische_religionsgemeinschaft_baden"
    IW_ISRAELITISCHE_RELIGIONSGEMEINSCHAFT_WUERTTEMBERGS = "iw_israelitische_religionsgemeinschaft_wuerttembergs"
    JUE_JUEDISCH = "jue_juedisch"
    JH_JUEDISCHE_KULTUSSTEUER = "jh_juedische_kultussteuer"
    JD_JUEDISCHE_KULTUSSTEUER = "jd_juedische_kultussteuer"
    ICH_JUEDISCHE_KULTUSSTEUER = "ich_juedische_kultussteuer"
    RK_ROEMISCH_KATHOLISCHE_KIRCHENSTEUER = "rk_roemisch_katholische_kirchensteuer"
    UN_UNITARISCHE_RELIGIONSGEMEINSCHAFT_FREIE_PROTESTANTEN = "un_unitarische_religionsgemeinschaft_freie_protestanten"


class TaxClass(str, Enum):
    """Tax class enum for German tax system"""
    CLASS_1 = "1"
    CLASS_2 = "2"
    CLASS_3 = "3"
    CLASS_4 = "4"
    CLASS_5 = "5"
    CLASS_6 = "6"


class TaxCardSchema(BrynQPanderaDataFrameModel):
    """Schema for employee tax card response"""
    id: Series[str] = pa.Field(alias="employee_id")
    tax_class: Optional[Series[str]] = pa.Field(nullable=True)
    factor_procedure: Optional[Series[bool]] = pa.Field(nullable=True)
    tax_factor: Optional[Series[float]] = pa.Field(nullable=True)
    number_of_children_allowances: Optional[Series[pd.Int64Dtype]] = pa.Field(nullable=True)
    church_tax: Optional[Series[str]] = pa.Field(nullable=True)
    spouse_church_tax: Optional[Series[str]] = pa.Field(nullable=True)
    monthly_exemption: Optional[Series[float]] = pa.Field(nullable=True)
    yearly_exemption: Optional[Series[float]] = pa.Field(nullable=True)
    monthly_additional_care_insurance_exemption: Optional[Series[float]] = pa.Field(nullable=True)
    tax_office_number: Optional[Series[str]] = pa.Field(nullable=True)
    tax_number: Optional[Series[str]] = pa.Field(nullable=True)
    valid_from: Optional[Series[datetime]] = pa.Field(nullable=True)
    valid_to: Optional[Series[datetime]] = pa.Field(nullable=True)

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

class TaxCardUpdateSchema(BaseModel):
    """Schema for validating tax card update requests"""
    id: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[str] = Field(None, description="The reference date, if not provided, the current date will be used")
    tax_class: Optional[TaxClass] = None
    factor_procedure: Optional[bool] = None
    tax_factor: Optional[float] = None
    number_of_children_allowances: Optional[int] = None
    church_tax: Optional[Denomination] = None
    spouse_church_tax: Optional[Denomination] = None
    monthly_exemption: Optional[float] = None
    yearly_exemption: Optional[float] = None
    monthly_additional_care_insurance_exemption: Optional[float] = None
    tax_office_number: Optional[str] = None
    tax_number: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
