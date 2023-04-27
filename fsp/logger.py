from datetime import datetime
from flask import Flask

class _Log:

    def __init__(self, app: Flask):
        self._app: Flask = app

    def i(self, tag: str, msg: str):
        """
        Informational messages.
        """
        self._app.logger.info(f'::{tag}:: {msg}')
    
    def w(self, tag: str, msg: str):
        """
        Warning messages.
        """
        self._app.logger.warn(f'::{tag}:: {msg}')

    def f(self, tag: str, msg: str):
        """
        Fatal error messages.
        """
        self._app.logger.fatal(f'::{tag}:: {msg}')

    def e(self, tag: str, msg: str):
        """
        Regular error messages.
        """
        self._app.logger.error(f'::{tag}:: {msg}')

    def d(self, tag: str, msg: str):
        """
        Debug messages.
        """
        self._app.logger.debug(f'::{tag}:: {msg}')

def logger(app) -> _Log:
    return _Log(app)