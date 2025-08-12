import logging
from xml.etree import ElementTree

import markdown

log = logging.getLogger(__name__)

# Global Vars
URLIZE_RE = "(%s)" % "|".join(
    [
        r"<(?:f|ht)tps?://[^>]*>",
        r"\b(?:f|ht)tps?://[^)<>\s]+[^.,)<>\s]",
        r"\bwww\.[^)<>\s]+[^.,)<>\s]",
        r"[^(<\s]+\.(?:com|net|org)\b",
    ]
)


class UrlizePattern(markdown.inlinepatterns.Pattern):
    """This code comes from https://github.com/r0wb0t/markdown-urlize,
    and is made compatible with Python Markdown 3.4."""

    def handleMatch(self, m):
        url = m.group(2)

        if url.startswith("<"):
            url = url[1:-1]

        text = url

        if url.split("://")[0] not in ("http", "https", "ftp"):
            if "@" in url and "/" not in url:
                url = "mailto:" + url
            else:
                url = "http://" + url

        el = ElementTree.Element("a")
        el.set("href", url)
        el.text = markdown.util.AtomicString(text)
        return el


class UrlizeExtension(markdown.Extension):
    """Urlize Extension for Python-Markdown."""

    def extendMarkdown(self, md):
        """Replace autolink with UrlizePattern"""
        md.inlinePatterns.register(UrlizePattern(URLIZE_RE, md), "autolink", 120)


def markdown_publish(context, data):
    """publish a string formatted as MarkDown Text to HTML

    :type context: a cubicweb application object

    :type data: str
    :param data: some MarkDown text

    :rtype: unicode
    :return:
      the data formatted as HTML or the original data if an error occurred
    """
    md = markdown.Markdown(extensions=["extra", UrlizeExtension()])
    try:
        return md.convert(data)
    except Exception:
        import traceback

        traceback.print_exc()
        log.exception("Error while converting Markdown to HTML")
        return data
