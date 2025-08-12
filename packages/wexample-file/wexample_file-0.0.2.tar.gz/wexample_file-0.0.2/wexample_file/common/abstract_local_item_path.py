from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, model_validator
from wexample_file.excpetion.local_path_not_found_exception import LocalPathNotFoundException


class AbstractLocalItemPath(BaseModel, ABC):
    """Abstract base class for handling local file system paths.

    Accepts either a string or a pathlib.Path for ``path`` and always stores a
    resolved absolute Path (with user home expanded). This keeps comparisons and
    downstream usage consistent regardless of how the input was provided.
    """
    path: Path = Field(description="The path to the file or directory")
    check_exists: bool = False

    @field_validator("path", mode="before")
    @classmethod
    def _coerce_and_resolve_path(cls, v):
        """Coerce input into a resolved Path.

        - Accepts str or Path
        - Expands '~' and resolves to an absolute path with strict=False
        """
        if isinstance(v, str):
            v = Path(v)
        if isinstance(v, Path):
            return v.expanduser().resolve(strict=False)
        raise TypeError("path must be a str or pathlib.Path")

    @model_validator(mode="after")
    def _validate_existence(self):
        """If check_exists is True, ensure the path exists."""
        if self.check_exists and not self.path.exists():
            # Defer to subclass to choose the most specific exception
            exc = self._not_found_exc()
            if exc is None:
                # Fallback to a generic not-found exception
                raise LocalPathNotFoundException(self.path)
            raise exc
        return self

    @abstractmethod
    def _kind(self) -> str:
        """Return the kind of local item (e.g., 'file' or 'directory').

        Subclasses must implement this to mark the class as abstract and to
        provide a simple discriminator for debugging and representation.
        """

    @abstractmethod
    def _not_found_exc(self) -> Exception | None:
        """Return a specific 'not found' exception instance for this item type.

        Subclasses should return an instance of a custom exception that best
        represents the missing path for their type (e.g., FileNotFoundException
        or DirectoryNotFoundException). Returning None will make the base class
        fall back to LocalPathNotFoundException.
        """

    @abstractmethod
    def remove(self) -> None:
        """Remove the underlying path from the filesystem.

        - For a file implementation, this should delete the file.
        - For a directory implementation, this should delete the directory
          recursively.
        - This operation should be idempotent: if the path does not exist,
          the method should complete without raising.
        """

    def __str__(self) -> str:
        return str(self.path)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={repr(str(self.path))}, check_exists={self.check_exists})"

    def __eq__(self, other) -> bool:
        if isinstance(other, AbstractLocalItemPath):
            return self.path == other.path
        if isinstance(other, (str, Path)):
            other_path = Path(other).expanduser().resolve(strict=False)
            return self.path == other_path
        return NotImplemented
