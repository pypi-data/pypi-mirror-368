from pathlib import Path

from pydantic import field_validator

from wexample_file.excpetion.directory_not_found_exception import DirectoryNotFoundException
from wexample_file.excpetion.not_a_directory_exception import NotADirectoryException
from .abstract_local_item_path import AbstractLocalItemPath


class LocalDirectory(AbstractLocalItemPath):
    """Represents a local directory path.

    The path is stored as a resolved absolute Path. If the path exists, it must
    be a directory.
    """

    @field_validator("path")
    @classmethod
    def _validate_is_dir(cls, v: Path) -> Path:
        if v.exists() and not v.is_dir():
            raise NotADirectoryException(v)
        return v

    def _kind(self) -> str:
        from wexample_file.const.globals import PATH_NAME_DIRECTORY

        return PATH_NAME_DIRECTORY

    def _not_found_exc(self):
        return DirectoryNotFoundException(self.path)

    def remove(self) -> None:
        """Delete the directory recursively if it exists; no-op if it doesn't.

        This method is idempotent and will not raise if the directory is missing.
        """
        if not self.path.exists():
            return
        if self.path.is_dir():
            # Remove contents recursively
            import shutil
            shutil.rmtree(self.path)
        else:
            # If for some reason it's not a dir anymore, best-effort unlink
            try:
                self.path.unlink()
            except FileNotFoundError:
                pass

    def create(self, parents: bool = True, exist_ok: bool = True) -> None:
        if self.path.exists() and self.path.is_file():
            return None

        self.path.mkdir(parents=parents, exist_ok=exist_ok)
