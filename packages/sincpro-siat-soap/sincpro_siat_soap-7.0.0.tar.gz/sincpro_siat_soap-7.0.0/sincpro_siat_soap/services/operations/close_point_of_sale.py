from typing import Any

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.domain import SIATEnvironment
from sincpro_siat_soap.global_definitions import SIAT_WSDL


class CommandClosePointOfSale(DataTransferObject):
    point_of_sale: int
    system_code: str
    branch_office: int
    cuis: str
    nit: int | str
    enviroment: SIATEnvironment


class ResponseClosePointOfSale(DataTransferObject):
    raw_response: Any
    success: bool


@siat_soap_sdk.feature(CommandClosePointOfSale)
class ClosePointOfSale(Feature):
    def execute(self, param_object: CommandClosePointOfSale) -> ResponseClosePointOfSale:
        response = self.soap_client(SIAT_WSDL.OPERACIONES).service.cierrePuntoVenta(
            SolicitudCierrePuntoVenta={
                "codigoAmbiente": param_object.enviroment,
                "codigoPuntoVenta": param_object.point_of_sale,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
            }
        )

        return ResponseClosePointOfSale(
            success=response["transaccion"], raw_response=response
        )
