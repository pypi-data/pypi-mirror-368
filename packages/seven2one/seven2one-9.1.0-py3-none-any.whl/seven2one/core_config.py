from typing import Optional

from seven2one.utils.defaults import Defaults

class TechStackConfig():
    def __init__(self):
        self._raiseException = False
        self._proxies = None
        self._host = ""
        self._defaults = Defaults()
        return

    @property
    def raiseException(self) -> bool:
        return self._raiseException

    @raiseException.setter
    def raiseException(self, value: bool) -> None:
        self._raiseException = value

    @property
    def proxies(self) -> Optional[dict]:
        return self._proxies

    @proxies.setter
    def proxies(self, value: Optional[dict]) -> None:
        self._proxies = value

    @property
    def host(self) -> str:
        return self._host

    @host.setter
    def host(self, value: str) -> None:
        self._host = value

    @property
    def defaults(self) -> Defaults:
        return self._defaults

    @defaults.setter
    def defaults(self, value: Defaults) -> None:
        self._defaults = value
