"""Codigo unico de factura digital (CUFD) generation for a given system code, point of sale, branch office, environment and billing type."""

from datetime import datetime, timedelta
from typing import Any

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.domain import SIATEnvironment, SIATModality
from sincpro_siat_soap.global_definitions import SIAT_WSDL
from sincpro_siat_soap.shared import core_exceptions, fn_datetime


class CommandGenerateCUFD(DataTransferObject):
    nit: int | str
    system_code: str
    point_of_sale: int
    branch_office: int
    cuis: str
    environment: SIATEnvironment
    billing_type: SIATModality


class ResponseGenerateCUFD(DataTransferObject):
    cufd: str
    control_code: str
    start_datetime: datetime
    end_datetime: datetime
    address: str
    raw_response: Any


@siat_soap_sdk.app_service(CommandGenerateCUFD)
class GenerateCUFD(Feature):

    def execute(self, dto: CommandGenerateCUFD) -> ResponseGenerateCUFD:
        response = self.soap_client(SIAT_WSDL.OBTENCION_CODIGO).service.cufd(
            SolicitudCufd={
                "codigoAmbiente": dto.environment,
                "codigoModalidad": dto.billing_type,
                "codigoSistema": dto.system_code,
                "codigoSucursal": dto.branch_office,
                "codigoPuntoVenta": dto.point_of_sale,
                "cuis": dto.cuis,
                "nit": dto.nit,
            }
        )

        if response["codigo"] is None or response["codigoControl"] is None:
            raise core_exceptions.SIATException(
                f"Error: the cufd was not able to be generated:\n{response}"
            )

        end_datetime = fn_datetime.from_bolivia_tz_to_naive_utc(response["fechaVigencia"])
        start_datime = end_datetime - timedelta(hours=24)

        return ResponseGenerateCUFD(
            raw_response=response,
            cufd=response["codigo"],
            start_datetime=start_datime,
            end_datetime=end_datetime,
            address=response["direccion"],
            control_code=response["codigoControl"],
        )
