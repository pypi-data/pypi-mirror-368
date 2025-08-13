import pandera as pa
from pandera.typing import Series, DataFrame
from typing import Optional
from pydantic import BaseModel, Field
import pandas as pd
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from enum import Enum


class ContributionClassHealthInsurance(str, Enum):
    """Contribution class health insurance enum from Payroll-3.1.1.yaml"""
    KEIN_BEITRAG_PRIVATE_KV_ODER_FREIWILLIGE_KV_ALS_SELBSTZAHLER = "kein_beitrag_private_kv_oder_freiwillige_kv_als_selbstzahler"
    ALLGEMEINER_BEITRAG = "allgemeiner_beitrag"
    ERHOEHTER_BEITRAG_NUR_BIS_12_2008_GUELTIG = "erhoehter_beitrag_nur_bis_12_2008_gueltig"
    ERMAESSIGTER_BEITRAG = "ermaessigter_beitrag"
    BEITRAG_ZUR_LANDWIRTSCHAFTLICHEN_KV = "beitrag_zur_landwirtschaftlichen_kv"
    ARBEITGEBERBEITRAG_ZUR_LANDWIRTSCHAFTLICHEN_KV = "arbeitgeberbeitrag_zur_landwirtschaftlichen_kv"
    PAUSCHALBEITRAG_FUER_GERINGFUEGIG_BESCHAEFTIGTE = "pauschalbeitrag_fuer_geringfuegig_beschaeftigte"
    FIRMENZAHLER = "firmenzahler"


class ContributionClassPensionInsurance(str, Enum):
    """Contribution class pension insurance enum from Payroll-3.1.1.yaml"""
    KEIN_BEITRAG = "kein_beitrag"
    VOLLER_BEITRAG = "voller_beitrag"
    HALBER_BEITRAG = "halber_beitrag"
    BEITRAG_ZUR_ANGESTELLTENVERSICHERUNG_NUR_BIS_12_2004_GUELTIG = "beitrag_zur_angestelltenversicherung_nur_bis_12_2004_gueltig"
    HALBER_BEITRAG_ZUR_ANGESTELLTENVERSICHERUNG_NUR_BIS_12_2004_GUELTIG = "halber_beitrag_zur_angestelltenversicherung_nur_bis_12_2004_gueltig"
    PAUSCHALBEITRAG_FUER_GERINGFUEGIG_BESCHAEFTIGTE = "pauschalbeitrag_fuer_geringfuegig_beschaeftigte"
    GERINGFUEGIG_ENTLOHNTE_ANGESTELLTE_NUR_BIS_12_2004_GUELTIG = "geringfuegig_entlohnte_angestellte_nur_bis_12_2004_gueltig"


class ContributionClassUnemploymentInsurance(str, Enum):
    """Contribution class unemployment insurance enum from Payroll-3.1.1.yaml"""
    KEIN_BEITRAG = "kein_beitrag"
    VOLLER_BEITRAG = "voller_beitrag"
    HALBER_BEITRAG = "halber_beitrag"


class ContributionClassNursingInsurance(str, Enum):
    """Contribution class nursing insurance enum from Payroll-3.1.1.yaml"""
    KEIN_BEITRAG = "kein_beitrag"
    VOLLER_BEITRAG = "voller_beitrag"
    HALBER_BEITRAG = "halber_beitrag"


class AllocationMethod(str, Enum):
    """Allocation method enum from Payroll-3.1.1.yaml"""
    NEIN = "nein"
    UMLAGE_1_UND_2 = "umlage_1_und_2"
    UMLAGE_2 = "umlage_2"
    WIE_MANDANTENEINSTELLUNG = "wie_mandanteneinstellung"


class LegalTreatment(str, Enum):
    """Legal treatment enum from Payroll-3.1.1.yaml"""
    ANWENDUNG_DER_SV_BESTIMMUNGEN_OST = "anwendung_der_sv_bestimmungen_ost"
    ANWENDUNG_DER_SV_BESTIMMUNGEN_WEST = "anwendung_der_sv_bestimmungen_west"


class SocialInsuranceSchema(BrynQPanderaDataFrameModel):
    """Schema for employee social insurance response"""
    id: Series[str] = pa.Field(alias="employee_id")
    contribution_class_health_insurance: Optional[Series[str]] = pa.Field(nullable=True)
    contribution_class_pension_insurance: Optional[Series[str]] = pa.Field(nullable=True)
    contribution_class_unemployment_insurance: Optional[Series[str]] = pa.Field(nullable=True)
    contribution_class_nursing_insurance: Optional[Series[str]] = pa.Field(nullable=True)
    is_additional_contribution_to_nursing_insurance_for_childless_ignored: Optional[Series[bool]] = pa.Field(nullable=True)
    allocation_method: Optional[Series[str]] = pa.Field(nullable=True)
    legal_treatment: Optional[Series[str]] = pa.Field(nullable=True)
    company_number_of_health_insurer: Optional[Series[pd.Int64Dtype]] = pa.Field(nullable=True)
    branch_office_of_health_insurer: Optional[Series[pd.Int64Dtype]] = pa.Field(nullable=True)

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


class SocialInsuranceUpdateSchema(BaseModel):
    """Schema for validating social insurance update requests"""
    id: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[str] = Field(None, description="The reference date, if not provided, the current date will be used")
    contribution_class_health_insurance: Optional[ContributionClassHealthInsurance] = None
    contribution_class_pension_insurance: Optional[ContributionClassPensionInsurance] = None
    contribution_class_unemployment_insurance: Optional[ContributionClassUnemploymentInsurance] = None
    contribution_class_nursing_insurance: Optional[ContributionClassNursingInsurance] = None
    is_additional_contribution_to_nursing_insurance_for_childless_ignored: Optional[bool] = None
    allocation_method: Optional[AllocationMethod] = None
    legal_treatment: Optional[LegalTreatment] = None
    company_number_of_health_insurer: Optional[int] = None
    branch_office_of_health_insurer: Optional[int] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "employee_id": "00010",
                    "contribution_class_health_insurance": "allgemeiner_beitrag",
                    "contribution_class_pension_insurance": "voller_beitrag",
                    "contribution_class_unemployment_insurance": "voller_beitrag",
                    "contribution_class_nursing_insurance": "voller_beitrag",
                    "is_additional_contribution_to_nursing_insurance_for_childless_ignored": False,
                    "allocation_method": "umlage_1_und_2",
                    "legal_treatment": "anwendung_der_sv_bestimmungen_west"
                }
            ]
        }
