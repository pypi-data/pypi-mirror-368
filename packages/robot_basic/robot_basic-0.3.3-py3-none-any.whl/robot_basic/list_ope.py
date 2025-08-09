import random

from robot_base import log_decorator


@log_decorator
def create_list(**kwargs):
    return []


@log_decorator
def list_contains_value(list_instance, value, **kwargs):
    if not (isinstance(list_instance, list) or isinstance(list_instance, tuple)):
        raise Exception("输入内容不是列表对象")
    else:
        return value in list_instance


@log_decorator
def empty_list(list_instance, **kwargs):
    if not isinstance(list_instance, list):
        raise Exception("输入内容不是列表对象")
    else:
        list_instance.clear()


@log_decorator
def insert_list(list_instance, value, insert_type="append", index=None, **kwargs):
    if not isinstance(list_instance, list):
        raise Exception("输入内容不是列表对象")
    else:
        if insert_type == "append":
            list_instance.append(value)
        else:
            index = int(index)
            list_instance.insert(index, value)


@log_decorator
def replace_list(list_instance, index, new_value, **kwargs):
    if not (isinstance(list_instance, list) or isinstance(list_instance, tuple)):
        raise Exception("输入内容不是列表对象")
    else:
        index = int(index)
        list_instance[index] = new_value


@log_decorator
def get_value_by_index(list_instance, index, **kwargs):
    if not (isinstance(list_instance, list) or isinstance(list_instance, tuple)):
        raise Exception("输入内容不是列表对象")
    else:
        index = int(index)
        return list_instance[index]


@log_decorator
def get_length_of_list(list_instance, **kwargs):
    if not (isinstance(list_instance, list) or isinstance(list_instance, tuple)):
        raise Exception("输入内容不是列表对象")
    else:
        return len(list_instance)


@log_decorator
def delete_list(
    list_instance, delete_type="by_index", value=None, index=None, **kwargs
):
    if not isinstance(list_instance, list):
        raise Exception("输入内容不是列表对象")
    else:
        if delete_type == "by_value":
            list_instance.remove(value)
        elif delete_type == "by_index":
            index = int(index)
            del list_instance[index]


@log_decorator
def filter_list_by_value(list_instance, filter_value, **kwargs):
    return [value for value in list_instance if value not in filter_value]


@log_decorator
def sort_list(list_instance, sort_type="descending", **kwargs):
    if not isinstance(list_instance, list):
        raise Exception("输入内容不是列表对象")
    else:
        if sort_type == "ascending":
            list_instance.sort()
        elif sort_type == "descending":
            list_instance.sort(reverse=True)


@log_decorator
def shuffle_list(list_instance, **kwargs):
    if not isinstance(list_instance, list):
        raise Exception("输入内容不是列表对象")
    else:
        random.shuffle(list_instance)


@log_decorator
def extend_list(list_instance, list_instance2, **kwargs):
    if not isinstance(list_instance, list):
        raise Exception("列表1不是列表对象")
    if not isinstance(list_instance2, list):
        raise Exception("列表2不是列表对象")
    else:
        return list_instance + list_instance2


@log_decorator
def reverse_list(list_instance, **kwargs):
    if not isinstance(list_instance, list):
        raise Exception("输入内容不是列表对象")
    else:
        list_instance.reverse()


@log_decorator
def remove_duplicates(list_instance, **kwargs):
    if not isinstance(list_instance, list):
        raise Exception("输入内容不是列表对象")
    else:
        return list(set(list_instance))


@log_decorator
def get_intersection(list_instance, list_instance2, **kwargs):
    if not isinstance(list_instance, list):
        raise Exception("列表1不是列表对象")
    if not isinstance(list_instance2, list):
        raise Exception("列表2不是列表对象")
    else:
        return list(set(list_instance).intersection(set(list_instance2)))
