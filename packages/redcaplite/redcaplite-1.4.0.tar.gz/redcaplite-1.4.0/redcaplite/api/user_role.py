from .utils import json_data_formatter, field_to_index


def get_user_roles(data):
    new_data = {
        'content': 'userRole',
        'format': 'json'
    }
    return (new_data)


@json_data_formatter
def import_user_roles(data):
    new_data = {
        'content': 'userRole',
    }
    return (new_data)


@field_to_index('roles', True)
def delete_user_roles(data):
    new_data = {
        'content': 'userRole',
        'action': 'delete',
        'format': 'json'
    }
    return (new_data)
