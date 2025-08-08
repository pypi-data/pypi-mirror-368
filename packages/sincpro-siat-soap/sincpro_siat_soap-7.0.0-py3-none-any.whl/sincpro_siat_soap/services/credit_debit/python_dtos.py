from datetime import datetime
from typing import Dict, List, Union

from sincpro_siat_soap import DataTransferObject


class DebitCreditHeaderDTO(DataTransferObject):
    nitEmisor: int | str
    razonSocialEmisor: str
    municipio: str
    telefono: str
    numeroNotaCreditoDebito: int
    cuf: str
    cufd: str
    codigoSucursal: int
    direccion: str
    codigoPuntoVenta: int
    fechaEmision: str | datetime
    nombreRazonSocial: str
    codigoTipoDocumentoIdentidad: int
    numeroDocumento: int
    complemento: str | None
    codigoCliente: str | int
    numeroFactura: int
    numeroAutorizacionCuf: str
    fechaEmisionFactura: str
    montoTotalOriginal: float
    montoTotalDevuelto: float
    montoDescuentoCreditoDebito: float
    montoEfectivoCreditoDebito: float
    codigoExcepcion: int | None
    leyenda: str
    usuario: str | int
    codigoDocumentoSector: int


class DebitCreditDetailDTO(DataTransferObject):
    actividadEconomica: int | str
    codigoProductoSin: int | str
    codigoProducto: int | str
    descripcion: str
    cantidad: Union[float, int]
    unidadMedida: int
    precioUnitario: float
    montoDescuento: float
    subTotal: float
    codigoDetalleTransaccion: int | str


class DebitCreditDTO(DataTransferObject):
    header: Union[Dict, DebitCreditHeaderDTO]
    details: Union[List[Dict], List[DebitCreditDetailDTO]]
