"""Verify a any document """

import uuid
from typing import Any, Literal

from sincpro_siat_soap import ApplicationService, DataTransferObject, siat_soap_sdk
from sincpro_siat_soap.domain import (
    SectorDocumentState,
    SIATEmissionType,
    SIATEnvironment,
    SIATInvoiceType,
    SIATModality,
)
from sincpro_siat_soap.global_definitions import SIATApprovedDocumentId
from sincpro_siat_soap.services.billing.verify_invoice_package import (
    CommandVerifyInvoicePackage,
)
from sincpro_siat_soap.services.billing.verify_invoice_state import CommandVerifyInvoiceState
from sincpro_siat_soap.services.billing.verify_masive_invoice import (
    CommandVerifyMassiveInvoice,
)
from sincpro_siat_soap.services.credit_debit.verify_credit_debit import (
    CmdVerifyCreditDebitState,
)
from sincpro_siat_soap.services.servicios_computarizada.verify_invoice import (
    CommandVerifyInvoiceStateComputarizada,
)
from sincpro_siat_soap.services.servicios_computarizada.verify_invoice_package import (
    CommandVerifyInvoicePackageComputarizada,
)
from sincpro_siat_soap.services.servicios_computarizada.verify_massive_invoice import (
    CommandVerifyMassiveInvoiceComputarizada,
)
from sincpro_siat_soap.services.servicios_electronica.verify_invoice import (
    CommandVerifyInvoiceStateElectronica,
)
from sincpro_siat_soap.services.servicios_electronica.verify_invoice_package import (
    CommandVerifyInvoicePackageElectronica,
)
from sincpro_siat_soap.services.servicios_electronica.verify_massive_invoice import (
    CommandVerifyMassiveInvoiceElectronic,
)


class CmdVerifyDocument(DataTransferObject):
    document_type: SIATApprovedDocumentId | int
    emission_code: SIATEmissionType | int
    point_of_sale: int
    system_code: str
    branch_office: int
    cufd: str
    cuis: str
    nit: int | str
    invoice_type: SIATInvoiceType | int
    cuf_or_reception_code: str
    modality: SIATModality
    environment: SIATEnvironment


type_verified_status = Literal["RECHAZADA", "OBSERVADA", "VALIDA", "ANULADA"]


class ResVerifyDocument(DataTransferObject):
    reception_code: str
    literal_status: SectorDocumentState | str
    raw_response: Any


@siat_soap_sdk.app_service(CmdVerifyDocument)
class VerifyDocument(ApplicationService):
    """Verify a any document
    - Single invoice
    - Package of invoices
    """

    def execute(self, dto: CmdVerifyDocument) -> ResVerifyDocument:
        is_package_invoice = self.is_valid_reception_code(dto.cuf_or_reception_code)
        match is_package_invoice:
            case True:
                cmd = self.get_cmd_verify_package_or_massive_invoice(dto)
                return self.feature_bus.execute(cmd, ResVerifyDocument)
            case False:
                cmd = self.get_cmd_verify_invoice(dto)
                return self.feature_bus.execute(cmd, ResVerifyDocument)

    def is_valid_reception_code(self, reception_code: str) -> bool:
        """The reception code must be a valid UUID
        The CUF is not UUID example: "1C337484B185F6AD6D2DCB0B5B1E3DA60CE0C391C465067B00DF51F74"
        """
        try:
            uuid.UUID(reception_code)
            return True
        except ValueError:
            return False

    def get_cmd_verify_invoice(
        self, dto: CmdVerifyDocument
    ) -> (
        CommandVerifyInvoiceState
        | CommandVerifyInvoiceStateElectronica
        | CommandVerifyInvoiceStateComputarizada
        | CmdVerifyCreditDebitState
    ):
        if dto.document_type == SIATApprovedDocumentId.COMPRA_VENTA:
            return CommandVerifyInvoiceState(
                document_type=dto.document_type,
                emission_code=dto.emission_code,
                point_of_sale=dto.point_of_sale,
                system_code=dto.system_code,
                branch_office=dto.branch_office,
                cufd=dto.cufd,
                cuis=dto.cuis,
                nit=dto.nit,
                invoice_type=dto.invoice_type,
                cuf=dto.cuf_or_reception_code,
                modality=dto.modality,
                environment=dto.environment,
            )

        if dto.document_type == SIATApprovedDocumentId.NOTA_DE_CREDITO_DEBITO:
            return CmdVerifyCreditDebitState(
                document_type=dto.document_type,
                emission_code=dto.emission_code,
                point_of_sale=dto.point_of_sale,
                system_code=dto.system_code,
                branch_office=dto.branch_office,
                cufd=dto.cufd,
                cuis=dto.cuis,
                nit=dto.nit,
                invoice_type=dto.invoice_type,
                cuf=dto.cuf_or_reception_code,
                modality=dto.modality,
                environment=dto.environment,
            )

        if dto.modality == SIATModality.ELECTRONICA:
            return CommandVerifyInvoiceStateElectronica(
                document_type=dto.document_type,
                emission_code=dto.emission_code,
                point_of_sale=dto.point_of_sale,
                system_code=dto.system_code,
                branch_office=dto.branch_office,
                cufd=dto.cufd,
                cuis=dto.cuis,
                nit=dto.nit,
                invoice_type=dto.invoice_type,
                cuf=dto.cuf_or_reception_code,
                modality=dto.modality,
                environment=dto.environment,
            )

        return CommandVerifyInvoiceStateComputarizada(
            document_type=dto.document_type,
            emission_code=dto.emission_code,
            point_of_sale=dto.point_of_sale,
            system_code=dto.system_code,
            branch_office=dto.branch_office,
            cufd=dto.cufd,
            cuis=dto.cuis,
            nit=dto.nit,
            invoice_type=dto.invoice_type,
            cuf=dto.cuf_or_reception_code,
            modality=dto.modality,
            environment=dto.environment,
        )

    def get_cmd_verify_package_or_massive_invoice(
        self, dto: CmdVerifyDocument
    ) -> (
        CommandVerifyMassiveInvoice
        | CommandVerifyMassiveInvoiceElectronic
        | CommandVerifyMassiveInvoiceComputarizada
        | CommandVerifyInvoicePackage
        | CommandVerifyInvoicePackageElectronica
        | CommandVerifyInvoicePackageComputarizada
    ):
        match dto.emission_code:
            case SIATEmissionType.MASSIVE:
                if dto.document_type == SIATApprovedDocumentId.COMPRA_VENTA:
                    return CommandVerifyMassiveInvoice(
                        document_type=dto.document_type,
                        emission_code=dto.emission_code,
                        point_of_sale=dto.point_of_sale,
                        system_code=dto.system_code,
                        branch_office=dto.branch_office,
                        cufd=dto.cufd,
                        cuis=dto.cuis,
                        nit=dto.nit,
                        invoice_type=dto.invoice_type,
                        reception_code=dto.cuf_or_reception_code,
                        modality=dto.modality,
                        environment=dto.environment,
                    )

                if dto.modality == SIATModality.ELECTRONICA:
                    return CommandVerifyMassiveInvoiceElectronic(
                        document_type=dto.document_type,
                        emission_code=dto.emission_code,
                        point_of_sale=dto.point_of_sale,
                        system_code=dto.system_code,
                        branch_office=dto.branch_office,
                        cufd=dto.cufd,
                        cuis=dto.cuis,
                        nit=dto.nit,
                        invoice_type=dto.invoice_type,
                        reception_code=dto.cuf_or_reception_code,
                        modality=dto.modality,
                        environment=dto.environment,
                    )

                return CommandVerifyMassiveInvoiceComputarizada(
                    document_type=dto.document_type,
                    emission_code=dto.emission_code,
                    point_of_sale=dto.point_of_sale,
                    system_code=dto.system_code,
                    branch_office=dto.branch_office,
                    cufd=dto.cufd,
                    cuis=dto.cuis,
                    nit=dto.nit,
                    invoice_type=dto.invoice_type,
                    reception_code=dto.cuf_or_reception_code,
                    modality=dto.modality,
                    environment=dto.environment,
                )
            #: Package case
            case _:
                if dto.document_type == SIATApprovedDocumentId.COMPRA_VENTA:
                    return CommandVerifyInvoicePackage(
                        document_type=dto.document_type,
                        emission_code=dto.emission_code,
                        point_of_sale=dto.point_of_sale,
                        system_code=dto.system_code,
                        branch_office=dto.branch_office,
                        cufd=dto.cufd,
                        cuis=dto.cuis,
                        nit=dto.nit,
                        invoice_type=dto.invoice_type,
                        reception_code=dto.cuf_or_reception_code,
                        modality=dto.modality,
                        environment=dto.environment,
                    )
                if dto.modality == SIATModality.ELECTRONICA:
                    return CommandVerifyInvoicePackageElectronica(
                        document_type=dto.document_type,
                        emission_code=dto.emission_code,
                        point_of_sale=dto.point_of_sale,
                        system_code=dto.system_code,
                        branch_office=dto.branch_office,
                        cufd=dto.cufd,
                        cuis=dto.cuis,
                        nit=dto.nit,
                        invoice_type=dto.invoice_type,
                        reception_code=dto.cuf_or_reception_code,
                        modality=dto.modality,
                        environment=dto.environment,
                    )
                return CommandVerifyInvoicePackageComputarizada(
                    document_type=dto.document_type,
                    emission_code=dto.emission_code,
                    point_of_sale=dto.point_of_sale,
                    system_code=dto.system_code,
                    branch_office=dto.branch_office,
                    cufd=dto.cufd,
                    cuis=dto.cuis,
                    nit=dto.nit,
                    invoice_type=dto.invoice_type,
                    reception_code=dto.cuf_or_reception_code,
                    modality=dto.modality,
                    environment=dto.environment,
                )
