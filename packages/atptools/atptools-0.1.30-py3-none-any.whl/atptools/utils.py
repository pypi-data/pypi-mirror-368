from pathlib import Path


def _path_suffix_check(path: Path | str, suffix: str) -> Path:
    if isinstance(path, str):
        path = Path(path)

    if path.suffix != suffix:
        path = path.with_suffix(suffix)
    return path
