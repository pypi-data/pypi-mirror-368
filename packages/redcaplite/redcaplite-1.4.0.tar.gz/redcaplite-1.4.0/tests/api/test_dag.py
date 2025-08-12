import json
from redcaplite.api import get_dags, import_dags, delete_dags


def test_get_dags():
    data = {}  # Sample input data, modify as needed
    expected_output = {'content': 'dag', 'format': 'json'}
    assert get_dags(data) == expected_output


def test_import_dags():
    data = {'data':
            [{"data_access_group_name": "test1", "unique_group_name": "test2", "data_access_group_id": 10001},
             {"data_access_group_name": "test3", "unique_group_name": "test4", "data_access_group_id": 10003}]
            }  # Sample input data
    expected_output = {
        'content': 'dag',
        'action': 'import',
        'format': 'json',
        'data': json.dumps(data['data'])
    }
    assert import_dags(data) == expected_output


def test_delete_dags():
    data = {'dags': ['dag1', 'dag2']}  # Sample input data
    expected_output = {
        'content': 'dag',
        'action': 'delete',
        'format': 'json',
        'dags[0]': 'dag1',
        'dags[1]': 'dag2'
    }
    assert delete_dags(data) == expected_output
