import atexit
from typing import Callable
from loguru import logger
from multiprocessing import Queue
from ..logging_loki import LokiQueueHandler, emitter

from . import __version__

class LogUtils():
    @staticmethod
    def _init_logging(
            url: str,
            get_access_token: Callable[..., str],
            log_level: str,
            sessionId: str,
            disableOAuth: bool,
            clientId: str = "S2O.TechStack.Python"):

        emitter.LokiEmitter.level_tag = "level"
        emitter.LokiEmitter.get_access_token = get_access_token
        emitter.LokiEmitter.disable_oauth = disableOAuth
        handler = LokiQueueHandler(
            Queue(), # type: ignore
            url=url,
            tags={"client": clientId},
            version="1"
        )

        logger.add(handler, level=log_level, serialize=True,
                   backtrace=True, diagnose=True)
        logger.configure(extra={
            "version": __version__,
            "session_id": sessionId,
        })

        def _teardown_logging(handler):
            handler.listener.stop()

        atexit.register(_teardown_logging, handler)
