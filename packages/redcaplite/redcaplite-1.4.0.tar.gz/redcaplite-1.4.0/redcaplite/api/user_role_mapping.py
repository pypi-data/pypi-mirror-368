from .utils import json_data_formatter


def get_user_role_mappings(data):
    new_data = {
        'content': 'userRoleMapping',
        'format': 'json'
    }
    return (new_data)


@json_data_formatter
def import_user_role_mappings(data):
    new_data = {
        'content': 'userRoleMapping',
        'action': 'import',
    }
    return (new_data)
