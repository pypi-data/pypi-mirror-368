import logging
import inspect
import functools
from typing import Generator

from ._bases import BaseReporter 



class _ProxyReporter:
    def __init__(self, func,gen, logger, attrs):
        self._gen = gen
        self.__name__, self.__qualname__ = gen.__name__, gen.__qualname__
        self._logger = logger 
        self._attrs = attrs
        self._func = func

    
    def __iter__(self):
        class_name = self.__class__.__name__
        self._logger.info({"msg":self.__name__,"filename":self._func.__code__.co_filename})
        i = None
        entered_sub_gen = False
        f_locals = None
        while True:
            try:
                result = self._gen.send(i)
                i = yield result 
            except StopIteration as e: # PEP 479 raising StopIteration within genrators raise RuntimeError
                self._logger.info({"msg": {f"return_value_of_{self.__name__}": repr(e.value)}, "filename": self._func.__code__.co_filename} | ({} if self._gen.gi_frame is None else {"lineno": self._gen.gi_frame.f_lineno }))
                return e.value
            
            except GeneratorExit as e:
                self._gen.close()
                self._logger.info({"msg": f'{self._gen.__name__!r} closed.', "filename": self._func.__code__.co_filename} | ({} if self._gen.gi_frame is None else {"lineno": self._gen.gi_frame.f_lineno }))
                raise
            
            except Exception as e:
                try:
                    i = self._gen.throw(e)
                    
                    
                except StopIteration as ex:# PEP 479 raising StopIteration within genrators raise RuntimeError
                    self._logger.info({"msg": {f"return_value_of_{self.__name__}": repr(e.value)}, "filename": self._func.__code__.co_filename} | ({} if self._gen.gi_frame is None else {"lineno": self._gen.gi_frame.f_lineno }))
                    return ex.value
                except Exception as e:
                    self._logger.error({"msg": "Unhandled error", "err":repr(e),"filename": self._func.__code__.co_filename} | ({} if self._gen.gi_frame is None else {"lineno": self._gen.gi_frame.f_lineno }))
                    raise e
                else:
                    i = yield i
                    self._logger.info({"msg": f"{self.__name__!r} recovered from exception `.throw`: exception as {e!r}", "filename": self._func.__code__.co_filename} | ({} if self._gen.gi_frame is None else {"lineno": self._gen.gi_frame.f_lineno }))
                

                    
            
                
            else:
                if not entered_sub_gen and self._gen.gi_yieldfrom is not None:
                    # assign that there is a subgenrator delgation
                    entered_sub_gen = True 
                    # to get correct subgenrator name instead of it being ProxyReporter.__iter__
                    # we check if the `sub genrator` name is ProxyReporter.__iter__
                    # if yes:
                    #        it means the subgenrator is decorated with @Reporter. so we read the value from gi_frame.f_locals. ===> This is equal to self._gen.gi_yieldfrom.gi_frame.f_locals['self']  `self`
                    # else:
                    #       it means the subgnerator is not decorated with @Reporter. so we read the name directly.
                    if not inspect.isgenerator(self._gen.gi_yieldfrom):
                        sub_gen_name = self._gen.gi_yieldfrom.__class__.__name__
                        self._logger.info({"msg": f'Yielding from iterator: {sub_gen_name}', "filename": self._func.__code__.co_filename} | ({} if self._gen.gi_frame is None else {"lineno": self._gen.gi_frame.f_lineno }))
                    else:
                        sub_gen_name = self._gen.gi_yieldfrom.gi_frame.f_locals['self']._gen.__name__ if self._gen.gi_yieldfrom.gi_code.co_qualname == f'{class_name}.__iter__' else self._gen.gi_yieldfrom.__name__
                        self._logger.info({"msg": f'Entered subgenerator: {sub_gen_name}', "filename": self._func.__code__.co_filename} | ({} if self._gen.gi_frame is None else {"lineno": self._gen.gi_frame.f_lineno }))
                    
                
                if entered_sub_gen and self._gen.gi_yieldfrom is None:
                    self._logger.info({"msg": f'Exited subgenrator.', "filename": self._func.__code__.co_filename} | ({} if self._gen.gi_frame is None else {"lineno": self._gen.gi_frame.f_lineno }))
                    entered_sub_gen = False
                    sub_gen_name = None
                    f_locals = None
                
                if entered_sub_gen:
                    # to get correct subgenrator name instead of it being ProxyReporter.__iter__
                    # we check if the `sub genrator` name is ProxyReporter.__iter__
                    # if yes:
                    #        it means the subgenrator is decorated with @Reporter. so we read the value from gi_frame.f_locals. ===> This is equal to self._gen.gi_yieldfrom.gi_frame.f_locals['self']  `self`
                    # else:
                    #       it means the subgnerator is not decorated with @Reporter. so we read f_locals directly.
                    if not inspect.isgenerator(self._gen.gi_yieldfrom):
                        self._logger.info({"msg": f'delegated to a iterator do has no locals', "filename": self._func.__code__.co_filename} | ({} if self._gen.gi_frame is None else {"lineno": self._gen.gi_frame.f_lineno }))
                    else:
                        f_locals = self._gen.gi_yieldfrom.gi_frame.f_locals['self']._gen.gi_frame.f_locals if self._gen.gi_yieldfrom.gi_code.co_qualname  == f'{class_name}.__iter__' else self._gen.gi_yieldfrom.gi_frame.f_locals
                        self._logger.info({"msg": {"sub_gen_name":sub_gen_name,"sub_gen_locals":f_locals}, "filename": self._func.__code__.co_filename} | ({} if self._gen.gi_frame is None else {"lineno": self._gen.gi_frame.f_lineno }))
                
                gi_yieldfrom = self._gen.gi_yieldfrom if not inspect.isgenerator(self._gen.gi_yieldfrom) else \
                        (self._gen.gi_yieldfrom.gi_frame.f_locals['self']._gen if entered_sub_gen and (self._gen.gi_yieldfrom.gi_code.co_qualname  == f'{class_name}.__iter__') else  self._gen.gi_yieldfrom)
                self._logger.info({"msg": {
                    attr: repr(getattr(self._gen,attr)) for attr in self._attrs if attr != 'gi_yieldfrom'
                }|{
                    "gi_yieldfrom": gi_yieldfrom
                }, "filename": self._func.__code__.co_filename} | {}| ({} if self._gen.gi_frame is None else {"lineno": self._gen.gi_frame.f_lineno }))
                
                self._logger.info({"msg": {"yielded_value":result}, "filename": self._func.__code__.co_filename}| ({} if self._gen.gi_frame is None else {"lineno": self._gen.gi_frame.f_lineno }))
                self._logger.info({"msg": {"value_sent_gen": f"Value sent to generator: {i}" if i is not None else "No value sent to,  the generator"}, "filename": self._func.__code__.co_filename
                                } | ({} if self._gen.gi_frame is None else {"lineno": self._gen.gi_frame.f_lineno }))
                               
                
                

class Reporter(BaseReporter):
    """
    This calls helps trace genrators internals.
    """
    def __new__(cls, *args, **kwargs):
        # Check if the function decorated `isgenerator`
        if args:
            func, = args
        else:
            func = kwargs.get('func')
        
        if func is not None and not inspect.isgeneratorfunction(func):
            raise TypeError(f'decorated object must be generator')
        
        if func is not None and isinstance(func, BaseReporter):
            raise TypeError(f"{func} cannot be an instance of Reporter")
        return super().__new__(cls)
    
    def __init__(self, func = None, *,logger: logging.Logger|None = None):
        """
        func(function):         is generator function.
        logger(logging.Logger): is logger which will report generation created from `func` internals. 
                                if no logger is passed then uses default root logger and emits to StreamHandler

        """
        super().__init__(func = func, logger = logger)
            
    
    
    
    def __call__(self,*args,
                obj = None, 
                cls = None,
                **kwargs):
        """
        This will create the generator from `func`
        """
        if self._func is None:
            self = self.__class__(func = args[0] if args else kwargs['func'], logger = self.logger) 
            return self
        
        gen: Generator = self._func(*args,**kwargs) if (obj is None or cls is None) else self._func((obj if obj is not None else cls),*args,**kwargs)
        attrs = list(filter(
            lambda x: x.startswith('gi'), dir(gen)
        )) 
        proxy_obj = _ProxyReporter(self._func,gen, self.logger, attrs)
        return iter(proxy_obj)
    

    