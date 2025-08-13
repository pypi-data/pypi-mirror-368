import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Union, Optional, Set, Mapping

from httpx import Response, BaseTransport, URL, Proxy

from checkbox_sdk import __version__
from checkbox_sdk.client.utils import strip_tags
from checkbox_sdk.consts import API_VERSION, BASE_API_URL, DEFAULT_REQUEST_TIMEOUT, DEFAULT_RATE_LIMIT
from checkbox_sdk.exceptions import CheckBoxAPIError, CheckBoxAPIValidationError, CheckBoxError
from checkbox_sdk.methods.base import AbstractMethod
from checkbox_sdk.storage.simple import SessionStorage

logger = logging.getLogger(__name__)


class BaseCheckBoxClient(ABC):  # pylint: disable=too-many-instance-attributes
    """
    Abstract base class for interacting with the Checkbox API.

    This class provides foundational methods and properties for making API requests,
    managing session storage, and handling common configurations like proxy, SSL verification,
    and request timeouts.

    Args:
        base_url: The base URL for the Checkbox API. Defaults to `BASE_API_URL`.
        requests_timeout: The timeout for API requests, in seconds. Defaults to `DEFAULT_REQUEST_TIMEOUT`.
        proxy: Optional proxy configuration. A proxy URL where all the traffic should be routed.
        proxy_mounts: Optional mapping of proxy configurations for specific transports or hosts.
                      This allows finer control over proxy behavior for different requests.
        verify_ssl: Whether to verify SSL certificates. Defaults to `True`.
        trust_env: Whether to trust environment variables for proxy configuration. Defaults to `True`.
        api_version: The version of the API to use. Defaults to `API_VERSION`.
        storage: Optional session storage to use for requests. Defaults to a new `SessionStorage` instance.
        client_name: The name of the client, used for identifying requests. Defaults to `"checkbox-sdk"`.
        client_version: The version of the client. Defaults to the package version `__version__`.
        integration_key: Optional integration key for accessing the API. Defaults to `None`.
        requests_per_10s: Maximum number of requests per 10 seconds to avoid rate limits. Defaults to
                          `DEFAULT_RATE_LIMIT`.

    Attributes:
        base_url: The base URL for the Checkbox API.
        api_version: The version of the API to use.
        timeout: The timeout for API requests, in seconds.
        proxy: The proxy configuration for the client.
        proxy_mounts: The mapping of proxy configurations for specific transports or hosts.
        verify_ssl: Whether SSL certificates are verified.
        storage: The session storage instance used for requests.
        client_name: The name of the client.
        client_version: The version of the client.
        integration_key: The integration key for accessing the API.
        trust_env: Whether to trust environment variables for proxy configuration.
        rate_limit: The number of requests allowed per 10 seconds (rate limit).
    """

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        base_url: str = BASE_API_URL,
        requests_timeout: int = DEFAULT_REQUEST_TIMEOUT,
        proxy: Optional[Union[URL, str, Proxy]] = None,
        proxy_mounts: Optional[(Mapping[str, BaseTransport | None])] = None,
        verify_ssl: bool = True,
        trust_env: bool = True,
        api_version: str = API_VERSION,
        storage: Optional[SessionStorage] = None,
        client_name: str = "checkbox-sdk",
        client_version: str = __version__,
        integration_key: Optional[str] = None,
        requests_per_10s: Optional[int] = None,
    ) -> None:
        self.base_url = base_url
        self.api_version = api_version
        self.timeout = requests_timeout
        self.proxy = proxy
        self.proxy_mounts = proxy_mounts
        self.verify_ssl = verify_ssl
        self.storage = storage or SessionStorage()
        self.client_name = client_name
        self.client_version = client_version
        self.integration_key = integration_key
        self.trust_env = trust_env
        self.rate_limit = requests_per_10s or DEFAULT_RATE_LIMIT

    @property
    def client_headers(self) -> Dict[str, Any]:
        """
        Constructs the headers to be used in API requests.

        Returns:
            A dictionary of headers including the client name, version, and optionally the integration key.
        """
        headers = {
            "X-Client-Name": self.client_name,
            "X-Client-Version": self.client_version,
        }
        if self.integration_key:
            headers["X-Access-Key"] = self.integration_key
        return headers

    @classmethod
    def _check_response(cls, response: Response):
        """
        Checks the API response for errors and raises appropriate exceptions.

        Args:
            response: The `Response` object returned from the API.

        Raises:
            CheckBoxError: If the response status code indicates a server error (500+).
            CheckBoxAPIValidationError: If the response status code is 422, indicating a validation error.
            CheckBoxAPIError: If the response status code indicates a client error (400+).
        """
        if response.status_code >= 500:
            raise CheckBoxError(
                f"Failed to make request [status={response.status_code}, text={strip_tags(response.text)[:200]!r}]"
            )
        if response.status_code == 422:
            raise CheckBoxAPIValidationError(status=response.status_code, content=response.json())
        if response.status_code >= 400:
            raise CheckBoxAPIError(status=response.status_code, content=response.json())

    def set_license_key(self, storage: Optional[SessionStorage], license_key: Optional[str]) -> None:
        """
        Sets the license key in the session storage.

        Args:
            storage: Optional session storage to use. If not provided, the default storage will be used.
            license_key: The license key to set in the storage. If `None`, no action is taken.
        """
        if license_key is None:
            return
        storage = storage or self.storage
        storage.license_key = license_key

    @staticmethod
    def handle_wait_status(result: Dict[str, Any], field: str, expected_value: Set[Any], initial: float):
        if result[field] not in expected_value:
            raise ValueError(
                f"Object did not change field {field!r} "
                f"to one of expected values {expected_value} (actually {result[field]!r}) "
                f"in {time.monotonic() - initial:.3f} seconds"  # noqa: E231
            )

        logger.info(
            "Status changed in %.3f seconds to %r",
            time.monotonic() - initial,
            result[field],
        )


class BaseSyncCheckBoxClient(BaseCheckBoxClient, ABC):
    @abstractmethod
    def emit(
        self,
        call: AbstractMethod,
        storage: Optional[SessionStorage] = None,
        request_timeout: Optional[float] = None,
    ):
        """
        Abstract method to be implemented by subclasses to send a request to the Checkbox API.

        Args:
            call: The method encapsulating the API request details.
            storage: Optional session storage to use for the request. If not provided, the default storage will be
                     used.
            request_timeout: Optional timeout for the request. If not provided, the client's default timeout will be
                             used.

        Returns:
            The response from the API.

        This method must be implemented by any subclass.
        """

    def __call__(self, *args, **kwargs):
        return self.emit(*args, **kwargs)


class BaseAsyncCheckBoxClient(BaseCheckBoxClient, ABC):
    @abstractmethod
    async def emit(
        self,
        call: AbstractMethod,
        storage: Optional[SessionStorage] = None,
        request_timeout: Optional[float] = None,
    ):
        """
        Abstract method to be implemented by subclasses to send an asynchronous request to the Checkbox API.

        Args:
            call: The method encapsulating the API request details.
            storage: Optional session storage to use for the request. If not provided, the default storage will be
                     used.
            request_timeout: Optional timeout for the request. If not provided, the client's default timeout will be
                             used.

        Returns:
            The response from the API.

        This method must be implemented by any subclass.
        """

    async def __call__(self, *args, **kwargs):
        return await self.emit(*args, **kwargs)
