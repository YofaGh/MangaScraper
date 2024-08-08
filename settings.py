import os

LOGGING: bool = True
SLEEP_TIME: int | float = 0.1
AUTO_MERGE: bool = False
AUTO_PDF_CONVERSION: bool = False
FIT_MERGE: bool = False
SEARCH_PAGE_LIMIT: int = 3
SEARCH_ABSOLUTE: bool = False
MODULES_FILE_PATH: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'modules.yaml')