from enum import Enum

class TriggerType(Enum):
    MANUAL = 'MANUAL'
    SCHEDULE = 'SCHEDULE'
    SCRIPT = 'SCRIPT'

class ExecutionStatus(Enum):
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    SUCCEEDED = 'SUCCEEDED'
    FAILED = 'FAILED'    
    

class LimitType(Enum):
    NEWEST = 'NEWEST' # meaning FIRST, TOP
    OLDEST = 'OLDEST' # meaning LAST, BOTTOM
