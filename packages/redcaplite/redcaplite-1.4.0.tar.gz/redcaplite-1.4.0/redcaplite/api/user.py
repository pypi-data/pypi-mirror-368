from .utils import json_data_formatter, field_to_index


def get_users(data):
    new_data = {
        'content': 'user',
        'format': 'json'
    }
    return (new_data)


@json_data_formatter
def import_users(data):
    new_data = {
        'content': 'user',
    }
    return (new_data)


@field_to_index('users', True)
def delete_users(data):
    new_data = {
        'content': 'user',
        'action': 'delete',
        'format': 'json'
    }
    return (new_data)
