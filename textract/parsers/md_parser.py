from .utils import BaseParser
import markdown


class Parser(BaseParser):
    """Parse ``.md`` files"""

    def extract(self, filename, method="", **kwargs):
        with open(filename) as stream:
            text = stream.read()

        if method == "" or method == "txt":
            return text

        elif method == "markdown":
            text = markdown.markdown(text)
            return text
