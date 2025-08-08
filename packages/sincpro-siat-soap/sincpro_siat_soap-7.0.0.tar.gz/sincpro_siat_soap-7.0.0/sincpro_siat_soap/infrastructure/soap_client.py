"""SoapClient wrapper for Zeep Client to handle SIAT services"""

from typing import Optional

from requests import Session
from sincpro_framework.sincpro_logger import logger
from zeep import Client
from zeep.cache import InMemoryCache
from zeep.transports import Transport

from sincpro_siat_soap.domain import SIATEnvironment
from sincpro_siat_soap.global_definitions import (
    SIAT_PRODUCTION_ENDPOINTS,
    SIAT_TESTING_ENDPOINTS,
    WSDL_DIR,
)
from sincpro_siat_soap.shared.timeout import timeout_with_check_exists_response


class SoapClient:
    """Wrapper for Zeep Client to handle SIAT SOAP services"""

    def __init__(
        self,
        service_name: str,
        environment: SIATEnvironment,
        token: str,
        timeout: int = 10,
        cache_ttl: int = 3600 * 8,
    ):
        """
        Initialize SoapClient with service configuration.

        Args:
            service_name: Name of the SIAT service
            environment: SIAT environment (TEST or PRODUCTION)
            token: Authentication token for SIAT services
            timeout: Request timeout in seconds
            cache_ttl: Cache time-to-live in seconds
        """
        self.service_name = service_name
        self.environment = environment
        self.token = token
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self._zeep_client: Optional[Client] = None
        self.build_zeep_client()

    @property
    def client(self) -> Client:
        """Get the underlying Zeep client, creating it if necessary."""
        if self._zeep_client is None:
            self._zeep_client = self.build_zeep_client()
        return self._zeep_client

    def _build_remote_soap_client(self) -> Client:
        """
        Build SOAP client using remote WSDL endpoint.

        Returns:
            Client: Configured Zeep client with remote WSDL

        Raises:
            Exception: If remote WSDL cannot be accessed or client creation fails
        """
        logger.info(
            f"Building remote soap client [{self.service_name}] env [{self.environment}]"
        )

        # Get remote WSDL URL
        endpoints = (
            SIAT_PRODUCTION_ENDPOINTS
            if self.environment == SIATEnvironment.PRODUCTION
            else SIAT_TESTING_ENDPOINTS
        )
        remote_wsdl_url = endpoints[self.service_name]

        return self._obj_zeep_client(remote_wsdl_url)

    def _build_local_soap_client(self) -> Client:
        """
        Build SOAP client using local WSDL file.

        Returns:
            Client: Configured Zeep client with local WSDL

        Raises:
            Exception: If local WSDL file cannot be accessed or client creation fails
        """
        logger.info(
            f"Building local soap client [{self.service_name}] env [{self.environment}]"
        )

        env_dir = (
            "production" if self.environment == SIATEnvironment.PRODUCTION else "testing"
        )
        local_wsdl_path = f"{WSDL_DIR}/{env_dir}/{self.service_name}.wsdl"

        return self._obj_zeep_client(local_wsdl_path)

    @timeout_with_check_exists_response(5)
    def _obj_zeep_client(self, wsdl_path: str) -> Optional[Client]:
        """
        Create a Zeep client with the given configuration.

        Args:
            wsdl_path: Path or URL to WSDL file

        Returns:
            Client: Configured Zeep client
        """
        headers = dict()
        if self.token:
            headers["apikey"] = f"TokenApi {self.token}"

        cache = InMemoryCache(timeout=self.cache_ttl)
        transport = Transport(
            timeout=self.timeout, cache=cache, operation_timeout=self.timeout
        )

        if headers:
            session = Session()
            session.headers.update(headers)
            transport.session = session

        try:
            return Client(wsdl=wsdl_path, transport=transport)
        except Exception:
            logger.exception(f"Failed to build soap client for [{wsdl_path}]")
            return None

    def build_zeep_client(self) -> Optional[Client]:
        """Create the Zeep client with fallback to local WSDL."""

        if remote_client := self._build_remote_soap_client():
            self._zeep_client = remote_client
            return self._zeep_client

        if local_client := self._build_local_soap_client():
            self._zeep_client = local_client
            return self._zeep_client

        self._zeep_client = None
        return self._zeep_client

    def is_healthy(self) -> bool:
        """Check if the client is healthy and ready to use."""
        return self._zeep_client is not None

    def __repr__(self) -> str:
        """String representation of the SoapClient."""
        return (
            f"SoapClient(service={self.service_name}, "
            f"env={self.environment}, "
            f"client_ready={self._zeep_client is not None})"
        )
