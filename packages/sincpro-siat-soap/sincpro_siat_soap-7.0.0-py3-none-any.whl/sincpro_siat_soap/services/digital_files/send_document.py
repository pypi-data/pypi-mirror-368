"""Send Any document"""

from datetime import datetime
from typing import Any

from pydantic import Field

from sincpro_siat_soap import ApplicationService, DataTransferObject, siat_soap_sdk
from sincpro_siat_soap.domain import (
    SIATEmissionType,
    SIATEnvironment,
    SIATInvoiceType,
    SIATModality,
)
from sincpro_siat_soap.domain.sector_document import SectorDocumentState
from sincpro_siat_soap.global_definitions import SIATApprovedDocumentId
from sincpro_siat_soap.services.billing.invoice_reception_request import (
    CommandInvoiceReceptionRequest,
)
from sincpro_siat_soap.services.credit_debit import CommandReceptionCreditDebitNote
from sincpro_siat_soap.services.servicios_computarizada.invoice_reception_computarizada import (
    CommandInvoiceReceptionComputarizada,
)
from sincpro_siat_soap.services.servicios_electronica.invoice_reception_electronica import (
    CommandInvoiceReceptionElectronica,
)
from sincpro_siat_soap.shared.fn_datetime import datetime_for_send_invoice


class CmdSendDocumentToSiat(DataTransferObject):
    """Command to trigger the use case"""

    nit: int | str
    cuis: str
    cufd: str
    sector_document: SIATApprovedDocumentId | int
    emission_code: SIATEmissionType | int
    sent_date: str | datetime
    hash_invoice_file: str
    xml: bytes = Field(repr=False)
    branch_office: int
    system_code: str
    point_of_sale: int
    type_invoice: SIATInvoiceType | int
    environment: SIATEnvironment
    modality: SIATModality


class ResSendDocumentToSiat(DataTransferObject):
    """Response from the use case"""

    literal_status: SectorDocumentState
    reception_code: str
    raw_response: Any


@siat_soap_sdk.app_service(CmdSendDocumentToSiat)
class SendDocumentToSiat(ApplicationService):

    def execute(self, dto: CmdSendDocumentToSiat) -> ResSendDocumentToSiat:
        cmd_send_document = self.get_command_to_sent(dto)
        return self.feature_bus.execute(cmd_send_document, ResSendDocumentToSiat)

    def get_command_to_sent(
        self, dto: CmdSendDocumentToSiat
    ) -> (
        CommandInvoiceReceptionComputarizada
        | CommandReceptionCreditDebitNote
        | CommandInvoiceReceptionRequest
        | CommandInvoiceReceptionElectronica
    ):
        if dto.sector_document == SIATApprovedDocumentId.COMPRA_VENTA:
            return CommandInvoiceReceptionRequest(
                nit=dto.nit,
                cuis=dto.cuis,
                cufd=dto.cufd,
                sector_document=dto.sector_document,
                emission_code=dto.emission_code,
                sent_date=datetime_for_send_invoice(dto.sent_date),
                hash_invoice_file=dto.hash_invoice_file,
                branch_office=dto.branch_office,
                system_code=dto.system_code,
                point_of_sell=dto.point_of_sale,
                xml=dto.xml,
                type_invoice=dto.type_invoice,
                environment=dto.environment,
                modality=dto.modality,
            )

        if dto.sector_document == SIATApprovedDocumentId.NOTA_DE_CREDITO_DEBITO:
            return CommandReceptionCreditDebitNote(
                nit=dto.nit,
                cuis=dto.cuis,
                cufd=dto.cufd,
                sector_document=dto.sector_document,
                emission_code=dto.emission_code,
                sent_date=datetime_for_send_invoice(dto.sent_date),
                hash_invoice_file=dto.hash_invoice_file,
                branch_office=dto.branch_office,
                system_code=dto.system_code,
                point_of_sell=dto.point_of_sale,
                xml=dto.xml,
                type_invoice=dto.type_invoice,
                environment=dto.environment,
                modality=dto.modality,
            )

        if dto.modality == SIATModality.COMPUTARIZADA:
            return CommandInvoiceReceptionComputarizada(
                nit=dto.nit,
                cuis=dto.cuis,
                cufd=dto.cufd,
                sector_document=dto.sector_document,
                emission_code=dto.emission_code,
                sent_date=datetime_for_send_invoice(dto.sent_date),
                hash_invoice_file=dto.hash_invoice_file,
                branch_office=dto.branch_office,
                system_code=dto.system_code,
                point_of_sell=dto.point_of_sale,
                xml=dto.xml,
                type_invoice=dto.type_invoice,
                environment=dto.environment,
                modality=dto.modality,
            )

        return CommandInvoiceReceptionElectronica(
            nit=dto.nit,
            cuis=dto.cuis,
            cufd=dto.cufd,
            sector_document=dto.sector_document,
            emission_code=dto.emission_code,
            sent_date=datetime_for_send_invoice(dto.sent_date),
            hash_invoice_file=dto.hash_invoice_file,
            branch_office=dto.branch_office,
            system_code=dto.system_code,
            point_of_sell=dto.point_of_sale,
            xml=dto.xml,
            type_invoice=dto.type_invoice,
            environment=dto.environment,
            modality=dto.modality,
        )
