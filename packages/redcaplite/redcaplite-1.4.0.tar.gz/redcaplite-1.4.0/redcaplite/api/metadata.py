import json
import pandas as pd
from .utils import field_to_index, optional_field


@optional_field('format', 'csv')
@field_to_index('fields')
@field_to_index('forms')
def get_metadata(data):
    new_data = {
        'content': 'metadata',
    }
    return (new_data)


def import_metadata(data):
    new_data = {
        'content': 'metadata',
        'format': data['format'],
    }
    if data['format'] == 'csv' and isinstance(data['data'], pd.DataFrame):
        new_data['data'] = data['data'].to_csv(index=False)
    elif data['format'] == 'json':
        new_data['data'] = json.dumps(data['data'])
    else:
        new_data['data'] = data['data']
    return (new_data)
