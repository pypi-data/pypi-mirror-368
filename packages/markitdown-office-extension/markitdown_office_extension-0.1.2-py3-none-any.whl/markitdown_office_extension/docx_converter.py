from typing import BinaryIO, Any, Type

from markdownify import MarkdownConverter
try:
    from markitdown import StreamInfo, DocumentConverterResult
    from markitdown.converters._docx_converter import DocxConverter as _DocxConverter
except ImportError:
    from markitdown_no_magika import StreamInfo, DocumentConverterResult
    from markitdown_no_magika.converters._docx_converter import DocxConverter as _DocxConverter

from .html_converter import HtmlConverter


class DocxConverter(HtmlConverter):
    def __init__(self, markdownify: Type[MarkdownConverter], **kwargs):
        super().__init__(markdownify=markdownify, **kwargs)
        self._html_converter = HtmlConverter(markdownify=markdownify, **kwargs)

    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> bool:
        return _DocxConverter.accepts(self, file_stream, stream_info, **kwargs)

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:
        return _DocxConverter.convert(self, file_stream, stream_info, **kwargs)
