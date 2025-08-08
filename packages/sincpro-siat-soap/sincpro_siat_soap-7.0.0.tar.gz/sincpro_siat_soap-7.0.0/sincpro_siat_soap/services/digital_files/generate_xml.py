"""Generate Any XML file based on dict."""

import base64
from typing import Any

from pydantic import Field

from sincpro_siat_soap import ApplicationService, DataTransferObject, siat_soap_sdk
from sincpro_siat_soap.domain import SIATModality
from sincpro_siat_soap.domain.siat_template import SIAT_XML_Template
from sincpro_siat_soap.global_definitions import (
    SIATApprovedDocumentId,
    get_root_name_by_document_id,
)
from sincpro_siat_soap.infrastructure.encryption import get_hash_base64
from sincpro_siat_soap.services.digital_files.compress_file import (
    CommandCompressFile,
    ResponseCompressFile,
)
from sincpro_siat_soap.services.digital_files.sign_xml_siat import (
    CommandSignXML,
    ResponseSignXML,
)


class CmdGenerateXML(DataTransferObject):
    modality: SIATModality
    sector_document: SIATApprovedDocumentId
    header: dict
    details: list
    private_key: str | None = Field(repr=False, default=None)
    cert: str | None = Field(repr=False, default=None)
    password_key: str | None = Field(repr=False, default=None)


class ResGenerateXML(DataTransferObject):
    xml: str = Field(repr=False)
    xml_base_64: bytes = Field(repr=False)
    compressed_xml: bytes = Field(repr=False)
    compressed_xml_base_64: bytes = Field(repr=False)
    hash_file: str
    python_root_obj: Any


@siat_soap_sdk.app_service(CmdGenerateXML)
class GenerateXML(ApplicationService):

    def execute(self, dto: CmdGenerateXML) -> ResGenerateXML:
        """Generate XML file for SIAT.
        - Generate XML file
        - Sign XML file (Only for ELECTRONICA modality)
        - Create compressed file
        - Create hash of file
        """
        node_name = get_root_name_by_document_id(dto.sector_document, dto.modality)
        template = SIAT_XML_Template(node_name)
        template.add_header(dto.header)
        template.add_details(dto.details)

        # Create XML file
        template.build_xml_obj()
        xml = template.generate_string_xml()

        # Sign XML file
        if dto.modality == SIATModality.ELECTRONICA:
            cmd_sign = CommandSignXML(
                xml=xml, key=dto.private_key, cert=dto.cert, password_key=dto.password_key
            )
            signed_xml = self.feature_bus.execute(cmd_sign, ResponseSignXML)
            xml = signed_xml.xml

        # Compress XML file
        cmd_compress_file = CommandCompressFile(string_file=xml)
        compressed_file = self.feature_bus.execute(cmd_compress_file, ResponseCompressFile)

        # Create hash of file
        hash_file = get_hash_base64(compressed_file.zip_file)
        return ResGenerateXML(
            xml=xml,
            xml_base_64=base64.b64encode(xml.encode("utf-8")),
            compressed_xml=compressed_file.zip_file,
            compressed_xml_base_64=base64.b64encode(compressed_file.zip_file),
            hash_file=hash_file,
            python_root_obj=template.python_root_obj(),
        )
