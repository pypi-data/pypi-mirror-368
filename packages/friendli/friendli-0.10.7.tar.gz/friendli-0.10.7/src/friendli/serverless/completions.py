# Copyright (c) 2025-present, FriendliAI Inc. All rights reserved.

"""Friendli Python SDK."""

from __future__ import annotations

from typing import Mapping, Optional, Union

from friendli.core import models, utils
from friendli.core.sdk import AsyncFriendliCore, SyncFriendliCore
from friendli.core.types import UNSET, OptionalNullable
from friendli.core.utils import eventstreaming

from ..config import Config


class SyncCompletions:
    def __init__(self, core: SyncFriendliCore, config: Config):
        self._core = core
        self._config = config

    def complete(
        self,
        *,
        serverless_completions_body: Union[
            models.ServerlessCompletionsBody, models.ServerlessCompletionsBodyTypedDict
        ],
        x_friendli_team: OptionalNullable[str] = UNSET,
        retries: OptionalNullable[utils.RetryConfig] = UNSET,
        server_url: Optional[str] = None,
        timeout_ms: Optional[int] = None,
        http_headers: Optional[Mapping[str, str]] = None,
    ) -> models.ServerlessCompletionsSuccess:
        """Completions

        Generate text based on the given text prompt.

        :param serverless_completions_body:
        :param x_friendli_team: ID of team to run requests as (optional parameter).
        :param retries: Override the default retry configuration for this method
        :param server_url: Override the default server URL for this method
        :param timeout_ms: Override the default request timeout configuration for this method in milliseconds
        :param http_headers: Additional headers to set or replace on requests.
        """
        return self._core.serverless.completions.complete(
            serverless_completions_body=serverless_completions_body,
            x_friendli_team=x_friendli_team,
            retries=retries,
            server_url=server_url,
            timeout_ms=timeout_ms,
            http_headers=http_headers,
        )

    def stream(
        self,
        *,
        serverless_completions_stream_body: Union[
            models.ServerlessCompletionsStreamBody,
            models.ServerlessCompletionsStreamBodyTypedDict,
        ],
        x_friendli_team: OptionalNullable[str] = UNSET,
        retries: OptionalNullable[utils.RetryConfig] = UNSET,
        server_url: Optional[str] = None,
        timeout_ms: Optional[int] = None,
        http_headers: Optional[Mapping[str, str]] = None,
    ) -> eventstreaming.EventStream[models.ServerlessCompletionsStreamSuccess]:
        """Stream completions

        Generate text based on the given text prompt.

        :param serverless_completions_stream_body:
        :param x_friendli_team: ID of team to run requests as (optional parameter).
        :param retries: Override the default retry configuration for this method
        :param server_url: Override the default server URL for this method
        :param timeout_ms: Override the default request timeout configuration for this method in milliseconds
        :param http_headers: Additional headers to set or replace on requests.
        """
        return self._core.serverless.completions.stream(
            serverless_completions_stream_body=serverless_completions_stream_body,
            x_friendli_team=x_friendli_team,
            retries=retries,
            server_url=server_url,
            timeout_ms=timeout_ms,
            http_headers=http_headers,
        )


class AsyncCompletions:
    def __init__(self, core: AsyncFriendliCore, config: Config):
        self._core = core
        self._config = config

    async def complete(
        self,
        *,
        serverless_completions_body: Union[
            models.ServerlessCompletionsBody, models.ServerlessCompletionsBodyTypedDict
        ],
        x_friendli_team: OptionalNullable[str] = UNSET,
        retries: OptionalNullable[utils.RetryConfig] = UNSET,
        server_url: Optional[str] = None,
        timeout_ms: Optional[int] = None,
        http_headers: Optional[Mapping[str, str]] = None,
    ) -> models.ServerlessCompletionsSuccess:
        """Completions

        Generate text based on the given text prompt.

        :param serverless_completions_body:
        :param x_friendli_team: ID of team to run requests as (optional parameter).
        :param retries: Override the default retry configuration for this method
        :param server_url: Override the default server URL for this method
        :param timeout_ms: Override the default request timeout configuration for this method in milliseconds
        :param http_headers: Additional headers to set or replace on requests.
        """
        return await self._core.serverless.completions.complete(
            serverless_completions_body=serverless_completions_body,
            x_friendli_team=x_friendli_team,
            retries=retries,
            server_url=server_url,
            timeout_ms=timeout_ms,
            http_headers=http_headers,
        )

    async def stream(
        self,
        *,
        serverless_completions_stream_body: Union[
            models.ServerlessCompletionsStreamBody,
            models.ServerlessCompletionsStreamBodyTypedDict,
        ],
        x_friendli_team: OptionalNullable[str] = UNSET,
        retries: OptionalNullable[utils.RetryConfig] = UNSET,
        server_url: Optional[str] = None,
        timeout_ms: Optional[int] = None,
        http_headers: Optional[Mapping[str, str]] = None,
    ) -> eventstreaming.EventStreamAsync[models.ServerlessCompletionsStreamSuccess]:
        """Stream completions

        Generate text based on the given text prompt.

        :param serverless_completions_stream_body:
        :param x_friendli_team: ID of team to run requests as (optional parameter).
        :param retries: Override the default retry configuration for this method
        :param server_url: Override the default server URL for this method
        :param timeout_ms: Override the default request timeout configuration for this method in milliseconds
        :param http_headers: Additional headers to set or replace on requests.
        """
        return await self._core.serverless.completions.stream(
            serverless_completions_stream_body=serverless_completions_stream_body,
            x_friendli_team=x_friendli_team,
            retries=retries,
            server_url=server_url,
            timeout_ms=timeout_ms,
            http_headers=http_headers,
        )
