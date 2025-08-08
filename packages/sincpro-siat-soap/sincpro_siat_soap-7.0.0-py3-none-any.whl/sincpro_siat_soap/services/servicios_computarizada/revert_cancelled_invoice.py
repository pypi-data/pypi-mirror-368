from typing import Literal

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.domain import SIATEnvironment, SIATModality
from sincpro_siat_soap.global_definitions import SIAT_WSDL


class CommandRevertCancelledInvoiceComputarizada(DataTransferObject):
    sector_document: int
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


type_verified_status = Literal[
    "RECHAZADA", "OBSERVADA", "VALIDA", "ANULADA", "REVERSION DE ANULACION CONFIRMADA"
]


class ResponseRevertCancelledInvoiceComputarizada(DataTransferObject):
    reception_code: str | None
    literal_status: type_verified_status | str
    raw_response: dict


@siat_soap_sdk.feature(CommandRevertCancelledInvoiceComputarizada)
class RevertCancelledInvoiceComputarizada(Feature):

    def execute(
        self, dto: CommandRevertCancelledInvoiceComputarizada
    ) -> ResponseRevertCancelledInvoiceComputarizada:
        response = self.soap_client(
            SIAT_WSDL.SERVICIOS_COMPUTARIZADA
        ).service.reversionAnulacionFactura(
            SolicitudServicioReversionAnulacionFactura={
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
                "tipoFacturaDocumento": dto.invoice_type,
                "cuf": dto.cuf,
            }
        )

        return ResponseRevertCancelledInvoiceComputarizada(
            reception_code=response["codigoRecepcion"],
            literal_status=response["codigoDescripcion"],
            raw_response=response,
        )
