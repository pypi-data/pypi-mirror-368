from redcaplite import api
from .http import Client
from typing import List, Optional, Dict, Any, Union, Literal
from datetime import datetime
import pandas as pd


RedcapDataType = List[Dict[str, Any]]


class RedcapClient(Client):
    """
    A client for interacting with the REDCap API.
    """

    def __init__(self, url: str, token: str):
        """
        Initialize the RedcapClient.

        Args:
            url (str): The URL of the REDCap API.
            token (str): The API token for authentication.
        """
        super().__init__(url, token)

    # arms
    def get_arms(self, arms: List[int] = []):
        """
        Get arm information from the project.

        Args:
            arms (List[int], optional): List of arm numbers to fetch. Defaults to an empty list (all arms).

        Returns:
            The response from the API containing arm information.
        """
        return self.post(api.get_arms({"arms": arms}))

    def import_arms(
        self, data: RedcapDataType, override: Optional[Literal[0, 1]] = None
    ):
        """
        Import arms into the project.

        Args:
            data (RedcapDataType): The arm data to import.
            override (Optional[Literal[0, 1]]): Whether to override existing arms.

        Returns:
            The response from the API after importing arms.
        """
        return self.post(api.import_arms({"data": data, "override": override}))

    def delete_arms(self, arms: List[int]):
        """
        Delete arms from the project.

        Args:
            arms (List[int]): List of arm numbers to delete.

        Returns:
            The response from the API after deleting arms.
        """
        return self.post(api.delete_arms({"arms": arms}))

    # dags
    def get_dags(self):
        """
        Get all Data Access Groups (DAGs) for the project.

        Returns:
            The response from the API containing DAG information.
        """
        return self.post(api.get_dags({}))

    def import_dags(self, data: RedcapDataType):
        """
        Import Data Access Groups (DAGs) into the project.

        Args:
            data (RedcapDataType): The DAG data to import.

        Returns:
            The response from the API after importing DAGs.
        """
        return self.post(api.import_dags({"data": data}))

    def delete_dags(self, dags: List[str]):
        """
        Delete Data Access Groups (DAGs) from the project.

        Args:
            dags (List[str]): List of DAG unique names to delete.

        Returns:
            The response from the API after deleting DAGs.
        """
        return self.post(api.delete_dags({"dags": dags}))

    def switch_dag(self, dag: str):
        """
        Switch to a different Data Access Group (DAG).

        Args:
            dag (str): The unique name of the DAG to switch to.

        Returns:
            The response from the API after switching DAGs.
        """
        return self.post(api.switch_dag({"dag": dag}))

    # user_dag_mapping
    def get_user_dag_mappings(self):
        """
        Get the user-DAG mappings for the project.

        Returns:
            The response from the API containing user-DAG mapping information.
        """
        return self.post(api.get_user_dag_mappings({}))

    def import_user_dag_mappings(self, data: RedcapDataType):
        """
        Import user-DAG mappings into the project.

        Args:
            data (RedcapDataType): The user-DAG mapping data to import.

        Returns:
            The response from the API after importing user-DAG mappings.
        """
        return self.post(api.import_user_dag_mappings({"data": data}))

    # events
    def get_events(self, arms: List[int] = []):
        """
        Get events for the specified arms.

        Args:
            arms (List[int], optional): List of arm numbers to fetch events for. Defaults to an empty list (all arms).

        Returns:
            The response from the API containing event information.
        """
        return self.post(api.get_events({"arms": arms}))

    def import_events(self, data: RedcapDataType):
        """
        Import events into the project.

        Args:
            data (RedcapDataType): The event data to import.

        Returns:
            The response from the API after importing events.
        """
        return self.post(api.import_events({"data": data}))

    def delete_events(self, events: List[str]):
        """
        Delete events from the project.

        Args:
            events (List[str]): List of event unique names to delete.

        Returns:
            The response from the API after deleting events.
        """
        return self.post(api.delete_events({"events": events}))

    # field_names
    def get_field_names(self, field: Optional[str] = None):
        """
        Get a list of the project's field names.

        Args:
            field (Optional[str]): A specific field name to return information about.

        Returns:
            The response from the API containing field name information.
        """
        return self.post(api.get_field_names({"field": field}))

    # file
    def get_file(
        self,
        record: str,
        field: str,
        event: Optional[str] = None,
        repeat_instance: Optional[int] = None,
        file_dictionary: str = "",
    ):
        """
        Download a file from a File Upload field.

        Args:
            record (str): The record ID.
            field (str): The name of the field containing the file.
            event (Optional[str]): The unique event name.
            repeat_instance (Optional[int]): The repeat instance number.
            file_dictionary (str): The directory to save the file to.

        Returns:
            The response from the API containing the file data.
        """
        return self.file_download_api(
            api.get_file(
                {
                    "record": record,
                    "field": field,
                    "event": event,
                    "repeat_instance": repeat_instance,
                }
            ),
            file_dictionary=file_dictionary,
        )

    def import_file(
        self,
        file_path: str,
        record: str,
        field: str,
        event: Optional[str] = None,
        repeat_instance: Optional[int] = None,
    ):
        """
        Upload a file to a File Upload field.

        Args:
            file_path (str): The path to the file to upload.
            record (str): The record ID.
            field (str): The name of the field to upload the file to.
            event (Optional[str]): The unique event name.
            repeat_instance (Optional[int]): The repeat instance number.

        Returns:
            The response from the API after uploading the file.
        """
        return self.file_upload_api(
            file_path,
            api.import_file(
                {
                    "record": record,
                    "field": field,
                    "event": event,
                    "repeat_instance": repeat_instance,
                }
            ),
        )

    def delete_file(
        self,
        record: str,
        field: str,
        event: Optional[str] = None,
        repeat_instance: Optional[int] = None,
    ):
        """
        Delete a file from a File Upload field.

        Args:
            record (str): The record ID.
            field (str): The name of the field containing the file to delete.
            event (Optional[str]): The unique event name.
            repeat_instance (Optional[int]): The repeat instance number.

        Returns:
            The response from the API after deleting the file.
        """
        return self.post(
            api.delete_file(
                {
                    "record": record,
                    "field": field,
                    "event": event,
                    "repeat_instance": repeat_instance,
                }
            )
        )

    # file_repository
    def create_folder_file_repository(
        self,
        name: str,
        folder_id: Optional[int] = None,
        dag_id: Optional[int] = None,
        role_id: Optional[int] = None,
    ):
        """
        Create a new folder in the File Repository.

        Args:
            name (str): The name of the new folder.
            folder_id (Optional[int]): The parent folder ID.
            dag_id (Optional[int]): The DAG ID to associate the folder with.
            role_id (Optional[int]): The role ID to associate the folder with.

        Returns:
            The response from the API after creating the folder.
        """
        return self.post(
            api.create_folder_file_repository(
                {
                    "name": name,
                    "folder_id": folder_id,
                    "dag_id": dag_id,
                    "role_id": role_id,
                }
            )
        )

    def list_file_repository(self, folder_id: Optional[int] = None):
        """
        List files and folders in the File Repository.

        Args:
            folder_id (Optional[int]): The ID of the folder to list contents from.

        Returns:
            The response from the API containing the file repository listing.
        """
        return self.post(api.list_file_repository({"folder_id": folder_id}))

    def export_file_repository(self, doc_id: int, file_dictionary: str = ""):
        """
        Export a file from the File Repository.

        Args:
            doc_id (int): The document ID of the file to export.
            file_dictionary (str): The directory to save the file to.

        Returns:
            The response from the API containing the file data.
        """
        return self.file_download_api(
            api.export_file_repository({"doc_id": doc_id}),
            file_dictionary=file_dictionary,
        )

    def import_file_repository(self, file_path: str,
                               folder_id: Optional[int] = None):
        """
        Import a file into the File Repository.

        Args:
            file_path (str): The path to the file to import.
            folder_id (Optional[int]): The ID of the folder to import the file into.

        Returns:
            The response from the API after importing the file.
        """
        return self.file_upload_api(
            file_path, api.import_file_repository({"folder_id": folder_id})
        )

    def delete_file_repository(self, doc_id: int):
        """
        Delete a file from the File Repository.

        Args:
            doc_id (int): The document ID of the file to delete.

        Returns:
            The response from the API after deleting the file.
        """
        return self.post(api.delete_file_repository({"doc_id": doc_id}))

    # instrument
    def get_instruments(self):
        """
        Get a list of the project's instruments (data collection instruments).

        Returns:
            The response from the API containing instrument information.
        """
        return self.post(api.get_instruments({}))

    # pdf
    def export_pdf(
        self,
        record: Optional[str] = None,
        event: Optional[str] = None,
        instrument: Optional[str] = None,
        repeat_instance: Optional[int] = None,
        allRecords: Optional[bool] = None,
        compactDisplay: Optional[bool] = None,
        file_dictionary: str = "",
    ):
        """
        Export a PDF file of data collection instruments.

        Args:
            record (Optional[str]): The record ID.
            event (Optional[str]): The unique event name.
            instrument (Optional[str]): The unique instrument name.
            repeat_instance (Optional[int]): The repeat instance number.
            allRecords (Optional[bool]): Whether to export all records.
            compactDisplay (Optional[bool]): Whether to use compact display.
            file_dictionary (str): The directory to save the PDF file to.

        Returns:
            The response from the API containing the PDF file data.
        """
        return self.file_download_api(
            api.export_pdf(
                {
                    "record": record,
                    "event": event,
                    "instrument": instrument,
                    "repeat_instance": repeat_instance,
                    "allRecords": allRecords,
                    "compactDisplay": compactDisplay,
                }
            ),
            file_dictionary=file_dictionary,
        )

    # form_event_mapping
    def get_form_event_mappings(self, arms: List[int] = []):
        """
        Get form-event mappings for the specified arms.

        Args:
            arms (List[int], optional): List of arm numbers to fetch mappings for. Defaults to an empty list (all arms).

        Returns:
            The response from the API containing form-event mapping information.
        """
        return self.post(api.get_form_event_mappings({"arms": arms}))

    def import_form_event_mappings(self, data: RedcapDataType):
        """
        Import form-event mappings into the project.

        Args:
            data (RedcapDataType): The form-event mapping data to import.

        Returns:
            The response from the API after importing form-event mappings.
        """
        return self.post(api.import_form_event_mappings({"data": data}))

    # log
    def get_logs(
        self,
        format: Literal["json", "csv"] = "csv",
        logtype: Optional[
            Literal[
                "export",
                "manage",
                "user",
                "record",
                "record_add",
                "record_edit",
                "record_delete",
                "lock_record",
                "page_view",
            ]
        ] = None,
        user: Optional[str] = None,
        record: Optional[str] = None,
        dag: Optional[str] = None,
        beginTime: Optional[datetime] = None,
        endTime: Optional[datetime] = None,
        pd_read_csv_kwargs: Optional[Dict[str, Any]] = {},
    ):
        """
        Export logs from the project.

        Args:
            format (Literal["json", "csv"]): The format of the exported data.
            logtype (Optional[Literal]): The type of log to export.
            user (Optional[str]): Filter logs by username.
            record (Optional[str]): Filter logs by record ID.
            dag (Optional[str]): Filter logs by Data Access Group.
            beginTime (Optional[datetime]): Filter logs by start time.
            endTime (Optional[datetime]): Filter logs by end time.
            pd_read_csv_kwargs (Optional[Dict[str, Any]]): Additional keyword arguments to pass to pandas' `read_csv` function when format is 'csv'. Defaults to {}.

        Returns:
            The response from the API containing the log data.
        """
        return self.post(
            api.get_logs(
                {
                    "format": format,
                    "logtype": logtype,
                    "user": user,
                    "record": record,
                    "dag": dag,
                    "beginTime": beginTime,
                    "endTime": endTime,
                }
            ),
            pd_read_csv_kwargs=pd_read_csv_kwargs,
        )

    # metadata
    def get_metadata(
        self,
        fields: List[str] = [],
        forms: List[str] = [],
        format: Literal["json", "csv"] = "csv",
        pd_read_csv_kwargs: Optional[Dict[str, Any]] = {},
    ):
        """
        Export metadata (data dictionary) from the project.

        Args:
            fields (List[str]): Specific fields to export metadata for.
            forms (List[str]): Specific forms to export metadata for.
            format (Literal["json", "csv"]): The format of the exported data.
            pd_read_csv_kwargs (Optional[Dict[str, Any]]): Additional keyword arguments to pass to pandas' `read_csv` function when format is 'csv'. Defaults to {}.

        Returns:
            The response from the API containing the metadata.
        """
        return self.post(
            api.get_metadata(
                {"fields": fields, "forms": forms, "format": format}),
            pd_read_csv_kwargs=pd_read_csv_kwargs,
        )

    def import_metadata(
        self,
        data: Union[pd.DataFrame, List[Dict[str, Any]], str],
        format: Literal["json", "csv"] = "csv",
    ):
        """
        Import metadata (data dictionary) into the project.

        Args:
            data (Union[pd.DataFrame, List[Dict[str, Any]], str]): The metadata to import.
            format (Literal["json", "csv"]): The format of the imported data.

        Returns:
            The response from the API after importing the metadata.
        """
        return self.post(api.import_metadata({"data": data, "format": format}))

    # project
    def create_project(self, data: RedcapDataType):
        """
        Create a new REDCap project.

        Args:
            data (RedcapDataType): The project settings and metadata.

        Returns:
            The response from the API after creating the project.
        """
        return self.post(api.create_project({"data": data}))

    def get_project(self):
        """
        Export project information.

        Returns:
            The response from the API containing project information.
        """
        return self.post(api.get_project({}))

    def get_project_xml(
        self,
        returnMetadataOnly: bool = False,
        records: List[str] = [],
        fields: List[str] = [],
        events: List[str] = [],
        exportSurveyFields: bool = False,
        exportDataAccessGroups: bool = False,
        filterLogic: Optional[str] = None,
        exportFiles: bool = False,
    ):
        """
        Export the entire project as an XML file.

        Args:
            returnMetadataOnly (bool): Whether to return only metadata.
            records (List[str]): Specific records to export.
            fields (List[str]): Specific fields to export.
            events (List[str]): Specific events to export.
            exportSurveyFields (bool): Whether to export survey fields.
            exportDataAccessGroups (bool): Whether to export Data Access Groups.
            filterLogic (Optional[str]): Logic to filter the data.
            exportFiles (bool): Whether to export files.

        Returns:
            The response from the API containing the project XML.
        """
        return self.post(
            api.get_project_xml(
                {
                    "returnMetadataOnly": returnMetadataOnly,
                    "records": records,
                    "fields": fields,
                    "events": events,
                    "exportSurveyFields": exportSurveyFields,
                    "exportDataAccessGroups": exportDataAccessGroups,
                    "filterLogic": filterLogic,
                    "exportFiles": exportFiles,
                }
            )
        )

    def import_project_settings(self, data: RedcapDataType):
        """
        Import project settings.

        Args:
            data (RedcapDataType): The project settings to import.

        Returns:
            The response from the API after importing project settings.
        """
        return self.post(api.import_project_settings({"data": data}))

    # record
    def export_records(
        self,
        format: Literal["json", "csv"] = "csv",
        records: List[str] = [],
        fields: List[str] = [],
        forms: List[str] = [],
        events: List[str] = [],
        rawOrLabel: Literal["raw", "label"] = "raw",
        rawOrLabelHeaders: Optional[Literal["raw", "label"]] = None,
        exportCheckboxLabel: Optional[bool] = None,
        exportSurveyFields: Optional[bool] = None,
        exportDataAccessGroups: Optional[bool] = None,
        filterLogic: Optional[str] = None,
        dateRangeBegin: Optional[datetime] = None,
        dateRangeEnd: Optional[datetime] = None,
        csvDelimiter: Optional[str] = None,
        decimalCharacter: Optional[str] = None,
        exportBlankForGrayFormStatus: Optional[bool] = None,
        pd_read_csv_kwargs: Optional[Dict[str, Any]] = {},
    ):
        """
        Export records from the project.

        Args:
            format (Literal["json", "csv"]): The format of the exported data.
            records (List[str]): Specific records to export.
            fields (List[str]): Specific fields to export.
            forms (List[str]): Specific forms to export.
            events (List[str]): Specific events to export.
            rawOrLabel (Literal["raw", "label"]): Export raw or label values.
            rawOrLabelHeaders (Optional[Literal["raw", "label"]]): Export raw or label headers.
            exportCheckboxLabel (Optional[bool]): Whether to export checkbox labels.
            exportSurveyFields (Optional[bool]): Whether to export survey fields.
            exportDataAccessGroups (Optional[bool]): Whether to export Data Access Groups.
            filterLogic (Optional[str]): Logic to filter the data.
            dateRangeBegin (Optional[datetime]): Start date for filtering.
            dateRangeEnd (Optional[datetime]): End date for filtering.
            csvDelimiter (Optional[str]): Delimiter for CSV export.
            decimalCharacter (Optional[str]): Decimal character for number fields.
            exportBlankForGrayFormStatus (Optional[bool]): Whether to export blank for gray form status.
            pd_read_csv_kwargs (Optional[Dict[str, Any]]): Additional keyword arguments to pass to pandas' `read_csv` function when format is 'csv'. Defaults to {}.

        Returns:
            The response from the API containing the exported records.
        """
        return self.post(
            api.export_records(
                {
                    "format": format,
                    "records": records,
                    "fields": fields,
                    "forms": forms,
                    "events": events,
                    "rawOrLabel": rawOrLabel,
                    "rawOrLabelHeaders": rawOrLabelHeaders,
                    "exportCheckboxLabel": exportCheckboxLabel,
                    "exportSurveyFields": exportSurveyFields,
                    "exportDataAccessGroups": exportDataAccessGroups,
                    "filterLogic": filterLogic,
                    "dateRangeBegin": dateRangeBegin,
                    "dateRangeEnd": dateRangeEnd,
                    "csvDelimiter": csvDelimiter,
                    "decimalCharacter": decimalCharacter,
                    "exportBlankForGrayFormStatus": exportBlankForGrayFormStatus,
                }
            ),
            pd_read_csv_kwargs=pd_read_csv_kwargs,
        )

    def import_records(
        self,
        data: Union[pd.DataFrame, List[Dict[str, Any]], str],
        format: Literal["json", "csv"] = "csv",
        returnContent: Literal["count", "ids", "auto_ids"] = "ids",
        overwriteBehavior: Literal["normal", "overwrite"] = "normal",
        forceAutoNumber: bool = False,
        backgroundProcess: Optional[bool] = None,
        dateFormat: Optional[Literal["MDY", "DMY", "YMD"]] = None,
        csvDelimiter: Optional[str] = None,
    ):
        """
        Import records into the project.

        Args:
            data (Union[pd.DataFrame, List[Dict[str, Any]], str]): The records to import.
            format (Literal["json", "csv"]): The format of the imported data.
            returnContent (Literal["count", "ids", "auto_ids"]): Type of content to return.
            overwriteBehavior (Literal["normal", "overwrite"]): How to handle existing records.
            forceAutoNumber (bool): Whether to force auto-numbering of record IDs.
            backgroundProcess (Optional[bool]): Whether to run as a background process.
            dateFormat (Optional[Literal["MDY", "DMY", "YMD"]]): The date format used in the data.
            csvDelimiter (Optional[str]): Delimiter for CSV import.

        Returns:
            The response from the API after importing the records.
        """
        return self.post(
            api.import_records(
                {
                    "data": data,
                    "format": format,
                    "returnContent": returnContent,
                    "overwriteBehavior": overwriteBehavior,
                    "forceAutoNumber": forceAutoNumber,
                    "backgroundProcess": backgroundProcess,
                    "dateFormat": dateFormat,
                    "csvDelimiter": csvDelimiter,
                }
            )
        )

    def delete_records(
        self,
        records: List[str],
        arm: Optional[str] = None,
        instrument: Optional[str] = None,
        event: Optional[str] = None,
        repeat_instance: Optional[int] = None,
        delete_logging: Optional[str] = None,
    ):
        """
        Delete records from the project.

        Args:
            records (List[str]): The record IDs to delete.
            arm (Optional[str]): The arm number to restrict deletion to.
            instrument (Optional[str]): The instrument to restrict deletion to.
            event (Optional[str]): The unique event name to restrict deletion to.
            repeat_instance (Optional[int]): The repeat instance to delete.
            delete_logging (Optional[str]): The type of logging to perform for the deletion.

        Returns:
            The response from the API after deleting the records.
        """
        return self.post(
            api.delete_records(
                {
                    "records": records,
                    "arm": arm,
                    "instrument": instrument,
                    "event": event,
                    "repeat_instance": repeat_instance,
                    "delete_logging": delete_logging,
                }
            )
        )

    def rename_record(
        self,
        record: str,
        new_record_name: str,
        arm: Optional[str] = None,
    ):
        """
        Rename a record in the project.

        Args:
            record (str): The current record ID.
            new_record_name (str): The new record ID.
            arm (Optional[str]): The arm number for the record.

        Returns:
            The response from the API after renaming the record.
        """
        return self.post(
            api.rename_record(
                {
                    "record": record,
                    "new_record_name": new_record_name,
                    "arm": arm,
                }
            )
        )

    def generate_next_record_name(self):
        """
        Generate the next record name.

        Returns:
            The response from the API containing the next record name.
        """
        return self.post(api.generate_next_record_name({}))

    # repeating_forms_events
    def get_repeating_forms_events(self):
        """
        Export repeating forms events.

        Returns:
            The response from the API containing repeating forms events.
        """
        return self.post(api.get_repeating_forms_events({}))

    def import_repeating_forms_events(self, data: RedcapDataType):
        """
        Import repeating forms events.

        Args:
            data (RedcapDataType): The repeating forms events data to import.

        Returns:
            The response from the API after importing repeating forms events.
        """
        return self.post(api.import_repeating_forms_events({"data": data}))

    # report
    def get_report(
        self,
        report_id: int,
        format: Literal["json", "csv"] = "csv",
        rawOrLabel: Literal["raw", "label"] = "raw",
        rawOrLabelHeaders: Literal["raw", "label"] = "raw",
        exportCheckboxLabel: bool = False,
        csvDelimiter: str = ",",
        decimalCharacter: Optional[str] = None,
        pd_read_csv_kwargs: Optional[Dict[str, Any]] = {},
    ):
        """
        Retrieve a report from REDCap.

        Args:
            report_id (int): The ID of the report to retrieve.
            format (Literal["json", "csv"], optional): The format of the returned data. Defaults to "csv".
            rawOrLabel (Literal["raw", "label"], optional): Whether to export raw or labeled data. Defaults to "raw".
            rawOrLabelHeaders (Literal["raw", "label"], optional): Whether to export raw or labeled headers. Defaults to "raw".
            exportCheckboxLabel (bool, optional): Whether to export checkbox labels. Defaults to False.
            csvDelimiter (str, optional): The delimiter for CSV format. Defaults to ",".
            decimalCharacter (Optional[str], optional): The decimal character for numeric data. Defaults to None.
            pd_read_csv_kwargs (Optional[Dict[str, Any]]): Additional keyword arguments to pass to pandas' `read_csv` function when format is 'csv'. Defaults to {}.

        Returns:
            The report data in the specified format.
        """
        return self.post(
            api.get_report(
                {
                    "report_id": report_id,
                    "format": format,
                    "rawOrLabel": rawOrLabel,
                    "rawOrLabelHeaders": rawOrLabelHeaders,
                    "exportCheckboxLabel": exportCheckboxLabel,
                    "csvDelimiter": csvDelimiter,
                    "decimalCharacter": decimalCharacter,
                }
            ),
            pd_read_csv_kwargs=pd_read_csv_kwargs,
        )

    # version
    def get_version(self):
        """
        Get the version of the REDCap instance.

        Returns:
            str: The version number of the REDCap instance.
        """
        return self.text_api(api.get_version({}))

    # survey
    def get_survey_link(
        self,
        record: str,
        instrument: str,
        event: Optional[str] = None,
        repeat_instance: Optional[int] = None,
    ):
        """
        Get a survey link for a specific record and instrument.

        Args:
            record (str): The record ID.
            instrument (str): The name of the instrument (form).
            event (Optional[str], optional): The unique event name. Defaults to None.
            repeat_instance (Optional[int], optional): The repeat instance number. Defaults to None.

        Returns:
            str: The survey link URL.
        """
        return self.text_api(
            api.get_survey_link(
                {
                    "record": record,
                    "instrument": instrument,
                    "event": event,
                    "repeat_instance": repeat_instance,
                }
            )
        )

    def get_participant_list(
        self,
        instrument: str,
        event: Optional[str] = None,
        format: Literal["json", "csv"] = "csv",
        pd_read_csv_kwargs: Optional[Dict[str, Any]] = {},
    ):
        """
        Get the participant list for a specific instrument.

        Args:
            instrument (str): The name of the instrument (form).
            event (Optional[str], optional): The unique event name. Defaults to None.
            format (Literal["json", "csv"], optional): The format of the returned data. Defaults to "csv".
            pd_read_csv_kwargs (Optional[Dict[str, Any]]): Additional keyword arguments to pass to pandas' `read_csv` function when format is 'csv'. Defaults to {}.

        Returns:
            The participant list in the specified format.
        """
        return self.post(
            api.get_participant_list(
                {
                    "instrument": instrument,
                    "event": event,
                    "format": format,
                }
            ),
            pd_read_csv_kwargs=pd_read_csv_kwargs,
        )

    def get_survey_queue_link(
        self,
        record: str,
    ):
        """
        Get the survey queue link for a specific record.

        Args:
            record (str): The record ID.

        Returns:
            str: The survey queue link URL.
        """
        return self.text_api(
            api.get_survey_queue_link(
                {
                    "record": record,
                }
            )
        )

    def get_survey_return_code(
        self,
        record: str,
        instrument: str,
        event: Optional[str] = None,
        repeat_instance: Optional[int] = None,
    ):
        """
        Get the survey return code for a specific record and instrument.

        Args:
            record (str): The record ID.
            instrument (str): The name of the instrument (form).
            event (Optional[str], optional): The unique event name. Defaults to None.
            repeat_instance (Optional[int], optional): The repeat instance number. Defaults to None.

        Returns:
            str: The survey return code.
        """
        return self.text_api(
            api.get_survey_return_code(
                {
                    "record": record,
                    "instrument": instrument,
                    "event": event,
                    "repeat_instance": repeat_instance,
                }
            )
        )

    # user
    def get_users(self):
        """
        Get a list of all users in the project.

        Returns:
            List[Dict]: A list of dictionaries containing user information.
        """
        return self.post(api.get_users({}))

    def import_users(self, data: RedcapDataType):
        """
        Import or update user information.

        Args:
            data (RedcapDataType): A list of dictionaries containing user information to import or update.

        Returns:
            str: A message indicating the number of users added or updated.
        """
        return self.post(api.import_users({"data": data}))

    def delete_users(self, users: List[str]):
        """
        Delete users from the project.

        Args:
            users (List[str]): A list of usernames to delete.

        Returns:
            str: A message indicating the number of users deleted.
        """
        return self.post(api.delete_users({"users": users}))

    # user_role
    def get_user_roles(self):
        """
        Get a list of all user roles defined in the project.

        Returns:
            List[Dict]: A list of dictionaries containing user role information.
        """
        return self.post(api.get_user_roles({}))

    def import_user_roles(self, data: RedcapDataType):
        """
        Import or update user role information.

        Args:
            data (RedcapDataType): A list of dictionaries containing user role information to import or update.

        Returns:
            str: A message indicating the number of user roles added or updated.
        """
        return self.post(api.import_user_roles({"data": data}))

    def delete_user_roles(self, roles: List[str]):
        """
        Delete user roles from the project.

        Args:
            roles (List[str]): A list of role names to delete.

        Returns:
            str: A message indicating the number of user roles deleted.
        """
        return self.post(api.delete_user_roles({"roles": roles}))

    #  user_role_mappings
    def get_user_role_mappings(self):
        """
        Get a list of all user-role assignments in the project.

        Returns:
            List[Dict]: A list of dictionaries containing user-role assignment information.
        """
        return self.post(api.get_user_role_mappings({}))

    def import_user_role_mappings(self, data: RedcapDataType):
        """
        Import or update user-role assignment information.

        Args:
            data (RedcapDataType): A list of dictionaries containing user-role assignment information to import or update.

        Returns:
            str: A message indicating the number of user-role assignments added or updated.
        """
        return self.post(api.import_user_role_mappings({"data": data}))
