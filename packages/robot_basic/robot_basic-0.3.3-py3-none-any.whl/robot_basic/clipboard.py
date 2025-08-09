import pyperclip
from robot_base import log_decorator, func_decorator


@log_decorator
@func_decorator
def set_text_to_clipboard(text_content, **kwargs):
    pyperclip.copy(text_content)


@log_decorator
@func_decorator
def get_text_from_clipboard(**kwargs):
    return pyperclip.paste()
