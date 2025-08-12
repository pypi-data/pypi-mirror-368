from wowool.diagnostic import Diagnostics, Diagnostic, DiagnosticType
from wowool.document.analysis.document import AnalysisDocument
from functools import wraps
from wowool.document.analysis.text_analysis import APP_ID as APP_ID_ANALYSIS
from typing import Callable
from wowool.document.analysis.utilities import get_pipeline_concepts


def exceptions_to_diagnostics(
    fn: Callable[..., AnalysisDocument],
) -> Callable[..., AnalysisDocument]:
    @wraps(fn)
    def wrapper(self, document: AnalysisDocument, *args, **kwargs):
        diagnostics = Diagnostics()
        app_id = self.ID if hasattr(self, "ID") else f"{type(self)}"
        try:
            document = fn(self, document, *args, diagnostics=diagnostics, **kwargs)
        except Exception as ex:
            if isinstance(document, AnalysisDocument):
                diagnostics.add(Diagnostic(document.id, f"Exception {ex}", DiagnosticType.Critical))
            else:
                raise ex
        if diagnostics:
            document.add_diagnostics(app_id, diagnostics)
        return document

    return wrapper


def requires_app(app_id):
    def decorator(fn):
        @wraps(fn)
        def wrapper(self, document: AnalysisDocument, diagnostics: Diagnostics, *args, **kwargs):
            if not document.has(app_id):
                diagnostics.add(Diagnostic(document.id, f"Missing {app_id}", DiagnosticType.Critical))
                return document

            result = fn(self, document, *args, diagnostics=diagnostics, **kwargs)
            return result

        return wrapper

    return decorator


def requires_analysis(fn):
    @wraps(fn)
    def wrapper(self, document: AnalysisDocument, diagnostics: Diagnostics, *args, **kwargs):
        if not isinstance(document, AnalysisDocument):
            raise TypeError("Document must be an AnalysisDocument")
        if not document.has_results(APP_ID_ANALYSIS):
            diagnostics.add(Diagnostic(document.id, f"Missing language component ({APP_ID_ANALYSIS})", DiagnosticType.Critical))
            return document
        document = fn(self, document, *args, diagnostics=diagnostics, **kwargs)
        return document

    return wrapper


def check_requires_concepts(app_id, document: AnalysisDocument, diagnostics: Diagnostics, required_concepts, msg=None):
    available_entities = get_pipeline_concepts(document)
    if not available_entities or (available_entities & required_concepts) != required_concepts:
        if msg is None:
            if document.metadata:
                missing_concepts = required_concepts - (available_entities & required_concepts)
            else:
                missing_concepts = required_concepts
            msg = f"Missing a domain that can produce any of these required concepts: {missing_concepts}, add a domain domain in your pipeline."
        diagnostics.add(Diagnostic(document.id, msg, DiagnosticType.Warning))
        document.add_diagnostics(app_id, diagnostics)
