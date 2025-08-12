from .utils import json_data_formatter, field_to_index, require_field


def get_dags(data):
    new_data = {
        'content': 'dag',
        'format': 'json'
    }
    return (new_data)


@json_data_formatter
def import_dags(data):
    new_data = {
        'content': 'dag',
        'action': 'import',
    }
    return (new_data)


@field_to_index('dags', True)
def delete_dags(data):
    new_data = {
        'content': 'dag',
        'action': 'delete',
        'format': 'json'
    }
    return (new_data)


@require_field('dag')
def switch_dag(data):
    new_data = {
        'content': 'dag',
        'action': 'switch',
    }
    return (new_data)
