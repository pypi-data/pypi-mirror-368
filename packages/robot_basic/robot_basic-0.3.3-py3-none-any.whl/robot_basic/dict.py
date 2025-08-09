from robot_base import log_decorator


@log_decorator
def generate_dict(**kwargs):
    return {}


@log_decorator
def has_key(dict_instance, key, **kwargs):
    if not isinstance(dict_instance, dict):
        raise TypeError("dict_instance must be a dict")
    return key in dict_instance


@log_decorator
def set_key_value(dict_instance, key, value, **kwargs):
    if not isinstance(dict_instance, dict):
        raise TypeError("dict_instance must be a dict")
    dict_instance[key] = value


@log_decorator
def get_key_value(
    dict_instance, key, not_found_value=None, not_found_action="return", **kwargs
):
    if not isinstance(dict_instance, dict):
        raise TypeError("dict_instance must be a dict")
    if not_found_action == "raise":
        return dict_instance[key]
    return dict_instance.get(key, not_found_value)


@log_decorator
def get_keys(dict_instance, **kwargs):
    if not isinstance(dict_instance, dict):
        raise TypeError("dict_instance must be a dict")
    return dict_instance.keys()


@log_decorator
def get_values(dict_instance, **kwargs):
    if not isinstance(dict_instance, dict):
        raise TypeError("dict_instance must be a dict")
    return dict_instance.values()


@log_decorator
def delete_key(dict_instance, key, **kwargs):
    if not isinstance(dict_instance, dict):
        raise TypeError("dict_instance must be a dict")
    return dict_instance.__delitem__(key)
