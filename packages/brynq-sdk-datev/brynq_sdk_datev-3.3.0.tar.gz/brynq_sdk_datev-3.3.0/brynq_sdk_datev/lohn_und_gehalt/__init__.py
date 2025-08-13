import base64
import os
from .clients import Client
from .employees import Employee
from .personal_data import PersonalData
from .address import Address
from .social_insurance import SocialInsurance
from .account import Account
from .disability import Disability
from .activity import Activity
from .taxation import Taxation
from .tax_card import TaxCard
from .working_hours import WorkingHours
from .employment_periods import EmploymentPeriods
from .month_records import MonthRecords
from .gross_payments import GrossPayments
from .hourly_wages import HourlyWages
from .individual_data import IndividualData
from .vacation_entitlement import VacationEntitlement
from .vocational_trainings import VocationalTrainings
from .voluntary_insurance import VoluntaryInsurance
from .private_insurance import PrivateInsurance
from .salaries import Salaries
from .salary_types import SalaryTypes
from .reasons_for_absence import ReasonsForAbsence
from .departments import Departments
from .cost_centers import CostCenters
from .cost_units import CostUnits
from .financial_accounting import FinancialAccounting
from .accountable_employees import AccountableEmployees
from datetime import datetime
from typing import List, Optional, Literal
from brynq_sdk_brynq import BrynQ
import pandas as pd

class DatevLohnUndGehalt(BrynQ):
    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, debug: bool = False):
        super().__init__()
        # Initialize with parent class
        self.debug = debug
        self.timeout = 3600

        self.local_url = "http://localhost:58454/datev/api/hr/v3"
        self.headers = {
            "domain": os.getenv("BRYNQ_SUBDOMAIN"),
            "Authorization": f"Bearer {os.getenv('BRYNQ_API_TOKEN')}",
        }
        credentials = self.interfaces.credentials.get(system="datev-lohn-und-gehalt", system_type=system_type)
        credential_data = credentials.get('data')
        self.agent_url = f"{credentials.get('agent_url')}/brynq-agent/rest-request"
        basic_auth = base64.b64encode(f"{credential_data.get('username')}:{credential_data.get('password')}".encode()).decode()
        self.local_headers = {
            "Authorization": f"Basic {basic_auth}"
        }
        self.consultant_number = int(credential_data.get('consultant_number'))
        self.client_number = int(credential_data.get('client_number'))

        # Create resources
        self.client = Client(self)
        self.employees = Employee(self)
        self.personal_data = PersonalData(self)
        self.address = Address(self)
        self.social_insurance = SocialInsurance(self)
        self.account = Account(self)
        self.disability = Disability(self) # Note: batch-only operations, no per-employee endpoint
        self.activity = Activity(self)
        self.taxation = Taxation(self)
        self.tax_card = TaxCard(self)
        self.working_hours = WorkingHours(self) # Note: batch-only operations, no per-employee endpoint
        self.employment_periods = EmploymentPeriods(self)
        self.month_records = MonthRecords(self)
        self.gross_payments = GrossPayments(self)
        self.hourly_wages = HourlyWages(self)
        self.individual_data = IndividualData(self)
        self.vacation_entitlement = VacationEntitlement(self)
        self.vocational_trainings = VocationalTrainings(self)
        self.voluntary_insurance = VoluntaryInsurance(self)
        self.private_insurance = PrivateInsurance(self)
        self.salaries = Salaries(self)
        self.salary_types = SalaryTypes(self)
        self.reasons_for_absence = ReasonsForAbsence(self)
        self.departments = Departments(self)
        self.cost_centers = CostCenters(self)
        self.cost_units = CostUnits(self)
        self.financial_accounting = FinancialAccounting(self)
        self.accountable_employees = AccountableEmployees(self)

        # Initialize client ID
        self.client_id = None
        try:
            self._initialize_client_id()
        except Exception as e:
            if self.debug:
                print(f"Failed to initialize client ID during startup: {str(e)}")

    def _initialize_client_id(self):
        """Initialize client ID based on consultant_number and client_number"""
        valid_clients, _ = self.client.get(datetime.now())

        # Find the client that matches both consultant_number and client_number
        matching_clients = valid_clients[
            (valid_clients['consultant_number'] == self.consultant_number) &
            (valid_clients['number'] == self.client_number)
        ]

        if matching_clients.empty:
            error_msg = f"No client found with consultant_number={self.consultant_number} and client_number={self.client_number}"
            if self.debug:
                print(error_msg)
            raise ValueError(error_msg)

        # Take the first matching client ID
        self.client_id = matching_clients.iloc[0]['client_id']

        if self.debug:
            print(f"Initialized client ID: {self.client_id} for consultant_number={self.consultant_number}, client_number={self.client_number}")

    def get_client_id(self, reference_date: Optional[datetime] = None, force_refresh: bool = False) -> str:
        """
        Get the client ID matching the consultant_number and client_number

        Args:
            reference_date: Optional reference date
            force_refresh: Force a refresh of the client ID

        Returns:
            Client ID as string
        """
        # If we don't have a client ID or a refresh is requested, fetch it
        if self.client_id is None or force_refresh:
            reference_date = reference_date or datetime.now()
            self._initialize_client_id()

        return self.client_id
