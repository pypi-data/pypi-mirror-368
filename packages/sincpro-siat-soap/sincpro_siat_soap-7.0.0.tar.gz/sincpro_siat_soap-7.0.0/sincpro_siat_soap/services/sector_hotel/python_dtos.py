from typing import Dict, List, Union

from sincpro_siat_soap import DataTransferObject


class HotelInvoiceHeaderDTO(DataTransferObject):
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
    cantidadHuespedes: Union[int, None]
    cantidadHabitaciones: Union[int, None]
    cantidadMayores: Union[int, None]
    cantidadMenores: Union[int, None]
    fechaIngresoHospedaje: str
    codigoMetodoPago: int
    numeroTarjeta: int | str | None
    montoTotal: float
    montoTotalSujetoIva: float
    codigoMoneda: int
    tipoCambio: int | float
    montoTotalMoneda: float
    montoGiftCard: bool | None
    descuentoAdicional: float | None
    codigoExcepcion: int | None
    cafc: Union[str, None]
    leyenda: str
    usuario: str | int
    codigoDocumentoSector: int


class HotelInvoiceDetailDTO(DataTransferObject):
    actividadEconomica: int | str
    codigoProductoSin: int | str
    codigoProducto: int | str
    codigoTipoHabitacion: Union[int, None]
    descripcion: str
    cantidad: float
    unidadMedida: int
    precioUnitario: float
    montoDescuento: float
    subTotal: float
    detalleHuespedes: Union[str, None]


class HotelInvoiceDTO(DataTransferObject):
    header: Union[Dict, HotelInvoiceHeaderDTO]
    details: Union[List[Dict], List[HotelInvoiceDetailDTO]]
