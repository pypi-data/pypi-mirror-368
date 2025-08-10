from typing import Type

from markdownify import MarkdownConverter
from markitdown.converters._xlsx_converter import XlsxConverter as _XlsxConverter, XlsConverter as _XlsConverter

from .html_converter import HtmlConverter


class XlsxConverter(_XlsxConverter):
    def __init__(self, markdownify: Type[MarkdownConverter], **kwargs):
        super().__init__()
        self._html_converter = HtmlConverter(markdownify=markdownify, **kwargs)

class XlsConverter(_XlsConverter):
    def __init__(self, markdownify: Type[MarkdownConverter], **kwargs):
        super().__init__()
        self._html_converter = HtmlConverter(markdownify=markdownify, **kwargs)