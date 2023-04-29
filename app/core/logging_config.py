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


def _create_logs_folder(settings: config.Settings) -> str:
    """
    Create a log folder
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: The logs folder path
    :rtype: str
    """
    current_file_directory: str = os.path.dirname(os.path.abspath(__file__))
    project_root: str = current_file_directory
    while os.path.basename(project_root) != settings.PROJECT_NAME:
        project_root = os.path.dirname(project_root)
    logs_folder_path: str = f"{project_root}/logs"
    if not os.path.exists(logs_folder_path):
        os.makedirs(logs_folder_path, exist_ok=True)
    return logs_folder_path


def _build_log_filename(settings: config.Settings) -> str:
    """
    Build the log filename
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: The log filename
    :rtype: str
    """
    current_date: str = datetime.today().strftime(settings.FILE_DATE_FORMAT)
    log_filename: str = f"log-{current_date}.log"
    return log_filename


def _configure_file_handler(
        log_filename: str, log_level: int, settings: config.Settings
) -> logging.FileHandler:
    """
    Configure the file handler
    :param log_filename: The log filename
    :type log_filename: str
    :param log_level: The log level
    :type log_level: int
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: The logger file handler object
    :rtype: logging.FileHandle
    """
    fmt: str = "[%(name)s][%(asctime)s][%(levelname)s][%(module)s]" \
               "[%(funcName)s][%(lineno)d]: %(message)s"
    formatter: logging.Formatter = logging.Formatter(fmt, settings.DATE_FORMAT)
    file_handler: logging.FileHandler = logging.FileHandler(log_filename)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    return file_handler


def _setup_file_handler(
        logger: logging.Logger, log_level: int,
        settings: config.Settings = config.get_settings()
) -> None:
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
    logs_folder_path = _create_logs_folder(settings)
    log_filename = _build_log_filename(settings)
    filename_path: str = f"{logs_folder_path}/{log_filename}"
    file_handler = _configure_file_handler(filename_path, log_level, settings)
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
