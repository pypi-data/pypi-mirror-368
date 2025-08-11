# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Wrappers for Azure Search client operations."""

import logging
from typing import Any, Dict, Optional, Union
import wrapt

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.semconv.trace import SpanAttributes

logger = logging.getLogger(__name__)

# Semantic conventions for Azure Search
class AzureSearchAttributes:
    AZURE_SEARCH_SERVICE_NAME = "azure.search.service_name"
    AZURE_SEARCH_INDEX_NAME = "azure.search.index_name"
    AZURE_SEARCH_OPERATION = "azure.search.operation"
    AZURE_SEARCH_QUERY = "azure.search.query"
    AZURE_SEARCH_FILTER = "azure.search.filter"
    AZURE_SEARCH_RESULT_COUNT = "azure.search.result_count"
    AZURE_SEARCH_TOP = "azure.search.top"
    AZURE_SEARCH_SKIP = "azure.search.skip"
    AZURE_SEARCH_SEMANTIC_RANKING = "azure.search.semantic_ranking"
    AZURE_SEARCH_DOCUMENT_COUNT = "azure.search.document_count"


def _get_tracer():
    """Get the tracer for Azure Search operations."""
    return trace.get_tracer(__name__, "0.1.0")


def _extract_endpoint_info(endpoint: str) -> Dict[str, str]:
    """Extract service name from Azure Search endpoint."""
    try:
        if ".search.windows.net" in endpoint:
            service_name = (
                endpoint.replace("https://", "").replace(".search.windows.net", "")
            )
            return {"service_name": service_name}
    except Exception:
        pass
    return {}


def _safe_set_attribute(span, key: str, value: Any):
    """Safely set span attribute, handling None values."""
    if value is not None:
        span.set_attribute(key, str(value))


class _PagedSearchResultWrapper:
    """Wrapper for paginated search results that maintains instrumentation."""

    def __init__(self, original_paged_result, span, main_wrapper):
        self._original_paged_result = original_paged_result
        self._span = span
        self._main_wrapper = main_wrapper  # Reference to the main wrapper to share state

    def __aiter__(self):
        return self

    async def __anext__(self):
        """Return the next page, wrapped to maintain instrumentation."""
        try:
            page = await self._original_paged_result.__anext__()

            # Wrap each page to maintain instrumentation
            return _SearchResultWrapper(page, self._span)
        except StopAsyncIteration:
            raise

    def __getattr__(self, name):
        """Forward any other attributes to the original paged result."""
        return getattr(self._original_paged_result, name)


class _SearchResultWrapper:
    """Wrapper for search results that captures telemetry data."""

    def __init__(self, original_result, span):
        self._original_result = original_result
        self._span = span
        self._result_count = 0
        self._sample_results = []
        self._consumed = False

    def __iter__(self):
        return self

    def __next__(self):
        try:
            result = next(self._original_result)
            self._result_count += 1

            # Capture sample results (first 3 for analysis)
            if len(self._sample_results) < 3:
                result_key = f"top{self._result_count}"

                if hasattr(result, "get"):
                    # Extract all fields from the result
                    result_data = {}
                    for key, value in result.items():
                        if key == "content":
                            # Truncate content to keep span size reasonable
                            result_data[key] = (
                                str(value)[:200] + "..." if len(str(value)) > 200 else str(value)
                            )
                        elif key == "title":
                            result_data[key] = str(value)[:100] if value else "No title"
                        else:
                            # Include all other fields as-is
                            result_data[key] = value

                    # Ensure score is included
                    if "@search.score" in result:
                        result_data["score"] = result["@search.score"]

                    self._sample_results.append({result_key: result_data})

                elif hasattr(result, "__dict__"):
                    # Handle object-style results
                    result_data = {
                        "type": str(type(result)),
                        "fields": list(result.__dict__.keys()),
                        "data": str(result)[:200],
                    }
                    self._sample_results.append({result_key: result_data})
                else:
                    # Handle raw data
                    result_data = {
                        "data": str(result)[:200],
                        "type": str(type(result)),
                    }
                    self._sample_results.append({result_key: result_data})

            return result
        except StopIteration:
            if not self._consumed:
                self._consumed = True
                # Set final count
                _safe_set_attribute(
                    self._span,
                    AzureSearchAttributes.AZURE_SEARCH_RESULT_COUNT,
                    self._result_count,
                )

                # Combine all sample results into a single JSON attribute
                if self._sample_results:
                    import json

                    combined_results = {}
                    for result_dict in self._sample_results:
                        combined_results.update(result_dict)

                    result_json = json.dumps(combined_results, default=str)
                    _safe_set_attribute(self._span, "azure.search.result", result_json)

                # End the span now that results are fully consumed
                self._span.end()
            raise

    def __aiter__(self):
        return self

    def by_page(self, *args, **kwargs):
        """Forward by_page method to the original result object for pagination support."""

        # Get the original by_page result
        original_by_page = self._original_result.by_page(*args, **kwargs)

        # We need to wrap the pages as well to maintain our instrumentation
        return _PagedSearchResultWrapper(original_by_page, self._span, self)

    def get_count(self):
        """Forward get_count method to get total result count."""

        result = self._original_result.get_count()
        # get_count() can be async in AsyncSearchItemPaged
        return result

    async def get_coverage(self):
        """Forward get_coverage method to get coverage percentage (async version)."""

        result = self._original_result.get_coverage()
        # Check if it's a coroutine (async) and await it
        if hasattr(result, "__await__"):
            return await result
        return result

    async def get_facets(self):
        """Forward get_facets method to get facet results (async version)."""
        result = self._original_result.get_facets()
        # Check if it's a coroutine (async) and await it
        if hasattr(result, "__await__"):
            return await result
        return result

    async def get_answers(self):
        """Forward get_answers method to get semantic answers (async version)."""
        result = self._original_result.get_answers()
        # Check if it's a coroutine (async) and await it
        if hasattr(result, "__await__"):
            return await result
        return result

    def __getattr__(self, name):
        """Forward any other attributes/methods to the original result object."""
        if name.startswith("_"):
            # Don't forward private attributes to avoid infinite recursion
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        return getattr(self._original_result, name)

    async def __anext__(self):
        try:
            result = await self._original_result.__anext__()
            self._result_count += 1

            # Capture sample results (first 3 for analysis)
            if len(self._sample_results) < 3:
                result_key = f"top{self._result_count}"

                if hasattr(result, "get"):
                    # Extract all fields from the result
                    result_data = {}
                    for key, value in result.items():
                        if key == "content":
                            # Truncate content to keep span size reasonable
                            result_data[key] = (
                                str(value)[:200] + "..." if len(str(value)) > 200 else str(value)
                            )
                        elif key == "title":
                            result_data[key] = str(value)[:100] if value else "No title"
                        else:
                            # Include all other fields as-is
                            result_data[key] = value

                    # Ensure score is included
                    if "@search.score" in result:
                        result_data["score"] = result["@search.score"]

                    self._sample_results.append({result_key: result_data})

                elif hasattr(result, "__dict__"):
                    # Handle object-style results
                    result_data = {
                        "type": str(type(result)),
                        "fields": list(result.__dict__.keys()),
                        "data": str(result)[:200],
                    }
                    self._sample_results.append({result_key: result_data})
                else:
                    # Handle raw data
                    result_data = {
                        "data": str(result)[:200],
                        "type": str(type(result)),
                    }
                    self._sample_results.append({result_key: result_data})

            return result
        except StopAsyncIteration:
            if not self._consumed:
                self._consumed = True
                # Set final count
                _safe_set_attribute(
                    self._span,
                    AzureSearchAttributes.AZURE_SEARCH_RESULT_COUNT,
                    self._result_count,
                )

                # Combine all sample results into a single JSON attribute
                if self._sample_results:
                    import json

                    combined_results = {}
                    for result_dict in self._sample_results:
                        combined_results.update(result_dict)

                    result_json = json.dumps(combined_results, default=str)
                    _safe_set_attribute(self._span, "azure.search.result", result_json)

                # End the span now that results are fully consumed
                self._span.end()
            raise


def _wrap_search_method(wrapped, instance, args, kwargs):
    """Wrapper for SearchClient.search method (handles both sync and async)."""
    tracer = _get_tracer()

    # Check if this is an async call by looking at the module
    is_async = hasattr(instance, "__module__") and "aio" in instance.__module__

    if is_async:
        return _wrap_async_search_method(wrapped, instance, args, kwargs, tracer)
    else:
        return _wrap_sync_search_method(wrapped, instance, args, kwargs, tracer)


def _wrap_sync_search_method(wrapped, instance, args, kwargs, tracer):
    """Wrapper for synchronous SearchClient.search method."""
    span = tracer.start_span("azure_search.search_operation")
    try:
        # Extract operation details
        search_text = args[0] if args else kwargs.get("search_text", "")
        filter_param = kwargs.get("filter")
        top = kwargs.get("top")
        skip = kwargs.get("skip")

        _set_search_attributes(span, instance, search_text, filter_param, top, skip)

        # Execute the search
        result = wrapped(*args, **kwargs)

        # Create a result wrapper that will keep the span active and end it when iteration completes
        result_wrapper = _SearchResultWrapper(result, span)

        span.set_status(Status(StatusCode.OK))
        return result_wrapper

    except Exception as e:
        span.record_exception(e)
        span.set_status(Status(StatusCode.ERROR, str(e)))
        span.end()  # End span on error
        raise


async def _wrap_async_search_method(wrapped, instance, args, kwargs, tracer):
    """Wrapper for asynchronous SearchClient.search method."""
    span = tracer.start_span("azure_search.search_operation")
    try:
        # Extract operation details
        search_text = args[0] if args else kwargs.get("search_text", "")
        filter_param = kwargs.get("filter")
        top = kwargs.get("top")
        skip = kwargs.get("skip")

        _set_search_attributes(span, instance, search_text, filter_param, top, skip)

        # Execute the search
        result = await wrapped(*args, **kwargs)

        # Create a result wrapper that will keep the span active and end it when iteration completes
        result_wrapper = _SearchResultWrapper(result, span)

        span.set_status(Status(StatusCode.OK))
        return result_wrapper

    except Exception as e:
        span.record_exception(e)
        span.set_status(Status(StatusCode.ERROR, str(e)))
        span.end()  # End span on error
        raise


def _set_search_attributes(span, instance, search_text, filter_param, top, skip):
    """Set search attributes on span."""
    # Set span attributes
    span.set_attribute(SpanAttributes.DB_OPERATION, "search")
    span.set_attribute(AzureSearchAttributes.AZURE_SEARCH_OPERATION, "search")

    # Extract service info from client
    if hasattr(instance, "_endpoint"):
        endpoint_info = _extract_endpoint_info(instance._endpoint)
        if "service_name" in endpoint_info:
            _safe_set_attribute(
                span,
                AzureSearchAttributes.AZURE_SEARCH_SERVICE_NAME,
                endpoint_info["service_name"],
            )

    if hasattr(instance, "_index_name"):
        _safe_set_attribute(
            span, AzureSearchAttributes.AZURE_SEARCH_INDEX_NAME, instance._index_name
        )

    # Set search parameters
    if search_text:
        _safe_set_attribute(span, AzureSearchAttributes.AZURE_SEARCH_QUERY, search_text)
    if filter_param:
        _safe_set_attribute(span, AzureSearchAttributes.AZURE_SEARCH_FILTER, filter_param)
    if top:
        _safe_set_attribute(span, AzureSearchAttributes.AZURE_SEARCH_TOP, top)
    if skip:
        _safe_set_attribute(span, AzureSearchAttributes.AZURE_SEARCH_SKIP, skip)


def _wrap_upload_documents_method(wrapped, instance, args, kwargs):
    """Wrapper for SearchClient.upload_documents method."""
    tracer = _get_tracer()

    with tracer.start_as_current_span("azure_search.upload_documents") as span:
        try:
            documents = args[0] if args else kwargs.get("documents", [])

            # Set span attributes
            span.set_attribute(SpanAttributes.DB_OPERATION, "upload")
            span.set_attribute(
                AzureSearchAttributes.AZURE_SEARCH_OPERATION, "upload_documents"
            )

            # Extract service info
            if hasattr(instance, "_endpoint"):
                endpoint_info = _extract_endpoint_info(instance._endpoint)
                if "service_name" in endpoint_info:
                    _safe_set_attribute(
                        span,
                        AzureSearchAttributes.AZURE_SEARCH_SERVICE_NAME,
                        endpoint_info["service_name"],
                    )

            if hasattr(instance, "_index_name"):
                _safe_set_attribute(
                    span,
                    AzureSearchAttributes.AZURE_SEARCH_INDEX_NAME,
                    instance._index_name,
                )

            # Set document count
            if documents:
                _safe_set_attribute(
                    span, AzureSearchAttributes.AZURE_SEARCH_DOCUMENT_COUNT, len(documents)
                )

            # Execute the upload
            result = wrapped(*args, **kwargs)
            span.set_status(Status(StatusCode.OK))
            return result

        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise


def _wrap_delete_documents_method(wrapped, instance, args, kwargs):
    """Wrapper for SearchClient.delete_documents method."""
    tracer = _get_tracer()

    with tracer.start_as_current_span("azure_search.delete_documents") as span:
        try:
            documents = args[0] if args else kwargs.get("documents", [])

            # Set span attributes
            span.set_attribute(SpanAttributes.DB_OPERATION, "delete")
            span.set_attribute(
                AzureSearchAttributes.AZURE_SEARCH_OPERATION, "delete_documents"
            )

            # Extract service info
            if hasattr(instance, "_endpoint"):
                endpoint_info = _extract_endpoint_info(instance._endpoint)
                if "service_name" in endpoint_info:
                    _safe_set_attribute(
                        span,
                        AzureSearchAttributes.AZURE_SEARCH_SERVICE_NAME,
                        endpoint_info["service_name"],
                    )

            if hasattr(instance, "_index_name"):
                _safe_set_attribute(
                    span,
                    AzureSearchAttributes.AZURE_SEARCH_INDEX_NAME,
                    instance._index_name,
                )

            # Set document count
            if documents:
                _safe_set_attribute(
                    span, AzureSearchAttributes.AZURE_SEARCH_DOCUMENT_COUNT, len(documents)
                )

            # Execute the delete
            result = wrapped(*args, **kwargs)
            span.set_status(Status(StatusCode.OK))
            return result

        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise


def _wrap_search_client():
    """Wrap SearchClient methods."""
    try:
        from azure.search.documents import SearchClient

        # Wrap sync methods
        wrapt.wrap_function_wrapper(SearchClient, "search", _wrap_search_method)
        wrapt.wrap_function_wrapper(
            SearchClient, "upload_documents", _wrap_upload_documents_method
        )
        wrapt.wrap_function_wrapper(
            SearchClient, "delete_documents", _wrap_delete_documents_method
        )

        logger.info("SearchClient methods wrapped for instrumentation")

    except ImportError:
        logger.warning(
            "azure.search.documents.SearchClient not available for instrumentation"
        )
    except Exception as e:
        logger.error(f"Failed to wrap SearchClient: {e}")


def _wrap_search_index_client():
    """Wrap SearchIndexClient methods."""
    try:
        from azure.search.documents.indexes import SearchIndexClient

        # For now, we'll just log that it's available
        # We can add specific method wrapping later
        logger.info("SearchIndexClient available for instrumentation")

    except ImportError:
        logger.warning(
            "azure.search.documents.indexes.SearchIndexClient not available"
        )
    except Exception as e:
        logger.error(f"Failed to wrap SearchIndexClient: {e}")


def _unwrap_search_client():
    """Remove SearchClient instrumentation."""
    try:
        from azure.search.documents import SearchClient

        # Unwrap methods
        if hasattr(SearchClient.search, "__wrapped__"):
            SearchClient.search = SearchClient.search.__wrapped__
        if hasattr(SearchClient.upload_documents, "__wrapped__"):
            SearchClient.upload_documents = (
                SearchClient.upload_documents.__wrapped__
            )
        if hasattr(SearchClient.delete_documents, "__wrapped__"):
            SearchClient.delete_documents = (
                SearchClient.delete_documents.__wrapped__
            )

        logger.info("SearchClient methods unwrapped")

    except Exception as e:
        logger.error(f"Failed to unwrap SearchClient: {e}")


def _wrap_async_search_client():
    """Wrap async SearchClient methods."""
    try:
        from azure.search.documents.aio import SearchClient

        # Wrap async methods
        wrapt.wrap_function_wrapper(SearchClient, "search", _wrap_search_method)
        wrapt.wrap_function_wrapper(
            SearchClient, "upload_documents", _wrap_upload_documents_method
        )
        wrapt.wrap_function_wrapper(
            SearchClient, "delete_documents", _wrap_delete_documents_method
        )

        logger.info("Async SearchClient methods wrapped for instrumentation")

    except ImportError:
        logger.warning(
            "azure.search.documents.aio.SearchClient not available for instrumentation"
        )
    except Exception as e:
        logger.error(f"Failed to wrap async SearchClient: {e}")


def _unwrap_async_search_client():
    """Remove async SearchClient instrumentation."""
    try:
        from azure.search.documents.aio import SearchClient

        # Unwrap methods
        if hasattr(SearchClient.search, "__wrapped__"):
            SearchClient.search = SearchClient.search.__wrapped__
        if hasattr(SearchClient.upload_documents, "__wrapped__"):
            SearchClient.upload_documents = (
                SearchClient.upload_documents.__wrapped__
            )
        if hasattr(SearchClient.delete_documents, "__wrapped__"):
            SearchClient.delete_documents = (
                SearchClient.delete_documents.__wrapped__
            )

        logger.info("Async SearchClient methods unwrapped")

    except Exception as e:
        logger.error(f"Failed to unwrap async SearchClient methods: {e}")


def _unwrap_search_index_client():
    """Remove SearchIndexClient instrumentation."""
    try:
        logger.info("SearchIndexClient unwrapped")
    except Exception as e:
        logger.error(f"Failed to unwrap SearchIndexClient: {e}")


def _wrap_search_client_methods():
    """Main function to wrap SearchClient methods for instrumentation."""

    try:
        # Wrap synchronous SearchClient
        _wrap_search_client()

        # Wrap asynchronous SearchClient
        _wrap_async_search_client()

        # Wrap SearchIndexClient (placeholder for now)
        _wrap_search_index_client()

        logger.info("Azure Search client methods instrumentation completed")

    except Exception as e:
        logger.error(f"Failed to wrap SearchClient methods: {e}")
        raise


def _unwrap_search_client_methods():
    """Main function to remove SearchClient method instrumentation."""
    try:
        _unwrap_search_client()
        _unwrap_async_search_client()
        _unwrap_search_index_client()
        logger.info("Azure Search client methods unwrapped")
    except Exception as e:
        logger.error(f"Failed to unwrap SearchClient methods: {e}")


