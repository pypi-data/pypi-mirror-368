import json
from redcaplite.api import get_arms, import_arms, delete_arms


def test_get_arms():
    data = {}  # Any necessary input data for the function
    result = get_arms(data)
    expected = {'content': 'arm', 'format': 'json'}
    assert result == expected


def test_import_arms():
    data = {
        'data': [
            {'arm_num': 1, 'name': 'Arm 1'},
            {'arm_num': 2, 'name': 'Arm 2'}
        ]
    }
    result = import_arms(data)
    expected = {
        'content': 'arm',
        'action': 'import',
        'format': 'json',
        'data': json.dumps(data['data'])
    }
    assert result == expected


def test_delete_arms():
    data = {
        'arms': [1, 2, 3]
    }
    result = delete_arms(data)
    expected = {
        'content': 'arm',
        'action': 'delete',
        'format': 'json',
        'arms[0]': '1',
        'arms[1]': '2',
        'arms[2]': '3'
    }
    assert result == expected
