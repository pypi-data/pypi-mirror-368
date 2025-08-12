import json
from datetime import datetime


def json_data_formatter(func):
    def wrapper(data):

        result = func(data)

        result['format'] = 'json'
        result['data'] = json.dumps(data['data'])
        return result
    return wrapper


def field_to_index(field: str, required: bool = False):
    def decorator(func):
        def wrapper(data):

            result = func(data)

            for index, item in enumerate(data[field] if required else data.get(field, [])):
                result[f"{field}[{index}]"] = str(item)
            return result
        return wrapper
    return decorator


def require_field(field: str):
    def decorator(func):
        def wrapper(data):

            result = func(data)

            result[field] = data[field]
            return result
        return wrapper
    return decorator


def optional_field(field: str, default=None):
    def decorator(func):
        def wrapper(data):

            result = func(data)
            if (field in data and data[field] is not None) or default is not None:
                result[field] = data.get(field, default)
                if isinstance(result[field], datetime):
                    result[field] = result[field].strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(result[field], bool):
                    result[field] = "true" if result[field] else "false"
            return result
        return wrapper
    return decorator
