"""Application service send packages Offline or massive invoices"""

import base64
from datetime import datetime, timedelta
from typing import Any

import xmltodict
from pydantic import Field

from sincpro_siat_soap import ApplicationService, DataTransferObject, siat_soap_sdk
from sincpro_siat_soap.domain import (
    SectorDocumentState,
    SIATEmissionType,
    SIATEnvironment,
    SIATInvoiceType,
    SIATModality,
    SIATSignificantEvent,
)
from sincpro_siat_soap.global_definitions import (
    MAP_DESCRIPTION_SIGNIFICANT_EVENT,
    SIATApprovedDocumentId,
)
from sincpro_siat_soap.infrastructure.encryption import get_hash_base64
from sincpro_siat_soap.services.auth_permissions.generate_cufd import (
    CommandGenerateCUFD,
    ResponseGenerateCUFD,
)
from sincpro_siat_soap.services.billing.masive_invoice_reception import (
    CommandMasiveInvoceReception,
    ResponseMasiveInvoiceReception,
)
from sincpro_siat_soap.services.billing.send_invoice_package import CommandSendInvoicePackage
from sincpro_siat_soap.services.digital_files.compress_file import (
    CommandCompressFile,
    ResponseCompressFile,
)
from sincpro_siat_soap.services.operations.get_signiticant_events import (
    CommandGetRegisteredSignificantEvents,
    ResponseGetRegisteredSignificantEvents,
    SignificantEventModel,
)
from sincpro_siat_soap.services.operations.regiter_significant_event import (
    CommandRegisterSignificantEvent,
    ResponseRegisterSignificantEvent,
)
from sincpro_siat_soap.services.servicios_computarizada.send_invoice_package import (
    CommandSendInvoicePackageComputarizada,
)
from sincpro_siat_soap.services.servicios_computarizada.send_massive_invoice import (
    CommandMassiveInvoiceReceptionComputarizada,
    ResponseMassiveInvoiceReceptionComputarizada,
)
from sincpro_siat_soap.services.servicios_electronica.send_invoice_package import (
    CommandSendInvoicePackageElectronica,
)
from sincpro_siat_soap.services.servicios_electronica.send_masive_invoice import (
    CommandMassiveInvoiceReceptionElectronica,
    ResponseMassiveInvoiceReceptionElectronica,
)
from sincpro_siat_soap.shared import fn_datetime


class CmdSendDocumentPackage(DataTransferObject):
    emission_code: SIATEmissionType | int
    modality: SIATModality
    nit: int | str
    cuis: str
    cufd: str
    sector_document: SIATApprovedDocumentId | int
    branch_office: int
    point_of_sale: int
    system_code: str
    xml_list: list[str | bytes] = Field(repr=False)
    invoice_type: SIATInvoiceType | int
    environment: SIATEnvironment
    cafc: str | None = None

    # The significant was registered previously use this field to send the significant event
    significant_event_res: ResponseRegisterSignificantEvent | None = None

    # If this is set register significant event
    with_significant_event_type: SIATSignificantEvent | None = None


class ResSendDocumentPackage(DataTransferObject):
    reception_code: str
    count_invoices: int
    compressed_file: bytes = Field(repr=False)
    compreseed_file_base64: bytes = Field(repr=False)
    raw_response: Any
    literal_status: SectorDocumentState | str
    new_cufd: ResponseGenerateCUFD | None = None


@siat_soap_sdk.app_service(CmdSendDocumentPackage)
class SendDocumentPackage(ApplicationService):

    def execute(self, dto: CmdSendDocumentPackage) -> ResSendDocumentPackage:
        """This Application service will send package Massive or Offline invoices
        - Massive invoices: requires only compress all files and send the right data
        - Offline invoices: requires to use a significant event
            - Use the previous significant event to send the invoices based on that event
            - Register significant event if the with_significant_event is set and significant_event_res is None
        """
        compressed_file, count_invoices, hash_file, start_datetime, end_datetime = (
            self.compress_invoices(dto.xml_list)
        )

        match dto.emission_code:
            case SIATEmissionType.OFFLINE:
                return self.send_package(
                    dto,
                    count_invoices,
                    compressed_file,
                    hash_file,
                    start_datetime,
                    end_datetime,
                )

            case SIATEmissionType.MASSIVE:
                res = self.send_massive_invoice(
                    dto,
                    count_invoices,
                    compressed_file,
                    hash_file,
                )
                return ResSendDocumentPackage(
                    literal_status=res.literal_status,
                    raw_response=res.raw_response,
                    reception_code=res.reception_code,
                    compreseed_file_base64=base64.b64encode(compressed_file),
                    compressed_file=compressed_file,
                    count_invoices=count_invoices,
                )

    def compress_invoices(
        self, list_xml: list[str | bytes]
    ) -> tuple[bytes, int, str, datetime, datetime]:
        """
        - If the xml is binary encode transform to xml string
        - Compress all xml files
        - Return the compressed file, Hash, length of invoices, number of files, and start and end datetime
        """
        string_list_xml = [
            xml.decode("utf-8") if isinstance(xml, bytes) else xml for xml in list_xml
        ]
        parsed_list = []
        for xml in string_list_xml:
            parsed = xmltodict.parse(xml)
            root_node = list(parsed.keys())[0]
            emission_date = parsed[root_node]["cabecera"]["fechaEmision"]
            parsed_list.append(
                {"xml": xml, "fechaEmision": datetime.fromisoformat(emission_date)}
            )

        sorted_list = sorted(parsed_list, key=lambda x: x["fechaEmision"])
        ordered_string_list = [item["xml"] for item in sorted_list]
        start_datetime = sorted_list[0]["fechaEmision"] - timedelta(seconds=1)
        end_datetime = sorted_list[-1]["fechaEmision"] + timedelta(seconds=1)
        compress_cmd = CommandCompressFile(string_file=ordered_string_list)
        res_compress = self.feature_bus.execute(compress_cmd, ResponseCompressFile)
        hash_file = get_hash_base64(res_compress.zip_file)
        return (
            res_compress.zip_file,
            len(list_xml),
            hash_file,
            start_datetime,
            end_datetime,
        )

    def register_significant_event(
        self,
        dto: CmdSendDocumentPackage,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> tuple[ResponseRegisterSignificantEvent, ResponseGenerateCUFD | None]:
        """Create or get existing significant event based on the start and end datetime"""

        cmd_get_significant_event = CommandGetRegisteredSignificantEvents(
            point_of_sale=dto.point_of_sale,
            system_code=dto.system_code,
            branch_office=dto.branch_office,
            event_date=fn_datetime.now_bolivia().date(),
            cufd=dto.cufd,
            cuis=dto.cuis,
            nit=dto.nit,
            enviroment=dto.environment,
        )
        res_get_significant_event = self.feature_bus.execute(
            cmd_get_significant_event, ResponseGetRegisteredSignificantEvents
        )

        # TODO: Define better way to decide if the significant event is already created
        existing_significant_event = list(
            filter(
                lambda se: se.start_datetime_event <= start_datetime
                and se.end_datetime_event >= end_datetime,
                res_get_significant_event.list_significant_events,
            )
        )

        if existing_significant_event:
            found_significant_event: SignificantEventModel = existing_significant_event[0]
            siat_soap_sdk.logger.info(
                f"Evento singificativo encontrado ({len(existing_significant_event)})",
                significant_event_type=found_significant_event.significant_event_code,
            )
            return (
                ResponseRegisterSignificantEvent(
                    raw_response=None,
                    event_type=found_significant_event.event_type,
                    code_significant_event=found_significant_event.significant_event_code,
                    start_datetime_event=found_significant_event.start_datetime_event,
                    end_datetime_event=found_significant_event.end_datetime_event,
                    cuis=dto.cuis,
                    cufd=dto.cufd,
                    nit=dto.nit,
                    system_code=dto.system_code,
                    point_of_sale=dto.point_of_sale,
                    branch_office=dto.branch_office,
                ),
                None,
            )

        # Create new significant event TODO: Add feature flag
        cmd_new_cufd = CommandGenerateCUFD(
            nit=dto.nit,
            system_code=dto.system_code,
            point_of_sale=dto.point_of_sale,
            branch_office=dto.branch_office,
            cuis=dto.cuis,
            billing_type=SIATModality.ELECTRONICA,
            environment=dto.environment,
        )
        # new_cufd = self.feature_bus.execute(cmd_new_cufd, ResponseGenerateCUFD)
        cmd = CommandRegisterSignificantEvent(
            event_type=dto.with_significant_event_type,
            description=MAP_DESCRIPTION_SIGNIFICANT_EVENT[dto.with_significant_event_type],
            point_of_sale=dto.point_of_sale,
            system_code=dto.system_code,
            branch_office=dto.branch_office,
            cufd=dto.cufd,
            cufd_event=dto.cufd,
            cuis=dto.cuis,
            nit=dto.nit,
            start_datetime_event=start_datetime,
            end_datetime_event=end_datetime,
            enviroment=dto.environment,
        )
        new_significant_event = self.feature_bus.execute(
            cmd, ResponseRegisterSignificantEvent
        )

        siat_soap_sdk.logger.info(
            "Evento significativo creado",
            significant_event_type=dto.with_significant_event_type,
            code_significant_event=new_significant_event.code_significant_event,
        )
        return new_significant_event, None

    def send_package(
        self,
        dto: CmdSendDocumentPackage,
        count_invoices: int,
        compressed_file: bytes,
        hash_file: str,
        start_datetime: datetime,
        end_datetime: datetime,
    ):
        _significant_event_record = dto.significant_event_res
        _current_cufd = dto.cufd

        if dto.significant_event_res is None and dto.with_significant_event_type is not None:
            registered_significant_event, new_cufd = self.register_significant_event(
                dto, start_datetime, end_datetime
            )

            if new_cufd:
                _current_cufd = new_cufd.cufd

            _significant_event_record = registered_significant_event

        if dto.sector_document == SIATApprovedDocumentId.COMPRA_VENTA:
            cmd = CommandSendInvoicePackage(
                emission_code=dto.emission_code,
                nit=dto.nit,
                cuis=dto.cuis,
                cufd=_current_cufd,
                sent_date=fn_datetime.now_bolivia(),
                sector_document=dto.sector_document,
                branch_office=dto.branch_office,
                point_of_sell=dto.point_of_sale,
                system_code=dto.system_code,
                xml=compressed_file,
                hash_invoice_file=hash_file,
                count_invoice=count_invoices,
                type_invoice=dto.invoice_type,
                cafc=dto.cafc,
                environment=dto.environment,
                modality=dto.modality,
                event_code=_significant_event_record.code_significant_event,
            )
            res = self.feature_bus.execute(cmd, ResSendDocumentPackage)
            return ResSendDocumentPackage(
                literal_status=res.literal_status,
                reception_code=res.reception_code,
                count_invoices=count_invoices,
                compressed_file=compressed_file,
                compreseed_file_base64=base64.b64encode(compressed_file),
                raw_response=res.raw_response,
            )

        if dto.modality == SIATModality.COMPUTARIZADA:
            cmd = CommandSendInvoicePackageComputarizada(
                emission_code=dto.emission_code,
                nit=dto.nit,
                cuis=dto.cuis,
                cufd=_current_cufd,
                sent_date=fn_datetime.now_bolivia(),
                sector_document=dto.sector_document,
                branch_office=dto.branch_office,
                point_of_sell=dto.point_of_sale,
                system_code=dto.system_code,
                xml=compressed_file,
                hash_invoice_file=hash_file,
                count_invoice=count_invoices,
                type_invoice=dto.invoice_type,
                cafc=dto.cafc,
                environment=dto.environment,
                modality=dto.modality,
                event_code=_significant_event_record.code_significant_event,
            )
            res = self.feature_bus.execute(cmd, ResSendDocumentPackage)
            return ResSendDocumentPackage(
                literal_status=res.literal_status,
                reception_code=res.reception_code,
                count_invoices=count_invoices,
                compressed_file=compressed_file,
                compreseed_file_base64=base64.b64encode(compressed_file),
                raw_response=res.raw_response,
            )

        cmd = CommandSendInvoicePackageElectronica(
            emission_code=dto.emission_code,
            nit=dto.nit,
            cuis=dto.cuis,
            cufd=_current_cufd,
            sent_date=fn_datetime.now_bolivia(),
            sector_document=dto.sector_document,
            branch_office=dto.branch_office,
            point_of_sell=dto.point_of_sale,
            system_code=dto.system_code,
            xml=compressed_file,
            hash_invoice_file=hash_file,
            count_invoice=count_invoices,
            type_invoice=dto.invoice_type,
            cafc=dto.cafc,
            environment=dto.environment,
            modality=dto.modality,
            event_code=_significant_event_record.code_significant_event,
        )
        res = self.feature_bus.execute(cmd, ResSendDocumentPackage)
        return ResSendDocumentPackage(
            literal_status=res.literal_status,
            reception_code=res.reception_code,
            count_invoices=count_invoices,
            compressed_file=compressed_file,
            compreseed_file_base64=base64.b64encode(compressed_file),
            raw_response=res.raw_response,
        )

    def send_massive_invoice(
        self,
        dto: CmdSendDocumentPackage,
        count_invoice: int,
        compressed_file: bytes,
        hash_file: str,
    ) -> ResSendDocumentPackage:
        """Massive invoice"""
        if dto.sector_document == SIATApprovedDocumentId.COMPRA_VENTA:
            cmd = CommandMasiveInvoceReception(
                emission_code=dto.emission_code,
                nit=dto.nit,
                cuis=dto.cuis,
                cufd=dto.cufd,
                sent_date=fn_datetime.now_bolivia(),
                sector_document=dto.sector_document,
                branch_office=dto.branch_office,
                point_of_sell=dto.point_of_sale,
                system_code=dto.system_code,
                xml=compressed_file,
                hash_invoice_file=hash_file,
                count_invoice=count_invoice,
                type_invoice=dto.invoice_type,
                environment=dto.environment,
                modality=dto.modality,
            )
            res = self.feature_bus.execute(cmd, ResponseMasiveInvoiceReception)
            return ResSendDocumentPackage(
                literal_status=res.literal_status,
                reception_code=res.reception_code,
                count_invoices=count_invoice,
                compressed_file=compressed_file,
                compreseed_file_base64=base64.b64encode(compressed_file),
                raw_response=res.raw_response,
            )

        if dto.modality == SIATModality.COMPUTARIZADA:
            cmd = CommandMassiveInvoiceReceptionComputarizada(
                emission_code=dto.emission_code,
                nit=dto.nit,
                cuis=dto.cuis,
                cufd=dto.cufd,
                sent_date=fn_datetime.now_bolivia(),
                sector_document=dto.sector_document,
                branch_office=dto.branch_office,
                point_of_sell=dto.point_of_sale,
                system_code=dto.system_code,
                xml=compressed_file,
                hash_invoice_file=hash_file,
                count_invoice=count_invoice,
                type_invoice=dto.invoice_type,
                environment=dto.environment,
                modality=dto.modality,
            )
            res = self.feature_bus.execute(cmd, ResponseMassiveInvoiceReceptionComputarizada)
            return ResSendDocumentPackage(
                literal_status=res.literal_status,
                reception_code=res.reception_code,
                count_invoices=count_invoice,
                compressed_file=compressed_file,
                compreseed_file_base64=base64.b64encode(compressed_file),
                raw_response=res.raw_response,
            )

        cmd = CommandMassiveInvoiceReceptionElectronica(
            emission_code=dto.emission_code,
            nit=dto.nit,
            cuis=dto.cuis,
            cufd=dto.cufd,
            sent_date=fn_datetime.now_bolivia(),
            sector_document=dto.sector_document,
            branch_office=dto.branch_office,
            point_of_sell=dto.point_of_sale,
            system_code=dto.system_code,
            xml=compressed_file,
            hash_invoice_file=hash_file,
            count_invoice=count_invoice,
            type_invoice=dto.invoice_type,
            environment=dto.environment,
            modality=dto.modality,
        )
        res = self.feature_bus.execute(cmd, ResponseMassiveInvoiceReceptionElectronica)
        return ResSendDocumentPackage(
            literal_status=res.literal_status,
            reception_code=res.reception_code,
            count_invoices=count_invoice,
            compressed_file=compressed_file,
            compreseed_file_base64=base64.b64encode(compressed_file),
            raw_response=res.raw_response,
        )
