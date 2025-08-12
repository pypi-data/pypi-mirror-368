import pandas as pd
import json
from .utils import field_to_index, optional_field, require_field


@optional_field('format', 'csv')
@field_to_index('records')
@field_to_index('fields')
@field_to_index('forms')
@field_to_index('events')
@optional_field('rawOrLabel')
@optional_field('rawOrLabelHeaders')
@optional_field('exportCheckboxLabel')
@optional_field('exportSurveyFields')
@optional_field('exportDataAccessGroups')
@optional_field('filterLogic')
@optional_field('dateRangeBegin')
@optional_field('dateRangeEnd')
@optional_field('csvDelimiter')
@optional_field('decimalCharacter')
@optional_field('exportBlankForGrayFormStatus')
def export_records(data):
    new_data = {
        'content': 'record',
        'action': 'export',
        'type': 'flat',
    }
    return (new_data)


@optional_field('overwriteBehavior', 'normal')
@optional_field('forceAutoNumber', 'false')
@optional_field('backgroundProcess')
@optional_field('dateFormat')
@optional_field('csvDelimiter')
@optional_field('returnContent', 'ids')
def import_records(data):
    new_data = {
        'content': 'record',
        'action': 'import',
        'format': data['format'],
        'type': 'flat',
    }
    if data['format'] == 'csv' and isinstance(data['data'], pd.DataFrame):
        new_data['data'] = data['data'].to_csv(index=False)
    elif data['format'] == 'json':
        new_data['data'] = json.dumps(data['data'])
    else:
        new_data['data'] = data['data']
    return (new_data)


@field_to_index('records', True)
@optional_field('arm')
@optional_field('instrument')
@optional_field('event')
@optional_field('repeat_instance')
@optional_field('delete_logging')
def delete_records(data):
    new_data = {
        'content': 'record',
        'action': 'delete',
        'format': 'json'
    }
    return (new_data)


@require_field('record')
@require_field('new_record_name')
@optional_field('arm')
def rename_record(data):
    new_data = {
        'content': 'record',
        'action': 'rename',
        'format': 'json'
    }
    return (new_data)


def generate_next_record_name(data):
    new_data = {
        'content': 'generateNextRecordName',
        'format': 'json'
    }
    return (new_data)
