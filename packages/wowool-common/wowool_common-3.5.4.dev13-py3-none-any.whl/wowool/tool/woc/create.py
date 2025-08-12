from pathlib import Path


def create_project(fn_project: Path, language: str = "english") -> Path:
    """create a project skeleton with a project file (.wopr)"""
    assert language, "language should not be None"
    ffn = fn_project.expanduser().resolve()
    fn_wopr = ffn / Path(ffn.stem).with_suffix(".wopr")
    project_root = fn_wopr.parent
    project_name = fn_wopr.stem
    project_name_initcap = project_name.capitalize()
    if project_name_initcap.endswith("s"):
        # beers -> become Beer
        project_name_initcap = project_name_initcap[:-1]

    if project_root.exists():
        raise RuntimeError(f"The project '{fn_project}' already exists")

    project_root.mkdir(parents=True)
    with open(fn_wopr, "w") as fh:
        fh.write(
            f"""{{
  "domain": "{project_name}",
  "language": "{language}",
  "concepts": ["{project_name_initcap}"],
  "sources": ["src/{project_name}.wow"]
}}
"""
        )
    fp_project_src = project_root / "src"
    fp_project_src.mkdir(parents=True)
    fn_project_src = fp_project_src / f"{project_name}.wow"

    with open(fn_project_src, "w") as fh:
        fh.write(
            f"""
lexicon:(input="normalized_stem") {{
  {project_name},
}}={project_name_initcap}@(example_att = "some stuff");
        """
        )
    return fn_wopr
