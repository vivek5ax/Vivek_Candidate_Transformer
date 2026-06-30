from abc import ABC, abstractmethod
from typing import Any, Union, List
import logging

from app.models.extracted_candidate import ExtractedCandidate

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """
    Abstract Base Class for all candidate source parsers.
    Every parser must implement `parse()` and gracefully handle errors without crashing.
    """

    def __init__(self, source_type: str):
        self.source_type = source_type

    @abstractmethod
    def parse(self, source: Any, **kwargs) -> Union[ExtractedCandidate, List[ExtractedCandidate]]:
        """
        Parse raw source data (file path, bytes, dict, string) into ExtractedCandidate(s).
        Must never raise unhandled exceptions; return ExtractedCandidate with error status in metadata on failure.
        """
        pass
