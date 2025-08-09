import abc 
import logging 
import functools
from types import FunctionType, MethodType

from ._logger import JSONFormatter


class BaseReporter(abc.ABC):
    
    def __init__(self, func: FunctionType = None, *,logger: logging.Logger|None = None):
        self._func = func 
        if func is not None:
            self.__name__ = func.__name__
            self.__qualname__ = func.__qualname__
        self.logger = logger if logger is not None else \
                (self._get_logger() if func is not None and logger is None else None)
        for hdlr in self.logger.handlers:
            hdlr.setFormatter(JSONFormatter())
        
        

    def _get_logger(self):
        logger = logging.getLogger(self.__name__)
        logger.setLevel(logging.DEBUG)
        strm_hdlr = logging.StreamHandler()
        strm_hdlr.setLevel(logging.DEBUG)
        strm_hdlr.setFormatter(JSONFormatter())
        if not logger.handlers:
            logger.addHandler(strm_hdlr)
        return logger
    
    @property
    def __annotations__(self):
        return self._func.__annotations__ 
    
    @property
    def __closure__(self):
        return self._func.__closure__
    
    @property
    def __code__(self):
        return self._func.__code__
    
    @property
    def __defaults__(self):
        return self._func.__defaults__
    
    @property
    def __kwdefaults__(self):
        return self._func.__kwdefaults__
    
     
    def __dir__(self):
        return dir(self._func)
    
    def __get__(self, obj = None, cls = None):
        # return container that hold, obj and cls 
        return ReporterHelper(reporter = self, obj = obj, cls = cls)
    
    @abc.abstractmethod
    def __call__(self, *args,**kwargs):
        pass


    
class ReporterHelper:
    def __init__(self, reporter: BaseReporter, obj = None,cls = None):
        self.reporter = reporter
        self.obj = obj
        self.cls = cls

    def __repr__(self):
        return repr(self.reporter)
    
    def __call__(self,*args,**kwargs):
        return self.reporter(*args,obj = self.obj,cls = self.cls,**kwargs)

    def __getattribute__(self, attr):
        if attr not in ['reporter','obj','cls']:
            return getattr(self.reporter, attr)

        return super().__getattribute__(attr)

