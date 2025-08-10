from typing import Type

from markdownify import MarkdownConverter
from markitdown.converters._pptx_converter import PptxConverter as _PptxConverter

from .html_converter import HtmlConverter


class PptxConverter(_PptxConverter):
    def __init__(self, markdownify: Type[MarkdownConverter], **kwargs):
        super().__init__()
        self._html_converter = HtmlConverter(markdownify=markdownify, **kwargs)
