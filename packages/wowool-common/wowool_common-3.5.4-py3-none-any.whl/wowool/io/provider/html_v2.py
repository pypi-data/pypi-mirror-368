from wowool.document.document_interface import DocumentInterface, MT_PLAINTEXT
from bs4 import BeautifulSoup
import re
from enum import Enum
import logging
from html.parser import HTMLParser

logger = logging.getLogger(__name__)
INTERNAL = 0
logging.addLevelName(INTERNAL, "INTERNAL")


def dict_fmerge(base_dct, merge_dct, add_keys=True):
    rtn_dct = base_dct.copy()
    if add_keys is False:
        merge_dct = {key: merge_dct[key] for key in set(rtn_dct).intersection(set(merge_dct))}

    rtn_dct.update(
        {
            key: (
                dict_fmerge(rtn_dct[key], merge_dct[key], add_keys=add_keys)
                if isinstance(rtn_dct.get(key), dict) and isinstance(merge_dct[key], dict)
                else merge_dct[key]
            )
            for key in merge_dct.keys()
        }
    )
    return rtn_dct


end_sentence_tag = ".\n\n"
begin_list_tag = "\n * "
default_remove = ""


default_config = {
    "tags_begin": {
        "b": default_remove,
        "i": default_remove,
        "u": default_remove,
        "span": default_remove,
        "ul": end_sentence_tag,
        "p": """\n\n""",
        "li": begin_list_tag,
        "title": "# ",
        "h1": "\n# ",
        "h2": "\n\n## ",
        "h3": "\n\n### ",
        "h4": "\n\n#### ",
        "h5": "\n\n##### ",
        "h6": "\n\n###### ",
    },
    "tags_end": {
        "ul": default_remove,
        "b": default_remove,
        "i": default_remove,
        "u": default_remove,
        "span": default_remove,
        "p": end_sentence_tag,
        "li": end_sentence_tag,
        "title": f"{end_sentence_tag}",
        "h1": f"{end_sentence_tag}",
        "h2": f"{end_sentence_tag}",
        "h3": f"{end_sentence_tag}",
        "h4": f"{end_sentence_tag}",
        "h5": f"{end_sentence_tag}",
        "h6": f"{end_sentence_tag}",
    },
    "remove_tags": ["style", "noscript", "footer", "svg", "form", "figure"],
    "remove_class": [
        "copyright",
        "footer",
        "language.*",
        "cookie.*",
        "sitemap.*",
        "nav",
        "quickjump",
        "print",
        "squareAd",
    ],
    "remove_id": [
        "copyright",
        "footer",
        "language.*",
        "cookie.*",
        "sitemap.*",
        "nav",
        "quickjump",
        "print",
        "squareAd",
    ],
    "remove_text": [
        "Visit.*(s|S)ite",
        "Follow.* on .*",
        "Take a look at the .*",
    ],
}

header_tags = {"title", "h1", "h2", "h3", "h4", "h5", "h6"}


def is_last_char(input, char):
    it = reversed(input)
    while (v := next(it, None)) is not None:
        if v == char:
            return True
        elif v == "\n" or v == " ":
            continue
        else:
            return False
    return None


def cleanup_spaces(string):
    split_string = string.split(" ")

    # To account for leading/trailing spaces that would simply be removed
    beg = " " if not split_string[0] else ""
    end = " " if not split_string[-1] else ""

    # versus simply ' '.join(item for item in string.split(' ') if item)
    return beg + " ".join(item for item in split_string if item) + end


def terminates_with_dot(text: str):
    for char in reversed(text):
        if char == ".":
            return True
        elif char == "\n" or char == " ":
            continue
        else:
            return False

    return False


class Content(Enum):
    NONE = 1
    TEXT = 2
    SCRIPT = 3


class MyHTMLParser(HTMLParser):

    def __init__(self, config, script_handler=None):
        super().__init__()
        self.output = ""
        self.strip_tags = {
            "script": 0,
            "style": 0,
            "footer": 0,
            "noscript": 0,
            "svg": 0,
            "form": 0,
        }
        self.content = Content.TEXT
        self.last_inserted_data = ""
        self.tables = []
        self.table_idx = -1
        self.add_table_data = False
        self.tags_begin = config["tags_begin"]
        self.tags_end = config["tags_end"]
        self.analyzer = None
        self.script_data = ""
        self.script_handler = script_handler

    def write(self, data, end=""):
        data = re.sub(r"\n ", " ", data)
        if not data:
            return
        # data_ending = self.output[-4:]
        # current_ending = re.sub(r"(\s|[A-Za-z0-9]|\n)", "", data_ending)
        # data_ending = re.sub(r"(\s|\n)", "", data[:3])
        # # print(f"       ==> [{current_ending}] vs [{data_ending}]")
        # if data_ending == current_ending:
        #     # print("do not add")
        #     return
        # if self.output and len(data) == 1 and self.output[-1] == "\n" and self.output[-1] == data[0]:
        #     return

        # re.match(r"^\s*$", data)
        # print(f"Write: [{data=}] [{self.output[-20:]}]")
        if data.startswith(".") and terminates_with_dot(self.output):
            data = data[1:]  # remove leading dot if output already ends with a dot
        if self.output.endswith(" ") and data.startswith(" "):
            data = data.lstrip(" ")
        self.output += data
        if self.output.endswith("  "):
            self.output = self.output.rstrip(" ")
            self.output += " "

    def write_text(self, data):
        # if len(self.output) >= 1 and self.output[-1] == "\n":
        #     if data.startswith(".\n"):
        #         self.output = f"{self.output[:-1]+' '+data}"
        #     else:
        #         self.write(data.strip())
        if len(self.output) > 1 and self.output[-1] == "\n":
            self.write(data.strip())
        else:
            self.write(data)

    def reset_tables(self):
        self.tables.clear()
        self.table_idx = -1

    def handle_starttag(self, tag, attrs):
        logger.log(INTERNAL, f"<{tag}>, [{self.output[-20:]}]")
        if tag in self.tags_begin:
            self.write(self.tags_begin[tag])
            if tag in header_tags:
                if is_last_char(self.output, ".") is False:
                    if self.output[-1] == "\n":
                        self.output = self.output.rstrip("\n")
                    # self.write(".\n\n")

        elif tag == "script":
            # print("TAG:Script")
            self.content = Content.SCRIPT
            self.strip_tags[tag] += 1

        elif tag in self.strip_tags:
            self.strip_tags[tag] += 1
            self.content = Content.NONE

        elif tag == "table":
            self.tables.append({"headers": [], "idx": -1, "field": None})
            self.table_idx = len(self.tables) - 1
        elif tag == "tr":
            try:
                self.tables[self.table_idx]["idx"] = 0
            except Exception:
                self.reset_tables()

        elif tag == "th":
            try:
                self.add_table_data = True
                self.tables[self.table_idx]["headers"].append([])
                self.tables[self.table_idx]["idx"] = len(self.tables[self.table_idx]["headers"]) - 1
            except Exception:
                self.reset_tables()

        elif tag == "td":
            try:
                field = "\n"
                for table in self.tables:
                    idx = table["idx"]
                    text = table["headers"][idx]
                    field += f"{text}:"
                self.tables[self.table_idx]["field"] = field
            except Exception:
                self.reset_tables()

        else:
            self.write_text(" ")

    def handle_endtag(self, tag):
        logger.log(INTERNAL, f"</{tag}>, [{self.output[-20:]}]")
        if tag in self.tags_end:
            self.write_text(self.tags_end[tag])
            if tag in header_tags:
                if is_last_char(self.output, ".") is False:
                    self.write(".\n")
        elif tag == "script":
            if self.script_handler:
                self.write(self.script_handler(self.script_data))
                self.script_data = ""
            self.content = Content.TEXT
            self.strip_tags[tag] -= 1
        elif tag in self.strip_tags:
            self.strip_tags[tag] -= 1
            if self.strip_tags[tag] == 0:
                self.content = Content.TEXT
        elif tag == "table":
            try:
                if self.tables:
                    self.tables.pop()
                    self.table_idx = len(self.tables) - 1
                else:
                    self.table_idx = -1
            except Exception:
                self.reset_tables()
        elif tag == "th":
            try:
                idx = self.tables[self.table_idx]["idx"]
                self.tables[self.table_idx]["headers"][idx] = " ".join(filter(None, self.tables[self.table_idx]["headers"][idx]))
            except Exception:
                self.reset_tables()
        elif tag == "tr":
            self.add_table_data = False
        elif tag == "br" or tag == "div":
            self.write("\n")
        elif tag == "td":
            try:
                if self.table_idx >= 0:
                    # idx = self.tables[self.table_idx]['idx']
                    # text = self.tables[self.table_idx]['headers'][idx]
                    self.last_inserted_data = ""
                    self.write(end_sentence_tag)
                    self.tables[self.table_idx]["idx"] += 1
            except Exception:
                self.reset_tables()
        else:
            self.write_text(" ")

    def handle_data(self, data):
        logger.log(INTERNAL, f"  {data=}, [{self.output[-20:]}]")
        if self.content == Content.TEXT:
            text = cleanup_spaces(data)
            if text:
                if self.table_idx >= 0:
                    try:
                        if self.add_table_data:
                            idx = self.tables[self.table_idx]["idx"]
                            text = text.strip()
                            if text:
                                self.tables[self.table_idx]["headers"][idx].append(text.strip())
                            return

                        if self.tables[self.table_idx]["field"]:
                            self.write_text(self.tables[self.table_idx]["field"])
                            self.tables[self.table_idx]["field"] = None
                    except Exception:
                        self.reset_tables()

                self.write_text(text)
            else:
                self.write_text(" ")
        elif self.content == Content.SCRIPT:
            self.script_data += data


def cleanup_output(text):
    text = re.sub(r"\n.\n", ".\n\n", text)
    text = re.sub(r"\n{3,5}", "\n\n", text)
    text = text.replace("\n.\n", "\n")
    return text


class HTMLFileInputProvider(DocumentInterface):

    def __init__(
        self,
        fid,
        data=None,
        config=None,
        merge=True,
        encoding="utf8",
        script_handler=None,
        use_readability: bool = True,
        metadata: dict | None = None,
        css_selector: str | None = None,
        **kwargs,
    ):
        self._id = str(fid)
        if config:
            if merge:
                self.config = dict_fmerge(default_config, config)
            else:
                self.config = config
        else:
            self.config = default_config
        self.encoding_ = encoding
        self.html_data = data
        self._text = None
        self.script_handler = script_handler
        self.use_readability = use_readability
        self._metadata = metadata if metadata is not None else {}
        self.css_selector = css_selector

    def _get_text(self, input):
        if self.use_readability and input:
            if isinstance(input, bytes):
                input = input.decode(self.encoding_ or "utf-8")
            try:
                from readability import Document

                readability_doc = Document(input)
                title = readability_doc.title()
                input = f"<title>{title}</title>" if title != "[no-title]" else ""
                input += readability_doc.summary(True)

            except ModuleNotFoundError as ex:
                logger.error(
                    f"Readability is probably not installed, install the package using 'pip install readability-lxml lxml_html_clean.' {ex}"
                )
            except ValueError:
                # going brute force
                pass
            except Exception as ex:
                logger.exception(ex)

        soup = BeautifulSoup(input, "html.parser")

        if "remove_tags" in self.config:
            remove_tags = self.config["remove_tags"]
            if self.script_handler:
                del remove_tags[0]
            # kill all script and style elements
            for script in soup(remove_tags):
                script.extract()  # rip it out

        if "remove_class" in self.config:
            remove_class = self.config["remove_class"]
            remove_pattern = re.compile("|".join(remove_class))
            remove_pattern = f"^({remove_pattern})$"
            for element in soup.find_all(class_=remove_pattern):
                element.extract()  # rip it out

        if "remove_id" in self.config:
            remove_id = self.config["remove_id"]
            remove_pattern = re.compile("|".join(remove_id))
            remove_pattern = f"^({remove_pattern})$"
            for element in soup.find_all(id=remove_pattern):
                element.extract()  # rip it out

        if "remove_text" in self.config:
            remove_text = self.config["remove_text"]
            remove_pattern = re.compile("|".join(remove_text))
            remove_pattern = f"^({remove_pattern})$"
            for element in soup.find_all(string=remove_pattern):
                element.parent.extract()  # rip it out

        if "remove_parent_text" in self.config:
            remove_parent_text = self.config["remove_parent_text"]
            remove_pattern = re.compile("|".join(remove_parent_text))
            remove_pattern = f"^({remove_pattern})$"
            for element in soup.find_all(string=remove_pattern):
                element.parent.parent.extract()  # rip it out

        if self.css_selector:
            # remove all elements that do not match the css selector
            # for element in soup.select(f":not({self.css_selector})"):
            #     element.extract()
            input_data = "\n".join(str(element) for element in soup.select(self.css_selector))
        else:
            # cleanup html
            input_data = soup.prettify(formatter="html")
        # print(f"Input data: {input_data}")

        # remove spaces in front of tags
        input_data = re.sub(r"\n^\s+", r" ", input_data, flags=re.MULTILINE)
        parser = MyHTMLParser(self.config, self.script_handler)
        parser.feed(input_data)
        # .decode("unicode_escape")
        output = cleanup_output(parser.output)
        return output

    @property
    def id(self):
        return self._id

    @property
    def mime_type(self) -> str:
        return MT_PLAINTEXT

    @property
    def encoding(self) -> str:
        return "utf-8"

    @property
    def data(self):
        if self._text is not None:
            return self._text
        elif self.html_data is not None:
            _text = self._get_text(self.html_data)
            return _text
        else:
            # read from file
            with open(self.id, "r", encoding=self.encoding) as fh:
                html_data = fh.read()
            _text = self._get_text(html_data)
            return _text

    @property
    def metadata(self) -> dict:
        return self._metadata
