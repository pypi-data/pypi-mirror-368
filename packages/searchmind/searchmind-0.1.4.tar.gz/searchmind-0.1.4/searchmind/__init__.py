# searchmind/__init__.py

__version__ = "0.1.4"

from .client import SearchMindClient
from .formatter import format_for_llm
from .exceptions import SearchMindError, APIError