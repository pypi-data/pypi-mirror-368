from pathlib import Path
from typing import Union
from xml.dom import minidom

import lxml.builder
import signxml
from lxml import etree
from signxml import XMLSigner, XMLVerifier

from sincpro_siat_soap.config import settings

xml_builder = lxml.builder.ElementMaker()


def from_xml_file_to_xml_python_obj(xml_or_xsd_path: str):
    return etree.parse(xml_or_xsd_path)


# TODO: fix Is not working properly
def validate_xml_with_schema(
    xml: Union[str, etree._Element], xsd: Union[str, etree._Element]
):
    _xml = xml
    _xsd = xsd

    if isinstance(xml, str):
        _xml = etree.fromstring(xml)

    if isinstance(xsd, str):
        _xsd = etree.fromstring(_xsd)

    xml_schema = etree.XMLSchema(_xsd)
    return xml_schema.validate(_xml)


def generate_str_xml_from_obj(xml_python_obj, with_format=False) -> str:
    if not with_format:
        return etree.tostring(xml_python_obj).decode("utf-8")

    string_xml_without_format = etree.tostring(xml_python_obj)
    parse_obj = minidom.parseString(string_xml_without_format)
    return parse_obj.toprettyxml()


def load_siat_xsd_file_to_python_obj(file_name: str) -> etree._Element:
    """
    Function in charge to read/load schema xml validator files from folder 'siat_xsd'
    :param file_name: name of file example: 'facturaElectronicaCompraVenta.xsd'
    :return: etree._Element obj library from lxml
    """
    path = Path(__file__).parent.resolve()
    path_file = f"{path}/../resources/siat_xsd/{file_name}"
    result = from_xml_file_to_xml_python_obj(path_file)
    return result


def sign_xml_root(xml: str, key: str, cert: str, password_key: str = None):
    """Function to sign any SIAT xml resources"""
    _xml = xml

    if isinstance(xml, str):
        _xml = etree.fromstring(xml)

    ns_digital_sign = "http://www.w3.org/2000/09/xmldsig#"
    signature = lxml.builder.ElementMaker(
        namespace=ns_digital_sign, nsmap={None: ns_digital_sign}
    )

    _xml.append(signature.Signature(Id="placeholder"))
    _xml.getroottree()

    signer_conf = XMLSigner(
        method=signxml.methods.enveloped,
        signature_algorithm="rsa-sha256",
        digest_algorithm="sha256",
        c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315",
    )

    key_password = password_key
    if password_key is None:
        key_password = settings.sign_password

    if key_password and len(str(key_password)) > 0:
        bin_key_password = str(key_password).encode("utf-8")
        return signer_conf.sign(_xml, key=key, cert=cert, passphrase=bin_key_password)

    return signer_conf.sign(_xml, key=key, cert=cert)


# TODO: is now working properly it seems due to the key is encripted
def validate_signed_xml(cert, signed_root):
    """
    Function to validate a signed XML
    :param cert: str
    :param signed_root: xml.etree.ElementTree
    :return: boolean
    """
    try:
        signed_data = etree.tostring(signed_root)
        return XMLVerifier().verify(signed_data, x509_cert=cert)
    except Exception as ex:
        raise ValueError(f"Error in validate_signed_xml Error: {ex}")


def xml_to_canonical_c14n(xml: Union[etree._Element, str]) -> bytes:
    xml_to_transform = xml

    if isinstance(xml, str):
        xml_to_transform = etree.fromstring(xml)

    return etree.tostring(xml_to_transform, method="c14n")


def add_signature_node_to_xml(
    xml: Union[etree._Element, str, bytes], signature_node: etree._Element
):
    xml_py_obj = xml

    if isinstance(xml, str):
        xml_py_obj = etree.fromstring(xml)

    if isinstance(xml, bytes):
        string_xml = xml.decode("utf-8")
        xml_py_obj = etree.fromstring(string_xml)

    xml_py_obj.append(signature_node)
    return xml_py_obj


def build_signature_tags(string_hash_invoice: str) -> etree._Element:
    ns_digital_sign = "http://www.w3.org/2000/09/xmldsig#"

    signature_builder = lxml.builder.ElementMaker(
        namespace=ns_digital_sign, nsmap={None: ns_digital_sign}
    )

    signagure_node = signature_builder.Signature(
        signature_builder.SignedInfo(
            signature_builder.CanonicalizationMethod(
                Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"
            ),
            signature_builder.SignatureMethod(
                Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"
            ),
            signature_builder.Reference(
                signature_builder.Transforms(
                    signature_builder.Transform(
                        Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"
                    ),
                    signature_builder.Transform(
                        Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315#WithComments"
                    ),
                ),
                signature_builder.DigestMethod(
                    Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"
                ),
                signature_builder.DigestValue(string_hash_invoice),
                URI="",
            ),
        ),
        signature_builder.SignatureValue(),
        signature_builder.KeyInfo(
            signature_builder.X509Data(signature_builder.X509Certificate())
        ),
    )
    return signagure_node


def add_signature_value_to_signature_node(signature: str, signature_node: etree._Element):
    signature_value_node = signature_node.find(".//SignatureValue", signature_node.nsmap)
    signature_value_node.text = signature


def add_public_key_to_signature_node(public_key: str, signature_node: etree._Element):
    x509_certificade_node = signature_node.find(".//X509Certificate", signature_node.nsmap)
    x509_certificade_node.text = public_key
