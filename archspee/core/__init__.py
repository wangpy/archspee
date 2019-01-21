from abc import ABC, abstractmethod
import logging
logging.basicConfig()

def fullname(o):
    # o.__module__ + "." + o.__class__.__qualname__ is an example in
    # this context of H.L. Mencken's "neat, plausible, and wrong."
    # Python makes no guarantees as to whether the __module__ special
    # attribute is defined, so we take a more circumspect approach.
    # Alas, the module name is explicitly excluded from __qualname__
    # in Python 3.

    module = o.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return o.__class__.__name__  # Avoid reporting __builtin__
    else:
        return module + '.' + o.__class__.__name__

_LOG_LEVELS = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG
}

def _get_log_level(log_level_str):
    assert log_level_str in _LOG_LEVELS
    return _LOG_LEVELS[log_level_str]

class ArchspeeBaseClass(ABC):
    def __init__(self):
        self.logger = logging.getLogger(fullname(self))
        self.logger.setLevel(logging.INFO)
        try:
            if self.__log_level is not None:
                self.logger.setLevel(get_log_level(self.__log_level))
        except:
            pass
