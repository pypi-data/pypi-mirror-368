import json

from robot_base import log_decorator


@log_decorator
def object_to_json(data, is_pretty=True, indent=4,  **kwargs):
    return json.dumps(data, indent=indent if is_pretty else None)


@log_decorator
def json_to_object(json_str, **kwargs):
    return json.loads(json_str)