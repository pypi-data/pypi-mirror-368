from typing import Any

from pydantic import Field

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.adapters.siat_exception_builder import siat_exception_builder
from sincpro_siat_soap.domain import SIATEnvironment, SIATModality
from sincpro_siat_soap.domain.sector_document import SectorDocumentState
from sincpro_siat_soap.global_definitions import SIAT_WSDL


class CommandInvoiceReceptionRequest(DataTransferObject):
    nit: int | str
    cuis: str
    cufd: str
    sector_document: int  # codigoDocumentoSector
    emission_code: int  # codigoEmision
    sent_date: str  # fechaEnvio
    hash_invoice_file: str  # hashArchivoXML No del comprimido
    branch_office: int  # codigoSucursal
    system_code: str  # codigoSistema
    point_of_sell: int  # codigoPuntoVenta
    xml: bytes = Field(repr=False)  # archivo
    type_invoice: int
    environment: SIATEnvironment  # codigoAmbiente
    modality: SIATModality  # codigo Modalidad


class ResponseInvoiceReception(DataTransferObject):
    literal_status: SectorDocumentState
    reception_code: str
    raw_response: Any


@siat_soap_sdk.feature(CommandInvoiceReceptionRequest)
class InvoiceReceptionRequest(Feature):

    def execute(self, dto: CommandInvoiceReceptionRequest) -> ResponseInvoiceReception:
        response = self.soap_client(SIAT_WSDL.FACTURA_COMPRA_VENTA).service.recepcionFactura(
            SolicitudServicioRecepcionFactura={
                "codigoAmbiente": dto.environment,
                "codigoDocumentoSector": dto.sector_document,
                "codigoEmision": dto.emission_code,
                "codigoModalidad": dto.modality,
                "codigoPuntoVenta": dto.point_of_sell,
                "codigoSistema": dto.system_code,
                "codigoSucursal": dto.branch_office,
                "cufd": dto.cufd,
                "cuis": dto.cuis,
                "nit": dto.nit,
                "tipoFacturaDocumento": dto.type_invoice,
                "archivo": dto.xml,
                "fechaEnvio": dto.sent_date,
                "hashArchivo": dto.hash_invoice_file,
            }
        )

        if response["transaccion"] is False:
            fn = siat_exception_builder(response)
            fn()

        return ResponseInvoiceReception(
            literal_status=response["codigoDescripcion"],
            reception_code=response["codigoRecepcion"],
            raw_response=response,
        )
