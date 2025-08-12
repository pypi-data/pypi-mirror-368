from wexample_file.excpetion.local_path_not_found_exception import LocalPathNotFoundException


class DirectoryNotFoundException(LocalPathNotFoundException):
    error_code: str = "DIRECTORY_NOT_FOUND"

    def __init__(self, path, message: str | None = None):
        msg = message or f"Directory does not exist: {path}"
        super().__init__(path=path, message=msg)
