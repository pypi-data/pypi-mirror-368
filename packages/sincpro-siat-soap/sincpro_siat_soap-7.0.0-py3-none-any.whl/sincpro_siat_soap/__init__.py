"""SDK for SINCPRO SIAT SOAP API."""

from typing import Any, Dict, NotRequired, TypedDict, Union

from sincpro_framework import ApplicationService as _ApplicationService
from sincpro_framework import DataTransferObject
from sincpro_framework import Feature as _Feature
from sincpro_framework import UseFramework as _UseFramework

from sincpro_siat_soap.adapters.siat_exception_builder import siat_exception_builder
from sincpro_siat_soap.adapters.soap import Client, ProxySiatRegistry, proxy_siat
from sincpro_siat_soap.config import settings
from sincpro_siat_soap.domain import SIATEnvironment
from sincpro_siat_soap.logger import logger
from sincpro_siat_soap.shared.core_exceptions import SIATException

# ------------------------------------------------------------------------------------
# Initialize the framework
# ------------------------------------------------------------------------------------
siat_soap_sdk = _UseFramework("siat-soap-sdk", log_features=False)
siat_soap_sdk.add_dependency("proxy_siat", proxy_siat)


class KnownContextKeys(TypedDict, total=False):
    """Known context keys with their types"""

    TOKEN: NotRequired[str]
    SIAT_ENV: NotRequired[SIATEnvironment]


# Type alias for better readability
ContextType = Union[Dict[str, Any], KnownContextKeys]


class DependencyContextType:
    proxy_siat: ProxySiatRegistry
    context: ContextType

    def soap_client(self, wsdl: str) -> Client:
        """
        Helper function to get SOAP client with context-aware proxy selection.

        Args:
            wsdl: WSDL service name to get client for

        Returns:
            Client: SOAP client instance for the requested service
        """
        token = self.context.get("TOKEN")
        siat_env = self.context.get("SIAT_ENV")

        if token and siat_env:
            return self.proxy_siat.get_proxy(
                SIATEnvironment(siat_env), token
            ).get_client_for_service(wsdl)

        return self.proxy_siat.default.get_client_for_service(wsdl)

    def raise_if_transaction_is_false(self, response: Dict[str, Any]) -> None:
        """
        Raise exception if transaction response indicates failure.

        Args:
            response: Response dictionary containing transaction status

        Raises:
            SIATException: If transaction is False
        """
        if response.get("transaccion") is False:
            fn_raise_exception = siat_exception_builder(response)
            fn_raise_exception()


class Feature(_Feature, DependencyContextType):
    pass


class ApplicationService(_ApplicationService, DependencyContextType):
    pass


# ------------------------------------------------------------------------------------
# Exporting modules
# ------------------------------------------------------------------------------------

from sincpro_siat_soap.services import (
    auth_permissions,
    billing,
    digital_files,
    operations,
    synchronization_data,
)

__all__ = [
    "siat_soap_sdk",
    "auth_permissions",
    "synchronization_data",
    "Feature",
    "DataTransferObject",
]
