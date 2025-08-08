from enum import IntEnum
from typing import Any

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.domain import SIATEnvironment, SIATModality
from sincpro_siat_soap.global_definitions import SIAT_WSDL


class PointOfSaleType(IntEnum):
    COMISIONISTA = 1
    VENTANILLA_COBRANZA = 2
    MOVILES = 3
    YPFB = 4
    VENTA_CAJERO = 5


class CommandCreatePointOfSale(DataTransferObject):
    type_point_of_sale: int
    description: str
    point_of_sale_name: str
    system_code: str
    branch_office: int
    cuis: str
    nit: int | str
    enviroment: SIATEnvironment
    billing_type: SIATModality


class ResponseCreatePointOfSale(DataTransferObject):
    raw_response: Any
    point_of_sale_id: int


@siat_soap_sdk.feature(CommandCreatePointOfSale)
class CreatePointOfSale(Feature):

    def execute(self, param_object: CommandCreatePointOfSale) -> ResponseCreatePointOfSale:
        response = self.soap_client(SIAT_WSDL.OPERACIONES).service.registroPuntoVenta(
            SolicitudRegistroPuntoVenta={
                "nombrePuntoVenta": param_object.point_of_sale_name,
                "descripcion": param_object.description,
                "codigoAmbiente": param_object.enviroment,
                "codigoModalidad": param_object.billing_type,
                "codigoTipoPuntoVenta": param_object.type_point_of_sale,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
            }
        )

        return ResponseCreatePointOfSale(
            point_of_sale_id=response["codigoPuntoVenta"], raw_response=response
        )
