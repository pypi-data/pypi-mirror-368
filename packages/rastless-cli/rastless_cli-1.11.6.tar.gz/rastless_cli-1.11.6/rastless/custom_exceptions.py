class CustomError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class SensorNotDefinedError(Exception):
    pass


class LayerStepExistsError(Exception):
    pass


class LayerStepAppendOverwriteError(Exception):
    pass


class FileUploadError(Exception):
    pass


class ColorMapParseError(Exception):
    pass


class ColorMapDoesNotExistError(Exception):
    pass
