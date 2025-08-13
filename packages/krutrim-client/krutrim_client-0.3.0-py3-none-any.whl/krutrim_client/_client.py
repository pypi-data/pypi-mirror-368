from __future__ import annotations

import os
from typing import Any, Union, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from .resources import highlvlvpc, kbs, securityGroup, startStopVM, sshkey
from .resources.kos import kos
from .resources.kpod import kpod
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError, KrutrimClientError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "KrutrimClient",
    "AsyncKrutrimClient",
    "Client",
    "AsyncClient",
]


class KrutrimClient(SyncAPIClient):
    highlvlvpc: highlvlvpc.HighlvlvpcResource
    kbs: kbs.KbsResource
    securityGroup: securityGroup.SecurityGroupResource
    startStopVM: startStopVM.StartStopResource
    sshkey :sshkey.SshkeysResource
    kpod: kpod.KpodResource
    kos: kos.KosResource
    
    
    with_raw_response: KrutrimClientWithRawResponse
    with_streaming_response: KrutrimClientWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous KrutrimClient client instance.

        This automatically infers the `api_key` argument from the `KRUTRIMCLIENT_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("KRUTRIMCLIENT_API_KEY")
        if api_key is None:
            raise KrutrimClientError(
                "The api_key client option must be set either by passing api_key to the client or by setting the KRUTRIMCLIENT_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("KRUTRIMCLIENT_BASE_URL")
        if base_url is None:
            base_url = f"https://cloud.olakrutrim.com"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.highlvlvpc = highlvlvpc.HighlvlvpcResource(self)
        self.kbs =  kbs.KbsResource(self)
        self.securityGroup = securityGroup.SecurityGroupResource(self)
        self.startStopVM = startStopVM.StartStopResource(self)
        self.sshkey = sshkey.SshkeysResource(self)
        self.kpod = kpod.KpodResource(self)
        self.kos = kos.KosResource(self)
        
        
        self.with_raw_response = KrutrimClientWithRawResponse(self)
        self.with_streaming_response = KrutrimClientWithStreamedResponse(self)
        

        

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncKrutrimClient(AsyncAPIClient):
    highlvlvpc: highlvlvpc.AsyncHighlvlvpcResource
    kbs: kbs.AsyncKbsResource
    securityGroup: securityGroup.AsyncSecurityGroupResource
    startStopVM: startStopVM.AsyncStartStopResource
    sshkey: sshkey.AsyncSshkeysResource
    kpod: kpod.AsyncKpodResource
    kos: kos.AsyncKosResource 
    
    
    with_raw_response: AsyncKrutrimClientWithRawResponse
    with_streaming_response: AsyncKrutrimClientWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncKrutrimClient client instance.

        This automatically infers the `api_key` argument from the `KRUTRIMCLOUD_Client_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("KRUTRIMCLIENT_API_KEY")
        if api_key is None:
            raise KrutrimClientError(
                "The api_key client option must be set either by passing api_key to the client or by setting the KRUTRIMCLIENT_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("KRUTRIMCLIENT_BASE_URL")
        if base_url is None:
            base_url = f"https://cloud.olakrutrim.com"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.highlvlvpc = highlvlvpc.AsyncHighlvlvpcResource(self)
        self.kbs = kbs.AsyncKbsResource(self)
        self.securityGroup: securityGroup.AsyncSecurityGroupResource(self)
        self.startStopVM: startStopVM.AsyncStartStopResource(self)
        self.sshkey: sshkey.AsyncSshkeysResource(self)
        self.kpod = kpod.AsyncKpodResource(self)
        self.kos = kos.AsyncKosResource(self) 
        
        
        self.with_raw_response = AsyncKrutrimClientWithRawResponse(self)
        self.with_streaming_response = AsyncKrutrimClientWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class KrutrimClientWithRawResponse:
    def __init__(self, client: KrutrimClient) -> None:
        self.highlvlvpc = highlvlvpc.HighlvlvpcResourceWithRawResponse(client.highlvlvpc)
        self.kbs = kbs.KbsResourceWithRawResponse(client.kbs)
        self.securityGroup = securityGroup.SecurityGroupResourceWithRawResponse(client.securityGroup)
        self.startStopVM = startStopVM.StartStopResourceWithRawResponse(client.startStopVM)
        self.sshkey = sshkey.SshkeysResourceWithRawResponse(client.sshkey)
        self.kpod = kpod.KpodResourceWithRawResponse(client.kpod)
        self.kos =kos.KosResourceWithRawResponse(client.kos)
        
        


class AsyncKrutrimClientWithRawResponse:
    def __init__(self, client: AsyncKrutrimClient) -> None:
        self.highlvlvpc = highlvlvpc.AsyncHighlvlvpcResourceWithRawResponse(client.highlvlvpc)
        self.kbs = kbs.AsyncKbsResourceWithRawResponse(client.kbs)
        self.securityGroup = securityGroup.AsyncSecurityGroupResourceWithRawResponse(client.securityGroup)
        self.startStopVM = startStopVM.AsyncStartStopResourceWithRawResponse(client.startStopVM)
        self.sshkey = sshkey.AsyncSshkeysResourceWithRawResponse(client.sshkey)
        self.kpod = kpod.AsyncKpodResourceWithRawResponse(client.kpod)
        self.kos = kos.AsyncKosResourceWithRawResponse(client.kos)
        
       


class KrutrimClientWithStreamedResponse:
    def __init__(self, client: KrutrimClient) -> None:
        self.highlvlvpc = highlvlvpc.HighlvlvpcResourceWithStreamingResponse(client.highlvlvpc)
        self.kbs = kbs.KbsResourceWithStreamingResponse(client.kbs)
        self.securityGroup = securityGroup.SecurityGroupResourceWithStreamingResponse(client.securityGroup)
        self.startStopVM = startStopVM.StartStopResourceWithStreamingResponse(client.startStopVM)
        self.sshkey = sshkey.SshkeysResourceWithStreamingResponse(client.sshkey)
        self.kpod = kpod.KpodResourceWithStreamingResponse(client.kpod)
        self.kos = kos.KosResourceWithStreamingResponse(client.kos)
        
        

class AsyncKrutrimClientWithStreamedResponse:
    def __init__(self, client: AsyncKrutrimClient) -> None:
        self.highlvlvpc = highlvlvpc.AsyncHighlvlvpcResourceWithStreamingResponse(client.highlvlvpc)
        self.kbs = kbs.AsyncKbsResourceWithStreamingResponse(client.kbs)
        self.securityGroup = securityGroup.AsyncSecurityGroupResourceWithStreamingResponse(client.securityGroup)
        self.startStopVM = startStopVM.AsyncStartStopResourceWithStreamingResponse(client.startStopVM)
        self.sshkey = sshkey.AsyncSshkeysResourceWithStreamingResponse(client.sshkey)
        self.kpod = kpod.AsyncKpodResourceWithStreamingResponse(client.kpod)
        self.kos = kos.AsyncKosResourceWithStreamingResponse(client.kos)
        
        

Client = KrutrimClient

AsyncClient = AsyncKrutrimClient
