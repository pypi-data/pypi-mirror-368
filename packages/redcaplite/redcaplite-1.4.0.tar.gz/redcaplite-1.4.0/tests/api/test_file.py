import pytest
from redcaplite.api import get_file, import_file, delete_file


def test_get_file_required_fields():
    data = {'record': '123', 'field': 'file_field'}
    result = get_file(data)
    assert result == {'content': 'file', 'action': 'export',
                      'field': 'file_field', 'record': '123'}


def test_get_file_optional_fields():
    data = {'record': '123', 'field': 'file_field',
            'event': 'event_name', 'repeat_instance': 1}
    result = get_file(data)
    assert result == {'content': 'file', 'action': 'export', 'record': '123',
                      'field': 'file_field', 'event': 'event_name', 'repeat_instance': 1}


def test_get_file_missing_required_field():
    data = {'field': 'file_field'}
    with pytest.raises(KeyError):
        get_file(data)


def test_import_file_required_fields():
    data = {'record': '123', 'field': 'file_field'}
    result = import_file(data)
    assert result == {'content': 'file', 'action': 'import',
                      'record': '123', 'field': 'file_field'}


def test_import_file_optional_fields():
    data = {'record': '123', 'field': 'file_field',
            'event': 'event_name', 'repeat_instance': 1}
    result = import_file(data)
    assert result == {'content': 'file', 'action': 'import', 'record': '123',
                      'field': 'file_field', 'event': 'event_name', 'repeat_instance': 1}


def test_import_file_missing_required_field():
    data = {'field': 'file_field'}
    with pytest.raises(KeyError):
        import_file(data)


def test_delete_file_required_fields():
    data = {'record': '123', 'field': 'file_field'}
    result = delete_file(data)
    assert result == {'content': 'file', 'action': 'delete',
                      'format': 'json', 'record': '123', 'field': 'file_field'}


def test_delete_file_optional_fields():
    data = {'record': '123', 'field': 'file_field',
            'event': 'event_name', 'repeat_instance': 1}
    result = delete_file(data)
    assert result == {'content': 'file', 'action': 'delete', 'format': 'json',
                      'record': '123', 'field': 'file_field', 'event': 'event_name', 'repeat_instance': 1}


def test_delete_file_missing_required_field():
    data = {'field': 'file_field'}
    with pytest.raises(KeyError):
        delete_file(data)


def test_get_file_invalid_input():
    data = 'invalid_input'
    with pytest.raises(TypeError):
        get_file(data)


def test_import_file_invalid_input():
    data = 'invalid_input'
    with pytest.raises(TypeError):
        import_file(data)


def test_delete_file_invalid_input():
    data = 'invalid_input'
    with pytest.raises(TypeError):
        delete_file(data)
