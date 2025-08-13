# brynq_sdk_datev

A Python SDK developed by Salure for integrating with DATEV payroll and accounting systems. This package provides a streamlined interface for interacting with DATEV services.

## Overview

The brynq_sdk_datev package consists of two main modules:

1. **DatevLodas** - A module for creating DATEV Lodas import files
2. **DatevLohnUndGehalt** - A module for interacting with DATEV Lohn und Gehalt API

## Installation

```bash
pip install brynq_sdk_datev
```

## Dependencies

- brynq-sdk-brynq>=2
- brynq-sdk-functions>=2
- pandas>=1,<=3

## Usage

### DatevLodas

The DatevLodas module helps create import files for DATEV Lodas with employee data:

```python
from brynq_sdk_datev import Datev

# Initialize Datev with consultant and client numbers
datev = Datev(berater_nr=12345, mandanten_nr=67890)

# Access the Lodas module
lodas = datev.lodas

# Export data to a Lodas import file
lodas.full_export(
    filepath="/path/to/export/",
    valid_from="01.01.2023",
    df=employee_dataframe,
    df_employment_periods=employment_periods_dataframe
)
```

### DatevLohnUndGehalt

The DatevLohnUndGehalt module provides an interface to the DATEV Lohn und Gehalt API via the BrynQ agent:

```python
from brynq_sdk_datev import Datev

# Initialize Datev with consultant and client numbers
datev = Datev(berater_nr=12345, mandanten_nr=67890)

# Access the Lohn und Gehalt module
lug = datev.lohn_und_gehalt

# Get employees data
employees_df, errors = lug.employees.get()

# Access specific employee data
employee_personal_data, errors = lug.personal_data.get(employee_id="12345")

# Update employee data
lug.personal_data.put(employee_id="12345", data=updated_data)
```

## Key Features

- **DatevLodas**:
  - Generate DATEV Lodas import files with proper formatting
  - Support for different types of employee data (personal, employment, wage components, etc.)
  - Comparison mode to only upload changed data

- **DatevLohnUndGehalt**:
  - Complete interface to DATEV Lohn und Gehalt API
  - Access to employee data, personal information, addresses, tax information, etc.
  - Support for batch operations
  - Handles API authentication and request formatting

## Available Resources in DatevLohnUndGehalt

- Client
- Employee
- PersonalData
- Address
- SocialInsurance
- Account
- Disability
- Activity
- Taxation
- TaxCard
- WorkingHours
- EmploymentPeriods
- MonthRecords
- GrossPayments
- HourlyWages
- IndividualData
- VacationEntitlement
- VocationalTrainings
- VoluntaryInsurance
- PrivateInsurance
- Salaries
- SalaryTypes
- ReasonsForAbsence
- Departments
- CostCenters
- CostUnits
- FinancialAccounting
- AccountableEmployees

## License

BrynQ License
