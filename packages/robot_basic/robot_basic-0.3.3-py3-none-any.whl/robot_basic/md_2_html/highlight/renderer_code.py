import importlib.resources
import os
import configparser

config = configparser.ConfigParser()
file_dir = os.path.abspath(__file__).replace("renderer_code.py", "")
before_path = os.path.join(file_dir, "transform/before.html")
after_path = os.path.join(file_dir, "transform/after.html")
js_path = os.path.join(file_dir, "renderer_code.js")


# highlight.js高亮转换
def renderer_by_node(content, theme, language=None):
    # 读取对应主题配置文件，获取class和style对应字典
    config.read(
        os.path.join(
            os.path.split(os.path.realpath(__file__))[0],
            "styles_conf/{}.ini".format(theme),
        ),
        encoding="utf8",
    )
    items = config.items("theme")
    with open(before_path, "w", encoding="utf-8") as f:
        f.write(content)
    with importlib.resources.path("playwright", "driver/node.exe") as module_path:
        node_command = f'"{module_path}" {js_path}'
    if language is not None:
        node_command += " " + language
    os.system(node_command)
    result = ""
    with open(after_path, "r+", encoding="utf-8") as f:
        for line in f:
            # 获得左侧空格数量
            left_blank_count = 0
            for c in line:
                if c == " ":
                    left_blank_count += 1
                else:
                    break
            result += "{}{}<br>".format("&nbsp;" * left_blank_count, line.lstrip())
    for key, value in items:
        result = result.replace('class="{}"'.format(key), 'style="{}"'.format(value))
    result = result.replace("~", "%")
    return result
