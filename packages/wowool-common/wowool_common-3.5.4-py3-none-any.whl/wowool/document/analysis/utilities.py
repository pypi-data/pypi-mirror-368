from wowool.document.analysis.document import AnalysisDocument


def get_pipeline_concepts(document: AnalysisDocument) -> set[str]:
    return document.pipeline_concepts
