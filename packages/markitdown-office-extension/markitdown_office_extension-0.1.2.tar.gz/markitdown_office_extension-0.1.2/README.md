# markitdown-office-extension
A markitdown plugin use to customize markdownif. Supports docx, pptx, xlsx, epub, and html file formats.

## Usage
```python
from typing import Any, Optional
from io import BytesIO
try:
    from markitdown import MarkItDown
except ImportError:
    from markitdown_no_magika import MarkItDown
from markitdown_office_extension.markdown_converter import MarkdownConverter


class CustomMarkdownConverter(MarkdownConverter):
    def convert_img(
        self,
        el: Any,
        text: str,
        convert_as_inline: Optional[bool] = False,
        **kwargs,
    ) -> str:
        if (src := el.attrs.get("src", None)) is not None:
            # process extracted image such as upload to s3
            # in example, we print image attr only
            print("image alt: {alt}, title: {title}, src: {src}".format(
                alt=el.attrs.get("alt", ""),
                title=el.attrs.get("title", ""),
                src=src,
            ))

            # ... or modify image attr such as `src`
            el.attrs["src"] = "https://example.com/assets/example.png"

            # if not set keep_data_uris, or keep_data_uris is False,
            # markitdown won't display whole image uri
            kwargs["keep_data_uris"] = True

        return super().convert_img(el, text, convert_as_inline, **kwargs)

converter = MarkItDown(enable_plugins=True, markdownify=CustomMarkdownConverter)
document = converter.convert(BytesIO(bytes(
    "![title](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAArYAAAOdCAYAAABwHy)",
    encoding="utf-8"
)))

print(document) # ![](https://example.com/assets/example.png)
```