import sys

try:
    from markitdown import MarkItDown
except ImportError:
    from markitdown_no_magika import MarkItDown, StreamInfo

from src.custom_markdown_converter import CustomMarkdownConverter


with open(sys.argv[1], "rb") as fp:
    document = MarkItDown(enable_plugins=True, markdownify=CustomMarkdownConverter).convert(fp, stream_info=StreamInfo(extension=".docx"))
    print(document)
