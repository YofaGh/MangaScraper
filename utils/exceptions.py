class MissingModuleException(Exception):
    def __init__(self, domain: str):
        super().__init__(f"No module found for the given domain: {domain}")


class ImageActionException(Exception):
    def __init__(
        self,
        action: str,
        path_to_folder: str,
        invalid_image: str | None,
        images_path: list[str],
    ):
        err = "Unknown"
        if invalid_image:
            err = f"Invalid image: {invalid_image}"
        elif not images_path:
            err = "Empty folder"
        super().__init__(f"Failed to {action} {path_to_folder}: {err}")


class ImageMergerException(ImageActionException):
    def __init__(self, path_to_folder: str, invalid_image: str, images_path: list[str]):
        super().__init__("merge", path_to_folder, invalid_image, images_path)


class PDFConverterException(ImageActionException):
    def __init__(self, path_to_folder: str, invalid_image: str, images_path: list[str]):
        super().__init__("convert", path_to_folder, invalid_image, images_path)


class MissingFunctionException(Exception):
    def __init__(self, domain: str, function: str):
        super().__init__(f"{domain}: {function} function is not yet implemented.")
