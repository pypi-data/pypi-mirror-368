"""Decode CUF feature."""

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.infrastructure.encoding import parse_base16_to_integer_string


class CommandDecodeCUF(DataTransferObject):
    cuf: str


class ResponseDecodeCUF(DataTransferObject):
    branch_office: int
    point_of_sale: int


@siat_soap_sdk.feature(CommandDecodeCUF)
class DecodeCUF(Feature):
    """
    Decode CUF to extract branch_office and point_of_sale.
    """

    def execute(self, dto: CommandDecodeCUF) -> ResponseDecodeCUF:
        """
        Decode CUF to extract branch_office and point_of_sale.
        - Remove the control code from CUF.
        - Decode CUF to get the original code.
        - Remove the mod11 digit from the original code.
        - Extract the first 4 digits of the original code for branch_office.
        - Extract the last 4 digits of the original code for point_of_sale.
        """
        # Decode CUF
        code = dto.cuf[:-15]
        string_code = parse_base16_to_integer_string(code)
        original_code = string_code[:-1]
        sub_string_code = original_code[-23:]
        # Get branch_office and point_of_sale
        branch_office = int(sub_string_code[:4])
        point_of_sale = int(sub_string_code[-4:])

        return ResponseDecodeCUF(
            branch_office=branch_office,
            point_of_sale=point_of_sale,
        )
