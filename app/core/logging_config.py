"""
Logging script for Core module
"""
import logging
import os
from datetime import datetime
from logging.handlers import SMTPHandler

from app.core import config


def _setup_console_handler(logger: logging.Logger, log_level: int) -> None:
    """
    Setup console handler
    :param logger: Logger instance
    :type logger: logging.Logger
    :param log_level: The log level
    :type log_level: int
    :return: None
    :rtype: NoneType
    """
    console_handler: logging.StreamHandler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)


def _setup_mail_handler(
        logger: logging.Logger, log_level: int,
        settings: config.Settings = config.get_settings()) -> None:
    """
    Setup mail handler
    :param logger: Logger instance
    :type logger: logging.Logger
    :param log_level: The log level
    :type log_level: int
    :return: None
    :rtype: NoneType
    """
    if not settings.SMTP_USER:
        raise AttributeError("Mail server is not set.")
    if not settings.EMAILS_FROM_EMAIL:
        raise AttributeError("Mail from address is not set.")
    if not settings.SMTP_USER:
        raise AttributeError("Mail to address is not set.")
    if not settings.MAIL_SUBJECT:
        raise AttributeError("Mail subject is not set.")
    if not settings.MAIL_TIMEOUT:
        raise AttributeError("Mail timeout is not set.")
    creds: list = [settings.SMTP_USER, settings.SMTP_PASSWORD]
    if log_level == logging.CRITICAL:
        mail_handler = SMTPHandler(
            mailhost=settings.SMTP_USER, fromaddr=settings.EMAILS_FROM_EMAIL,
            toaddrs=settings.SMTP_USER, subject=settings.MAIL_SUBJECT,
            credentials=tuple(creds), timeout=settings.MAIL_TIMEOUT
        )
        mail_handler.setLevel(log_level)
        logger.addHandler(mail_handler)


def _setup_file_handler(
        logger: logging.Logger, log_level: int,
        settings: config.Settings = config.get_settings()) -> None:
    """
    Setup file handler
    :param logger: The logger instance
    :type logger: logging.Logger
    :param log_level: The log level
    :type log_level: int
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: None
    :rtype: NoneType
    """
    formatter: logging.Formatter = logging.Formatter(
        "[%(name)s][%(asctime)s][%(levelname)s][%(module)s][%(funcName)s][%("
        "lineno)d]: %(message)s", datefmt=settings.DATE_FORMAT)
    current_file_directory: str = os.path.dirname(os.path.abspath(__file__))
    project_root: str = current_file_directory
    while os.path.basename(project_root) != settings.PROJECT_NAME:
        project_root = os.path.dirname(project_root)
    current_date: str = datetime.today().strftime(settings.FILE_DATE_FORMAT)
    log_filename: str = f"log-{current_date}.log"
    filename_path: str = f"{project_root}/logs/{log_filename}"
    file_handler: logging.FileHandler = logging.FileHandler(filename_path)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    file_handler.flush()


def setup_logging(
        log_level: int = logging.DEBUG,
        settings: config.Settings = config.get_settings()) -> None:
    """
    Setup logging
    :param log_level: Level of logging
    :type log_level: int
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: None
    :rtype: NoneType
    """
    logger: logging.Logger = logging.getLogger()
    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(log_level)
    _setup_console_handler(logger, log_level)
    _setup_mail_handler(logger, log_level, settings)
    _setup_file_handler(logger, log_level, settings)
