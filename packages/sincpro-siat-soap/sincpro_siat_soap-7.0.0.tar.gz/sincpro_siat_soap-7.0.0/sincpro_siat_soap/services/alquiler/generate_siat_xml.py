"""Factura De Alquiler"""

from typing import Any, Dict, List, Literal, Union

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.domain.siat_template import SIAT_XML_Template

education_document = Literal[
    "facturaElectronicaAlquilerBienInmueble",
    "facturaComputarizadaAlquilerBienInmueble",
]


class CommandGenerate_SIAT_XML_Alquiler(DataTransferObject):
    cabecera: Dict
    detalle: List[Dict]
    node_name: Union[education_document, str] = "facturaElectronicaAlquilerBienInmueble"


class ResponseGenerate_SIAT_XML_Alquiler(DataTransferObject):
    xml: str
    root_element: Any


@siat_soap_sdk.feature(CommandGenerate_SIAT_XML_Alquiler)
class Generate_SIAT_XML_Alquiler(Feature):
    def execute(
        self, dto: CommandGenerate_SIAT_XML_Alquiler
    ) -> ResponseGenerate_SIAT_XML_Alquiler:
        template = SIAT_XML_Template(dto.node_name)
        template.add_header(dto.cabecera)
        template.add_details(dto.detalle)
        template.build_xml_obj()
        xml = template.generate_string_xml()
        return ResponseGenerate_SIAT_XML_Alquiler(
            xml=xml, root_element=template.python_root_obj()
        )
