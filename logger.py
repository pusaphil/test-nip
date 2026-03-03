import logging
from typing import Optional


class Logger:
  def __init__(self, name: Optional[str] = None, level: int = logging.INFO) -> None:
    """
    Simple wrapper around Python's logging module.
    """
    logger_name = name or __name__
    self._logger = logging.getLogger(logger_name)
    if not self._logger.handlers:
      handler = logging.StreamHandler()
      formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
      )
      handler.setFormatter(formatter)
      self._logger.addHandler(handler)
    self._logger.setLevel(level)
    # self._logger.propagate = False

  def debug(self, msg: str, *args, **kwargs) -> None:
    self._logger.debug(msg, *args, **kwargs)

  def info(self, msg: str, *args, **kwargs) -> None:
    self._logger.info(msg, *args, **kwargs)

  def warning(self, msg: str, *args, **kwargs) -> None:
    self._logger.warning(msg, *args, **kwargs)

  def error(self, msg: str, *args, **kwargs) -> None:
    self._logger.error(msg, *args, **kwargs)

  def critical(self, msg: str, *args, **kwargs) -> None:
    self._logger.critical(msg, *args, **kwargs)

