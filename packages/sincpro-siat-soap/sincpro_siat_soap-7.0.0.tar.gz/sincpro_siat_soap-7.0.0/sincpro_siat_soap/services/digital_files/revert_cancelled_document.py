"""Rever cancelled document."""

from typing import Any, Literal

from sincpro_siat_soap import ApplicationService, DataTransferObject, siat_soap_sdk
from sincpro_siat_soap.domain import (
    SIATEmissionType,
    SIATEnvironment,
    SIATInvoiceType,
    SIATModality,
)
from sincpro_siat_soap.global_definitions import SIATApprovedDocumentId
from sincpro_siat_soap.services.billing.revert_cancelled_invoice import (
    CommandRevertCancelledInvoice,
)
from sincpro_siat_soap.services.credit_debit.revert_cancelled_credit_note import (
    CommandRevertCancelledCreditNote,
)
from sincpro_siat_soap.services.servicios_computarizada.revert_cancelled_invoice import (
    CommandRevertCancelledInvoiceComputarizada,
)
from sincpro_siat_soap.services.servicios_electronica.revert_cancelled_invoice import (
    CommandRevertCancelledInvoiceElectronica,
)


class CmdRevertCancelledDocument(DataTransferObject):
    sector_document: SIATApprovedDocumentId | int
    emission_code: SIATEmissionType | int
    point_of_sale: int
    system_code: str
    branch_office: int
    cufd: str
    cuis: str
    nit: int | str
    invoice_type: SIATInvoiceType | int
    cuf: str
    modality: SIATModality
    environment: SIATEnvironment


type_verified_status = Literal[
    "RECHAZADA", "OBSERVADA", "VALIDA", "ANULADA", "REVERSION DE ANULACION CONFIRMADA"
]


class ResRevertCancelledDocument(DataTransferObject):
    reception_code: str | None
    literal_status: type_verified_status | str
    raw_response: Any


@siat_soap_sdk.app_service(CmdRevertCancelledDocument)
class RevertCancelledDocument(ApplicationService):

    def execute(self, dto: CmdRevertCancelledDocument) -> ResRevertCancelledDocument:
        if dto.sector_document == SIATApprovedDocumentId.COMPRA_VENTA:
            command = CommandRevertCancelledInvoice(
                sector_document=dto.sector_document,
                emission_code=dto.emission_code,
                point_of_sale=dto.point_of_sale,
                system_code=dto.system_code,
                branch_office=dto.branch_office,
                cufd=dto.cufd,
                cuis=dto.cuis,
                nit=dto.nit,
                invoice_type=dto.invoice_type,
                cuf=dto.cuf,
                modality=dto.modality,
                environment=dto.environment,
            )
            return self.feature_bus.execute(command, ResRevertCancelledDocument)

        if dto.sector_document == SIATApprovedDocumentId.NOTA_DE_CREDITO_DEBITO:
            command = CommandRevertCancelledCreditNote(
                sector_document=dto.sector_document,
                emission_code=dto.emission_code,
                point_of_sale=dto.point_of_sale,
                system_code=dto.system_code,
                branch_office=dto.branch_office,
                cufd=dto.cufd,
                cuis=dto.cuis,
                nit=dto.nit,
                invoice_type=dto.invoice_type,
                cuf=dto.cuf,
                modality=dto.modality,
                environment=dto.environment,
            )
            return self.feature_bus.execute(command, ResRevertCancelledDocument)

        if dto.modality == SIATModality.ELECTRONICA:
            command = CommandRevertCancelledInvoiceElectronica(
                sector_document=dto.sector_document,
                emission_code=dto.emission_code,
                point_of_sale=dto.point_of_sale,
                system_code=dto.system_code,
                branch_office=dto.branch_office,
                cufd=dto.cufd,
                cuis=dto.cuis,
                nit=dto.nit,
                invoice_type=dto.invoice_type,
                cuf=dto.cuf,
                modality=dto.modality,
                environment=dto.environment,
            )
            return self.feature_bus.execute(command, ResRevertCancelledDocument)

        return siat_soap_sdk(
            CommandRevertCancelledInvoiceComputarizada(
                sector_document=dto.sector_document,
                emission_code=dto.emission_code,
                point_of_sale=dto.point_of_sale,
                system_code=dto.system_code,
                branch_office=dto.branch_office,
                cufd=dto.cufd,
                cuis=dto.cuis,
                nit=dto.nit,
                invoice_type=dto.invoice_type,
                cuf=dto.cuf,
                modality=dto.modality,
                environment=dto.environment,
            ),
            ResRevertCancelledDocument,
        )
