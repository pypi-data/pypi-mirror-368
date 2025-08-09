import os
import re
from urllib.parse import urljoin, urlparse
from loguru import logger

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify
from robot_base import log_decorator
from .md_2_html.markdown_2_html import render_article


def __download_image(url, directory):
	try:
		"""下载图片并返回新的文件名"""
		if url.startswith('http://') or url.startswith('https://'):
			response = requests.get(url)
			if response.status_code == 200:
				# 提取文件名
				parsed_url = urlparse(url)
				filename = os.path.basename(parsed_url.path)
				# 保存图片
				with open(os.path.join(directory, filename), 'wb') as f:
					f.write(response.content)
				return filename
			else:
				logger.info(f'Failed to download image: {url}')
	except:
		pass
	return None


@log_decorator
def convert_html_to_markdown(html_content, output_dir, file_name, base_url='', img_dir='images', **kwargs):
	"""将HTML转换为Markdown并下载图片"""
	soup = BeautifulSoup(html_content, 'html.parser')

	# 创建存放图片的目录
	if not os.path.exists(os.path.join(output_dir, img_dir)):
		os.makedirs(os.path.join(output_dir, img_dir))

	# 遍历所有图片标签
	for img in soup.find_all('img'):
		if 'src' not in img.attrs:
			continue
		src = img['src']
		# 如果是相对路径，则构建完整的URL
		if not bool(urlparse(src).netloc):
			if not base_url:
				continue
			src = urljoin(base_url, src)

		new_filename = __download_image(src, os.path.join(output_dir, img_dir))
		if new_filename:
			# 更新图片标签的src属性指向本地文件
			img['src'] = os.path.join(os.path.join(output_dir, img_dir), new_filename)
		else:
			# 如果下载失败，删除该图片节点
			img.decompose()

	# 转换HTML为Markdown
	md_text = markdownify(str(soup))

	# 保存Markdown文件
	with open(os.path.join(output_dir, file_name), 'w', encoding='utf-8') as f:
		f.write(md_text)


def extract_text_and_images(file_path, **kwargs):
	"""读取Markdown文件内容"""
	with open(file_path, 'r', encoding='utf-8') as file:
		markdown_content = file.read()
		# 正则表达式匹配Markdown中的图片
		image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')

		images = []
		positions = []

		for match in image_pattern.finditer(markdown_content):
			# 记录图片链接
			img_url = match.group(1)
			images.append(img_url)

			# 记录图片在文本中的起始和结束位置
			pos_start = match.start()
			pos_end = match.end()
			positions.append((pos_start, pos_end))

		text_parts = []
		last_end = 0

		for start, end in positions:
			# 添加非图片部分的文本
			if start > last_end:
				text_parts.append(markdown_content[last_end:start])

			# 更新last_end
			last_end = end

		# 添加最后一个非图片部分的文本
		if last_end < len(markdown_content):
			text_parts.append(markdown_content[last_end:])

		return text_parts, images


@log_decorator
def convert_markdown_to_html(markdown_content, style='默认', **kwargs):
	return render_article(markdown_content, style)
