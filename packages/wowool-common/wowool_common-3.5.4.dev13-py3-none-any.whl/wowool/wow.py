from pathlib import Path
from sys import stderr
import json
from wowool.utility import is_valid_kwargs, clean_up_empty_keywords
from wowool.utility.method_registry import register, get_bound_jump_table
from wowool.document.analysis.text_analysis import APP_ID as APP_ID_ANALYSIS
from wowool.document.analysis.document import AnalysisDocument
from operator import itemgetter
from wowool.utility.default_arguments import make_document_collection
import logging
from json import JSONEncoder
from os import environ
import gc
from wowool.io.console.console import has_rich

logger = logging.getLogger(__name__)


def print_attributes(attributes, begin="@(", end=")"):
    att = []
    for k, vs in attributes.items():
        for v in vs:
            att.append(f"{k}='{v}'")
    if att:
        print(begin, end="")
        print(*att, sep=",", end=end)


def print_attribute_keys(attributes, begin="@(", end=")"):
    att = []
    for k in attributes:
        att.append(f"{k}")
    if att:
        print(begin, end="")
        print(*att, sep=",", end=end)


class WowJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, set):
            return list(o)
        else:
            return getattr(o, "to_json")() if hasattr(o, "to_json") else super().default(o)


class WowTools:
    def __init__(self, console_):
        # Bind methods to instance
        self.functions = get_bound_jump_table(self)
        self.console = console_

    @register(command="none")
    def tool_none(self, cli, id: str, doc: AnalysisDocument):
        pass

    @register()
    def raw(self, cli, id: str, doc: AnalysisDocument):
        for app in doc.app_ids():
            if app == APP_ID_ANALYSIS:
                self.console.print(f"{app=}")
                if has_rich():
                    self.console.print(doc.results(app).rich())
                else:
                    print(doc.results(app))
            elif app == "wowool-print-annotations":
                app_results = doc.results(app)
                if app_results:
                    print("-" * 40)
                    printed_stream = set()
                    for step in app_results:
                        print(f"- {step['name']}")
                        print(" -" * 20)
                        data = step["data"]
                        print_stream_header = False
                        if "streams" in data:
                            for stream in data["streams"]:
                                if stream["type"] not in printed_stream:
                                    print_stream_header = True
                        if print_stream_header:
                            self.console.print(" <literal>Lexicon input stream:<literal>")
                            if "streams" in data:
                                for stream in data["streams"]:
                                    if stream["type"] not in printed_stream:
                                        printed_stream.add(stream["type"])
                                        self.console.print(f"  <lemma>{stream['type']: <18}</lemma> : {stream['text']}")
                            print(" -" * 20)
                        self.console.print(" <literal>Annotations:</literal>")
                        for sent in data["sentences"]:
                            for annotation in sent[3]:
                                annotation_type = annotation[0]
                                if annotation_type == 2:
                                    print_flags_indent = True
                                    if len(annotation) > 5:
                                        bits = annotation[5]
                                        if "deleted" in bits:
                                            print_flags_indent = False

                                    if print_flags_indent:
                                        self.console.print(
                                            f"   C:({annotation[1]},{annotation[2]}) <uri>{annotation[3]}</uri>",
                                            end="",
                                        )
                                    else:
                                        self.console.print(
                                            f"  [red]-[/red]C:({annotation[1]},{annotation[2]}) {annotation[3]}",
                                            end="",
                                        )
                                    if len(annotation) > 4:
                                        print_attributes(annotation[4])
                                    if len(annotation) > 5:
                                        print_attribute_keys(annotation[5], begin=" $(")
                                    print()

                                elif annotation_type == 3:
                                    self.console.print(
                                        f"\tT:({annotation[1]},{annotation[2]}) [green bold]{annotation[3]}[/ green bold]",
                                        end="",
                                    )
                                    properties = annotation[4]
                                    if properties:
                                        print(" (+", end="")
                                        print(*properties, sep=",+", end=")")

                                    for md in annotation[5]:
                                        print(f"[{md[0]}:{md[1]}", end="")
                                        properties = md[2:]
                                        if properties:
                                            print(" (+", end="")
                                            print(*properties, sep=",+", end=")")
                                        print("]", end="")

                                    print()

            else:
                if doc.results(app):
                    self.console.print(f"{app=}")
                    self.console.print_json(doc.results(app))

        if "show_metadata" in cli.kwargs and cli.kwargs["show_metadata"] and doc.metadata:
            self.console.print("metadata:")
            self.console.print_json(json.dumps(doc.metadata, cls=WowJSONEncoder))

    @register()
    def apps(self, cli, id: str, doc: AnalysisDocument):
        for app in doc.app_ids():
            if app != APP_ID_ANALYSIS:
                self.console.print(f"{app=}")
                self.console.print_json(doc.results(app))

    @register()
    def json(self, cli, id: str, doc: AnalysisDocument):
        jdoc = doc.to_json()
        print(json.dumps(jdoc, ensure_ascii=False))

    @register()
    def text(self, cli, id: str, doc: AnalysisDocument):
        if doc.analysis:
            for sentence in doc.analysis:
                print(sentence.text)
        else:
            print(doc.text)

    @register()
    def canonical(self, cli, id: str, doc: AnalysisDocument):
        from wowool.string import canonicalize

        assert doc.analysis
        for sentence in doc.analysis:
            print(canonicalize(sentence))

    @register(command="input_text")
    def input_text(self, cli, id: str, doc: AnalysisDocument):
        print(doc.text)

    @register()
    def grep(self, cli, id: str, doc: AnalysisDocument):
        from wowool.apps.grep import APP_ID
        from wowool.document.analysis.text_analysis import APP_ID as ID_ANALYSIS

        if not doc.has_results(ID_ANALYSIS):
            return

        grep_results = doc.results(APP_ID)
        if grep_results:
            # self.consolee.print_json(grep_results)
            if cli.grep_results is None:
                cli.grep_results = []
            matches = grep_results["matches"]
            cli.grep_results.extend(matches)
            prev_sentence_idx = -1
            sentences = doc.analysis.sentences
            for match in matches:
                sentence_index = match["sentence_index"]
                if sentence_index != prev_sentence_idx:
                    self.console.print(f"[green]Sentence:[/green] {sentences[sentence_index].text}")
                    prev_sentence_idx = sentence_index
                self.console.print(f" - [bold]{match['text']}[/bold] ")
                for group in match["groups"]:
                    if "literal" in group:
                        self.console.print(f"   - [blue]{group['name']}[/blue] -> {group['text']} = {group['literal']}")
                    else:
                        self.console.print(f"   - [blue]{group['name']}[/blue] -> {group['text']} ")

            self.console.print("- " * 20)

    @register()
    def concepts(self, cli, id: str, doc: AnalysisDocument):
        assert doc.analysis
        for c in doc.analysis.concepts():
            print({**c})

    @register()
    def stagger(self, cli, id: str, doc: AnalysisDocument):
        from wowool.annotation import Entity

        assert doc.analysis is not None
        for sentence in doc.analysis:
            self.console.print(f"""S({sentence.begin_offset},{sentence.end_offset}): "{sentence.text}" """)
            for concept in Entity.iter(sentence, lambda concept: concept.uri != "Sentence"):
                self.console.print(f"""  {concept.uri} -> "{concept.literal}" """, end="")
                if concept.attributes:
                    self.console.print("@( ", end="")
                    for idx, kv in enumerate(concept.attributes.items()):
                        key, value = kv
                        if idx != 0:
                            self.console.print(",", end="")
                        self.console.print(f"{key}=\"{','.join(value)}\"", end="")
                    self.console.print(")", end="")
                self.console.print("")

    @register()
    def stats(self, cli, id: str, doc: AnalysisDocument):
        assert cli.corpus_analyzer, "parent tool has not configured the corpus_analyzer"
        cli.corpus_analyzer(doc)

    def __getitem__(self, function_name: str):
        assert function_name in self.functions, f"Tool '{function_name}' not implemented."
        return self.functions[function_name]


def transform_grep_results(results, expression, console):
    from collections import defaultdict
    from tabulate import tabulate
    import os

    table_format = os.environ["WOWOOL_TABLE_FORMAT"] if "WOWOOL_TABLE_FORMAT" in os.environ else "presto"

    freq = defaultdict(int)
    collocations = {}
    groups = defaultdict(lambda: defaultdict(int))
    for match in results:
        collocation_hash = ""
        freq[match["text"]] += 1
        for group in match["groups"]:
            collocation_hash += f"""{group["name"]}{group["text"]}"""
            groups[group["name"]][group["text"]] += 1

        if len(match["groups"]):
            if collocation_hash in collocations:
                collocations[collocation_hash][0] += 1
            else:
                collocations[collocation_hash] = [1, match]

    freq = sorted(freq.items(), key=lambda k_v: k_v[1], reverse=False)
    collocations = sorted(collocations.items(), key=lambda k_v: k_v[1][0], reverse=False)

    columns = []
    headers = ["cnt"]
    for key, match in collocations:
        for group in match[1]["groups"]:
            headers.append(group["name"])
        break

    console.print("\n[bold]Match:[/bold]\n")
    print(tabulate([[v, k] for k, v in freq], tablefmt=table_format))

    for name, data in groups.items():
        console.print(f"\n[bold]Group: [blue]{name}[/blue][/bold]")
        freq = sorted(data.items(), key=lambda k_v: k_v[1], reverse=False)
        print(tabulate([[v, k] for k, v in freq], tablefmt=table_format))

    if collocations:
        console.print(f"\n[bold]Collocations: [blue]{expression}[/blue][/bold]\n")
        for key, match in collocations:
            item = [match[0]]
            for group in match[1]["groups"]:
                item.append(group["text"])
            columns.append(item)

        print(tabulate(columns, headers=headers, tablefmt=table_format))


def print_grep_results(results, console, **kwargs):
    results = sorted(results.items(), reverse=False, key=itemgetter(1))
    console.print("[", **kwargs)
    total = 0
    # sz = len(results) - 1
    for idx, item in enumerate(results):
        # comma = "," if idx != sz else ""
        total += item[1][0]
        console.print(f"""[{item[1][0]},"{item[0]}", {item[1][1]} ],""", **kwargs)
    console.print(f"""[{total},"TOTAL_COUNT" ]""", **kwargs)
    console.print("]", **kwargs)


class CLI:
    def __init__(self, kwargs, console_=None):
        self.console = console_
        if self.console is None:
            from wowool.io.console import console

            self.console = console

        self.kwargs = kwargs.copy()
        clean_up_empty_keywords(self.kwargs)
        if "expression" in self.kwargs:
            self.tool = "grep"
            kwargs["tool"] = "grep"
            expression = self.kwargs["expression"].replace('"', '\\"')
            if "pipeline" in self.kwargs:
                grep_lemma = "true" if "grep_lemma" in self.kwargs else "false"
                self.kwargs["pipeline"] = f"""{self.kwargs["pipeline"]},grep(expression= " {expression} ", lemma={grep_lemma}).app"""

        if "pipeline" not in self.kwargs and "domains" in self.kwargs:
            # We used domains as a alternative for pipelines
            self.kwargs["pipeline"] = self.kwargs["domains"]
        else:
            pipeline_filename = Path(f"""{self.kwargs["pipeline"]}""")
            if str(pipeline_filename).endswith(".pipeline") and pipeline_filename.exists():
                if pipeline_filename.suffix == ".pipeline":
                    with open(pipeline_filename) as fh:
                        self.kwargs["pipeline"] = fh.readline().strip()
        self.nrof_threads = 1
        if "nrof_threads" in self.kwargs:
            self.nrof_threads = self.kwargs["nrof_threads"]

        # if "tool" not in kwargs:
        self.tool = kwargs["tool"] if "tool" in kwargs else "raw"
        self.file_count = 0
        self.tools = WowTools(self.console)

        self.silent = True if (is_valid_kwargs(kwargs, "silent") and kwargs["silent"] is True) else False

        self.doc_collection = make_document_collection(**kwargs)

        self.corpus_analyzer = None
        self.grep_results = None
        self.ignore_errors = kwargs["ignore_errors"] if "ignore_errors" in kwargs else False

    def process(self, id, doc):
        from wowool.utility.diagnostics import log_diagnostics

        print(id, file=stderr)
        log_diagnostics(doc)
        if not doc:
            return
        self.tools[self.tool](self, id, doc)
        self.file_count += 1

    def run(self):
        try:
            self._run()
        except KeyboardInterrupt:
            if self.grep_results:
                expression = self.kwargs["expression"] if "expression" in self.kwargs else self.kwargs["pipeline"]
                transform_grep_results(self.grep_results, expression, self.console)

    def _run(self):
        assert hasattr(self, "pipeline") and self.pipeline is not None

        if self.tool == "info" or self.doc_collection is None:
            if hasattr(self, "info"):
                return self.info()
            else:
                raise Exception("The tool 'info' is not implemented in this driver")

        if self.nrof_threads >= 1 and "WOWOOL_LOCK_GIL" in environ and environ["WOWOOL_LOCK_GIL"].lower() == "true":
            raise Exception("The environment variable WOWOOL_LOCK_GIL is set to true, this is not supported with multiple threads")

        if self.nrof_threads == 1:
            for ip in self.doc_collection:
                try:
                    self.process(ip.id, self.pipeline(ip))
                except Exception as error:
                    if self.ignore_errors:
                        self.console.print(f"Error while processing '{ip.id()}': {error}")
                    else:
                        raise error
        else:
            from concurrent.futures import ThreadPoolExecutor

            def task(ip):
                try:
                    self.process(ip.id, self.pipeline(ip))
                except Exception as error:
                    if self.ignore_errors:
                        self.console.print(f"Error while processing '{ip.id()}': {error}")
                    else:
                        raise error
                finally:
                    del ip
                    gc.collect()

            with ThreadPoolExecutor(max_workers=self.nrof_threads) as executor:
                executor.map(task, self.doc_collection)

        if self.grep_results:
            expression = self.kwargs["expression"] if "expression" in self.kwargs else self.kwargs["pipeline"]
            transform_grep_results(self.grep_results, expression, self.console)

        if "output" in self.kwargs and self.kwargs["output"] is not None:
            fn = Path(self.kwargs["output"])
            suffix = fn.suffix.lower()
            if self.corpus_analyzer:
                # print(str(self.corpus_analyzer))
                if suffix == ".json":
                    print(f'Saving to: {self.kwargs["output"]}')
                    with open(fn, "w") as wfh:
                        json.dump(self.corpus_analyzer.to_json(), wfh)
                        return
                elif suffix == ".md":
                    print(f'Saving to: {self.kwargs["output"]}')
                    with open(fn, "w") as wfh:
                        wfh.write(self.corpus_analyzer.to_markdown())
                        return

        else:
            if self.corpus_analyzer:
                print(str(self.corpus_analyzer))
