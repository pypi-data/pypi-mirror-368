from typing import Type

from markitdown import DocumentConverter, MarkItDown
from markitdown._markitdown import ConverterRegistration


def try_patch(
        markitdown: MarkItDown,
        patch: Type[DocumentConverter],
        converter: Type[DocumentConverter],
        **kwargs
) -> None:
    for idx, conv in enumerate(markitdown._converters):
        if not issubclass(type(conv.converter), patch):
            continue
        markitdown._converters[idx] = ConverterRegistration(
            converter=converter(**kwargs),
            priority=conv.priority
        )
        break