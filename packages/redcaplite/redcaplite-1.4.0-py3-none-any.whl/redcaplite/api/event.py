from .utils import json_data_formatter, field_to_index


@field_to_index('arms')
def get_events(data):
    new_data = {
        'content': 'event',
        'format': 'json'
    }
    return (new_data)


@json_data_formatter
def import_events(data):
    new_data = {
        'content': 'event',
        'action': 'import',
    }
    return (new_data)


@field_to_index('events', True)
def delete_events(data):
    new_data = {
        'content': 'event',
        'action': 'delete',
        'format': 'json'
    }
    return (new_data)
