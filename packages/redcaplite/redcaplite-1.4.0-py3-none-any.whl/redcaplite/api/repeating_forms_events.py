from .utils import json_data_formatter


def get_repeating_forms_events(data):
    new_data = {
        'content': 'repeatingFormsEvents',
        'format': 'json'
    }
    return (new_data)


@json_data_formatter
def import_repeating_forms_events(data):
    new_data = {
        'content': 'repeatingFormsEvents',
    }
    return (new_data)
