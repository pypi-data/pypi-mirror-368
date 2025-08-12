# flake8: noqa: E402

import pdfminer.settings
from wowool.io.provider import InputProvider

pdfminer.settings.STRICT = False
import pdfminer.high_level
from pathlib import Path
from io import StringIO


def pdf_to_text(pdfname, codec="utf-8"):
    # PDFMiner boilerplate
    sio = StringIO()
    fp = open(pdfname, "rb")
    pdfminer.high_level.extract_text_to_fp(fp, sio, codec="utf-8", layoutmode="normal", line_margin=0.5, word_margin=1)
    text = sio.getvalue()
    sio.close()

    return text


class PdfFileInputProvider(InputProvider):
    def __init__(self, fid):
        InputProvider.__init__(self, fid)
        fn = Path(self.id())
        self.cfn = fn.with_suffix("._txt")

    @property
    def text(self, **kwargs):
        if self.cfn.exists():
            with open(self.cfn) as fd:
                return fd.read()
        else:
            try:
                with open(self.cfn, "w") as fd:
                    data = pdf_to_text(self.id())
                    fd.write(data)
                    return data
            except Exception as ex:
                print("Cannot create cache file", ex)
                return pdf_to_text(self.id())
