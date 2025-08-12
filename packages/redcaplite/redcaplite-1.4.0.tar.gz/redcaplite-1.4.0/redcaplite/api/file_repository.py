from .utils import optional_field, require_field


@require_field('name')
@optional_field('folder_id')
@optional_field('dag_id')
@optional_field('role_id')
def create_folder_file_repository(data):
    new_data = {
        'content': 'fileRepository',
        'action': 'createFolder',
        'format': 'json'
    }
    return (new_data)


@optional_field('folder_id')
def list_file_repository(data):
    new_data = {
        'content': 'fileRepository',
        'action': 'list',
        'format': 'json'
    }
    return (new_data)


@require_field('doc_id')
def export_file_repository(data):
    new_data = {
        'content': 'fileRepository',
        'action': 'export',
    }
    return (new_data)


@optional_field('folder_id')
def import_file_repository(data):
    new_data = {
        'content': 'fileRepository',
        'action': 'import'
    }
    return (new_data)


@require_field('doc_id')
def delete_file_repository(data):
    new_data = {
        'content': 'fileRepository',
        'action': 'delete',
        'format': 'json'
    }
    return (new_data)
