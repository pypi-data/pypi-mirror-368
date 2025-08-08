from typing import Dict, List, Union

from sincpro_siat_soap import DataTransferObject


class AlquierInvoiceHeaderDTO(DataTransferObject):
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
    complemento: str | None
    codigoCliente: str | int
    periodoFacturado: str
    codigoMetodoPago: int
    numeroTarjeta: int | str | None
    montoTotal: float
    montoTotalSujetoIva: float
    codigoMoneda: int
    tipoCambio: int
    montoTotalMoneda: float
    descuentoAdicional: Union[float, None]
    codigoExcepcion: int | None
    cafc: Union[str, None]
    leyenda: str
    usuario: str | int
    codigoDocumentoSector: int


class AlquilerInvoiceDetailDTO(DataTransferObject):
    actividadEconomica: int | str
    codigoProductoSin: int | str
    codigoProducto: int | str
    descripcion: str
    cantidad: float
    unidadMedida: int
    precioUnitario: float
    montoDescuento: float
    subTotal: float


class AlquierInvoiceDTO(DataTransferObject):
    header: Union[Dict, AlquierInvoiceHeaderDTO]
    details: Union[List[Dict], List[AlquilerInvoiceDetailDTO]]
