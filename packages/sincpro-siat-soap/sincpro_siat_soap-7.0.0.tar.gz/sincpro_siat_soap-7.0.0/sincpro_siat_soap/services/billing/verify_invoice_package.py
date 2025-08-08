from typing import Any

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.adapters.siat_exception_builder import siat_exception_builder
from sincpro_siat_soap.domain import SectorDocumentState, SIATEnvironment, SIATModality
from sincpro_siat_soap.global_definitions import SIAT_WSDL


class CommandVerifyInvoicePackage(DataTransferObject):
    document_type: int
    emission_code: int
    point_of_sale: int
    system_code: str
    branch_office: int
    cufd: str
    cuis: str
    nit: int | str
    invoice_type: int
    reception_code: str
    modality: SIATModality
    environment: SIATEnvironment


class ResponseVerifyInvoicePackage(DataTransferObject):
    literal_status: SectorDocumentState | str
    reception_code: str
    raw_response: Any


@siat_soap_sdk.feature(CommandVerifyInvoicePackage)
class VerifyInvoicePackageSiat(Feature):

    def execute(self, dto: CommandVerifyInvoicePackage) -> ResponseVerifyInvoicePackage:
        response = self.soap_client(
            SIAT_WSDL.FACTURA_COMPRA_VENTA
        ).service.validacionRecepcionPaqueteFactura(
            SolicitudServicioValidacionRecepcionPaquete={
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
                "codigoRecepcion": dto.reception_code,
            }
        )

        if response["transaccion"] is False or response["codigoDescripcion"] == "OBSERVADA":
            fn = siat_exception_builder(response)
            fn()

        return ResponseVerifyInvoicePackage(
            literal_status=response["codigoDescripcion"],
            reception_code=response["codigoRecepcion"],
            raw_response=response,
        )
