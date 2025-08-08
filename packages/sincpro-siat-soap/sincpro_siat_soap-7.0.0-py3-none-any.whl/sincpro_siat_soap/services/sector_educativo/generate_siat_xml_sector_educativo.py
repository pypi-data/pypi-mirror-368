from typing import Any, List, Literal, Union

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.domain.siat_template import SIAT_XML_Template

education_document = Literal[
    "facturaElectronicaSectorEducativo",
    "facturaComputarizadaSectorEducativo",
]


class CommandGenerate_SIAT_XML_SectorEducativo(DataTransferObject):
    cabecera: dict
    detalle: List[dict]
    node_name: Union[education_document, str] = "facturaElectronicaSectorEducativo"


class ResponseGenerate_SIAT_XML_SectorEducativo(DataTransferObject):
    xml: str
    root_element: Any


@siat_soap_sdk.feature(CommandGenerate_SIAT_XML_SectorEducativo)
class Generate_SIAT_XML_SectorEducativo(Feature):
    def execute(
        self, dto: CommandGenerate_SIAT_XML_SectorEducativo
    ) -> ResponseGenerate_SIAT_XML_SectorEducativo:
        template = SIAT_XML_Template(dto.node_name)
        template.add_header(dto.cabecera)
        template.add_details(dto.detalle)
        template.build_xml_obj()
        xml = template.generate_string_xml()
        return ResponseGenerate_SIAT_XML_SectorEducativo(
            xml=xml, root_element=template.python_root_obj()
        )
