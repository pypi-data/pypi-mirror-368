from .utils import optional_field, require_field


@require_field('record')
@require_field('field')
@optional_field('event')
@optional_field('repeat_instance')
def get_file(data):
    new_data = {
        'content': 'file',
        'action': 'export',
    }
    return (new_data)


@require_field('record')
@require_field('field')
@optional_field('event')
@optional_field('repeat_instance')
def import_file(data):
    new_data = {
        'content': 'file',
        'action': 'import',
    }
    return (new_data)


@require_field('record')
@require_field('field')
@optional_field('event')
@optional_field('repeat_instance')
def delete_file(data):
    new_data = {
        'content': 'file',
        'action': 'delete',
        'format': 'json'
    }
    return (new_data)
