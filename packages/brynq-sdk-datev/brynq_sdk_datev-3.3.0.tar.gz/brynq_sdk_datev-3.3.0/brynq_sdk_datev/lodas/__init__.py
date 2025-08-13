r"""
  _____        _               _               _
 |  __ \      | |             | |             | |
 | |  | | __ _| |_ _____   __ | |     ___   __| | __ _ ___
 | |  | |/ _` | __/ _ \ \ / / | |    / _ \ / _` |/ _` / __|
 | |__| | (_| | ||  __/\ V /  | |___| (_) | (_| | (_| \__ \
 |_____/ \__,_|\__\___| \_/   |______\___/ \__,_|\__,_|___/

 Hi there! This is the source code of the DatevLodas Salure Helper.
 When you want to use this helper, please import the DatevLodas class from this file with the following code:
 from salure_helpers.datev.datev_lodas import DatevLodas

 Now to the fun part! This helper is used to create a Datev Lodas import file. This file can be used to import data into Datev Lodas.
 The import file is a text file with a specific structure. This structure is described in the Datev Lodas documentation.
 The document can be found in the package_helper_data in the folder datev. The file is called "datev_lodas_manual.pdf".

 The import file is created by using the full_export method. This method has the following parameters:
    filepath: str
        The path where the file should be saved.
    valid_from: str
        The date from which the data is valid. The format should be "DD.MM.YYYY".
    use_alternative_employee_number: bool
        If True, the alternative employee number will be used. If False, the employee number will be used.
    filename: str
        The name of the file. The default value is "importfile_{month}_{year}.txt".
    comparison_data: bool
        If True, a comparison dataframe should be provided. If False, a dataframe with all the data should be provided.
    df: pd.DataFrame
        The dataframe with the data that should be exported. This dataframe should contain all the data that should be exported.
    df_employment_periods: pd.DataFrame
        The dataframe with the employment periods. This dataframe should contain all the employment periods for all the employees.
    df_formations: pd.DataFrame
        The dataframe with the formation division. This dataframe should contain all the formation division for all the employees.
    df_wage_components: pd.DataFrame
        The dataframe with the wage components. This dataframe should contain all the wage components for all the employees.
    df_declaration: pd.DataFrame
        The dataframe with the declarations. This dataframe should contain all the declarations for all the employees.

 When comparison_data is True, You should provide a dataframe created with the detect_changes_between_dataframes from the salure_functions package.
 The helper package will then only upload the changed data in the case of a change and the full data in the case of a new employee. Make sure you
 use the option: keep_old_values='list' in the detect_changes_between_dataframes method.

 Accepted values for the columns in the dataframe can be found in the description of the methods below. The accepted values are described in the datev_lodas_mapping.py file.
 The file can be found in the helper package as a separate file. The file contains a dictionary with the accepted values for each column. You can see which values are
 linked to which column in the DEID field. The code corresponds to a dict in the datev_lodas_mapping.py file.

 Some extra features that will be added in the future:
    - Error handling
    - Validation of the data
    - More documentation
    - Support for ümlauts and other special characters
    - validation of header information

 Viel spaß!
"""
import pandas as pd
from datetime import datetime
from brynq_sdk_brynq import BrynQ
from typing import List, Union, Literal, Optional


class DatevLodas(BrynQ):
    def __init__(self,  system_type: Optional[Literal['source', 'target']] = None, berater_nr: int = None, mandanten_nr: int = None):  # , pay_components: dict = None, departments: dict = None, costcenters: dict = None, companies: dict = None
        super().__init__()
        self.credentials = self.interfaces.credentials.get(system='datev', system_type=system_type)
        if berater_nr is None:
            self.berater_nr = self.credentials.get('data',{}).get('consultant_number')
        else:
            self.berater_nr = berater_nr
        if mandanten_nr is None:
            self.mandanten_nr = self.credentials.get('data',{}).get('client_number')
        else:
            self.mandanten_nr = mandanten_nr


    def full_export(self,
                    filepath: str,
                    valid_from: str = datetime.today().strftime('01.%m.%Y'),
                    use_alternative_employee_number: bool = False,
                    filename: str = f"importfile_{datetime.now().strftime('%B')}_{datetime.now().year}.txt",
                    comparison_data: bool = False,
                    # error_handling: str = None,  # TODO: still needs to be implemented
                    encoding: str = 'ascii',
                    set_employee_number: bool = False,
                    df: pd.DataFrame = None,
                    df_employment_periods: pd.DataFrame = None,
                    df_formations: pd.DataFrame = None,
                    df_wage_components: pd.DataFrame = None,
                    df_declaration: pd.DataFrame = None,
                    df_postcalculation: pd.DataFrame = None,
                    df_absence: pd.DataFrame = None):

        template_headers = ["[Allgemein]\n",
                            "Ziel=LODAS\n",
                            "Version_SST=1.0\n",
                            f"BeraterNr={self.berater_nr}\n",
                            f"MandantenNr={self.mandanten_nr}\n",
                            "Feldtrennzeichen=;\n",
                            "Zahlenkomma=,\n",
                            "Datumsformat=TT.MM.JJJJ\n",
                            f"StammdatenGueltigAb={valid_from}\n",
                            f"{'BetrieblichePNrVerwenden=Ja' if use_alternative_employee_number else 'BetrieblichePNrVerwenden=Nein'}" + '\n' + '\n']

        template_description = "[Satzbeschreibung]\n"
        template_body = '\n' + "[Stammdaten]" + '\n'

        description = []
        body = []

        if comparison_data:
            # Create the data for new employees
            if len(df[df['change_type'] == 'new']) > 0:
                description_temp, body_temp = self.create_template(
                    columns_to_compare=df.columns,
                    use_alternative_employee_number=use_alternative_employee_number,
                    set_employee_number=set_employee_number,
                    df=df[df['change_type'] == 'new']
                )
                description += description_temp
                body += body_temp

            # Create the data for edited employees
            for _, row in df[df['change_type'] == 'edited'].iterrows():
                description_temp, body_temp = self.create_template(
                    columns_to_compare=row['changed_fields'],
                    use_alternative_employee_number=use_alternative_employee_number,
                    df=row.to_frame().T,
                )
                description += description_temp
                body += body_temp

            # Adds all the other attached data
            description_temp, body_temp = self.create_template(
                columns_to_compare=[],
                use_alternative_employee_number=use_alternative_employee_number,
                df_employment_periods=df_employment_periods,
                df_formations=df_formations,
                df_wage_components=df_wage_components,
                df_declaration=df_declaration,
                df_postcalculation=df_postcalculation,
                df_absence=df_absence
            )
            description += description_temp
            body += body_temp

            # Drop the duplicates in description
            description = list(set(description))
        else:
            # Create the data for all employees in the provided dataframe
            description_temp, body_temp = self.create_template(
                columns_to_compare=df.columns,
                use_alternative_employee_number=use_alternative_employee_number,
                df=df,
                df_employment_periods=df_employment_periods,
                df_formations=df_formations,
                df_wage_components=df_wage_components,
                df_declaration=df_declaration,
                df_postcalculation=df_postcalculation,
                df_absence=df_absence
            )
            description += description_temp
            body += body_temp

        # Write the export file
        with open(f"{filepath}{filename}", 'w', encoding=encoding, newline='\r\n') as file:
            file.writelines(template_headers)
            file.writelines(template_description)
            file.writelines(description)
            file.writelines(template_body)
            file.writelines(body)

    def create_template(self,
                        use_alternative_employee_number: bool = False,
                        columns_to_compare: list = None,
                        df: pd.DataFrame = None,
                        set_employee_number: bool = False,
                        df_employment_periods: pd.DataFrame = None,
                        df_formations: pd.DataFrame = None,
                        df_wage_components: pd.DataFrame = None,
                        df_declaration: pd.DataFrame = None,
                        df_postcalculation: pd.DataFrame = None,
                        df_absence: pd.DataFrame = None) -> (list, list):

        description_list = []
        body = []

        # Name
        columns = ['lastname', 'firstname', 'academic_title', 'name_addition', 'prefix', 'birthname', 'name_addition_birthname', 'prefix_birthname']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_name(df, use_alternative_employee_number, set_employee_number)
            description_list += description
            body += data

        # Address
        columns = ['street', 'housenumber', 'supplement', 'country', 'postalcode', 'postalcode_foreign_country', 'city']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_address(df, use_alternative_employee_number)
            description_list += description
            body += data

        # Contact
        columns = ['email', 'phone_number', 'fax_number']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_contact(df, use_alternative_employee_number)
            description_list += description
            body += data

        # Birth data
        columns = ['date_of_birth', 'place_of_birth', 'country_of_birth', 'gender']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_birth_data(df, use_alternative_employee_number)
            description_list += description
            body += data

        # Other data
        columns = ['insurance_number', 'european_insurance_number', 'married', 'single_parent', 'nationality', 'work_permit', 'residence_permit', 'study_certificate', 'disabled']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_other(df, use_alternative_employee_number)
            description_list += description
            body += data

        # Bank data
        columns = ['payment_method', 'settle_overpayments', 'iban', 'bic', 'account_holder', 'bank_postalcode', 'bank_city']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_bank(df, use_alternative_employee_number)
            description_list += description
            body += data

        # Bank data individual
        columns = ['individual_payment_reference', 'individual_text_payroll', 'individual_text_input', 'individual_text_advance', 'bank_employee_name', 'bank_employee_id']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_bank_individual(df, use_alternative_employee_number)
            description_list += description
            body += data

        # Employment periods
        columns = ['date_in_service', 'date_out_of_service', 'employment_relationship']
        if df_employment_periods is not None:
            description, data = self.employee_employment_periods(df_employment_periods, use_alternative_employee_number)
            description_list += description
            body += data
        elif df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_employment_periods(df, use_alternative_employee_number)
            description_list += description
            body += data

        # Formation division
        columns = ['costcenter_division', 'percentage_division']
        if df_formations is not None:
            description, data = self.employee_formation_division(df_formations, use_alternative_employee_number)
            description_list += description
            body += data
        elif df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_formation_division(df, use_alternative_employee_number)
            description_list += description
            body += data

        # Employment 1
        columns = ['job_title', 'employee_type', 'employee_group', 'employment_company', 'department', 'costcenter']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_employment(df, use_alternative_employee_number)
            description_list += description
            body += data

        # Employment 2
        columns = ['payroll_group', 'date_in_service_historical', 'date_in_service_aag', 'employee_group']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_employment_2(df, use_alternative_employee_number)
            description_list += description
            body += data

        # Employment 3
        columns = ['salary_type', 'disabled_person_indicator']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_employment_3(df, use_alternative_employee_number)
            description_list += description
            body += data

        # Employment 4
        columns = ['probation_end_date']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_employment_4(df, use_alternative_employee_number)
            description_list += description
            body += data

        # Activity key
        columns = ['output_activity', 'school_degree', 'training_degree', 'commercial_transfer', 'contract_form']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_activity_key(df, use_alternative_employee_number)
            description_list += description
            body += data

        # Tax class
        columns = ['tax_class', 'factor', 'number_of_child_allowances', 'religion', 'religion_spouse', 'identification_number', 'employer_identification', 'desired_annual_allowances', 'calculate_flat_tax', 'take_over_flat_tax']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_tax(df, use_alternative_employee_number)
            description_list += description
            body += data

        # Allowances
        columns = ['annual_allowance_amount', 'monthly_allowance_amount', 'annual_additional_amount', 'monthly_additional_amount']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_allowances(df, use_alternative_employee_number)
            description_list += description
            body += data

        # Social insurance key
        columns = ['health_insurance', 'pension_insurance', 'unemployment_insurance', 'nursing_care_insurance']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_insurance_key(df, use_alternative_employee_number)
            description_list += description
            body += data

        # Social insurance data
        columns = ['apply_midijob_regulation', 'contribution_pv_childless', 'allocation_key', 'statutory_health_insurance', 'voluntary_health_insurance', 'low_wage_employees', 'minijob_health_insurance', 'insurance_status_short']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_insurance(df, use_alternative_employee_number)
            description_list += description
            body += data

        # Private insurance
        columns = ['private_health_insurance', 'private_nursing_care', 'monthly_contribution_health', 'monthly_contribution_share', 'monthly_contribution_nursing']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_private_insurance(df, use_alternative_employee_number)
            description_list += description
            body += data

        # Payroll
        columns = ['hourly_wage_1', 'hourly_wage_1', 'hourly_wage_1', 'gross_salary']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_payroll(df, use_alternative_employee_number)
            description_list += description
            body += data

        # Wage components
        columns = ['sequence_number', 'wage_component', 'amount', 'interval', 'valid_months', 'reduction', 'monthly_salary']
        if df_wage_components is not None:
            description, data = self.employee_wage_components(df_wage_components, use_alternative_employee_number)
            description_list += description
            body += data
        elif df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_wage_components(df, use_alternative_employee_number)
            description_list += description
            body += data

        # Schedule
        columns = ['hours_per_week', 'hours_monday', 'hours_tuesday', 'hours_wednesday', 'hours_thursday', 'hours_friday', 'hours_saturday', 'hours_sunday']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_schedule(df, use_alternative_employee_number)
            description_list += description
            body += data

        if df_declaration is not None:
            description, data = self.employee_declarations(df_declaration, use_alternative_employee_number)
            description_list += description
            body += data

        columns = ['vwl_saving_formation', 'vwl_wage_component', 'vwl_direct_debit', 'vwl_amount']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_vwl(df, use_alternative_employee_number)
            description_list += description
            body += data

        columns = ['vwl_iban', 'vwl_bic', 'vwl_institute', 'vwl_contract_number', 'vwl_contract_type', 'vwl_start_date', 'vwl_end_date']
        if df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_vwl_bank(df, use_alternative_employee_number)
            description_list += description
            body += data

        if df_postcalculation is not None:
            description, data = self.postcalculation(df_postcalculation, use_alternative_employee_number)
            description_list += description
            body += data

        # Absence
        columns = ['absence_start_date', 'absence_end_date', 'absence_reason_code', 'number_of_children', 'childcare_injury_benefit', 'worked_first_day', 'last_working_day', 'last_payment_day_before_birth', 'contractual_weekly_hours', 'unable_to_work_since', 'comment']
        if df_absence is not None:
            description, data = self.employee_absence(df_absence, use_alternative_employee_number)
            description_list += description
            body += data
        elif df is not None and any(column in columns for column in columns_to_compare):
            description, data = self.employee_absence(df, use_alternative_employee_number)
            description_list += description
            body += data

        return description_list, body

    @staticmethod
    def employee_name(df: pd.DataFrame,
                      use_alternative_employee_number: bool = False,
                      set_employee_number: bool = False):
        """
        TECHNICAL NAME                  DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE             DEID (values)
        pnr_betriebliche#psd            Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                         Personalnummer                  Employee ID                         employee_id
        duevo_familienname#psd          Familienname                    Last name                           lastname
        duevo_vorname#psd               Vorname                         First name                          firstname
        duevo_titel#psd                 Akademischer Grad               Academic title                      academic_title
        duevo_namenszusatz#psd          Namenszusatz (familienname)     Name addition                       name_addition               4248
        duevo_vorsatzwort#psd           Vorsatzwort  (familienname)     Prefix                              prefix                      4249
        gebname#psd                     Geburtsname                     Birth name                          birthname
        nazu_gebname#psd                Namenszusatz (Geburtsname)      Name addition birth name            name_addition_birthname     4248
        vorsatzwort_gebname#psd         Vorsatzwort (Geburtsname)       Prefix birth name                   prefix_birthname            4249
        """

        required_fields = ['lastname', 'firstname']
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"{'999' if set_employee_number else '100'};u_lod_psd_mitarbeiter;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};{'pnr#psd;' if set_employee_number else ''}duevo_familienname#psd;duevo_vorname#psd;duevo_titel#psd;duevo_namenszusatz#psd;duevo_vorsatzwort#psd;gebname#psd;nazu_gebname#psd;vorsatzwort_gebname#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"{'999' if set_employee_number else '100'};"
                f"{row['employee_id']};"
                f"{row['set_employee_number'] + ';' if set_employee_number else ''}"
                f"{row['lastname']};"
                f"{row['firstname']};"
                f"{row['academic_title'] if 'academic_title' in row.keys() else ''};"
                f"{row['name_addition'] if 'name_addition' in row.keys() else ''};"
                f"{row['prefix'] if 'prefix' in row.keys() else ''};"
                f"{row['birthname'] if 'birthname' in row.keys() else ''};"
                f"{row['name_addition_birthname'] if 'name_addition_birthname' in row.keys() else ''};"
                f"{row['prefix_birthname'] if 'prefix_birthname' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_address(df: pd.DataFrame,
                         use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                  DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE             DEID (values)
        pnr_betriebliche#psd            Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                         Personalnummer                  Employee ID                         employee_id
        adresse_strassenname#psd        Straße                          Street                              street
        adresse_strasse_nr#psd          Hausnummer                      House number (including addition)   housenumber
        adresse_anschriftenzusatz#psd   Adresszusatz                    supplement to address               supplement
        adresse_nation_kz#psd           Land                            Country code                        country                     4213
        adresse_plz#psd                 Postleitzahl Inland             Postal code                         postalcode
        adresse_plz_ausland#psd         Postleitzahl Ausland            Foreign postal code                 postalcode_foreign_country
        adresse_ort#psd                 Ort                             City                                city
        """

        required_fields = ['street']  # TODO: find the correct required columns
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"101;u_lod_psd_mitarbeiter;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};adresse_strassenname#psd;adresse_strasse_nr#psd;adresse_anschriftenzusatz#psd;adresse_nation_kz#psd;adresse_plz#psd;adresse_plz_ausland#psd;adresse_ort#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"101;"
                f"{row['employee_id']};"
                f"{row['street'] if 'street' in row.keys() else ''};"
                f"{row['housenumber'] if 'housenumber' in row.keys() else ''};"
                f"{row['supplement'] if 'supplement' in row.keys() else ''};"
                f"{row['country'] if 'country' in row.keys() else ''};"
                f"{row['postalcode'] if 'postalcode' in row.keys() else ''};"
                f"{row['postalcode_foreign_country'] if 'postalcode_foreign_country' in row.keys() else ''};"
                f"{row['city'] if 'city' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_contact(df: pd.DataFrame,
                         use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                  DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE             DEID (values)
        pnr_betriebliche#psd            Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                         Personalnummer                  Employee ID                         employee_id
        email#psd                       E-Mail                          Email                               email
        telefon#psd                     Telefon                         Phone number                        phone_number
        fax#psd                         Fax                             Fax number                          fax_number
        """

        required_fields = []
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"102;u_lod_psd_mitarbeiter;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};email#psd;telefon#psd;fax#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"102;"
                f"{row['employee_id']};"
                f"{row['email'] if 'email' in row.keys() else ''};"
                f"{row['phone_number'] if 'phone_number' in row.keys() else ''};"
                f"{row['fax_number'] if 'fax_number' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_birth_data(df: pd.DataFrame,
                            use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                  DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE             DEID (values)
        pnr_betriebliche#psd            Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                         Personalnummer                  Employee ID                         employee_id
        geburtsdatum_ttmmjj#psd         Geburtsdatum                    Date of birth                       date_of_birth
        gebort#psd                      Geburtsort                      Place of birth                      place_of_birth
        geburtsland#psd                 Geburtsland                     Country of birth                    country_of_birth            4214
        geschlecht#psd                  Geschlecht                      Gender                              gender                      4003
        """

        required_fields = []
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"103;u_lod_psd_mitarbeiter;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};geburtsdatum_ttmmjj#psd;gebort#psd;geburtsland#psd;geschlecht#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"103;"
                f"{row['employee_id']};"
                f"{row['date_of_birth'] if 'date_of_birth' in row.keys() else ''};"
                f"{row['place_of_birth'] if 'place_of_birth' in row.keys() else ''};"
                f"{row['country_of_birth'] if 'country_of_birth' in row.keys() else ''};"
                f"{row['gender'] if 'gender' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_other(df: pd.DataFrame,
                       use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                  DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE             DEID (values)
        pnr_betriebliche#psd            Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                         Personalnummer                  Employee ID                         employee_id
        sozialversicherung_nr#psd       Versicherungsnummer             Insurance number                    insurance_number
        eur_versnr#psd                  Europäische Versicherungsnummer European insurance number           european_insurance_number
        familienstand#psd               Verheirated                     Married                             married                     440
        kz_alleinerziehend#psd          Alleinerziehend                 Single parent                       single_parent               440
        staatsangehoerigkeit#psd        Staatsangehörigkeit             Nationality                         nationality                 4214
        arbeitserlaubnis#psd            Arbeitserlaubnis gültig bis     Work permit valid till              work_permit                 12
        aufenthaltserlaubnis#psd        Aufenthaltserlaubnis gültig bis Residence permit valid till         residence_permit            12
        datum_studienbesch#psd          studienbescheinigung gültig bis study certificate valid till        study_certificate           12
        schwerbeschaedigt#psd           Schwerbehindert                 Disabled                            disabled                    440
        """

        required_fields = ['insurance_number']
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"104;u_lod_psd_mitarbeiter;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};sozialversicherung_nr#psd;eur_versnr#psd;familienstand#psd;kz_alleinerziehend#psd;staatsangehoerigkeit#psd;arbeitserlaubnis#psd;aufenthaltserlaubnis#psd;datum_studienbesch#psd;schwerbeschaedigt#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"104;"
                f"{row['employee_id']};"
                f"{row['insurance_number'] if 'insurance_number' in row.keys() else ''};"
                f"{row['european_insurance_number'] if 'european_insurance_number' in row.keys() else ''};"
                f"{row['married'] if 'married' in row.keys() else ''};"
                f"{row['single_parent'] if 'single_parent' in row.keys() else ''};"
                f"{row['nationality'] if 'nationality' in row.keys() else ''};"
                f"{row['work_permit'] if 'work_permit' in row.keys() else ''};"
                f"{row['residence_permit'] if 'residence_permit' in row.keys() else ''};"
                f"{row['study_certificate'] if 'study_certificate' in row.keys() else ''};"
                f"{row['disabled'] if 'disabled' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_bank(df: pd.DataFrame,
                      use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                  DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE                 DEID (values)
        pnr_betriebliche#psd            Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                         Personalnummer                  Employee ID                         employee_id
        ma_bank_zahlungsart#psd         Zahlungsart                     Payment method                      payment_method                  4181
        ueberzahlg_kz#psd               Verrechnung von Überzahlungen   Settle overpayments                 settle_overpayments             4636
        ma_iban#psd                     IBAN                            IBAN                                iban
        ma_bic#psd                      BIC/Bankbezeichnung             BIC                                 bic
        ma_bank_kto_inhaber_abw#psd     Kontoinhaber                    Account holder                      account_holder
        ma_bank_plz_abw#psd             Postleitzahl                    Postal code                         bank_postalcode
        ma_bank_ort_abw#psd             Ort                             City                                bank_city
        """

        required_fields = ['payment_method']
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"200;u_lod_psd_ma_bank;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};ma_bank_zahlungsart#psd;ueberzahlg_kz#psd;ma_iban#psd;ma_bic#psd;ma_bank_kto_inhaber_abw#psd;ma_bank_plz_abw#psd;ma_bank_ort_abw#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"200;"
                f"{row['employee_id']};"
                f"{row['payment_method'] if 'payment_method' in row.keys() else ''};"
                f"{row['settle_overpayments'] if 'settle_overpayments' in row.keys() else ''};"
                f"{row['iban'] if 'iban' in row.keys() else ''};"
                f"{row['bic'] if 'bic' in row.keys() else ''};"
                f"{row['account_holder'] if 'account_holder' in row.keys() else ''};"
                f"{row['bank_postalcode'] if 'bank_postalcode' in row.keys() else ''};"
                f"{row['bank_city'] if 'bank_city' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_bank_individual(df: pd.DataFrame,
                                 use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                  DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE                 DEID (values)
        pnr_betriebliche#psd            Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                         Personalnummer                  Employee ID                         employee_id
        indiv_vwz_steuerung#psd         Individuelle Verwendungszweck   Individual payment reference        individual_payment_reference    4794
        indiv_vwz_lg_text#psd           Individueller Text Lohn/Gehalt  Individual text payroll             individual_text_payroll         440
        indiv_vwz_lg_texteingabe#psd    Individueller Texteingabe       Individual text input               individual_text_input
        indiv_vwz_vorschuss_text#psd    Individueller Text Vorschuss    Individual text advance             individual_text_advance         440
        indiv_vwz_vorschuss_txtein#psd  Individueller Texteingabe       Individual text input               individual_text_input
        indiv_vwz_ma#psd                Mitarbeitername                 Employee name                       bank_employee_name              440
        indiv_vwz_pnr#psd               Personalnummer                  Employee ID                         bank_employee_id                440
        """

        required_fields = ['individual_payment_reference']
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"201;u_lod_psd_ma_bank;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};indiv_vwz_steuerung#psd;indiv_vwz_lg_text#psd;indiv_vwz_lg_texteingabe#psd;indiv_vwz_vorschuss_text#psd;indiv_vwz_vorschuss_txtein#psd;indiv_vwz_ma#psd;indiv_vwz_pnr#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"201;"
                f"{row['employee_id']};"
                f"{row['individual_payment_reference'] if 'individual_payment_reference' in row.keys() else ''};"
                f"{row['individual_text_payroll'] if 'individual_text_payroll' in row.keys() else ''};"
                f"{row['individual_text_input'] if 'individual_text_input' in row.keys() else ''};"
                f"{row['individual_text_advance'] if 'individual_text_advance' in row.keys() else ''};"
                f"{row['individual_text_input'] if 'individual_text_input' in row.keys() else ''};"
                f"{row['bank_employee_name'] if 'bank_employee_name' in row.keys() else ''};"
                f"{row['bank_employee_id'] if 'bank_employee_id' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_employment_periods(df: pd.DataFrame,
                                    use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                  DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE             DEID (values)
        pnr_betriebliche#psd            Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                         Personalnummer                  Employee ID                         employee_id
        eintrittdatum#psd               Eintrittsdatum                  Date in service                     date_in_service
        austrittdatum#psd               Austrittsdatum                  Date out of service                 date_out_of_service
        arbeitsverhaeltnis#psd          Arbeitsverhältnis               Employment relationship             employment_relationship     4574
        kuendigung_am#psd               Kündigung am                    Notification Date of Termination    notification_date_of_termination
        """

        required_fields = ['date_in_service', 'employment_relationship']
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"300;u_lod_psd_beschaeftigung;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};eintrittdatum#psd;austrittdatum#psd;arbeitsverhaeltnis#psd;kuendigung_am#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"300;"
                f"{row['employee_id']};"
                f"{row['date_in_service'] if 'date_in_service' in row.keys() else ''};"
                f"{row['date_out_of_service'] if 'date_out_of_service' in row.keys() else ''};"
                f"{row['employment_relationship'] if 'employment_relationship' in row.keys() else ''};"
                f"{row['notification_date_of_termination'] if 'notification_date_of_termination' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_employment(df: pd.DataFrame,
                            use_alternative_employee_number: bool = False):

        # u_lod_psd_taetigkeit
        """
        TECHNICAL NAME                  DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE             DEID (values)
        pnr_betriebliche#psd            Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                         Personalnummer                  Employee ID                         employee_id
        berufsbezeichnung#psd           Berufsbezeichnung               Job title                           job_title
        rv_beitragsgruppe#psd           Arbeitnehmertyp                 Employee type                       employee_type               4097
        persgrs#psd                     Personengruppe                  Employee group                      person_group                4209
        beschaeft_nr#psd                Beschäftigungsbetrieb           Employment company                  employment_company
        kst_abteilungs_nr#psd           Abteilung                       Department                          department                  4279
        stammkostenstelle#psd           Stammkostenstelle               Costcenter                          costcenter                  4739
        """

        required_fields = []
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"501;u_lod_psd_taetigkeit;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};berufsbezeichnung#psd;rv_beitragsgruppe#psd;persgrs#psd;beschaeft_nr#psd;kst_abteilungs_nr#psd;stammkostenstelle#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"501;"
                f"{row['employee_id']};"
                f"{row['job_title'] if 'job_title' in row.keys() else ''};"
                f"{row['employee_type'] if 'employee_type' in row.keys() else ''};"
                f"{row['person_group'] if 'person_group' in row.keys() else ''};"
                f"{row['employment_company'] if 'employment_company' in row.keys() else ''};"
                f"{row['department'] if 'department' in row.keys() else ''};"
                f"{row['costcenter'] if 'costcenter' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_employment_2(df: pd.DataFrame,
                              use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                  DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE             DEID (values)
        pnr_betriebliche#psd            Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                         Personalnummer                  Employee ID                         employee_id
        vorweg_abr_abruf_termin_kz#psd  Zuordnung zur Abrechnungsgruppe Assignment to payroll group         payroll_group               4127
        ersteintrittsdatum#psd          Ersteintrittsdatum              First date of service               date_in_service_historical
        verw_ersteintr_elena_bn#psd     Ersteintrittsdatum für AAG      First date of service for AAG       date_in_service_aag         440
        ma_gruppe#psd                   Zuordnung Mitarbeitergruppe     Assignment to employee group        employee_group              4406
        """

        required_fields = []
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"502;u_lod_psd_mitarbeiter;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};vorweg_abr_abruf_termin_kz#psd;ersteintrittsdatum#psd;verw_ersteintr_elena_bn#psd;ma_gruppe#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"502;"
                f"{row['employee_id']};"
                f"{row['payroll_group'] if 'payroll_group' in row.keys() else ''};"
                f"{row['date_in_service_historical'] if 'date_in_service_historical' in row.keys() else ''};"
                f"{row['date_in_service_aag'] if 'date_in_service_aag' in row.keys() else ''};"
                f"{row['employee_group'] if 'employee_group' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_employment_3(df: pd.DataFrame,
                              use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                  DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE             DEID (values)
        pnr_betriebliche#psd            Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                         Personalnummer                  Employee ID                         employee_id
        entlohnungsform#psd             Entlohnungsform                 Type of salary                      salary_type                 4609
        behind_kz#psd                   Behinderte Menschen             Disabled person indicator           disabled_person_indicator   4118
        """

        required_fields = []
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"503;u_lod_psd_besonderheiten;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};entlohnungsform#psd;behind_kz#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"503;"
                f"{row['employee_id']};"
                f"{row['salary_type'] if 'salary_type' in row.keys() else ''};"
                f"{row['disabled_person_indicator'] if 'disabled_person_indicator' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_employment_4(df: pd.DataFrame,
                              use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                  DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE                 DEID (values)
        pnr_betriebliche#psd            Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                         Personalnummer                  Employee ID                         employee_id
        eintrittdatum#psd               Eintrittsdatum                  Date in service                     date_in_service
        datum_urspr_befr#psd            Betristungsdatum bei Vertrags   Probation end date                  probation_end_date
        """

        required_fields = ['probation_end_date', 'date_in_service']
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"503;u_lod_psd_beschaeftigung;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};eintrittdatum#psd;datum_urspr_befr#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"503;"
                f"{row['employee_id']};"
                f"{row['date_in_service'] if 'date_in_service' in row.keys() else ''};"
                f"{row['probation_end_date'] if 'probation_end_date' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_formation_division(df: pd.DataFrame,
                                    use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                  DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE             DEID (values)
        pnr_betriebliche#psd            Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                         Personalnummer                  Employee ID                         employee_id
        kostenstelle#psd                Kostenstelle                    Costcenter                          costcenter_division
        prozentsatz_kst#psd             Prozentsatz                     Percentage                          percentage_division
        """

        required_fields = ['costcenter_division', 'percentage_division']
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"400;u_lod_psd_kstellen_verteil;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};kostenstelle#psd;prozentsatz_kst#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"400;"
                f"{row['employee_id']};"
                f"{row['costcenter_division'] if 'costcenter_division' in row.keys() else ''};"
                f"{row['percentage_division'] if 'percentage_division' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_activity_key(df: pd.DataFrame,
                              use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                  DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE             DEID (values)
        pnr_betriebliche#psd            Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                         Personalnummer                  Employee ID                         employee_id
        ausg_taetigkeit#psd             Ausgabe Tätigkeit               Output activity                     output_activity             4606  # TODO: create accepted value list for this
        schulabschluss#psd              Höchster Schulabschluss         School degree                       school_degree               4604
        ausbildungsabschluss#psd        Höchster Ausbildungsabschluss   Training degree                     training_degree             4601
        arbeitnehmerueberlassung#psd    Gewerb. Arbeinehmerüberlassung  Commercial employee transfer        commercial_transfer         4602
        vertragsform#psd                Vertragsform                    Contract form                       contract_form               4603
        """

        required_fields = ['output_activity', 'school_degree', 'training_degree', 'commercial_transfer', 'contract_form']

        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"500;u_lod_psd_taetigkeit;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};ausg_taetigkeit#psd;schulabschluss#psd;ausbildungsabschluss#psd;arbeitnehmerueberlassung#psd;vertragsform#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"500;"
                f"{row['employee_id']};"
                f"{row['output_activity'] if 'output_activity' in row.keys() else ''};"
                f"{row['school_degree'] if 'school_degree' in row.keys() else ''};"
                f"{row['training_degree'] if 'training_degree' in row.keys() else ''};"
                f"{row['commercial_transfer'] if 'commercial_transfer' in row.keys() else ''};"
                f"{row['contract_form'] if 'contract_form' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_tax(df: pd.DataFrame,
                     use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                  DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE                 DEID (values)
        pnr_betriebliche#psd            Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                         Personalnummer                  Employee ID                         employee_id
        st_klasse#psd                   Steuerklasse                    Tax class                           tax_class                       4202
        faktor#psd                      Faktor                          Factor                              factor                          4586 (0.001 - 0.999)
        kfb_anzahl#psd                  Kinderfreibeträge Anzahl        Number of child allowances          number_of_child_allowances      1337 (0 - 99.5)
        konf_an#psd                     Steuerpflichtiger               Religion                            religion                        4624
        konf_ehe#psd                    Ehegatte/Lebenspartner          Religion spouse                     religion_spouse                 4624
        identifikationsnummer#psd       Identifikationsnummer           Identification number               identification_number
        els_2_haupt_ag_kz#psd           Kennzeichnung Arbeitgeber       Employer identification             employer_identification         4630
        els_2_wunsch_freib_jhrl#psd     Gewünschte jhrl Freibeträge     Desired annual allowances           desired_annual_allowances
        pausch_einhtl_2#psd             Pauschalsteuer berechnen        Calculate flat tax                  calculate_flat_tax              4640
        pausch_an_kz#psd                Übernahme Pauschsteuer          Take over flat tax                  take_over_flat_tax              4346
        """

        required_fields = []
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"600;u_lod_psd_steuer;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};st_klasse#psd;faktor#psd;kfb_anzahl#psd;konf_an#psd;konf_ehe#psd;identifikationsnummer#psd;els_2_haupt_ag_kz#psd;els_2_wunsch_freib_jhrl#psd;pausch_einhtl_2#psd;pausch_an_kz#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"600;"
                f"{row['employee_id']};"
                f"{row['tax_class'] if 'tax_class' in row.keys() else ''};"
                f"{row['factor'] if 'factor' in row.keys() else ''};"
                f"{row['number_of_child_allowances'] if 'number_of_child_allowances' in row.keys() else ''};"
                f"{row['religion'] if 'religion' in row.keys() else ''};"
                f"{row['religion_spouse'] if 'religion_spouse' in row.keys() else ''};"
                f"{row['identification_number'] if 'identification_number' in row.keys() else ''};"
                f"{row['employer_identification'] if 'employer_identification' in row.keys() else ''};"
                f"{row['desired_annual_allowances'] if 'desired_annual_allowances' in row.keys() else ''};"
                f"{row['calculate_flat_tax'] if 'calculate_flat_tax' in row.keys() else ''};"
                f"{row['take_over_flat_tax'] if 'take_over_flat_tax' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_allowances(df: pd.DataFrame,
                            use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                      DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE             DEID (values)
        pnr_betriebliche#psd                Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                             Personalnummer                  Employee ID                         employee_id
        freibetrag_jhrl#psd                 Freibetrag Jahresbetrag         Annual allowance amount             annual_allowance_amount
        freibetrag_mtl#psd                  Freibetrag Monatsbetrag         Monthly allowance amount            monthly_allowance_amount
        hinzu_jahresbetrag#psd              Hinzurechnungsbeträge Jahr.     Annual additional amount            annual_additional_amount
        hinzu_monatsbetrag#psd              Hinzurechnungsbeträge Mon.      Monthly additional amount           monthly_additional_amount
        """

        required_fields = []
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"700;u_lod_psd_freibetrag;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};freibetrag_jhrl#psd;freibetrag_mtl#psd;hinzu_jahresbetrag#psd;hinzu_monatsbetrag#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"700;"
                f"{row['employee_id']};"
                f"{row['annual_allowance_amount'] if 'annual_allowance_amount' in row.keys() else ''};"
                f"{row['monthly_allowance_amount'] if 'monthly_allowance_amount' in row.keys() else ''};"
                f"{row['annual_additional_amount'] if 'annual_additional_amount' in row.keys() else ''};"
                f"{row['monthly_additional_amount'] if 'monthly_additional_amount' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_insurance_key(df: pd.DataFrame,
                               use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                      DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE             DEID (values)
        pnr_betriebliche#psd                Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                             Personalnummer                  Employee ID                         employee_id
        kv_bgrs#psd                         Krankenversicherung             Health insurance                    health_insurance            4689
        rv_bgrs#psd                         Rentenversicherung              Pension insurance                   pension_insurance           4687
        av_bgrs#psd                         Arbeitslosenversicherung        Unemployment insurance              unemployment_insurance      4688
        pv_bgrs#psd                         Pflegeversicherung              Nursing care insurance              nursing_care_insurance      4690
        """

        required_fields = ['health_insurance', 'pension_insurance', 'unemployment_insurance', 'nursing_care_insurance']
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"800;u_lod_psd_sozialversicherung;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};kv_bgrs#psd;rv_bgrs#psd;av_bgrs#psd;pv_bgrs#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"800;"
                f"{row['employee_id']};"
                f"{row['health_insurance'] if 'health_insurance' in row.keys() else ''};"
                f"{row['pension_insurance'] if 'pension_insurance' in row.keys() else ''};"
                f"{row['unemployment_insurance'] if 'unemployment_insurance' in row.keys() else ''};"
                f"{row['nursing_care_insurance'] if 'nursing_care_insurance' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_insurance(df: pd.DataFrame,
                           use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                      DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE             DEID (values)
        pnr_betriebliche#psd                Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                             Personalnummer                  Employee ID                         employee_id
        midijob_kz#psd                      Midijobregelung anwenden        Apply midijob regulation            apply_midijob_regulation    440
        kz_zuschl_pv_kinderlose#psd         Beitr. zur PV für Kinderlose    Contribution to PV for childless    contribution_pv_childless   440
        uml_schluessel#psd                  Umlageschlüssel                 Allocation key                      allocation_key              4095
        kk_nr#psd                           Gesetzliche Krankenversicherung Statutory health insurance          statutory_health_insurance  4061 (1 - 999)
        kk_nr_frw#psd                       Freiwillige Krankenversicherung Voluntary health insurance          voluntary_health_insurance  4061 (1 - 999)
        gv_gf_schluessel#psd                Geringverdiender Beschäftige    Low-wage employees                  low_wage_employees          4092
        kk_minijob_betrnr#psd               Betriebsnr. abweichende KK      Company number different KK         minijob_health_insurance    1234  #TODO find values for this
        kv_status_kurzfr#psd                Versicherungsstatus kurzfristig Insurance status short-term         insurance_status_short      4812
        """

        required_fields = []
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"801;u_lod_psd_sozialversicherung;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};midijob_kz#psd;kz_zuschl_pv_kinderlose#psd;uml_schluessel#psd;kk_nr#psd;kk_nr_frw#psd;gv_gf_schluessel#psd;kk_minijob_betrnr#psd;kv_status_kurzfr#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"801;"
                f"{row['employee_id']};"
                f"{row['apply_midijob_regulation'] if 'apply_midijob_regulation' in row.keys() else ''};"
                f"{row['contribution_pv_childless'] if 'contribution_pv_childless' in row.keys() else ''};"
                f"{row['allocation_key'] if 'allocation_key' in row.keys() else ''};"
                f"{row['statutory_health_insurance'] if 'statutory_health_insurance' in row.keys() else ''};"
                f"{row['voluntary_health_insurance'] if 'voluntary_health_insurance' in row.keys() else ''};"
                f"{row['low_wage_employees'] if 'low_wage_employees' in row.keys() else ''};"
                f"{row['minijob_health_insurance'] if 'minijob_health_insurance' in row.keys() else ''};"
                f"{row['insurance_status_short'] if 'insurance_status_short' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_private_insurance(df: pd.DataFrame,
                                   use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                      DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE             DEID (values)
        pnr_betriebliche#psd                Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                             Personalnummer                  Employee ID                         employee_id
        kv_priv_kz#psd                      Privat krankenversichert        Private health insurance            private_health_insurance    440
        pv_priv_kz#psd                      Privat pflegeversichert         Private nursing care insurance      private_nursing_care        440
        gesamtbeitrag_kv#psd                Mon. gesamtbeitrag private KV   Monthly total contribution health   monthly_contribution_health
        monatl_beitrant_basis_kv#psd        Monatlicher beitragsanteil KV   Monthly contribution share health   monthly_contribution_share
        gesamtbeitrag_pv#psd                Mon. gesamtbeitrag private PV   Monthly total contribution nursing  monthly_contribution_nursing
        """

        required_fields = []
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"900;u_lod_psd_priv_versicherung;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};kv_priv_kz#psd;pv_priv_kz#psd;gesamtbeitrag_kv#psd;monatl_beitrant_basis_kv#psd;gesamtbeitrag_pv#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"900;"
                f"{row['employee_id']};"
                f"{row['private_health_insurance'] if 'private_health_insurance' in row.keys() else ''};"
                f"{row['private_nursing_care'] if 'private_nursing_care' in row.keys() else ''};"
                f"{row['monthly_contribution_health'] if 'monthly_contribution_health' in row.keys() else ''};"
                f"{row['monthly_contribution_share'] if 'monthly_contribution_share' in row.keys() else ''};"
                f"{row['monthly_contribution_nursing'] if 'monthly_contribution_nursing' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_payroll(df: pd.DataFrame,
                         use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                      DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE             DEID (values)
        pnr_betriebliche#psd                Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                             Personalnummer                  Employee ID                         employee_id
        std_lohn_1#psd                      Stundenlohn 1                   Hourly wage 1                       hourly_wage_1
        std_lohn_2#psd                      Stundenlohn 2                   Hourly wage 2                       hourly_wage_2
        std_lohn_3#psd                      Stundenlohn 3                   Hourly wage 3                       hourly_wage_3
        lfd_brutto_vereinbart#psd           Laufender Bruttolohn vereinbart Agreed gross salary                 gross_salary
        """

        required_fields = ['hourly_wage_1', 'hourly_wage_2', 'hourly_wage_3', 'gross_salary']
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"1000;u_lod_psd_lohn_gehalt_bezuege;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};std_lohn_1#psd;std_lohn_2#psd;std_lohn_3#psd;lfd_brutto_vereinbart#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"1000;"
                f"{row['employee_id']};"
                f"{row['hourly_wage_1'] if 'hourly_wage_1' in row.keys() else ''};"
                f"{row['hourly_wage_2'] if 'hourly_wage_2' in row.keys() else ''};"
                f"{row['hourly_wage_3'] if 'hourly_wage_3' in row.keys() else ''};"
                f"{row['gross_salary'] if 'gross_salary' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_wage_components(df: pd.DataFrame,
                                 use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                      DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE             DEID (values)
        pnr_betriebliche#psd                Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                             Personalnummer                  Employee ID                         employee_id
        festbez_id#psd                      Festbezüge ID                   Sequence number                     sequence_number
        lohnart_nr#psd                      Lohnart                         Wage component                      wage_component              4178 (1 - 8999)
        betrag#psd                          Betrag                          Amount                              amount
        intervall#psd                       Intervall                       Interval                            interval                    4491
        gab#psd                             Gültig in den Monaten           Valid in the months                 valid_months                4495
        kuerzung#psd                        Kürzung                         Reduction                           reduction                   4679
        kz_monatslohn#psd                   Monatslohn                      Monthly salary                      monthly_salary              4552
        """

        required_fields = ['sequence_number', 'wage_component', 'amount']
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"1100;u_lod_psd_festbezuege;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};festbez_id#psd;lohnart_nr#psd;betrag#psd;intervall#psd;gab#psd;kuerzung#psd;kz_monatslohn#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"1100;"
                f"{row['employee_id']};"
                f"{row['sequence_number'] if 'sequence_number' in row.keys() else ''};"
                f"{row['wage_component'] if 'wage_component' in row.keys() else ''};"
                f"{row['amount'] if 'amount' in row.keys() else ''};"
                f"{row['interval'] if 'interval' in row.keys() else ''};"
                f"{row['valid_months'] if 'valid_months' in row.keys() else ''};"
                f"{row['reduction'] if 'reduction' in row.keys() else ''};"
                f"{row['monthly_salary'] if 'monthly_salary' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_schedule(df: pd.DataFrame,
                          use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                      DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE             DEID (values)
        pnr_betriebliche#psd                Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                             Personalnummer                  Employee ID                         employee_id
        az_wtl_indiv#psd                    Individuelle Wochenarbeitszeit  Individual weekly working hours     hours_per_week
        regelm_az_mo#psd                    Montag                          Monday                              hours_monday
        regelm_az_di#psd                    Dienstag                        Tuesday                             hours_tuesday
        regelm_az_mi#psd                    Mittwoch                        Wednesday                           hours_wednesday
        regelm_az_do#psd                    Donnerstag                      Thursday                            hours_thursday
        regelm_az_fr#psd                    Freitag                         Friday                              hours_friday
        regelm_az_sa#psd                    Samstag                         Saturday                            hours_saturday
        regelm_az_so#psd                    Sonntag                         Sunday                              hours_sunday
        """

        required_fields = ['hours_per_week', 'hours_monday', 'hours_tuesday', 'hours_wednesday', 'hours_thursday', 'hours_friday', 'hours_saturday', 'hours_sunday']
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"1200;u_lod_psd_arbeitszeit_regelm;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};az_wtl_indiv#psd;regelm_az_mo#psd;regelm_az_di#psd;regelm_az_mi#psd;regelm_az_do#psd;regelm_az_fr#psd;regelm_az_sa#psd;regelm_az_so#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"1200;"
                f"{row['employee_id']};"
                f"{row['hours_per_week'] if 'hours_per_week' in row.keys() else ''};"
                f"{row['hours_monday'] if 'hours_monday' in row.keys() else ''};"
                f"{row['hours_tuesday'] if 'hours_tuesday' in row.keys() else ''};"
                f"{row['hours_wednesday'] if 'hours_wednesday' in row.keys() else ''};"
                f"{row['hours_thursday'] if 'hours_thursday' in row.keys() else ''};"
                f"{row['hours_friday'] if 'hours_friday' in row.keys() else ''};"
                f"{row['hours_saturday'] if 'hours_saturday' in row.keys() else ''};"
                f"{row['hours_sunday'] if 'hours_sunday' in row.keys() else ''};\n"
            )

            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_declarations(df: pd.DataFrame,
                              use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME              DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE        DEID (values)
        pnr_betriebliche#bwd        Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#bwd                     Personalnummer                  Employee ID                         employee_id
        abrechnung_zeitraum#bwd     Abrechnungszeitraum             Payroll period                      booking_date
        bs_wert_butab#bwd           Wert                            Value (euro with two decimals)      value
        bs_nr#bwd                   Bearbeitungsschlüssel           Declaration type (picklist)         declaration_type        4269
        kostenstellen#bwd           Kostenstelle                    Costcenter                          costcenter
        eigene_la#bwd               Lohnart                         Wage component                      wage_component          4553
        abw_lohnfaktor#bwd          Abweicherender Lohnfaktor       Deviating wage factor               wage_factor
        """

        required_fields = ['employee_id', 'booking_date', 'value', 'declaration_type', 'wage_component']
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"309;u_lod_bwd_buchung_standard;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#bwd'};abrechnung_zeitraum#bwd;bs_wert_butab#bwd;bs_nr#bwd;kostenstelle#bwd;la_eigene#bwd;abw_lohnfaktor#bwd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"309;"
                f"{row['employee_id']};"
                f"{row['booking_date'] if 'booking_date' in row.keys() else ''};"
                f"{row['value'] if 'value' in row.keys() else ''};"
                f"{row['declaration_type'] if 'declaration_type' in row.keys() else ''};"
                f"{row['costcenter'] if 'costcenter' in row.keys() else ''};"
                f"{row['wage_component'] if 'wage_component' in row.keys() else ''};"
                f"{row['wage_factor'] if 'wage_factor' in row.keys() else ''};\n"
            )
            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def postcalculation(df: pd.DataFrame,
                        use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME              DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE        DEID (values)
        pnr_betriebliche#bwd        Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#bwd                     Personalnummer                  Employee ID                         employee_id
        abrechnung_zeitraum#bwd     Abrechnungszeitraum             Payroll period                      payroll_period
        nb_datum_mm#bwd             Nachberechnungsdatei            booking_date                        booking_date
        bs_wert_butab#bwd           Wert                            Value (euro with two decimals)      value
        bs_nr#bwd                   Bearbeitungsschlüssel           Declaration type (picklist)         declaration_type        4269
        kostenstellen#bwd           Kostenstelle                    Costcenter                          costcenter
        la_eigene#bwd               Lohnart                         Wage component                      wage_component          4553
        abw_lohnfaktor#bwd          Abweicherender Lohnfaktor       Deviating wage factor               wage_factor
        """

        required_fields = ['employee_id', 'booking_date', 'value', 'declaration_type', 'wage_component']
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"310;u_lod_bwd_buchung_nachber;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#bwd'};abrechnung_zeitraum#bwd;nb_datum_mm#bwd;bs_wert_butab#bwd;bs_nr#bwd;kostenstelle#bwd;la_eigene#bwd;abw_lohnfaktor#bwd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"310;"
                f"{row['employee_id']};"
                f"{row['payroll_period'] if 'payroll_period' in row.keys() else ''};"
                f"{row['booking_date'] if 'booking_date' in row.keys() else ''};"
                f"{row['value'] if 'value' in row.keys() else ''};"
                f"{row['declaration_type'] if 'declaration_type' in row.keys() else ''};"
                f"{row['costcenter'] if 'costcenter' in row.keys() else ''};"
                f"{row['wage_component'] if 'wage_component' in row.keys() else ''};"
                f"{row['wage_factor'] if 'wage_factor' in row.keys() else ''};\n"
            )
            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_vwl(df: pd.DataFrame,
                     use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME              DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE        DEID (values)
        pnr_betriebliche#psd        Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                     Personalnummer                  Employee ID                         employee_id
        vwl_1_netto_abz_1#psd       vermögungsbildung               Savings formation                   vwl_saving_formation
        vwl_ag_anteil_la_1#psd      Arbeitgeberanteil               Employer contribution               vwl_wage_component      4178
        vwl_ag_anteil_betrag_1#psd  Betrag                          Amount                              vwl_amount
        lastschrift1_kz#psd         Lastschrift                     Direct debit                        vwl_direct_debit        440
        """

        required_fields = []
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"1300;u_lod_psd_vermoegensbildung;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};vwl_1_netto_abz_1#psd;vwl_ag_anteil_la_1#psd;vwl_ag_anteil_betrag_1#psd;lastschrift1_kz#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"1300;"
                f"{row['employee_id']};"
                f"{row['vwl_saving_formation'] if 'vwl_saving_formation' in row.keys() else ''};"
                f"{row['vwl_wage_component'] if 'vwl_wage_component' in row.keys() else ''};"
                f"{row['vwl_amount'] if 'vwl_amount' in row.keys() else ''};"
                f"{row['vwl_direct_debit'] if 'vwl_direct_debit' in row.keys() else ''};\n"
            )
            body.append(formatted_string)

        return template_description, body

    @staticmethod
    def employee_vwl_bank(df: pd.DataFrame,
                          use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME              DESCRIPTION Lodas               DESCRIPTION English                 INTERFACE VALUE        DEID (values)
        pnr_betriebliche#psd        Betriebliche Personalnummer     Alternative employee ID             employee_id
        pnr#psd                     Personalnummer                  Employee ID                         employee_id
        vwl_1_iban#psd              IBAN                            IBAN                                vwl_iban
        vwl_1_bic#psd               BIC                             BIC                                 vwl_bic
        vwl_institut_1#psd          Institut                        Institute                           vwl_institute
        vwl_vertrag_nr_1#psd        Vertragsnummer                  Contract number                     vwl_contract_number
        vwl_1_vertragsart#psd       Vertragsart                     Contract type                       vwl_contract_type
        vwl_1_beginn_mmjj#psd       Beginn                          Start date                          vwl_start_date
        vwl_1_ende_mmjj#psd         Ende                            End date                            vwl_end_date
        """

        required_fields = []
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"1400;u_lod_psd_vermoegensbildung_bank;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};vwl_1_iban#psd;vwl_1_bic#psd;vwl_institut_1#psd;vwl_vertrag_nr_1#psd;vwl_1_vertragsart#psd;vwl_1_beginn_mmjj#psd;vwl_1_ende_mmjj#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"1400;"
                f"{row['employee_id']};"
                f"{row['vwl_iban'] if 'vwl_iban' in row.keys() else ''};"
                f"{row['vwl_bic'] if 'vwl_bic' in row.keys() else ''};"
                f"{row['vwl_institute'] if 'vwl_institute' in row.keys() else ''};"
                f"{row['vwl_contract_number'] if 'vwl_contract_number' in row.keys() else ''};"
                f"{row['vwl_contract_type'] if 'vwl_contract_type' in row.keys() else ''};"
                f"{row['vwl_start_date'] if 'vwl_start_date' in row.keys() else ''};"
                f"{row['vwl_end_date'] if 'vwl_end_date' in row.keys() else ''};\n"
            )
            body.append(formatted_string)

        return template_description, body


    @staticmethod
    def employee_absence(df: pd.DataFrame,
                         use_alternative_employee_number: bool = False):
        """
        TECHNICAL NAME                      DESCRIPTION Lodas                       DESCRIPTION English                     INTERFACE VALUE                     DEID (values)
        pnr_betriebliche#psd                Betriebliche Personalnummer             Alternative employee ID                 employee_id
        pnr#psd                             Personalnummer                          Employee number                         employee_id
        datum_von_ttmmjjjj#psd              Fehlzeit von Datum                      Absence start date                      absence_start_date
        datum_bis_ttmmjjjj#psd              Fehlzeit bis Datum                      Absence end date                        absence_end_date
        grund_fehlzeiten#psd                Fehlzeitengrund                         Absence reason code                     absence_reason_code                 4323
        kinderanzahl#psd                    Kinderanzahl                            Number of children                      number_of_children
        kinderpfl_verletztengeld#psd        Kinderpflege-Verletztengeld             Child-care injury benefit flag          childcare_injury_benefit            440
        kz_am_ersten_tag_gearb#psd          Am ersten Tag gearbeitet                Worked on first sick day                worked_first_day                    440
        letzter_arb_tag_am#psd              Letzter Arbeitstag am                   Last working day                        last_working_day
        letzter_bez_tag_vor_geburt#psd      Letzter Bezahlungstag vor Geburt        Last payment day before child-birth     last_payment_day_before_birth
        regel_arbeitszeit#psd               Regelarbeitszeit                        Contractual weekly working hours        contractual_weekly_hours
        arbeitsunfaehig_ab#psd              Arbeitsunfähig seit                     Unable to work since                    unable_to_work_since
        au_relevant_kz#psd                  für AU Abfrage relevant                 AU Relevant                             au_relevant                         440
        bemerkung#psd                       Bemerkung                               Comment / note                          comment
        """

        required_fields = ['employee_id', 'absence_start_date', 'absence_end_date', 'absence_reason_code']
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f'Column {field} is required. Required columns are: {tuple(required_fields)}')

        template_description = [f"1400;u_lod_psd_fehlzeiten;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};datum_von_ttmmjjjj#psd;datum_bis_ttmmjjjj#psd;grund_fehlzeiten#psd;kinderanzahl#psd;kinderpfl_verletztengeld#psd;kz_am_ersten_tag_gearb#psd;letzter_arb_tag_am#psd;letzter_bez_tag_vor_geburt#psd;regel_arbeitszeit#psd;arbeitsunfaehig_ab#psd;bemerkung#psd;\n"]

        body = []
        for _, row in df.iterrows():
            formatted_string = (
                f"1400;"
                f"{row['employee_id']};"
                f"{row['absence_start_date'] if 'absence_start_date' in row.keys() else ''};"
                f"{row['absence_end_date'] if 'absence_end_date' in row.keys() else ''};"
                f"{row['absence_reason_code'] if 'absence_reason_code' in row.keys() else ''};"
                f"{row['number_of_children'] if 'number_of_children' in row.keys() else ''};"
                f"{row['childcare_injury_benefit'] if 'childcare_injury_benefit' in row.keys() else ''};"
                f"{row['worked_first_day'] if 'worked_first_day' in row.keys() else ''};"
                f"{row['last_working_day'] if 'last_working_day' in row.keys() else ''};"
                f"{row['last_payment_day_before_birth'] if 'last_payment_day_before_birth' in row.keys() else ''};"
                f"{row['contractual_weekly_hours'] if 'contractual_weekly_hours' in row.keys() else ''};"
                f"{row['unable_to_work_since'] if 'unable_to_work_since' in row.keys() else ''};"
                f"{row['comment'] if 'comment' in row.keys() else ''};\n"
            )
            body.append(formatted_string)

        return template_description, body


# Test employee with all fields
# datev = DatevLodas(mandanten_nr=10000, berater_nr=968570)
# dataframe = pd.DataFrame([{
#     'employee_id': 100,
#     'lastname': 'Mustermann',
#     'firstname': 'Max',
#     'academic_title': 'Dr.',
#     'name_addition': 'Baron',
#     'prefix': 'zu',
#     'birthname': 'Musterfrau',
#     'name_addition_birthname': 'BARONESS',
#     'prefix_birthname': 'zu',
#     'street': 'Musterstrasse',
#     'housenumber': '1',
#     'supplement': 'A',
#     'country': '0',
#     'postalcode': '12345',
#     'city': 'Musterstadt',
#     'email': 'test@gmail.com',
#     'phone_number': '0123456789',
#     'fax_number': '0123456789',
#     'date_of_birth': '01.01.1990',
#     'place_of_birth': 'Musterstadt',
#     'country_of_birth': '000',
#     'gender': '0',
#     'insurance_number': '1975010190',
#     'european_insurance_number': '1975010190',
#     'married': '1',
#     'single_parent': '0',
#     'nationality': '000',
#     'work_permit': '01.01.2024',
#     'residence_permit': '01.01.2024',
#     'study_certificate': '01.01.2024',
#     'disabled': '0',
#     'payment_method': '5',
#     'settle_overpayments': '1',
#     'iban': 'DE12345678901234567890',
#     'bic': 'ABCDEFGH',
#     'account_holder': 'Max Mustermann',
#     'bank_postalcode': '12345',
#     'bank_city': 'Musterstadt',
#     'individual_payment_reference': '1',
#     'individual_text_payroll': '1',
#     'individual_text_input': '1',
#     'individual_text_advance': '1',
#     'bank_employee_name': '1',
#     'bank_employee_id': '1',
#     'date_in_service': '01.01.2020',
#     'date_out_of_service': '01.01.2025',
#     'employment_relationship': '0',
#     'job_title': 'World leader',
#     'employee_type': '0',
#     'person_group': '140',
#     'employment_company': '',  # TODO: create value for this in Datev
#     'department': '1',
#     'costcenter': '1',
#     'payroll_group': '1',
#     'date_in_service_historical': '01.01.2020',
#     'date_in_service_aag': '1',
#     'probation_end_date': '01.03.2020',
#     'employee_group': 'Standard',
#     'costcenter_division': '1',
#     'percentage_division': '100',
#     'output_activity': '23224',
#     'school_degree': '1',
#     'training_degree': '1',
#     'commercial_transfer': '1',
#     'contract_form': '1',
#     'tax_class': '2',
#     'factor': '0,5',
#     'number_of_child_allowances': '1',
#     'religion': '1',
#     'religion_spouse': '1',
#     'identification_number': '12345678901',
#     'employer_identification': '1',
#     'desired_annual_allowances': '100',
#     'calculate_flat_tax': '1',
#     'take_over_flat_tax': '1',
#     'annual_allowance_amount': '10000',
#     'monthly_allowance_amount': '1000',
#     'annual_additional_amount': '20000',
#     'monthly_additional_amount': '2000',
#     'health_insurance': '1',
#     'pension_insurance': '1',
#     'unemployment_insurance': '1',
#     'nursing_care_insurance': '1',
#     'apply_midijob_regulation': '1',
#     'contribution_pv_childless': '1',
#     'allocation_key': '1',
#     'statutory_health_insurance': '123456789',
#     'voluntary_health_insurance': '123456789',
#     'low_wage_employees': '1',
#     'minijob_health_insurance': '123456789',
#     'insurance_status_short': '1',
#     'private_health_insurance': '1',
#     'private_nursing_care': '1',
#     'monthly_contribution_health': '10000',
#     'monthly_contribution_share': '20000',
#     'monthly_contribution_nursing': '30000',
#     'hourly_wage_1': '1000',
#     'hourly_wage_2': '2000',
#     'hourly_wage_3': '3000',
#     'gross_salary': '4000',
#     'sequence_number': '99',
#     'wage_component': '1',  # check
#     'amount': '1000',
#     'interval': '1',
#     'valid_months': '1',
#     'reduction': '1',
#     'monthly_salary': '1',
#     'hours_per_week': '40',
#     'hours_monday': '8',
#     'hours_tuesday': '8',
#     'hours_wednesday': '8',
#     'hours_thursday': '8',
#     'hours_friday': '8',
#     'hours_saturday': '0',
#     'hours_sunday': '0',
#     'vwl_saving_formation': '1',
#     'vwl_wage_component': '1',
#     'vwl_amount': '100',
#     'vwl_direct_debit': '1',
#     'change_type': 'edited',
#     'changed_fields': ['vwl_wage_component']
# }])
# datev.full_export(filepath='data_analytics', filename='test.txt', valid_from='01.01.2024', comparison_data=True, use_alternative_employee_number=True, df=dataframe)
