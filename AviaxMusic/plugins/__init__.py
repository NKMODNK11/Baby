from pathlib import Path


def _list_all_modules():
    work_dir = Path(__file__).parent

    return sorted(
        "." + ".".join(path.relative_to(work_dir).with_suffix("").parts)
        for path in work_dir.glob("*/*.py")
        if path.name != "__init__.py"
    )


ALL_MODULES = _list_all_modules()
__all__ = ALL_MODULES + ["ALL_MODULES"]
