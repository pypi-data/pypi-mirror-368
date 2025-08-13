import pandera as pa
from pandera.typing import Series, DataFrame
from typing import Optional
from pydantic import BaseModel, Field
import pandas as pd
from datetime import datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from enum import Enum


class ActivityType(str, Enum):
    """Activity type enum from Payroll-3.1.1.yaml"""
    ARBEITER = "arbeiter"
    ANGESTELLTER = "angestellter"
    AUSZUBILDENDER_GEWERBLICH = "auszubildender_gewerblich"
    AUSZUBILDENDER_KAUFMAENNISCH = "auszubildender_kaufmaennisch"
    GERINGFUEGIG_BESCHAEFTIGTER_MIT_PAUSCHALVERSTEUERUNG_ARBEITER = "geringfuegig_beschaeftigter_mit_pauschalversteuerung_arbeiter"
    GERINGFUEGIG_BESCHAEFTIGTER_MIT_PAUSCHALVERSTEUERUNG_ANGESTELLTER = "geringfuegig_beschaeftigter_mit_pauschalversteuerung_angestellter"
    KURZFRISTIG_BESCHAEFTIGTER_MIT_PAUSCHALVERSTEUERUNG_ARBEITER = "kurzfristig_beschaeftigter_mit_pauschalversteuerung_arbeiter"
    KURZFRISTIG_BESCHAEFTIGTER_MIT_PAUSCHALVERSTEUERUNG_ANGESTELLTER = "kurzfristig_beschaeftigter_mit_pauschalversteuerung_angestellter"
    KFR_BESCHAEFTIGTER_LAND_U_FORST_MIT_PAUSCHALVERSTEUERUNG_ARB = "kfr_beschaeftigter_land_u_forst_mit_pauschalversteuerung_arb"
    KFR_BESCHAEFTIGTER_LAND_U_FORST_MIT_PAUSCHALVERSTEUERUNG_ANGEST = "kfr_beschaeftigter_land_u_forst_mit_pauschalversteuerung_angest"
    PERMANENTER_LOHNSTEUER_JAHRESAUSGLEICH_FUER_KURZFRISTIG_BESCHAEFTIGTE = "permanenter_lohnsteuer_jahresausgleich_fuer_kurzfristig_beschaeftigte"


class ContractualStructure(str, Enum):
    """Contractual structure enum from Payroll-3.1.1.yaml"""
    UNBEFRISTET_IN_VOLLZEIT = "unbefristet_in_vollzeit"
    UNBEFRISTET_IN_TEILZEIT = "unbefristet_in_teilzeit"
    BEFRISTET_IN_VOLLZEIT = "befristet_in_vollzeit"
    BEFRISTET_IN_TEILZEIT = "befristet_in_teilzeit"


class HighestLevelOfEducation(str, Enum):
    """Highest level of education enum from Payroll-3.1.1.yaml"""
    OHNE_SCHULABSCHLUSS = "ohne_schulabschluss"
    HAUPT_VOLKSSCHULABSCHLUSS = "haupt_volksschulabschluss"
    MITTLERE_REIFE_ODER_GLEICHWERTIGER_ABSCHLUSS = "mittlere_reife_oder_gleichwertiger_abschluss"
    ABITUR_FACHABITUR = "abitur_fachabitur"
    ABSCHLUSS_UNBEKANNT = "abschluss_unbekannt"


class HighestLevelOfProfessionalTraining(str, Enum):
    """Highest level of professional training enum from Payroll-3.1.1.yaml"""
    OHNE_BERUFLICHEN_AUSBILDUNGSABSCHLUSS = "ohne_beruflichen_ausbildungsabschluss"
    ABSCHLUSS_EINER_ANERKANNTEN_BERUFSAUSBILDUNG = "abschluss_einer_anerkannten_berufsausbildung"
    MEISTER_TECHNIKER_ODER_GLEICHWERTIGER_FACHSCHULABSCHLUSS = "meister_techniker_oder_gleichwertiger_fachschulabschluss"
    BACHELOR = "bachelor"
    DIPLOM_MAGISTER_MASTER_STAATSEXAMEN = "diplom_magister_master_staatsexamen"
    PROMOTION = "promotion"
    ABSCHLUSS_UNBEKANNT = "abschluss_unbekannt"


class PersonnelLeasing(str, Enum):
    """Personnel leasing enum from Payroll-3.1.1.yaml"""
    WIE_MANDANTENEINSTELLUNG = "wie_mandanteneinstellung"
    JA = "ja"
    NEIN = "nein"


class FormOfRemuneration(str, Enum):
    """Form of remuneration enum from Payroll-3.1.1.yaml"""
    STUNDENLOHN = "stundenlohn"
    GEHALT = "gehalt"
    TAGESLOHN = "tageslohn"
    SONSTIGES = "sonstiges"
    LEISTUNGSLOHN = "leistungslohn"


class ActivitySchema(BrynQPanderaDataFrameModel):
    """Schema for employee activity response"""
    id: Series[str] = pa.Field(alias="employee_id")
    activity_type: Optional[Series[str]] = pa.Field(nullable=True)
    employee_type: Optional[Series[str]] = pa.Field(nullable=True)
    job_title: Optional[Series[str]] = pa.Field(nullable=True)
    occupational_title: Optional[Series[str]] = pa.Field(nullable=True)
    job_carried_out: Optional[Series[str]] = pa.Field(nullable=True)
    contractual_structure: Optional[Series[str]] = pa.Field(nullable=True)
    highest_level_of_education: Optional[Series[str]] = pa.Field(nullable=True)
    highest_level_of_professional_training: Optional[Series[str]] = pa.Field(nullable=True)
    personnel_leasing: Optional[Series[str]] = pa.Field(nullable=True)
    individual_cost_center_id: Optional[Series[str]] = pa.Field(nullable=True)
    individual_cost_unit_id: Optional[Series[str]] = pa.Field(nullable=True)

    class Config:
        coerce = True

    class _Annotation:
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeeSchema",
                "parent_column": "employee_id",
                "cardinality": "N:1"
            },
            "individual_cost_center_id": {
                "parent_schema": "CostCenterSchema",
                "parent_column": "cost_center_id",
                "cardinality": "N:1"
            },
            "individual_cost_unit_id": {
                "parent_schema": "CostUnitSchema",
                "parent_column": "cost_unit_id",
                "cardinality": "N:1"
            }
        }

class ActivityUpdateSchema(BaseModel):
    """Schema for validating activity update requests"""
    id: str = Field(..., description="The ID of the employee", alias="employee_id")
    reference_date: Optional[datetime] = Field(None, description="The reference date of the activity, if not provided, the current date will be used")
    activity_type: Optional[ActivityType] = None
    employee_type: Optional[str] = None
    job_title: Optional[str] = None
    occupational_title: Optional[str] = None
    job_carried_out: Optional[str] = None
    contractual_structure: Optional[ContractualStructure] = None
    highest_level_of_education: Optional[HighestLevelOfEducation] = None
    highest_level_of_professional_training: Optional[HighestLevelOfProfessionalTraining] = None
    personnel_leasing: Optional[PersonnelLeasing] = None
    individual_cost_center_id: Optional[str] = None
    individual_cost_unit_id: Optional[str] = None
    weekly_working_hours: Optional[float] = None
    allocation_of_working_hours_monday: Optional[float] = None
    allocation_of_working_hours_tuesday: Optional[float] = None
    allocation_of_working_hours_wednesday: Optional[float] = None
    allocation_of_working_hours_thursday: Optional[float] = None
    allocation_of_working_hours_friday: Optional[float] = None
    allocation_of_working_hours_saturday: Optional[float] = None
    allocation_of_working_hours_sunday: Optional[float] = None
    average_working_hours: Optional[float] = None
    form_of_remuneration: Optional[FormOfRemuneration] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "employee_id": "00010",
                    "activity_type": "arbeiter",
                    "employee_type": "101",
                    "occupational_title": "Tester",
                    "job_carried_out": "91341",
                    "contractual_structure": "unbefristet_in_vollzeit",
                    "highest_level_of_education": "abitur_fachabitur",
                    "highest_level_of_professional_training": "bachelor",
                    "personnel_leasing": "nein",
                    "individual_cost_center_id": "1",
                    "individual_cost_unit_id": "1",
                    "weekly_working_hours": 40,
                    "allocation_of_working_hours_monday": 8,
                    "allocation_of_working_hours_tuesday": 8,
                    "allocation_of_working_hours_wednesday": 8,
                    "allocation_of_working_hours_thursday": 8,
                    "allocation_of_working_hours_friday": 8
                }
            ]
        }
