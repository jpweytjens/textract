from .utils import ShellParser
import shutil
from tempfile import mkdtemp
import docx2txt


class Parser(ShellParser):
    """Extract text from doc files using antiword.
    """

    def extract(self, filename, method="", **kwargs):
        if method == "" or method == "antiword":
            return self.extract_antiword(filename)
        elif method == "libreoffice":
            temp_dir = mkdtemp()
            _ = self.convert_doc(filename, temp_dir)
            text = self.extract_docx2txt(temp_dir + "/" + filename + "x")
            shutil.rmtree(temp_dir)

            return text

    def convert_doc(self, filename, directory):

        stdout, _ = self.run(["soffice", "--headless", "--convert-to", "docx", filename, "--outdir", directory])

        return stdout


    def extract_docx2txt(self, filename):

        return docx2txt.process(filename)


    def extract_antiword(self, filename):
        stdout, stderr = self.run(['antiword', filename])
        return stdout
