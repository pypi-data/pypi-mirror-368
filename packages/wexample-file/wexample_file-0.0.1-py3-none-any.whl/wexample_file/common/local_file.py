from pathlib import Path

from pydantic import field_validator

from wexample_file.excpetion.file_not_found_exception import FileNotFoundException
from wexample_file.excpetion.not_a_file_exception import NotAFileException
from .abstract_local_item_path import AbstractLocalItemPath


class LocalFile(AbstractLocalItemPath):
    """Represents a local file path.

    The path is stored as a resolved absolute Path. If the path exists, it must
    be a file.
    """

    @field_validator("path")
    @classmethod
    def _validate_is_file(cls, v: Path) -> Path:
        # Only validate type when it exists; creation workflows may pass a non-existent path
        if v.exists() and not v.is_file():
            raise NotAFileException(v)
        return v

    def _kind(self) -> str:
        from wexample_file.const.globals import PATH_NAME_FILE

        return PATH_NAME_FILE

    def _not_found_exc(self):
        return FileNotFoundException(self.path)

    def remove(self) -> None:
        """Delete the file if it exists; no-op if it doesn't.

        This method is idempotent and will not raise if the file is missing.
        """
        try:
            # unlink(missing_ok=True) is available in Python 3.8+
            self.path.unlink(missing_ok=True)
        except TypeError:
            # Fallback for older Python: check existence first
            if self.path.exists():
                self.path.unlink()

    def read(self, encoding: str = "utf-8") -> str | None:
        """Read and return the file content as text, or None if it doesn't exist.

        Parameters:
            encoding: Text encoding used to decode file content. Defaults to 'utf-8'.
        """
        if not self.path.exists() or not self.path.is_file():
            return None

        return self.path.read_text(encoding=encoding)

    def touch(self, parents: bool = True, exist_ok: bool = True) -> bool:
        if parents:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists() or self.path.is_dir():
            return False

        self.path.touch(exist_ok=exist_ok)
        return True

    def write(self, content: str, encoding: str = "utf-8", make_parents: bool = True) -> None:
        """Write text content to the file, creating it if necessary.
        """
        if make_parents:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists() and self.path.is_dir():
            raise NotAFileException(self.path)
        self.path.write_text(content, encoding=encoding)

    def get_extension(self) -> str:
        """Return the last suffix without the leading dot.

        Examples:
            "archive.tar.gz" -> "gz"
            "report.pdf" -> "pdf"
            "README" -> ""
        """
        suf = self.path.suffix
        return suf[1:] if suf.startswith(".") else ""

    def change_extension(self, new_extension: str) -> None:
        # Normalize extension: allow callers to pass with or without dot
        ext = new_extension.lstrip(".")
        suffix = f".{ext}" if ext else ""
        target = self.path.with_suffix(suffix)

        self.path.replace(target)

    def is_empty(self) -> bool:
        return Path(self.path).stat().st_size == 0