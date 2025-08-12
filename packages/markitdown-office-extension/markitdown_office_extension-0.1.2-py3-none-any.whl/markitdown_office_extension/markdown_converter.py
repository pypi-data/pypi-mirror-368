try:
    from markitdown.converters._markdownify import _CustomMarkdownify
except ImportError:
    from markitdown_no_magika.converters._markdownify import _CustomMarkdownify

class MarkdownConverter(_CustomMarkdownify):
    pass