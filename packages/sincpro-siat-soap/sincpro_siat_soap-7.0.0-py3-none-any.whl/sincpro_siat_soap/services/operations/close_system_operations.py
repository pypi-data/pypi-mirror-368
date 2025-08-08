from typing import Any

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.domain import SIATEnvironment, SIATModality
from sincpro_siat_soap.global_definitions import SIAT_WSDL


class CommandCloseSystemOperations(DataTransferObject):
    point_of_sale: int
    system_code: str
    branch_office: int
    cuis: str
    nit: int | str
    enviroment: SIATEnvironment
    billing_type: SIATModality


class ResponseCloseSystemOperations(DataTransferObject):
    raw_response: Any
    success: bool


@siat_soap_sdk.feature(CommandCloseSystemOperations)
class CloseSystemOperations(Feature):
    def execute(
        self, param_object: CommandCloseSystemOperations
    ) -> ResponseCloseSystemOperations:
        siat_soap_sdk.logger.info(
            f"The CUIS and CUFD will be revoked for SUCURSAL: [{param_object.branch_office}] PUNTO DE VENTA: [{param_object}]"
        )
        response = self.soap_client(SIAT_WSDL.OPERACIONES).service.cierreOperacionesSistema(
            SolicitudOperaciones={
                "codigoAmbiente": param_object.enviroment,
                "codigoModalidad": param_object.billing_type,
                "codigoPuntoVenta": param_object.point_of_sale,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
            }
        )

        return ResponseCloseSystemOperations(
            success=response["transaccion"], raw_response=response
        )
