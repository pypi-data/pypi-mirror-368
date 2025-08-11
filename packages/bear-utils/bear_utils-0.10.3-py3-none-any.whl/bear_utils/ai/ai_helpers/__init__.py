"""Helper utilities for constructing AI endpoints with custom response parsing."""

from collections.abc import Callable

from bear_utils.logger_manager import BaseLogger

from ._common import PRODUCTION_MODE, TESTING_MODE, EnvironmentMode
from ._config import AIEndpointConfig
from ._parsers import (
    CommandResponseParser,
    JSONResponseParser,
    ModularAIEndpoint,
    PassthroughResponseParser,
    TypedResponseParser,
)
from ._types import ResponseParser


def create_endpoint[T_Response](
    config: AIEndpointConfig,
    logger: BaseLogger,
    response_parser: ResponseParser[T_Response],
    transformers: dict[str, Callable] | None = None,
    append_json: bool | None = None,
) -> ModularAIEndpoint[T_Response]:
    if append_json is not None:
        config.append_json_suffix = append_json
    if transformers and hasattr(response_parser, "response_transformers"):
        current = getattr(response_parser, "response_transformers")
        if isinstance(current, dict):
            current.update(transformers)
        else:
            setattr(response_parser, "response_transformers", transformers)
    return ModularAIEndpoint(config=config, logger=logger, response_parser=response_parser)


__all__ = [
    "PRODUCTION_MODE",
    "TESTING_MODE",
    "AIEndpointConfig",
    "EnvironmentMode",
    "ModularAIEndpoint",
    "JSONResponseParser",
    "TypedResponseParser",
    "CommandResponseParser",
    "PassthroughResponseParser",
    "create_endpoint",
]
