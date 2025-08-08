"""Module to manage the soap clients for the SIAT services"""

from datetime import datetime
from typing import Dict

from sincpro_framework.sincpro_logger import logger
from zeep import Client

# isort: off
from sincpro_siat_soap.domain import SIATEnvironment

# isort: on
from sincpro_siat_soap.config import settings
from sincpro_siat_soap.global_definitions import SIAT_WSDL, WSDL_SERVICE_LIST
from sincpro_siat_soap.infrastructure.soap_client import SoapClient
from sincpro_siat_soap.shared.core_exceptions import SIATInfrastructureError

TMAP_SOAP_CLIENT = Dict[str, SoapClient]


class ProxySiatServices:
    """Enhanced facade to manage SIAT services using SoapClient wrappers"""

    MAX_SECONDS_TO_REGENERATE_SOAP_CLIENTS = 60

    def __init__(self, siat_environment: SIATEnvironment, token: str):
        self.siat_environment = siat_environment
        self.token = token
        self.last_try_regenerate_all_soap_clients: datetime = datetime.now()
        self.soap_clients: TMAP_SOAP_CLIENT = {}
        self.setup()

    def setup(self) -> TMAP_SOAP_CLIENT:
        """Initialize all soap client wrappers"""
        for service_name in WSDL_SERVICE_LIST:
            self.soap_clients[service_name] = SoapClient(
                service_name,
                self.siat_environment,
                self.token,
            )
        return self.soap_clients

    def regenerate_unhealthy_soap_clients(self) -> None:
        """Regenerate soap clients that are unhealthy"""
        total_seconds_from_last_time = (
            datetime.now() - self.last_try_regenerate_all_soap_clients
        ).seconds

        if total_seconds_from_last_time < self.MAX_SECONDS_TO_REGENERATE_SOAP_CLIENTS:
            return

        self.last_try_regenerate_all_soap_clients = datetime.now()

        for service_name, soap_client in self.soap_clients.items():
            if not soap_client.is_healthy():
                logger.info(f"Regenerating unhealthy soap client: [{service_name}]")
                soap_client.build_zeep_client()

    def get_client_for_service(self, service_name: str) -> Client:
        """Get a specific SoapClient wrapper by service name"""
        if service_name not in self.soap_clients:
            raise SIATInfrastructureError(f"Unknown service: {service_name}")

        self.regenerate_unhealthy_soap_clients()

        soap_client = self.soap_clients[service_name]
        if not soap_client.is_healthy():
            raise SIATInfrastructureError(f"Service [{service_name}] is down")

        return soap_client.client

    def is_outage_services(self) -> bool:
        """Check if critical services are unavailable"""
        try:
            common_client = self.soap_clients[SIAT_WSDL.FACTURA_COMPRA_VENTA]
            electronic_client = self.soap_clients[SIAT_WSDL.SERVICIOS_ELECTRONICA]
            computarizada_client = self.soap_clients[SIAT_WSDL.SERVICIOS_COMPUTARIZADA]

            # Check if critical combinations are down
            if not common_client.is_healthy() and not electronic_client.is_healthy():
                return True

            if not common_client.is_healthy() and not computarizada_client.is_healthy():
                return True

            if not electronic_client.is_healthy() and not computarizada_client.is_healthy():
                return True

            return False
        except Exception:
            logger.exception("Error checking service outage status")
            return True

    @property
    def key(self) -> str:
        return f"{self.siat_environment}_{self.token}"


class ProxySiatRegistry:
    """Registry for multy tenancy"""

    def __init__(self):
        self.proxies: Dict[str, ProxySiatServices] = {}
        self._default_proxy = None

    def get_proxy(
        self, siat_env: SIATEnvironment, token: str, is_default=False
    ) -> ProxySiatServices:
        """Get a specific ProxySiatServices instance by key"""
        key = f"{siat_env}_{token}"
        if key not in self.proxies:
            self.proxies[key] = ProxySiatServices(siat_env, token)

        if is_default:
            self._default_proxy = self.proxies[key]
        return self.proxies[key]

    @property
    def default(self) -> ProxySiatServices:
        """Get the default ProxySiatServices instance"""
        if not self._default_proxy:
            raise SIATInfrastructureError("No default client services configured")
        return self._default_proxy


proxy_siat = ProxySiatRegistry()
proxy_siat.get_proxy(
    settings.environment or SIATEnvironment.TEST,
    settings.token,
    is_default=True,
)
