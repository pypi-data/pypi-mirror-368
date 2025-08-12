import json
from redcaplite.api import get_events, import_events, delete_events


def test_get_events():
    data = {"arms": [1, 2, 3]}
    expected_output = {
        'content': 'event',
        'format': 'json',
        'arms[0]': '1',
        'arms[1]': '2',
        'arms[2]': '3'
    }
    assert get_events(data) == expected_output


def test_import_events():
    data = {"data":
            [{"event_name": "Event 1", "arm_num": 1, "day_offset": 1, "offset_min": 0, "offset_max": 0, "unique_event_name": "event_1_arm_1", "custom_event_label": None, "event_id": 304804},
             {"event_name": "Event 2", "arm_num": 1, "day_offset": 2, "offset_min": 0, "offset_max": 0, "unique_event_name": "event_2_arm_1", "custom_event_label": None, "event_id": 340176}]
            }
    expected_output = {
        'content': 'event',
        'action': 'import',
        'format': 'json',
        'data': json.dumps(data['data'])
    }
    assert import_events(data) == expected_output


def test_delete_events():
    data = {"events": ["event1", "event2"]}
    expected_output = {
        'content': 'event',
        'action': 'delete',
        'format': 'json',
        'events[0]': 'event1',
        'events[1]': 'event2'
    }
    assert delete_events(data) == expected_output
