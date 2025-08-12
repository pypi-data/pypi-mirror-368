from .utils import optional_field


@optional_field('field')
def get_field_names(data):
    new_data = {
        'content': 'exportFieldNames',
        'format': 'json'
    }
    return (new_data)
