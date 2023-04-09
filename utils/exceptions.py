class TruncatedException(Exception):
    def __init__(self, save_path):
        self.save_path = save_path
        self.message = f' {save_path} was truncated. trying to download it one more time...'
        super(TruncatedException, self).__init__(self.message)

class MissingModuleException(Exception):
    def __init__(self, domain):
        self.domain = domain
        self.message = f'No module found for the given domain: {self.domain}'
        super(MissingModuleException, self).__init__(self.message)

class UnknownModuleException(Exception):
    def __init__(self, module):
        self.module = module
        self.message = f'No domain found for the given module: {self.module}'
        super(UnknownModuleException, self).__init__(self.message)

class ImageMergerException(Exception):
    def __init__(self, message):
        self.message = message
        super(ImageMergerException, self).__init__(message)

class PDFConverterException(Exception):
    def __init__(self, message):
        self.message = message
        super(PDFConverterException, self).__init__(message)

class MissingFunctionException(Exception):
    def __init__(self, domain):
        self.domain = domain
        self.message = f'{self.domain}: Search function is not yet implemented.'
        super(MissingFunctionException, self).__init__(self.message)