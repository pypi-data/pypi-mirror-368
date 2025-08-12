
import logging
import sys
import jsonpickle

#region log levels
CRITICAL_LEVEL = 50
FATAL_LEVEL = CRITICAL_LEVEL
ERROR_LEVEL = 40
WARNING_LEVEL = 30
WARN_LEVEL = WARNING_LEVEL
INFO_LEVEL = 20
DEBUG_LEVEL = 10

#Need a custom logging level for custom formats on error handler
#Also to tell them apart from other's DEBUGs
TRANSPARA_ERROR_LEVEL = 60
TRANSPARA_DEBUG_LEVEL = 15
logging.addLevelName(TRANSPARA_ERROR_LEVEL, "TERROR")
logging.addLevelName(TRANSPARA_DEBUG_LEVEL, "TDEBUG")
#endregion

#colors for formatters
GREY = "\x1b[38;20m"
YELLOW = "\x1b[33;20m"
RED = "\x1b[31;20m"
BLUE = "\x1b[34;20m"
BOLD_RED = "\x1b[31;1m"
RESET_COLOR = "\x1b[0m"


GLOBAL_VERBOSE = False 
#Probs want a delimiter? like >> << If we ever want to parse our logs it would be useful to have some sort of delimiter
default_format = f">> {BLUE}[%(levelname)s: %(asctime)s: %(name)s: %(filename)s:%(lineno)s - %(funcName)5s()]: %(message)s {RESET_COLOR}<<"
#the decorator cant use filename and fileno or it would use the own decorator, so what we do is we get the function name from the decorator and pass that
#we don't have the line number in this case but that's ok
error_handler_format = f">> {RED}[%(levelname)s: %(asctime)s: %(name)s:] %(message)s  {RESET_COLOR}<<"
debug_handler_format = f">> {YELLOW}[%(levelname)s: %(asctime)s: %(name)s:] %(message)s {RESET_COLOR}<<"

#region custom formatter based on log level
class TransparaCustomLogFormatter(logging.Formatter):


    def __init__(self):
        super().__init__(fmt=default_format,
                         datefmt=None, 
                         style='%')  
    
    def format(self, record):

        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._style._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == TRANSPARA_ERROR_LEVEL:
            self._style._fmt = error_handler_format

        if record.levelno == TRANSPARA_DEBUG_LEVEL:
            self._style._fmt = debug_handler_format

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_orig
        return result

formatter = TransparaCustomLogFormatter()
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logging.root.addHandler(stream_handler)
#endregion


#To store locals from the stack
class Locals():

    def any(self):
        return len(self.__dict_) > 0

    def set(self, locals_dict):
        self.__dict__ = locals_dict

    def to_json(self):
        return jsonpickle.encode(self.__dict__)


