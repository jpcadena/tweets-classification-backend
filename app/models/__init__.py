"""
Models initialization package
"""
from typing import TypeVar

from .analysis import Analysis
from .model import Model
from .user import User

T = TypeVar('T', User, Analysis, Model)
