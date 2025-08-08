from typing import Any

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.domain import SIATEnvironment, SIATModality
from sincpro_siat_soap.global_definitions import SIAT_WSDL


class CommandRevokeCerts(DataTransferObject):
    cert: str
    system_code: str
    branch_office: int
    cuis: str
    nit: str | int
    reason: str
    date_from_request_rovoke: str
    environment: SIATEnvironment
    billing_type: SIATModality


class ResponseRevokeCerts(DataTransferObject):
    was_revoked: str
    raw_reponse: Any


@siat_soap_sdk.feature(CommandRevokeCerts)
class RevokeCerts(Feature):

    def execute(self, param_object: CommandRevokeCerts) -> ResponseRevokeCerts:
        response = self.soap_client(
            SIAT_WSDL.OBTENCION_CODIGO
        ).service.notificaCertificadoRevocado(
            SolicitudNotificaRevocado={
                "certificado": param_object.cert,
                "codigoAmbiente": param_object.environment,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cuis": param_object.cuis,
                "fechaRevocacion": param_object.date_from_request_rovoke,
                "nit": param_object.nit,
                "razonRevocacion": param_object.reason,
            }
        )

        return ResponseRevokeCerts(was_revoked=response["transaccion"], raw_reponse=response)
