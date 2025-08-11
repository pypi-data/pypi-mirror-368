from enum import Enum


class Result(Enum):
    """Results of graph execution"""

    N_A = 3
    READY = 2
    RUNNING = 1
    WAITING = 4
    FINISHED_OK = 0
    ERROR = -1
    ABORTED = -2
    TIMEOUT = -3 
    UNKNOWN = -4 

# Data types:
class DataType(Enum):
    """Datatypes used in graphs"""

    BOOLEAN = 'boolean'
    BYTES = 'bytes'
    DATETIME = 'datetime'
    DECIMAL = 'decimal'
    INTEGER = 'integer'
    LONG = 'long'
    NUMBER = 'number'
    STRING = 'string'
    VARIANT = 'variant'

