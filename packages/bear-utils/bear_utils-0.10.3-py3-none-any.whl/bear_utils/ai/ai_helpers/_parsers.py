from collections.abc import Callable
import json
from typing import Any, cast

from httpx import AsyncClient, Headers, Response
from rich.markdown import Markdown

from bear_utils import EpochTimestamp
from bear_utils.ai.ai_helpers._types import ResponseParser
from bear_utils.constants import HTTPStatusCode
from bear_utils.logger_manager.logger_protocol import LoggerProtocol

from ._config import AIEndpointConfig


class JSONResponseParser(ResponseParser[dict[str, Any]]):
    """Parser for JSON responses with flexible output structure."""

    def __init__(self, required_fields: list | None = None, response_transformers: dict[str, Callable] | None = None):
        self.required_fields = required_fields or []
        self.response_transformers = response_transformers or {}

    async def parse(self, raw_response: dict, logger: LoggerProtocol) -> dict[str, Any]:
        """Parse JSON response with configurable validation and transformation."""
        default: dict[str, Any] = self.get_default_response()

        output = raw_response.get("output", "")
        if not output:
            logger.error("No output received from AI.")
            return default

        try:
            response_dict = json.loads(output)
            if not isinstance(response_dict, dict):
                logger.error("Response is not a valid JSON object.")
                return default

            logger.verbose(json.dumps(response_dict, indent=4))

            if self.required_fields:
                missing_fields = [field for field in self.required_fields if field not in response_dict]
                if missing_fields:
                    logger.error(f"Response JSON missing required fields: {missing_fields}")
                    return default

            for field_name, transformer in self.response_transformers.items():
                if field_name in response_dict:
                    response_dict[field_name] = transformer(response_dict[field_name])

            return response_dict

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response JSON: {e}")
            return default

    def get_default_response(self) -> dict[str, Any]:
        """Return a basic default response."""
        return {"error": "Failed to parse response"}


class TypedResponseParser[T_Response](ResponseParser[T_Response]):
    def __init__(self, default_response: T_Response, response_transformers: dict[str, Callable] | None = None):
        self.default_response: T_Response = default_response
        self.response_transformers = response_transformers or {}
        self.required_fields = list(cast("dict", self.default_response).keys())

    def get_default_response(self) -> T_Response:
        return cast("T_Response", self.default_response)

    async def parse(self, raw_response: dict, logger: LoggerProtocol) -> T_Response:
        """Parse JSON response with strict typing."""
        default: T_Response = self.get_default_response()

        output = raw_response.get("output", "")
        if not output:
            logger.error("No output received from AI.")
            return default

        try:
            response_dict = json.loads(output)
            if not isinstance(response_dict, dict):
                logger.error("Response is not a valid JSON object.")
                return default

            logger.verbose(json.dumps(response_dict, indent=4))

            missing_fields = [field for field in self.required_fields if field not in response_dict]
            if missing_fields:
                logger.error(f"Response JSON missing required fields: {missing_fields}")
                return default

            for field_name, transformer in self.response_transformers.items():
                if field_name in response_dict:
                    response_dict[field_name] = transformer(response_dict[field_name])
            return cast("T_Response", response_dict)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response JSON: {e}")
            return default


class CommandResponseParser[T_Response](TypedResponseParser[T_Response]):
    """Specialized parser for command-based responses."""

    def __init__(self, response_type: type[T_Response]):
        super().__init__(
            default_response=response_type(),
            response_transformers={
                "output": lambda x: Markdown(x) if isinstance(x, str) else x,
            },
        )


class PassthroughResponseParser(ResponseParser[dict[str, Any]]):
    """Parser that returns the raw output without JSON parsing."""

    async def parse(self, raw_response: dict, logger: LoggerProtocol) -> dict[str, Any]:
        """Return the raw output from the response without parsing."""
        output = raw_response.get("output", "")
        return {"output": output}

    def get_default_response(self) -> dict[str, Any]:
        return {"output": ""}


class ModularAIEndpoint[T_Response]:
    """Modular AI endpoint for flexible communication patterns."""

    def __init__(
        self,
        config: AIEndpointConfig,
        logger: LoggerProtocol,
        response_parser: ResponseParser[T_Response],
    ) -> None:
        self.config: AIEndpointConfig = config
        self.logger: LoggerProtocol = logger
        self.response_parser: ResponseParser[T_Response] = response_parser
        self.session_id: str | None = None

        self.logger.verbose(f"Using URL: {self.config.url}")
        self.logger.verbose(f"Using prompt: {self.config.prompt[:50]}...")

        self.set_session_id(new=True)

    def set_session_id(self, new: bool = False) -> None:
        """Set the session ID for the current interaction."""
        if new or self.session_id is None:
            self.logger.verbose("Starting a new session.")
            self.session_id = str(EpochTimestamp.now())
        else:
            self.logger.verbose("Continuing existing session with AI.")
        self.logger.debug(f"Using session ID: {self.session_id}")

    def _prepare_message(self, message: str) -> str:
        """Prepare the message with optional JSON suffix."""
        if self.config.append_json_suffix:
            return f"{message}{self.config.json_suffix}"
        return message

    async def send_message(self, message: str, override_parser: ResponseParser[T_Response] | None = None) -> T_Response:
        """Send a message to the AI endpoint with flexible response parsing."""
        parser: ResponseParser[T_Response] = override_parser or self.response_parser
        async with AsyncClient(timeout=self.config.connection_timeout) as client:
            try:
                response: Response = await client.post(
                    url=self.config.url,
                    json={
                        "chatModel": self.config.chat_model,
                        "chatInput": self._prepare_message(message),
                        "sessionId": self.session_id,
                        "systemPrompt": self.config.prompt,
                    },
                    headers=Headers(
                        {
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {self.config.bearer_token}",
                        }
                    ),
                )
                if response.status_code == HTTPStatusCode.SERVER_OK:
                    return await parser.parse(response.json(), self.logger)
                self.logger.error(f"Failed to send message to AI: {response.status_code} - {response.text}")
                return parser.get_default_response()
            except Exception as e:
                self.logger.error(f"Exception during AI communication: {e}")
                return parser.get_default_response()
