from datetime import datetime
from typing import Any

from pydantic import Field

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.adapters.siat_exception_builder import siat_exception_builder
from sincpro_siat_soap.domain import SectorDocumentState, SIATEnvironment, SIATModality
from sincpro_siat_soap.global_definitions import SIAT_WSDL
from sincpro_siat_soap.shared.fn_datetime import datetime_for_send_invoice


class CommandMassiveInvoiceReceptionComputarizada(DataTransferObject):
    nit: int | str
    cuis: str
    cufd: str
    sector_document: int  # codigoDocumentoSector
    emission_code: int  # codigoEmision
    sent_date: str | datetime  # fechaEnvio
    hash_invoice_file: str  # hashArchivoXML No del comprimido
    branch_office: int  # codigoSucursal
    system_code: str  # codigoSistema
    point_of_sell: int  # codigoPuntoVenta
    xml: bytes = Field(repr=False)  # archivo
    type_invoice: int
    count_invoice: int
    environment: SIATEnvironment
    modality: SIATModality


class ResponseMassiveInvoiceReceptionComputarizada(DataTransferObject):
    literal_status: SectorDocumentState | str
    reception_code: str
    raw_response: Any


@siat_soap_sdk.feature(CommandMassiveInvoiceReceptionComputarizada)
class MassiveReceptionComputarizada(Feature):

    def execute(
        self, dto: CommandMassiveInvoiceReceptionComputarizada
    ) -> ResponseMassiveInvoiceReceptionComputarizada:
        response = self.soap_client(
            SIAT_WSDL.SERVICIOS_COMPUTARIZADA
        ).service.recepcionMasivaFactura(
            SolicitudServicioRecepcionMasiva={
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
                "fechaEnvio": datetime_for_send_invoice(dto.sent_date),
                "hashArchivo": dto.hash_invoice_file,
                "cantidadFacturas": dto.count_invoice,
            }
        )

        if response["transaccion"] is False:
            fn = siat_exception_builder(response)
            fn()

        return ResponseMassiveInvoiceReceptionComputarizada(
            literal_status=response["codigoDescripcion"],
            reception_code=response["codigoRecepcion"],
            raw_response=response,
        )
