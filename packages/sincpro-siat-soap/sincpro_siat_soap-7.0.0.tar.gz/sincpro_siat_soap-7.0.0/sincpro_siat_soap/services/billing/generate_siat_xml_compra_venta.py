"""Base use case"""

from typing import Any, List

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.domain.siat_template import SIAT_XML_Template


class CommandGenerate_SIAT_XML_CompraVenta(DataTransferObject):
    cabecera: dict
    detalle: List[dict]
    node_name: str = "facturaElectronicaCompraVenta"


class ResponseGenerate_SIAT_XML_CompraVenta(DataTransferObject):
    xml: str
    root_element: Any


@siat_soap_sdk.feature(CommandGenerate_SIAT_XML_CompraVenta)
class Generate_SIAT_XML_CompraVenta(Feature):
    def execute(
        self, dto: CommandGenerate_SIAT_XML_CompraVenta
    ) -> ResponseGenerate_SIAT_XML_CompraVenta:
        template = SIAT_XML_Template(dto.node_name)
        template.add_header(dto.cabecera)
        template.add_details(dto.detalle)

        template.build_xml_obj()
        xml = template.generate_string_xml()

        return ResponseGenerate_SIAT_XML_CompraVenta(
            xml=xml, root_element=template.python_root_obj()
        )
