from sincpro_siat_soap import Feature, siat_soap_sdk
from sincpro_siat_soap.global_definitions import SIAT_WSDL

from .shared import BaseRequestSynchronization, BaseSIATResponse


class CommandSyncDate(BaseRequestSynchronization):
    pass


class ResponseSyncDate(BaseSIATResponse):
    pass


@siat_soap_sdk.feature(CommandSyncDate)
class SyncDate(Feature):

    def execute(self, param_object: CommandSyncDate) -> ResponseSyncDate:
        response = self.soap_client(
            SIAT_WSDL.SINCRONIZACION_DE_DATOS
        ).service.sincronizarFechaHora(
            SolicitudSincronizacion={
                "codigoAmbiente": param_object.environment,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "codigoPuntoVenta": param_object.point_of_sale,
                "nit": param_object.nit,
                "cuis": param_object.cuis,
            }
        )

        return ResponseSyncDate(raw_response=response, comparison_data=response["fechaHora"])
