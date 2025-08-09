# 表格单元格
import html
import os
from typing import Any, Optional

import mistune
from jinja2 import Environment, FileSystemLoader
from lxml import etree
from mistune.plugins.table import table


class Cell:
    def __init__(self, text, align):
        self.text = text
        self.align = align


class StyleRenderer(mistune.HTMLRenderer):
    def __init__(self, style: str, code_style: str = "atom-one-dark"):
        super().__init__()
        self.random_color_list = [
            "213, 15, 37",
            "51, 105, 232",
            "238, 178, 17",
            "15, 157, 88",
        ]
        self.codestyle = code_style
        self.current_color_index = -1  # 当前颜色下标
        self.items = [
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "image",
            "li",
            "link",
            "mac_window",
            "p",
            "strong",
            "table",
            "ul",
            "blockquote",
            "codespan",
            "codestyle",
            "header",
            "footer",
            "background",
        ]
        current_file_path = os.path.abspath(__file__)
        current_directory_path = os.path.dirname(current_file_path)
        # 创建一个包加载器对象(也可以使用PackageLoader包加载器的方式加载)
        self.env = Environment(
            loader=FileSystemLoader(
                os.path.join(current_directory_path, "template", style)
            )
        )
        self.template_dict = {}
        # 模板加载
        for item in self.items:
            self.template_dict[item + "_template"] = (
                self.env.get_template("/{}.html".format(item))
                if os.path.exists(
                    os.path.join(
                        current_directory_path, "template", style, item + ".html"
                    )
                )
                else None
            )

    # 分级标题
    def heading(self, text, level, **attrs: Any):
        if self.template_dict[f"h{level}_template"] is not None:
            return self.template_dict[f"h{level}_template"].render(text=text)
        else:
            return "<h{}>{}</h{}><br>".format(level, text, level)

    # 图片
    def image(self, src, alt="", title=None):
        if self.template_dict[f"image_template"] is not None:
            return self.template_dict[f"image_template"].render(
                src=src, alt=alt, title=title
            )
        else:
            return '<img src="{}" alt="{}" {}/>'.format(
                src, alt, 'title="' + escape_html(title) + '"' if title else None
            )

    # 粗体
    def strong(self, text):
        if self.template_dict[f"strong_template"] is not None:
            return self.template_dict[f"strong_template"].render(text=text)
        else:
            return "<strong>{}</strong>".format(text)

    # 行内代码
    def codespan(self, text):
        if self.template_dict[f"codespan_template"] is not None:
            return self.template_dict[f"codespan_template"].render(text=text)
        else:
            return "<code>{}</code>".format(escape(text))

    # 列表
    def list(self, text, ordered, **attrs: Any):
        if self.template_dict[f"ul_template"] is not None:
            return self.template_dict[f"ul_template"].render(text=text)
        else:
            if ordered:
                return "<ol{}>\n{}</ol>\n".format(
                    (
                        " start=" + str(attrs["start"]) + ""
                        if "start" in attrs and attrs["start"] is not None
                        else ""
                    ),
                    text,
                )
            return "<ul>\n{}</ul>\n".format(text)

    # 列表项
    def list_item(self, text):
        if self.template_dict[f"li_template"] is not None:
            return self.template_dict[f"li_template"].render(text=text)
        else:
            return "<li>{}</li>\n".format(text)

    # 链接
    def link(self, text: str, url: str, title: Optional[str] = None):
        if self.template_dict[f"link_template"] is not None:
            return self.template_dict[f"link_template"].render(link=url, text=text)
        else:
            if text is None:
                text = url
            s = '<a href="{}"'.format(self.safe_url(url))
            if title:
                s += ' title="{}"'.format(escape_html(title))
            return s + ">{}</a>".format((text or url))

    # 段落
    def paragraph(self, text):
        if self.template_dict[f"p_template"] is not None:
            return self.template_dict[f"p_template"].render(text=text)
        else:
            return "<p>{}</p>\n".format(text)

    # 代码块
    def block_code(self, code, info=None):
        if self.template_dict[f"mac_window_template"] is not None:
            from robot_basic.md_2_html.highlight.renderer_code import (
                renderer_by_node,
            )

            highlight_result = renderer_by_node(code, self.codestyle, info)
            return self.template_dict[f"mac_window_template"].render(
                text=highlight_result
            )
        else:
            result = "<pre><code"
            if info is not None:
                info = info.strip()
            if info:
                lang = info.split(None, 1)[0]
                lang = escape_html(lang)
                result += ' class="language-' + lang + '"'
            return result + ">" + escape(code) + "</code></pre>\n"

    # 表格
    def table(self, text):
        if self.template_dict[f"table_template"] is not None:
            table_selector = etree.HTML(text)
            ths = table_selector.xpath("//tr/th")
            tds = table_selector.xpath("//tr/td")
            th_cell_list = []
            for index, value in enumerate(ths):
                style = value.attrib.get("style")
                if style is not None:
                    style = style[11:]
                text = value.text
                th_cell_list.append(Cell(text, style))
            td_cell_list = []
            for index, value in enumerate(tds):
                style = value.attrib.get("style")
                if style is not None:
                    style = style[11:]
                text = value.text
                td_cell_list.append(Cell(text, style))
            return self.template_dict[f"table_template"].render(
                row_count=len(ths), header_list=th_cell_list, detail_list=td_cell_list
            )
        else:
            return text

    # 头部
    def header(self):
        if self.template_dict[f"header_template"] is not None:
            return self.template_dict[f"header_template"].render()
        else:
            return ""

    # 尾部
    def footer(self):
        if self.template_dict[f"footer_template"] is not None:
            return self.template_dict[f"footer_template"].render()
        else:
            return ""

    # 背景
    def background(self, text):
        if self.template_dict[f"background_template"] is not None:
            return self.template_dict[f"background_template"].render(text=text)
        else:
            return text

    # 下划线
    def thematic_break(self):
        return ""


def escape(s, quote=True):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
    return s


def escape_html(s):
    if html is not None:
        return html.escape(html.unescape(s)).replace("&#x27;", "'")
    return escape(s)


def render_article(content, style):
    """
    渲染文章

    :param content: Markdown内容
    :param style:  样式名称
    :return: 渲染后带样式的HTML内容
    """
    render = StyleRenderer(style)
    content_result = mistune.create_markdown(renderer=render, plugins=[table])(content)
    return render.background(
        text="{}{}{}".format(render.header(), content_result, render.footer())
    )
