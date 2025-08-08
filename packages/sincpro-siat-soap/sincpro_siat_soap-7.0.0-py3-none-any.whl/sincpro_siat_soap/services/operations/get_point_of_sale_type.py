from typing import Any, List

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.domain import SIATEnvironment
from sincpro_siat_soap.global_definitions import SIAT_WSDL


class CommandGetPointOfSales(DataTransferObject):
    system_code: str
    branch_office: int
    cuis: str
    nit: int | str
    enviroment: SIATEnvironment


class ResponseGetPointOfSale(DataTransferObject):
    raw_response: Any
    list_point_of_sales: List[Any]


@siat_soap_sdk.feature(CommandGetPointOfSales)
class GetPointOfSales(Feature):

    def execute(self, param_object: CommandGetPointOfSales) -> ResponseGetPointOfSale:
        response = self.soap_client(SIAT_WSDL.OPERACIONES).service.consultaPuntoVenta(
            SolicitudConsultaPuntoVenta={
                "codigoAmbiente": param_object.enviroment,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
            }
        )

        return ResponseGetPointOfSale(
            list_point_of_sales=response["listaPuntosVentas"], raw_response=response
        )
