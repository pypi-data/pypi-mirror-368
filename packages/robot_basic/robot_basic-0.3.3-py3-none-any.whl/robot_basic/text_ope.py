import hashlib
import os
import re
import uuid

from jinja2 import Template

from robot_base import log_decorator, ParamException


@log_decorator
def extract_from_content(
    content, extract_type, pattern, match_first=True, ignore_case=True, **kwargs
):
    if extract_type == "number":
        pattern = r"([\-\+]?\d+(\.\d+)?)"
    elif extract_type == "phone_number":
        pattern = r"(1[3-9]\d{9})"
    elif extract_type == "email":
        pattern = r"([A-Za-z0-9_\-\u4e00-\u9fa5\.]+@[a-zA-Z0-9\-]+(\.[a-zA-Z0-9\-]+)+)"
    elif extract_type == "idcard":
        pattern = r"((\d{17}(x|x|\d))|(\d{15}))"

    if match_first:
        match = re.search(pattern, content, re.IGNORECASE if ignore_case else 0)
        if match:
            return match.group()
        else:
            return ""
    else:
        return [
            result[0] if isinstance(result, tuple) else result
            for result in re.findall(
                pattern, content, re.IGNORECASE if ignore_case else 0
            )
        ]


@log_decorator
def get_text_length(content, **kwargs):
    if not isinstance(content, str):
        raise ParamException(f"{content}不是字符串类型")
    return len(content)


@log_decorator
def append_text(original_content, content, need_break, **kwargs):
    return original_content + ("\n" if need_break else "") + content


@log_decorator
def sub_text(
    original_content,
    start_type,
    end_type,
    start_pos,
    start_text,
    is_contains_start_text,
    sub_len,
    **kwargs,
):
    if start_type == "start" and end_type == "end":
        return original_content
    elif start_type == "start" and end_type == "len":
        sub_len = int(sub_len)
        return original_content[:sub_len]
    elif start_type == "start_pos" and end_type == "end":
        start_pos = int(start_pos)
        return original_content[start_pos:]
    elif start_type == "start_pos" and end_type == "len":
        start_pos = int(start_pos)
        sub_len = int(sub_len)
        return original_content[start_pos : start_pos + sub_len]
    elif start_type == "start_text" and end_type == "end":
        if is_contains_start_text:
            return original_content[original_content.index(start_text) :]
        else:
            return original_content[
                original_content.index(start_text) + len(start_text) :
            ]
    elif start_type == "start_text" and end_type == "len":
        sub_len = int(sub_len)
        if is_contains_start_text:
            start_index = original_content.index(start_text)
            return original_content[
                start_index : (
                    len(original_content)
                    if sub_len + start_index > len(original_content)
                    else sub_len + start_index
                )
            ]
        else:
            start_index = original_content.index(start_text) + len(start_text)
            return original_content[
                start_index : (
                    len(original_content)
                    if sub_len + start_index > len(original_content)
                    else sub_len + start_index
                )
            ]
    else:
        raise ParamException("未知的起始位置和结束位置")


@log_decorator
def padding_text(original_content, padding_type, padding_char, padding_count, **kwargs):
    if len(padding_char) != 1:
        raise ParamException("填充文本的长度必须为1")
    padding_count = int(padding_count)
    if padding_type == "left":
        return original_content.rjust(padding_count, padding_char)
    else:
        return original_content.ljust(padding_count, padding_char)


@log_decorator
def trim_text(original_content, trim_type, **kwargs):
    if trim_type == "left":
        return original_content.lstrip()
    elif trim_type == "right":
        return original_content.rstrip()
    else:
        return original_content.strip()


@log_decorator
def upper_lower_text(original_content: str, change_type, **kwargs):
    if change_type == "all_upper":
        return original_content.upper()
    elif change_type == "all_lower":
        return original_content.lower()
    else:
        return " ".join(word.capitalize() for word in original_content.split())


@log_decorator
def join_text(list_of_string, join_type, separator, separator_count, **kwargs):
    if not isinstance(list_of_string, list):
        raise ParamException(f"{list_of_string} 不是列表类型")
    separator_count = int(separator_count)
    if join_type == "no_separator":
        return "".join(list_of_string)
    elif join_type == "space":
        return (" " * separator_count).join(list_of_string)
    elif join_type == "tab":
        return ("\t" * separator_count).join(list_of_string)
    elif join_type == "break_line":
        return ("\n" * separator_count).join(list_of_string)
    return (separator * separator_count).join(list_of_string)


@log_decorator
def split_text(content: str, split_type, separator, ignore_blank, **kwargs):
    if split_type == "space":
        result_array = content.split(" ")
    elif split_type == "tab":
        result_array = content.split("\t")
    elif split_type == "break_line":
        result_array = content.split(os.linesep)
    else:
        result_array = content.split(separator)
    if ignore_blank:
        return list([text for text in result_array if len(text) > 0])
    else:
        return result_array


@log_decorator
def replace_text(
    content: str,
    replace_type,
    to_replace,
    pattern,
    replace_content,
    replace_first=True,
    ignore_case=True,
    **kwargs,
):
    if replace_type == "content":
        return content.replace(to_replace, replace_content, 1 if replace_first else -1)
    if replace_type == "number":
        pattern = r"([\-\+]?\d+(\.\d+)?)"
    elif replace_type == "phone_number":
        pattern = r"(1[3-9]\d{9})"
    elif replace_type == "email":
        pattern = r"([A-Za-z0-9_\-\u4e00-\u9fa5\.]+@[a-zA-Z0-9\-]+(\.[a-zA-Z0-9\-]+)+)"
    elif replace_type == "idcard":
        pattern = r"((\d{17}(x|x|\d))|(\d{15}))"

    return re.sub(
        pattern,
        replace_content,
        content,
        count=1 if replace_first else 0,
        flags=re.IGNORECASE if ignore_case else 0,
    )


@log_decorator
def template_text(
    content_type,
    template_content,
    template_content2,
    data,
    **kwargs,
):
    if content_type == "plain":
        tm = Template(template_content)
    else:
        tm = Template(template_content2)
    return tm.render(data)


@log_decorator
def text_hash(text, hash_type, **kwargs):
    """
    hash_type: md5, sha1, sha224, sha256, sha384, sha512
    """
    hash_type = hash_type.lower()
    if hash_type == "md5":
        hash_object = hashlib.md5(text.encode())
    elif hash_type == "sha1":
        hash_object = hashlib.sha1(text.encode())
    elif hash_type == "sha224":
        hash_object = hashlib.sha224(text.encode())
    elif hash_type == "sha256":
        hash_object = hashlib.sha256(text.encode())
    elif hash_type == "sha384":
        hash_object = hashlib.sha384(text.encode())
    elif hash_type == "sha512":
        hash_object = hashlib.sha512(text.encode())
    else:
        raise ValueError("hash_type is not supported")
    hash_value = hash_object.hexdigest()
    return hash_value


@log_decorator
def generate_uuid(text_length, **kwargs):
    text_length = int(text_length)
    return str(uuid.uuid4())[:text_length]
