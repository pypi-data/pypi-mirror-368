"""Factura Pre-valorada"""

from typing import Any, Dict, List, Literal, Union

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.domain.siat_template import SIAT_XML_Template

education_document = Literal[
    "facturaElectronicaPrevalorada",
    "facturaComputarizadaPrevalorada",
    "facturaElectronicaPrevaloradaSD",
    "facturaComputarizadaPrevaloradaSD",
]


class CommandGenerate_SIAT_XML_Prevalorada(DataTransferObject):
    cabecera: Dict
    detalle: List[Dict]
    node_name: Union[education_document, str] = "facturaElectronicaPrevalorada"


class ResponseGenerate_SIAT_XML_Prevalorada(DataTransferObject):
    xml: str
    root_element: Any


@siat_soap_sdk.feature(CommandGenerate_SIAT_XML_Prevalorada)
class Generate_SIAT_XML_Prevalorada(Feature):
    def execute(
        self, dto: CommandGenerate_SIAT_XML_Prevalorada
    ) -> ResponseGenerate_SIAT_XML_Prevalorada:
        template = SIAT_XML_Template(dto.node_name)
        template.add_header(dto.cabecera)
        template.add_details(dto.detalle)
        template.build_xml_obj()
        xml = template.generate_string_xml()
        return ResponseGenerate_SIAT_XML_Prevalorada(
            xml=xml, root_element=template.python_root_obj()
        )
