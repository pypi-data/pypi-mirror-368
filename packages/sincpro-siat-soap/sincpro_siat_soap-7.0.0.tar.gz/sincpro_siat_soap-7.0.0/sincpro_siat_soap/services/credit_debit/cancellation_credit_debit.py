from typing import Any

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.adapters.siat_exception_builder import siat_exception_builder
from sincpro_siat_soap.domain import SIATEnvironment, SIATModality
from sincpro_siat_soap.global_definitions import SIAT_WSDL


class CommandCancellationCreditDebit(DataTransferObject):
    nit: int | str
    cuis: str
    cufd: str
    cuf: str
    sector_document: int  # codigoDocumentoSector
    emission_code: int  # codigoEmision
    branch_office: int  # codigoSucursal
    system_code: str  # codigoSistema
    point_of_sale: int  # codigoPuntoVenta
    cancellation_reason: int
    type_invoice: int
    environment: SIATEnvironment
    modality: SIATModality


class ResponseCancellationCreditDebit(DataTransferObject):
    transaction: bool
    raw_response: Any


@siat_soap_sdk.feature(CommandCancellationCreditDebit)
class CancellationCreditDebit(Feature):

    def execute(self, dto: CommandCancellationCreditDebit) -> ResponseCancellationCreditDebit:
        response = self.soap_client(
            SIAT_WSDL.NOTA_DE_CREDITO
        ).service.anulacionDocumentoAjuste(
            SolicitudServicioAnulacionDocumentoAjuste={
                "codigoAmbiente": dto.environment,
                "codigoDocumentoSector": dto.sector_document,
                "codigoEmision": dto.emission_code,
                "codigoModalidad": dto.modality,
                "codigoPuntoVenta": dto.point_of_sale,
                "codigoSistema": dto.system_code,
                "codigoSucursal": dto.branch_office,
                "cufd": dto.cufd,
                "cuis": dto.cuis,
                "nit": dto.nit,
                "tipoFacturaDocumento": dto.type_invoice,
                "codigoMotivo": dto.cancellation_reason,
                "cuf": dto.cuf,
            }
        )

        if response["transaccion"] is False:
            fn = siat_exception_builder(response)
            fn()

        return ResponseCancellationCreditDebit(
            transaction=response["transaccion"], raw_response=response
        )
