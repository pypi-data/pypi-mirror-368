import re
from logging import getLogger
from bs4 import BeautifulSoup, Comment

logger = getLogger(__name__)


remove_tags = ["script", "style", "noscript", "footer", "svg", "form"]


def cleanup_scripts(input: str):
    soup = BeautifulSoup(input, "html.parser")
    for script in soup(remove_tags):
        script.extract()  # rip it out

    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    # Iterate over the comments and print them
    for comment in comments:
        comment.extract()

    html_data = soup.prettify(formatter="minimal")
    return html_data


class SkipDocument(Exception):
    pass


def cleanup_text(text: str, filters: list, strip_lines=True, exceptions=[]):
    lines = text.splitlines()
    new_lines = []
    for line in lines:
        exclude = None
        if strip_lines:
            line = line.strip()
        for exception in exceptions:
            if "starts_with" in exception:
                if line.startswith(exception["starts_with"]):
                    raise SkipDocument(f"""Exception filter {exception["starts_with"]}""")
            elif "regex" in exception:
                if "regex_" not in exception:
                    exception["regex_"] = re.compile(exception["regex"])
                m = exception["regex_"].search(line)
                if m:
                    raise SkipDocument(f"""Exception filter {exception["regex"]}""")
        for filter in filters:
            if "starts_with" in filter:
                if line.startswith(filter["starts_with"]):
                    # print("removing line starts_with ", line)
                    if "remove" in filter:
                        exclude = filter["remove"]
                    else:
                        exclude = "line"
            elif "regex" in filter:
                pattern = re.compile(filter["regex"])
                m = pattern.search(line)
                if m:
                    if "remove" in filter:
                        if filter["remove"] == "match":
                            substring = filter["sub"] if "sub" in filter else ""
                            line = pattern.sub(substring, line)
                        else:
                            exclude = filter["remove"]
                    else:
                        exclude = "line"
            elif "match" in filter:
                if line == filter["match"]:
                    exclude = "line"
            else:
                raise ValueError("Unknown filter, possible values are starts_with, regex")
            if exclude:
                break

        if not exclude:
            new_lines.append(line)
        elif exclude == "line":
            logger.debug(f"Removing line {line}")
            pass
        elif exclude == "eof":
            logger.debug(f"Removing until eof {line}")
            break
    return "\n".join(new_lines)
