from typing import Any, Dict, List

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.domain.siat_template import SIAT_XML_Template


class CommandGenerateCreditDebitXML(DataTransferObject):
    cabecera: Dict
    detalles: List[Dict]
    node_name: str = "notaFiscalElectronicaCreditoDebito"


class ResponseGenerateCreditDebitXML(DataTransferObject):
    xml: str
    root_element: Any


@siat_soap_sdk.feature(CommandGenerateCreditDebitXML)
class GenerateCreditDebitXML(Feature):
    def execute(self, dto: CommandGenerateCreditDebitXML) -> ResponseGenerateCreditDebitXML:
        template = SIAT_XML_Template(dto.node_name)
        template.add_header(dto.cabecera)
        template.add_details(dto.detalles)

        template.build_xml_obj()
        xml = template.generate_string_xml()

        return ResponseGenerateCreditDebitXML(
            xml=xml, root_element=template.python_root_obj()
        )
