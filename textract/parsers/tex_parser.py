from .utils import ShellParser


class Parser(ShellParser):
    """Parse ``.tex`` files"""

    def extract(self, filename, method="", **kwargs):
        if method == "" or method == "pandoc":
            stdout, _ = self.run(["pandoc", "-f", "latex", "-t", "plain", filename])
            return stdout
        elif method == "opendetex":
            stdout, _ = self.run(["opendetex", filename])
            return stdout
