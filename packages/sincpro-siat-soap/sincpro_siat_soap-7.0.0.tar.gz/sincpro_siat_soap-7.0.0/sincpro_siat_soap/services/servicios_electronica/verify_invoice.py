from typing import Any

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.domain import SectorDocumentState, SIATEnvironment, SIATModality
from sincpro_siat_soap.global_definitions import SIAT_WSDL


class CommandVerifyInvoiceStateElectronica(DataTransferObject):
    document_type: int
    emission_code: int
    point_of_sale: int
    system_code: str
    branch_office: int
    cufd: str
    cuis: str
    nit: int | str
    invoice_type: int
    cuf: str
    modality: SIATModality
    environment: SIATEnvironment


class ResponseVerifyInvoiceStateElectronica(DataTransferObject):
    reception_code: str | None
    literal_status: SectorDocumentState | str
    raw_response: Any


@siat_soap_sdk.feature(CommandVerifyInvoiceStateElectronica)
class VerifyInvoiceStateSiat(Feature):

    def execute(
        self, dto: CommandVerifyInvoiceStateElectronica
    ) -> ResponseVerifyInvoiceStateElectronica:
        response = self.soap_client(
            SIAT_WSDL.SERVICIOS_ELECTRONICA
        ).service.verificacionEstadoFactura(
            SolicitudServicioVerificacionEstadoFactura={
                "codigoAmbiente": dto.environment,
                "codigoDocumentoSector": dto.document_type,
                "codigoEmision": dto.emission_code,
                "codigoModalidad": dto.modality,
                "codigoPuntoVenta": dto.point_of_sale,
                "codigoSistema": dto.system_code,
                "codigoSucursal": dto.branch_office,
                "cufd": dto.cufd,
                "cuis": dto.cuis,
                "nit": dto.nit,
                "tipoFacturaDocumento": dto.invoice_type,
                "cuf": dto.cuf,
            }
        )

        return ResponseVerifyInvoiceStateElectronica(
            reception_code=response["codigoRecepcion"],
            literal_status=response["codigoDescripcion"],
            raw_response=response,
        )
