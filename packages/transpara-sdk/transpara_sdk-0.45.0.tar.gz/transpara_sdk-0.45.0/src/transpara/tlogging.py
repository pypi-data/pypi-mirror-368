import logging
from logging import Logger
from transpara.logging_config import TRANSPARA_DEBUG_LEVEL, TRANSPARA_ERROR_LEVEL, CRITICAL_LEVEL, FATAL_LEVEL, ERROR_LEVEL, WARN_LEVEL, WARNING_LEVEL, INFO_LEVEL, DEBUG_LEVEL
from transpara.logging_config import RED, RESET_COLOR, BOLD_RED, BLUE, GREY, YELLOW
from transpara import logging_config
from transpara.tracing import get_current_trace_id

import asyncio
import logging
import os
import sys
import time
import traceback
from functools import wraps

import jsonpickle
class TransparaLogger(Logger):
    
    def terror(self, msg):
        self.log(TRANSPARA_ERROR_LEVEL, msg)

    def tdebug(self, msg):
        self.log(TRANSPARA_DEBUG_LEVEL, msg)

#Monkeypatching the class as I don't want to lose information by calling the logger from an interim function
Logger.terror = TransparaLogger.terror
Logger.tdebug = TransparaLogger.tdebug

def get_logger(logger_name) -> TransparaLogger:
    return logging.getLogger(logger_name)

def set_log_level(level:int):
    logging.root.setLevel(level)

"""
Sets verbose exception stacks
"""
def set_global_verbose(val:bool):
    logging_config.GLOBAL_VERBOSE = val

def set_default_format(fmt:str):
    logging_config.default_format = fmt
    logging_config.stream_handler.setFormatter(logging_config.TransparaCustomLogFormatter())

def set_tdebug_format(fmt:str):
    logging_config.debug_handler_format = fmt
    logging_config.stream_handler.setFormatter(logging_config.TransparaCustomLogFormatter())

def set_terror_format(fmt:str):
    logging_config.error_handler_format = fmt 
    logging_config.stream_handler.setFormatter(logging_config.TransparaCustomLogFormatter())



#Decorators


from transpara.logging_config import (GLOBAL_VERBOSE, TRANSPARA_DEBUG_LEVEL,
                                      TRANSPARA_ERROR_LEVEL, Locals)


def __is_primitive(obj):
    return not hasattr(obj, '__dict__')
    
#Async helper for wrapping decorators and prevent blocking on methods that are indeed async
async def __async_wrapper(func, *args, **kwargs):
    if asyncio.iscoroutinefunction(func):
        #print(f"this function is a coroutine: {func.__name__}")
        return await func(*args, **kwargs)
    else:
        #print(f"not a coroutine: {func.__name__}")
        return func(*args, **kwargs)

__exc_message = "RETURNEXCEPTION" #Used for returning the exception string when suppressing exceptions

def logd_async(verbose_exc=False, suppress_exc=False, 
                suppressed_return_value = __exc_message,
                log_locals_on_exc=False, 
                debug_locals = False,
                debug_elapsed = True,
                debug_params = False,
                include_trace_id = True
            ):
    """
        [OPTIONAL][Default False] verbose_exc              if true, logs the stack trace, else just log the exception message
        [OPTIONAL][Default False] suppress_exc             will surround the exception and won't rethrow it by default it will return the error message to the caller
        [OPTIONAL][Default False] suppressed_return_value  If suppressing the exception, by default the function will return the error message unless this argument is set
        [OPTIONAL][Default False] log_locals_on_exc        if true, the locals of the called function will be logged when there is an exception
        [OPTIONAL][Default False] debug_locals             if true, the locals of the called function will be logged when there are no exceptions
        [OPTIONAL][Default True] debug_elapsed            by default regardless of exception conditions, the elapsed time of the called function will be logged
        [OPTIONAL][Default False] debug_params              whether or not we add parameters to the logged function signature, example: sum(1+2): result was 3, only for primitives, others are ignored

        @transpara_middleware(suppress_exc=True, log_locals_on_exc=True, debug_elapsed=True)
        @transpara_middleware()
    """
    def decorator(function):

        @wraps(function)
        async def wrapper(*args, **kwargs):

            if debug_elapsed:
                start = time.time()


            #Get a logger
            logger = logging.getLogger(function.__module__)

            params = ''

            if debug_params:
                params = []
                [params.append(str(arg)) if __is_primitive(arg) else None for arg in args]
                [params.append(str(k) + "=" + str(v)) if __is_primitive(v) else None for k, v in kwargs.items()]
                params = ','.join(params)


            #If debugging locals then set a tracer to get the locals
            #From the stack frame
            if debug_locals:
                locals = Locals()
                def tracer(frame, event, arg):
                    if event=='return':
                        locals.set(frame.f_locals.copy())

            try:
                #set local tracer
                if debug_locals: sys.setprofile(tracer)
                #invoke actual function
                result = await __async_wrapper(function, *args, **kwargs)
                #Set back original tracer
                if debug_locals: sys.setprofile(None)        
            except BaseException as e:
                #Set back original tracer
                if debug_locals: sys.setprofile(None)

                error_message = e.__class__.__name__ + ': ' + (str(e)) 

                #If exceptions are set to verbose then print the stack trace 
                if verbose_exc or GLOBAL_VERBOSE:
                    error_message = traceback.format_exc()

                #Capture locals from stack and add them to the error message
                if log_locals_on_exc:
                    try:
                        tb = sys.exc_info()[2]
                        locals_dict = tb.tb_next.tb_frame.f_locals
                        locals_json = jsonpickle.encode(locals_dict)
                        error_message = error_message + os.linesep + "locals: "+ locals_json
                    except:
                        pass

                #Log the error
                logger.log(TRANSPARA_ERROR_LEVEL, f"{function.__name__}({params}):{error_message}")

                #If measuring elapsed, log it before we bail
                if debug_elapsed or include_trace_id:
                    debug_message = f"{function.__name__}({params}):"
                    
                    if include_trace_id:
                        trace_id = get_current_trace_id()
                        if trace_id: debug_message = f"{debug_message} trace_id: {trace_id}"
                        
                    if debug_elapsed: debug_message =  f"{debug_message} elapsed: {(time.time() - start)*1000}ms"
                    logger.log(TRANSPARA_DEBUG_LEVEL, debug_message)     

                #If suppresing decide whether to return the exception message or an override value set as func param
                if suppress_exc: 
                    return error_message if suppressed_return_value == __exc_message else suppressed_return_value

                #If exception wasn't suppresed above, then raise all chaos!
                raise
            
            if debug_locals or debug_elapsed or include_trace_id: 

                #If there is anythign to debug (locals or elapsed) prepare message
                debug_message = f"{function.__name__}({params}):"

                if include_trace_id:
                    trace_id = get_current_trace_id()
                    if trace_id: debug_message = f"{debug_message} trace_id: {trace_id}"

                #if measuring executing time, add to debug message
                if debug_elapsed: debug_message = f"{debug_message} elapsed: {(time.time() - start)*1000}ms"

                #if debugging the locals, add them to the message
                if debug_locals and locals.any: debug_message = f"{debug_message} locals: {locals.to_json()}"

                #log the debug message
                logger.log(TRANSPARA_DEBUG_LEVEL, debug_message)     


            return result
        return wrapper
    return decorator


def logd(verbose_exc=False, suppress_exc=False, 
                suppressed_return_value = __exc_message,
                log_locals_on_exc=False, 
                debug_locals = False,
                debug_elapsed = True,
                debug_params = False,
                include_trace_id = True
            ):
    """
        [OPTIONAL][Default False] verbose_exc              if true, logs the stack trace, else just log the exception message
        [OPTIONAL][Default False] suppress_exc             will surround the exception and won't rethrow it by default it will return the error message to the caller
        [OPTIONAL][Default False] suppressed_return_value  If suppressing the exception, by default the function will return the error message unless this argument is set
        [OPTIONAL][Default False] log_locals_on_exc        if true, the locals of the called function will be logged when there is an exception
        [OPTIONAL][Default False] debug_locals             if true, the locals of the called function will be logged when there are no exceptions
        [OPTIONAL][Default True] debug_elapsed            by default regardless of exception conditions, the elapsed time of the called function will be logged
        [OPTIONAL][Default False] debug_params              whether or not we add parameters to the logged function signature, example: sum(1+2): result was 3, non primitives are ignored
        @transpara_middleware(suppress_exc=True, log_locals_on_exc=True, debug_elapsed=True)
        @transpara_middleware()
    """
    def decorator(function):

        def wrapper(*args, **kwargs):

            params = ''

            if debug_params:
                params = []
                [params.append(str(arg)) if __is_primitive(arg) else None for arg in args]
                [params.append(str(k) + "=" + str(v)) if __is_primitive(v) else None for k, v in kwargs.items()]
                params = ','.join(params)


            if debug_elapsed:
                start = time.time()


            #Get a logger
            logger = logging.getLogger(function.__module__)

            #If debugging locals then set a tracer to get the locals
            #From the stack frame
            if debug_locals:
                locals = Locals()
                def tracer(frame, event, arg):
                    if event=='return':
                        locals.set(frame.f_locals.copy())

            try:
                #set local tracer
                if debug_locals: sys.setprofile(tracer)
                #invoke actual function
                result = function(*args, **kwargs)
                #Set back original tracer
                if debug_locals: sys.setprofile(None)        
            except BaseException as e:
                #Set back original tracer
                if debug_locals: sys.setprofile(None)

                error_message = e.__class__.__name__ + ': ' + (str(e)) 

                #If exceptions are set to verbose then print the stack trace 
                if verbose_exc or GLOBAL_VERBOSE:
                    error_message = traceback.format_exc()

                #Capture locals from stack and add them to the error message
                if log_locals_on_exc:
                    try:
                        tb = sys.exc_info()[2]
                        locals_dict = tb.tb_next.tb_frame.f_locals
                        locals_json = jsonpickle.encode(locals_dict)
                        error_message = error_message + os.linesep + "locals: "+ locals_json
                    except:
                        pass

                #Log the error
                logger.log(TRANSPARA_ERROR_LEVEL, f"{function.__name__}({params}):{error_message}")

                #If measuring elapsed, log it before we bail
                if debug_elapsed or include_trace_id:
                    debug_message = f"{function.__name__}({params}):"
                    
                    if include_trace_id:
                        trace_id = get_current_trace_id()
                        if trace_id: debug_message = f"{debug_message} trace_id: {trace_id}"

                    if debug_elapsed: debug_message =  f"{debug_message} elapsed: {(time.time() - start)*1000}ms"
                    logger.log(TRANSPARA_DEBUG_LEVEL, debug_message)     


                #If suppresing decide whether to return the exception message or an override value set as func param
                if suppress_exc: 
                    return error_message if suppressed_return_value == __exc_message else suppressed_return_value

                #If exception wasn't suppresed above, then raise all chaos!
                raise
            
            if debug_locals or debug_elapsed or include_trace_id: 

                #If there is anythign to debug (locals or elapsed) prepare message
                debug_message = f"{function.__name__}({params}):"

                if include_trace_id:
                    trace_id = get_current_trace_id()
                    if trace_id: debug_message = f"{debug_message} trace_id: {trace_id}"

                #if measuring executing time, add to debug message
                if debug_elapsed: debug_message = f"{debug_message} elapsed: {(time.time() - start)*1000}ms"

                #if debugging the locals, add them to the message
                if debug_locals and locals.any: debug_message = f"{debug_message} locals: {locals.to_json()}"

                #log the debug message
                logger.log(TRANSPARA_DEBUG_LEVEL, debug_message)     


            return result
        return wrapper
    return decorator


def elapsed_async(func):
    async def wrapper(*args, **kwargs):
        start = time.time()
        logger = logging.getLogger(func.__module__)
        result = await __async_wrapper(func,*args, **kwargs)
        message = f"Elapsed: {(time.time() - start)*1000}ms"
        logger.log(TRANSPARA_DEBUG_LEVEL,f"{func.__name__}(): {message}")
        return result
    return wrapper

def elapsed(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        logger = logging.getLogger(func.__module__)
        result = func(*args, **kwargs)
        message = f"Elapsed: {(time.time() - start)*1000}ms"
        logger.log(TRANSPARA_DEBUG_LEVEL,f"{func.__name__}(): {message}")
        return result
    return wrapper