import warnings
from fiona import FionaDeprecationWarning

def ignoreWarnings():
    warnings.filterwarnings("ignore", category=FionaDeprecationWarning)

