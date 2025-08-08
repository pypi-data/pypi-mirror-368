"""Cancel Any SIAT Document"""

from typing import Any

from sincpro_siat_soap import ApplicationService, DataTransferObject, siat_soap_sdk
from sincpro_siat_soap.domain import SIATEmissionType, SIATEnvironment, SIATModality
from sincpro_siat_soap.global_definitions import SIATApprovedDocumentId
from sincpro_siat_soap.services.billing.invoice_cancellation import (
    CommandInvoiceCancellationRequest,
)
from sincpro_siat_soap.services.credit_debit.cancellation_credit_debit import (
    CommandCancellationCreditDebit,
)
from sincpro_siat_soap.services.servicios_computarizada.cancel_invoice import (
    CommandInvoiceCancelComputarizada,
)
from sincpro_siat_soap.services.servicios_electronica.cancel_invoice import (
    CommandInvoiceCancelElectronica,
)
from sincpro_siat_soap.shared.core_exceptions import UseCaseError


class CmdCancelDocument(DataTransferObject):
    """Command to cancel a document"""

    modality: SIATModality | int
    environment: SIATEnvironment | int
    cancellation_reason: int
    sector_document: SIATApprovedDocumentId | int
    emission_code: SIATEmissionType | int
    type_invoice: int
    system_code: str
    nit: int | str
    cuis: str
    cufd: str
    cuf: str
    branch_office: int
    point_of_sale: int


class ResCancelDocument(DataTransferObject):
    """Response from canceling a document"""

    transaction: bool
    raw_response: Any


@siat_soap_sdk.app_service(CmdCancelDocument)
class CancelDocument(ApplicationService):
    """Cancel any SIAT document"""

    def execute(self, dto: CmdCancelDocument) -> ResCancelDocument:
        """Execute the cancel document use case"""
        command = self.get_command(dto)

        if not command:
            raise UseCaseError("There no command to cancel the document")

        return self.feature_bus.execute(command, ResCancelDocument)

    def get_command(
        self, dto: CmdCancelDocument
    ) -> (
        CommandInvoiceCancellationRequest
        | CommandCancellationCreditDebit
        | CommandInvoiceCancelComputarizada
        | CommandInvoiceCancelElectronica
    ):
        if dto.sector_document == SIATApprovedDocumentId.COMPRA_VENTA:
            return CommandInvoiceCancellationRequest(
                nit=dto.nit,
                cuis=dto.cuis,
                cufd=dto.cufd,
                cuf=dto.cuf,
                sector_document=dto.sector_document,
                emission_code=dto.emission_code,
                branch_office=dto.branch_office,
                system_code=dto.system_code,
                point_of_sell=dto.point_of_sale,
                cancellation_reason=dto.cancellation_reason,
                type_invoice=dto.type_invoice,
                modality=SIATModality(dto.modality),
                environment=SIATEnvironment(dto.environment),
            )

        if dto.sector_document == SIATApprovedDocumentId.NOTA_DE_CREDITO_DEBITO:
            return CommandCancellationCreditDebit(
                nit=dto.nit,
                cuis=dto.cuis,
                cufd=dto.cufd,
                cuf=dto.cuf,
                sector_document=dto.sector_document,
                emission_code=dto.emission_code,
                branch_office=dto.branch_office,
                system_code=dto.system_code,
                point_of_sale=dto.point_of_sale,
                cancellation_reason=dto.cancellation_reason,
                type_invoice=dto.type_invoice,
                environment=SIATEnvironment(dto.environment),
                modality=SIATModality(dto.modality),
            )

        if dto.modality == SIATModality.COMPUTARIZADA:
            CommandInvoiceCancelComputarizada(
                nit=dto.nit,
                cuis=dto.cuis,
                cufd=dto.cufd,
                cuf=dto.cuf,
                sector_document=dto.sector_document,
                emission_code=dto.emission_code,
                branch_office=dto.branch_office,
                system_code=dto.system_code,
                point_of_sell=dto.point_of_sale,
                cancellation_reason=dto.cancellation_reason,
                type_invoice=dto.type_invoice,
                modality=SIATModality(dto.modality),
                environment=SIATEnvironment(dto.environment),
            )

        return CommandInvoiceCancelElectronica(
            nit=dto.nit,
            cuis=dto.cuis,
            cufd=dto.cufd,
            cuf=dto.cuf,
            sector_document=dto.sector_document,
            emission_code=dto.emission_code,
            branch_office=dto.branch_office,
            system_code=dto.system_code,
            point_of_sell=dto.point_of_sale,
            cancellation_reason=dto.cancellation_reason,
            type_invoice=dto.type_invoice,
            modality=SIATModality(dto.modality),
            environment=SIATEnvironment(dto.environment),
        )
