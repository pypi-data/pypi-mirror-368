from typing import BinaryIO, Any, Type

from bs4 import BeautifulSoup
from markdownify import MarkdownConverter
from markitdown import StreamInfo, DocumentConverterResult
from markitdown.converters import HtmlConverter as _HtmlConverter


class HtmlConverter(_HtmlConverter):
    def __init__(self, markdownify: Type[MarkdownConverter], **kwargs):
        super().__init__()
        assert issubclass(markdownify, MarkdownConverter)
        self._markdownify = markdownify

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:
        # Parse the stream
        encoding = "utf-8" if stream_info.charset is None else stream_info.charset
        soup = BeautifulSoup(file_stream, "html.parser", from_encoding=encoding)

        # Remove javascript and style blocks
        for script in soup(["script", "style"]):
            script.extract()

        # Print only the main content
        body_elm = soup.find("body")
        if body_elm:
            webpage_text = self._markdownify(**kwargs).convert_soup(body_elm)
        else:
            webpage_text = self._markdownify(**kwargs).convert_soup(soup)

        assert isinstance(webpage_text, str)

        # remove leading and trailing \n
        webpage_text = webpage_text.strip()

        return DocumentConverterResult(
            markdown=webpage_text,
            title=None if soup.title is None else soup.title.string,
        )
