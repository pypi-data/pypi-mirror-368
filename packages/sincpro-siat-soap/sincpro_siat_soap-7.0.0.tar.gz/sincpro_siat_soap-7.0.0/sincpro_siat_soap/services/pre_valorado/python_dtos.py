from typing import Dict, List

from sincpro_siat_soap import DataTransferObject


class PreValoradoDTO(DataTransferObject):
    nitEmisor: int | str
    razonSocialEmisor: str
    municipio: str
    telefono: str
    numeroFactura: int
    cuf: str
    cufd: str
    codigoSucursal: int
    direccion: str
    codigoPuntoVenta: int
    fechaEmision: str
    nombreRazonSocial: str
    codigoTipoDocumentoIdentidad: int
    numeroDocumento: str
    codigoCliente: str | int
    codigoMetodoPago: int
    numeroTarjeta: int | str | None
    montoTotal: float
    montoTotalSujetoIva: float
    codigoMoneda: int
    tipoCambio: int
    montoTotalMoneda: float
    leyenda: str
    usuario: str | int
    codigoDocumentoSector: int


class PreValoradoDetailDTO(DataTransferObject):
    actividadEconomica: int | str
    codigoProductoSin: int | str
    codigoProducto: int | str
    descripcion: str
    cantidad: float
    unidadMedida: int
    precioUnitario: float
    montoDescuento: float
    subTotal: float


class PreValoradoInvoiceDTO(DataTransferObject):
    header: PreValoradoDTO | Dict
    details: List[PreValoradoDetailDTO | Dict]
