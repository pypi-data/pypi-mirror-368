from loguru import logger


class ErrorHandler:
    
    def __init__(self):
        pass
    
    @staticmethod
    def error(raise_exception: bool, msg: str):
        if raise_exception:
            raise Exception(msg)
        else:
            logger.error(msg)