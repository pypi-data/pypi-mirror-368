"""Factura De Hospital"""

from typing import Any, Dict, List, Literal, Union

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.domain.siat_template import SIAT_XML_Template

hospital_document = Literal[
    "facturaElectronicaHospitalClinica",
    "facturaComputarizadaHospitalClinica",
]


class CommandGenerate_SIAT_XML_SectorHospital(DataTransferObject):
    cabecera: Dict
    detalle: List[Dict]
    node_name: Union[hospital_document, str] = "facturaElectronicaHospitalClinica"


class ResponseGenerate_SIAT_XML_SectorHospital(DataTransferObject):
    xml: str
    root_element: Any


@siat_soap_sdk.feature(CommandGenerate_SIAT_XML_SectorHospital)
class Generate_SIAT_XML(Feature):
    def execute(
        self, dto: CommandGenerate_SIAT_XML_SectorHospital
    ) -> ResponseGenerate_SIAT_XML_SectorHospital:
        template = SIAT_XML_Template(dto.node_name)
        template.add_header(dto.cabecera)
        template.add_details(dto.detalle)
        template.build_xml_obj()
        xml = template.generate_string_xml()
        return ResponseGenerate_SIAT_XML_SectorHospital(
            xml=xml, root_element=template.python_root_obj()
        )
