import os
import shutil
import six
from tempfile import mkdtemp

from ..exceptions import UnknownMethod, ShellError

from .utils import ShellParser
from .image import Parser as TesseractParser


class Parser(ShellParser):
    """Extract text from pdf files using either the ``pdftotext`` method
    (default) or the ``pdfminer`` method.
    """

    def extract(self, filename, method='', dpi=300, **kwargs):
        if method == '' or method == 'pdftotext':
            try:
                return self.extract_pdftotext(filename, **kwargs)
            except ShellError as ex:
                # If pdftotext isn't installed and the pdftotext method
                # wasn't specified, then gracefully fallback to using
                # pdfminer instead.
                if method == '' and ex.is_not_installed():
                    return self.extract_pdfminer(filename, **kwargs)
                else:
                    raise ex

        elif method == 'pdfminer':
            return self.extract_pdfminer(filename, **kwargs)
        elif method == 'tesseract':
            return self.extract_tesseract(filename, dpi, **kwargs)
        else:
            raise UnknownMethod(method)

    def extract_pdftotext(self, filename, **kwargs):
        """Extract text from pdfs using the pdftotext command line utility."""
        if 'layout' in kwargs:
            args = ['pdftotext', '-layout', filename, '-']
        else:
            args = ['pdftotext', filename, '-']
        stdout, _ = self.run(args)
        return stdout


    def convert_pdftoppm(self, filename, directory, dpi, **kwargs):
        """Convert pdf to images for tesseract using pdftoppm."""

        stdout, _ = self.run(['pdftoppm', '-r', str(dpi), filename, directory])

        return stdout

    def convert_imagemagick(self, filename, directory, dpi, **kwargs):
        """Convert pdf to images for tesseract using imagemagick."""

        stdout, _ = self.run(["convert", "-density", str(dpi), "+adjoin", "-alpha", "off", filename, directory + "/" + filename.replace(".pdf", "-%d.png")])

        return stdout

    def extract_pdfminer(self, filename, **kwargs):
        """Extract text from pdfs using pdfminer."""

        stdout, _ = self.run(['pdf2txt.py', filename])

        return stdout

    def extract_tesseract(self, filename, dpi, **kwargs):
        """Extract text from pdfs using tesseract (per-page OCR)."""

        try:
            for convert_pdf in [self.convert_pdftoppm, self.convert_imagemagick]:
                temp_dir = mkdtemp()
                # base = os.path.join(temp_dir, 'conv')
                contents = []

                try:
                    stdout = convert_pdf(filename, temp_dir, dpi)

                    for page in sorted(os.listdir(temp_dir)):
                        page_path = os.path.join(temp_dir, page)
                        page_content = TesseractParser().extract(page_path, **kwargs)
                        contents.append(page_content)

                    return six.b('').join(contents)

                except ShellError:
                    break
        finally:
            shutil.rmtree(temp_dir)
