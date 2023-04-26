class MissingModuleException(Exception):
    def __init__(self, domain):
        self.domain = domain
        self.message = f'No module found for the given domain: {self.domain}'
        super(MissingModuleException, self).__init__(self.message)

class ImageMergerException(Exception):
    def __init__(self, message):
        self.message = message
        super(ImageMergerException, self).__init__(message)

class PDFConverterException(Exception):
    def __init__(self, message):
        self.message = message
        super(PDFConverterException, self).__init__(message)

class MissingFunctionException(Exception):
    def __init__(self, domain, function):
        self.domain = domain
        self.function = function
        self.message = f'{self.domain}: {self.function} function is not yet implemented.'
        super(MissingFunctionException, self).__init__(self.message)