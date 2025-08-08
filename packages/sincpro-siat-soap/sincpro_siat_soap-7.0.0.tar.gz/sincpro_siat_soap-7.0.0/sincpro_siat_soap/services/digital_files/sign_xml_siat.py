"""Sign XML"""

from pydantic import Field

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.infrastructure.fn_xml import sign_xml_root, xml_to_canonical_c14n


class CommandSignXML(DataTransferObject):
    xml: str
    key: str = Field(repr=False)
    cert: str = Field(repr=False)
    password_key: str | None = None


class ResponseSignXML(DataTransferObject):
    xml: str


@siat_soap_sdk.feature(CommandSignXML)
class SignXMLSiat(Feature):
    def execute(self, dto: CommandSignXML) -> ResponseSignXML:
        signed_xml = sign_xml_root(dto.xml, dto.key, dto.cert, dto.password_key)
        # validate_signed_xml(param_object.cert, signed_xml)
        string_xml = xml_to_canonical_c14n(signed_xml)
        return ResponseSignXML(xml=string_xml.decode("utf-8"))
