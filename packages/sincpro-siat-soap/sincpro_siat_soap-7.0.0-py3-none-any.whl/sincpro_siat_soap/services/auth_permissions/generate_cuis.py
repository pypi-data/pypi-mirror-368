"""Generate Codigo Unico de Sistema (CUIS) for a given system code, point of sale, branch office, environment and billing type."""

from datetime import datetime
from typing import Any

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.domain import SIATEnvironment, SIATModality
from sincpro_siat_soap.global_definitions import SIAT_WSDL
from sincpro_siat_soap.shared import fn_datetime


class CommandGenerateCUIS(DataTransferObject):
    nit: int | str
    system_code: str
    point_of_sale: int
    branch_office: int
    environment: SIATEnvironment
    billing_type: SIATModality


class ResponseGenerateCUIS(DataTransferObject):
    cuis: str | None
    end_datetime: datetime | None
    raw_response: Any


@siat_soap_sdk.app_service(CommandGenerateCUIS)
class GenerateCUIS(Feature):
    def execute(self, dto: CommandGenerateCUIS) -> ResponseGenerateCUIS:
        response = self.soap_client(SIAT_WSDL.OBTENCION_CODIGO).service.cuis(
            SolicitudCuis={
                "codigoAmbiente": dto.environment,
                "codigoModalidad": dto.billing_type,
                "codigoSistema": dto.system_code,
                "codigoSucursal": dto.branch_office,
                "codigoPuntoVenta": dto.point_of_sale,
                "nit": dto.nit,
            }
        )
        return ResponseGenerateCUIS(
            raw_response=response,
            end_datetime=fn_datetime.from_bolivia_tz_to_naive_utc(response["fechaVigencia"]),
            cuis=response["codigo"],
        )
