"""Generate CODIGO UNICO DE FACTURA CUF"""

from datetime import datetime

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.domain import SIATModality
from sincpro_siat_soap.infrastructure.encoding import (
    get_mod_eleven_digit,
    parse_integer_string_to_base16,
)
from sincpro_siat_soap.shared.fn_datetime import datetime_for_CUF


class CommandGenerateCUF(DataTransferObject):
    control_code: str
    nit: str | int
    date_time: datetime | str
    branch_office: int
    emission_type: int
    invoice_type: int
    type_sector_document: int
    invoice_num: int
    point_of_sale: int
    modality: SIATModality


class ResponseGenerateCUF(DataTransferObject):
    cuf: str


@siat_soap_sdk.feature(CommandGenerateCUF)
class GenerateCUF(Feature):
    # · NIT EMISOR = 0000123456789
    # · FECHA / HORA = 20190113163721231
    # · SUCURSAL = 0000
    # · MODALIDAD = 1 # ELECTORNICA, COMPUTARIZADA
    # · TIPO EMISIÓN = 1 # ONLINE, OFFLINE, ETC
    # · TIPO FACTURA / DOCUMENTO AJUSTE = 1
    # · TIPO DOCUMENTO SECTOR = 01
    # · NÚMERO DE FACTURA = 0000000001
    # · POS: 0000

    def execute(self, dto: CommandGenerateCUF) -> ResponseGenerateCUF:
        invoice_date = datetime_for_CUF(dto.date_time)
        code = (
            f"{str(dto.nit).zfill(13)}"
            f"{invoice_date}"
            f"{str(dto.branch_office).zfill(4)}"
            f"{dto.modality}"
            f"{dto.emission_type}"
            f"{dto.invoice_type}"
            f"{str(dto.type_sector_document).zfill(2)}"
            f"{str(dto.invoice_num).zfill(10)}"
            f"{str(dto.point_of_sale).zfill(4)}"
        )
        mod11_digit = get_mod_eleven_digit(code)
        code_plus_mod = code + mod11_digit
        cuf_code = f"{parse_integer_string_to_base16(code_plus_mod)}{dto.control_code}"

        return ResponseGenerateCUF(cuf=cuf_code)
