import sys

from markitdown import MarkItDown

from src.custom_markdown_converter import CustomMarkdownConverter


with open(sys.argv[1], "rb") as fp:
    document = MarkItDown(enable_plugins=True, markdownify=CustomMarkdownConverter).convert(fp)
    print(document)
