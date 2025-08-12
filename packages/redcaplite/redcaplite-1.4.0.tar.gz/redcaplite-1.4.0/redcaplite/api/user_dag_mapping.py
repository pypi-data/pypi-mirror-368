from .utils import json_data_formatter


def get_user_dag_mappings(data):
    new_data = {
        'content': 'userDagMapping',
        'format': 'json'
    }
    return (new_data)


@json_data_formatter
def import_user_dag_mappings(data):
    new_data = {
        'content': 'userDagMapping',
        'action': 'import',
    }
    return (new_data)
