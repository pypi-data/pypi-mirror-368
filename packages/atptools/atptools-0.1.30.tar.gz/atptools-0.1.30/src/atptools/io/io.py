from pathlib import Path


def save_to_file(
    file_content: bytes | str,
    path: str | Path,
) -> None:
    if isinstance(file_content, str):
        with open(path, "w", encoding="utf-8") as file:
            file.write(file_content)
    elif isinstance(file_content, bytes):
        with open(path, "wb") as file:
            file.write(file_content)
    else:
        raise Exception("Invalid file content")

    return None


def load_from_file(path: str | Path) -> bytes:
    with open(path, "rb") as file:
        return file.read()


def load_from_file_str(
    path: str | Path,
    encoding: str = "utf-8",
) -> str:
    with open(path, encoding=encoding) as file:
        return file.read()
