from .utils import json_data_formatter, field_to_index, optional_field


@json_data_formatter
def create_project(data):
    new_data = {
        'content': 'project',
    }
    return (new_data)


@json_data_formatter
def import_project_settings(data):
    new_data = {
        'content': 'project_settings',
    }
    return (new_data)


def get_project(data):
    new_data = {
        'content': 'project',
        'format': 'json'
    }
    return (new_data)


@optional_field('returnMetadataOnly')
@field_to_index('records')
@field_to_index('fields')
@field_to_index('events')
@optional_field('exportSurveyFields')
@optional_field('exportDataAccessGroups')
@optional_field('filterLogic')
@optional_field('exportFiles')
def get_project_xml(data):
    new_data = {
        'content': 'project_xml',
        'format': 'xml',
    }
    return (new_data)
