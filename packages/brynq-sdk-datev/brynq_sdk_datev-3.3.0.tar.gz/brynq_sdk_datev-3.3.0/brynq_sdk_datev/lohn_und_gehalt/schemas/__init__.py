"""Schema definitions for Datev package"""

DATEFORMAT = '%Y-%m-%d'

from .clients import ClientSchema
from .employees import (
    EmployeeSchema,
    EmployeeCreateSchema,
    EmployeeUpdateSchema
)
from .personal_data import (
    PersonalDataSchema,
    PersonalDataUpdateSchema
)
from .address import (
    AddressSchema,
    AddressUpdateSchema
)
from .social_insurance import (
    SocialInsuranceSchema,
    SocialInsuranceUpdateSchema
)
from .account import (
    AccountSchema,
    AccountUpdateSchema
)
from .disability import (
    DisabilitySchema,
    DisabilityUpdateSchema
)
from .activity import (
    ActivitySchema,
    ActivityUpdateSchema
)
from .taxation import (
    TaxationSchema,
    TaxationUpdateSchema
)
from .tax_card import (
    TaxCardSchema,
    TaxCardUpdateSchema
)
from .working_hours import (
    WorkingHoursSchema
)
from .employment_periods import (
    EmploymentPeriodsSchema,
    EmploymentPeriodsUpdateSchema
)
from .month_records import (
    MonthRecordsSchema,
    MonthRecordsUpdateSchema,
    MonthRecordsCreateSchema
)
from .gross_payments import (
    GrossPaymentsSchema,
    GrossPaymentsUpdateSchema,
    GrossPaymentsCreateSchema
)
from .hourly_wages import (
    HourlyWagesSchema,
    HourlyWagesUpdateSchema
)
from .individual_data import IndividualDataSchema
from .vacation_entitlement import (
    VacationEntitlementSchema,
    VacationEntitlementUpdateSchema
)
from .vocational_trainings import (
    VocationalTrainingsSchema,
    VocationalTrainingsUpdateSchema,
    VocationalTrainingsCreateSchema
)
from .voluntary_insurance import (
    VoluntaryInsuranceSchema,
    VoluntaryInsuranceUpdateSchema
)
from .private_insurance import (
    PrivateInsuranceSchema,
    PrivateInsuranceUpdateSchema
)
from .salaries import (
    SalarySchema,
    SalaryCreateSchema,
    SalaryTypeSchema,
    SalaryTypeRequest
)
from .reasons_for_absence import (
    ReasonsForAbsenceSchema,
    ReasonsForAbsenceRequest
)
from .departments import (
    DepartmentsSchema,
    DepartmentsRequest
)
from .cost_centers import (
    CostCentersSchema,
    CostCentersUpdateSchema
)
from .cost_units import (
    CostUnitsSchema,
    CostUnitsUpdateSchema
)
from .financial_accounting import FinancialAccountingSchema
from .accountable_employees import AccountableEmployeesSchema
