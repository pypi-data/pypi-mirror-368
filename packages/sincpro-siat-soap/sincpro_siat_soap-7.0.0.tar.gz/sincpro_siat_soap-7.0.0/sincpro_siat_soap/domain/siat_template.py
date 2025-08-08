from functools import partial
from io import StringIO
from typing import Dict, List

from sincpro_siat_soap.infrastructure.fn_xml import (
    etree,
    generate_str_xml_from_obj,
    xml_builder,
)
from sincpro_siat_soap.logger import logger


class SIAT_XML_Template:
    root_element: etree._Element = None
    header_element: etree._Element = None
    detail_element: etree._Element = None

    def __init__(self, main_name_node):
        self.main_name_node = main_name_node
        self.xsi = "http://www.w3.org/2001/XMLSchema-instance"

        self.name_spaces = {"xsi": self.xsi}

        self.main_attributes = {
            "{%s}noNamespaceSchemaLocation" % self.xsi: f"{main_name_node}.xsd"
        }

        self.nodes_to_add = []

    def add_header(self, header: Dict):
        self.header_element = xml_builder.cabecera()

        for key, value in header.items():
            try:
                node_definition = partial(xml_builder, key)
                # node_definition = getattr(xml_builder, key)

                if value is None:
                    null_attribute = {"{%s}nil" % self.xsi: "true"}
                    self.header_element.append(node_definition(null_attribute))
                    continue

                if not isinstance(value, str):
                    value = str(value)

                self.header_element.append(node_definition(value))

            except Exception:
                logger.error(
                    f"Error while generating the Header: node[{key}], value[{value}]",
                    exc_info=True,
                )

    def add_details(self, details: List[Dict]):
        self.detail_element = []

        for detail in details:
            new_detail_node = xml_builder.detalle()
            for key, value in detail.items():
                try:
                    node_definition = partial(xml_builder, key)
                    # node_definition = getattr(xml_builder, key)

                    if value is None:
                        null_attribute = {"{%s}nil" % self.xsi: "true"}
                        new_detail_node.append(node_definition(null_attribute))
                        continue

                    if not isinstance(value, str):
                        value = str(value)

                    new_detail_node.append(node_definition(value))

                except Exception:
                    logger.error(
                        f"Error generating the details: node[{key}], value[{value}]",
                        exc_info=True,
                    )

            self.detail_element.append(new_detail_node)

    def build_xml_obj(self):
        self.root_element = etree.Element(
            self.main_name_node, attrib=self.main_attributes, nsmap=self.name_spaces
        )

        if self.header_element is not None:
            self.root_element.append(self.header_element)

        for node_to_add in self.detail_element:
            self.root_element.append(node_to_add)

        return self.root_element

    def python_root_obj(self):
        return self.root_element

    def generate_string_xml(self):
        return generate_str_xml_from_obj(self.root_element)

    # TODO: Error
    def generate_binary_obj_memory(self):
        memory_bin_obj = StringIO()
        self.root_element.getroottree().write(memory_bin_obj, method="c14n")
        return memory_bin_obj
