__plugin_interface_version__ = 1

from typing import Type

try:
    from markitdown import MarkItDown
except ImportError:
    from markitdown_no_magika import MarkItDown

from markdownify import MarkdownConverter as MarkdownifyMarkdownConverter


def register_converters(markitdown: MarkItDown, markdownify: Type[MarkdownifyMarkdownConverter] | None = None, **kwargs) -> None:
    from .patch import try_patch

    from .markdown_converter import MarkdownConverter
    from .docx_converter import DocxConverter
    from .html_converter import HtmlConverter
    from .xlsx_converter import XlsxConverter
    from .xlsx_converter import XlsConverter
    from .pptx_converter import PptxConverter
    from .epub_converter import EpubConverter

    try:
        from markitdown.converters._docx_converter import DocxConverter as MarkitdownDocxConverter
        from markitdown.converters._html_converter import HtmlConverter as MarkitdownHtmlConverter
        from markitdown.converters._xlsx_converter import XlsxConverter as MarkitdownXlsxConverter
        from markitdown.converters._xlsx_converter import XlsConverter  as MarkitdownXlsConverter
        from markitdown.converters._pptx_converter import PptxConverter as MarkitdownPptxConverter
        from markitdown.converters._epub_converter import EpubConverter as MarkitdownEpubConverter
    except ImportError:
        from markitdown_no_magika.converters._docx_converter import DocxConverter as MarkitdownDocxConverter
        from markitdown_no_magika.converters._html_converter import HtmlConverter as MarkitdownHtmlConverter
        from markitdown_no_magika.converters._xlsx_converter import XlsxConverter as MarkitdownXlsxConverter
        from markitdown_no_magika.converters._xlsx_converter import XlsConverter  as MarkitdownXlsConverter
        from markitdown_no_magika.converters._pptx_converter import PptxConverter as MarkitdownPptxConverter
        from markitdown_no_magika.converters._epub_converter import EpubConverter as MarkitdownEpubConverter


    markdownify = MarkdownConverter if markdownify is None else markdownify

    try_patch(markitdown, MarkitdownDocxConverter, DocxConverter, markdownify=markdownify, **kwargs)
    try_patch(markitdown, MarkitdownHtmlConverter, HtmlConverter, markdownify=markdownify, **kwargs)
    try_patch(markitdown, MarkitdownXlsxConverter, XlsxConverter, markdownify=markdownify, **kwargs)
    try_patch(markitdown, MarkitdownXlsConverter,  XlsConverter,  markdownify=markdownify, **kwargs)
    try_patch(markitdown, MarkitdownPptxConverter, PptxConverter, markdownify=markdownify, **kwargs)
    try_patch(markitdown, MarkitdownEpubConverter, EpubConverter, markdownify=markdownify, **kwargs)

