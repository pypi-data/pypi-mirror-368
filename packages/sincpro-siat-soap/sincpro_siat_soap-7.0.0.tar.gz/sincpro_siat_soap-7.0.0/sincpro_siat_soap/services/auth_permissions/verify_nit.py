"""Check if a NIT is valid for a given taxpayer."""

from typing import Any

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.domain import SIATEnvironment, SIATModality
from sincpro_siat_soap.global_definitions import SIAT_WSDL


class CommandVerifyNIT(DataTransferObject):
    nit: str | int
    nit_para_verificar: str | int
    cuis: str
    system_code: str
    point_of_sale: int
    branch_office: int
    environment: SIATEnvironment
    billing_type: SIATModality


class ResponseVerifyNIT(DataTransferObject):
    is_valid_nit: bool
    raw_response: Any


@siat_soap_sdk.feature(CommandVerifyNIT)
class VerifyNIT(Feature):

    def execute(self, dto: CommandVerifyNIT) -> ResponseVerifyNIT:
        response = self.soap_client(SIAT_WSDL.OBTENCION_CODIGO).service.verificarNit(
            SolicitudVerificarNit={
                "codigoAmbiente": dto.environment,
                "codigoModalidad": dto.billing_type,
                "codigoSistema": dto.system_code,
                "codigoSucursal": dto.branch_office,
                "nit": dto.nit,
                "nitParaVerificacion": dto.nit_para_verificar,
                "cuis": dto.cuis,
            }
        )
        return ResponseVerifyNIT(is_valid_nit=response["transaccion"], raw_response=response)
