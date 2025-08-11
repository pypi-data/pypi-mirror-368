from abc import ABC, abstractmethod

from bear_utils.logger_manager import LoggerProtocol


class ResponseParser[T_Response](ABC):
    """Abstract base class for response parsers."""

    @abstractmethod
    async def parse(self, raw_response: dict, logger: LoggerProtocol) -> T_Response:
        """Parse the raw response into the desired format."""

    @abstractmethod
    def get_default_response(self) -> T_Response:
        """Return a default response structure."""
