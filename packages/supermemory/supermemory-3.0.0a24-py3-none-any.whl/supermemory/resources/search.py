# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from ..types import search_execute_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.search_execute_response import SearchExecuteResponse

__all__ = ["SearchResource", "AsyncSearchResource"]


class SearchResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SearchResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/supermemoryai/python-sdk#accessing-raw-response-data-eg-headers
        """
        return SearchResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SearchResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/supermemoryai/python-sdk#with_streaming_response
        """
        return SearchResourceWithStreamingResponse(self)

    def execute(
        self,
        *,
        q: str,
        categories_filter: List[Literal["technology", "science", "business", "health"]] | NotGiven = NOT_GIVEN,
        chunk_threshold: float | NotGiven = NOT_GIVEN,
        container_tags: List[str] | NotGiven = NOT_GIVEN,
        doc_id: str | NotGiven = NOT_GIVEN,
        document_threshold: float | NotGiven = NOT_GIVEN,
        filters: search_execute_params.Filters | NotGiven = NOT_GIVEN,
        include_full_docs: bool | NotGiven = NOT_GIVEN,
        include_summary: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        only_matching_chunks: bool | NotGiven = NOT_GIVEN,
        rerank: bool | NotGiven = NOT_GIVEN,
        rewrite_query: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SearchExecuteResponse:
        """
        Search memories with advanced filtering

        Args:
          q: Search query string

          categories_filter: Optional category filters

          chunk_threshold: Threshold / sensitivity for chunk selection. 0 is least sensitive (returns most
              chunks, more results), 1 is most sensitive (returns lesser chunks, accurate
              results)

          container_tags: Optional tags this search should be containerized by. This can be an ID for your
              user, a project ID, or any other identifier you wish to use to filter memories.

          doc_id: Optional document ID to search within. You can use this to find chunks in a very
              large document.

          document_threshold: Threshold / sensitivity for document selection. 0 is least sensitive (returns
              most documents, more results), 1 is most sensitive (returns lesser documents,
              accurate results)

          filters: Optional filters to apply to the search

          include_full_docs: If true, include full document in the response. This is helpful if you want a
              chatbot to know the full context of the document.

          include_summary: If true, include document summary in the response. This is helpful if you want a
              chatbot to know the full context of the document.

          limit: Maximum number of results to return

          only_matching_chunks: If true, only return matching chunks without context. Normally, we send the
              previous and next chunk to provide more context for LLMs. If you only want the
              matching chunk, set this to true.

          rerank: If true, rerank the results based on the query. This is helpful if you want to
              ensure the most relevant results are returned.

          rewrite_query: If true, rewrites the query to make it easier to find documents. This increases
              the latency by about 400ms

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v3/search",
            body=maybe_transform(
                {
                    "q": q,
                    "categories_filter": categories_filter,
                    "chunk_threshold": chunk_threshold,
                    "container_tags": container_tags,
                    "doc_id": doc_id,
                    "document_threshold": document_threshold,
                    "filters": filters,
                    "include_full_docs": include_full_docs,
                    "include_summary": include_summary,
                    "limit": limit,
                    "only_matching_chunks": only_matching_chunks,
                    "rerank": rerank,
                    "rewrite_query": rewrite_query,
                },
                search_execute_params.SearchExecuteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SearchExecuteResponse,
        )


class AsyncSearchResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSearchResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/supermemoryai/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncSearchResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSearchResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/supermemoryai/python-sdk#with_streaming_response
        """
        return AsyncSearchResourceWithStreamingResponse(self)

    async def execute(
        self,
        *,
        q: str,
        categories_filter: List[Literal["technology", "science", "business", "health"]] | NotGiven = NOT_GIVEN,
        chunk_threshold: float | NotGiven = NOT_GIVEN,
        container_tags: List[str] | NotGiven = NOT_GIVEN,
        doc_id: str | NotGiven = NOT_GIVEN,
        document_threshold: float | NotGiven = NOT_GIVEN,
        filters: search_execute_params.Filters | NotGiven = NOT_GIVEN,
        include_full_docs: bool | NotGiven = NOT_GIVEN,
        include_summary: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        only_matching_chunks: bool | NotGiven = NOT_GIVEN,
        rerank: bool | NotGiven = NOT_GIVEN,
        rewrite_query: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SearchExecuteResponse:
        """
        Search memories with advanced filtering

        Args:
          q: Search query string

          categories_filter: Optional category filters

          chunk_threshold: Threshold / sensitivity for chunk selection. 0 is least sensitive (returns most
              chunks, more results), 1 is most sensitive (returns lesser chunks, accurate
              results)

          container_tags: Optional tags this search should be containerized by. This can be an ID for your
              user, a project ID, or any other identifier you wish to use to filter memories.

          doc_id: Optional document ID to search within. You can use this to find chunks in a very
              large document.

          document_threshold: Threshold / sensitivity for document selection. 0 is least sensitive (returns
              most documents, more results), 1 is most sensitive (returns lesser documents,
              accurate results)

          filters: Optional filters to apply to the search

          include_full_docs: If true, include full document in the response. This is helpful if you want a
              chatbot to know the full context of the document.

          include_summary: If true, include document summary in the response. This is helpful if you want a
              chatbot to know the full context of the document.

          limit: Maximum number of results to return

          only_matching_chunks: If true, only return matching chunks without context. Normally, we send the
              previous and next chunk to provide more context for LLMs. If you only want the
              matching chunk, set this to true.

          rerank: If true, rerank the results based on the query. This is helpful if you want to
              ensure the most relevant results are returned.

          rewrite_query: If true, rewrites the query to make it easier to find documents. This increases
              the latency by about 400ms

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v3/search",
            body=await async_maybe_transform(
                {
                    "q": q,
                    "categories_filter": categories_filter,
                    "chunk_threshold": chunk_threshold,
                    "container_tags": container_tags,
                    "doc_id": doc_id,
                    "document_threshold": document_threshold,
                    "filters": filters,
                    "include_full_docs": include_full_docs,
                    "include_summary": include_summary,
                    "limit": limit,
                    "only_matching_chunks": only_matching_chunks,
                    "rerank": rerank,
                    "rewrite_query": rewrite_query,
                },
                search_execute_params.SearchExecuteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SearchExecuteResponse,
        )


class SearchResourceWithRawResponse:
    def __init__(self, search: SearchResource) -> None:
        self._search = search

        self.execute = to_raw_response_wrapper(
            search.execute,
        )


class AsyncSearchResourceWithRawResponse:
    def __init__(self, search: AsyncSearchResource) -> None:
        self._search = search

        self.execute = async_to_raw_response_wrapper(
            search.execute,
        )


class SearchResourceWithStreamingResponse:
    def __init__(self, search: SearchResource) -> None:
        self._search = search

        self.execute = to_streamed_response_wrapper(
            search.execute,
        )


class AsyncSearchResourceWithStreamingResponse:
    def __init__(self, search: AsyncSearchResource) -> None:
        self._search = search

        self.execute = async_to_streamed_response_wrapper(
            search.execute,
        )
