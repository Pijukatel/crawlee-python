from __future__ import annotations

from dataclasses import dataclass
from logging import getLogger
from typing import Unpack, Coroutine

from crawlee._types import BasicCrawlingContext, JsonSerializable
from crawlee.http_clients import HttpCrawlingResult
from crawlee.storages._dataset import PushDataKwargs


logger = getLogger(__name__)


@dataclass(frozen=True)
class HttpCrawlingContext(BasicCrawlingContext, HttpCrawlingResult):
    """HTTP crawling context."""

    @staticmethod
    def get_valid_encoding(source_encoding: str) -> str:
        fallback_encoding = 'utf-8'
        try:
            ''.encode(source_encoding)
        except (UnicodeEncodeError, LookupError):
            logger.warning(
                f'Invalid encoding {source_encoding} in http response.'
                f'Trying to use fallback encoding {fallback_encoding}'
            )
            return fallback_encoding
        return source_encoding

    def push_data(
        self,
        data: JsonSerializable,
        dataset_id: str | None = None,
        dataset_name: str | None = None,
        dataset_encoding: str | None = None,
        **kwargs: Unpack[PushDataKwargs],
    ) -> Coroutine[None, None, None]:
        # Automatically enhance data from http response
        encoding = self.get_valid_encoding(self.http_response.encoding)
        data['response_metadata'] = {**data.get('response_metadata', {}), **{'encoding': encoding}}

        return self.push_data_callback(data, dataset_id, dataset_name, dataset_encoding, **kwargs)
