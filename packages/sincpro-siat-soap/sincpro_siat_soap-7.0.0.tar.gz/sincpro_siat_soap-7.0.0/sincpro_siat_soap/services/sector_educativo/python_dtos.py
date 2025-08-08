from typing import Dict, List, Union

from sincpro_siat_soap import DataTransferObject


class EducationSectorHeaderDTO(DataTransferObject):
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
    nombreEstudiante: str
    periodoFacturado: str
    codigoMetodoPago: int
    numeroTarjeta: int | str | None
    montoTotal: float
    montoTotalSujetoIva: float
    codigoMoneda: int
    tipoCambio: int
    montoTotalMoneda: float
    montoGiftCard: float | None
    descuentoAdicional: float | None
    codigoExcepcion: int | None
    cafc: Union[str, None]
    leyenda: str
    usuario: str | int
    codigoDocumentoSector: int


class EducationSectorDetailDTO(DataTransferObject):
    actividadEconomica: int | str
    codigoProductoSin: int | str
    codigoProducto: int | str
    descripcion: str
    cantidad: float
    unidadMedida: int
    precioUnitario: float
    montoDescuento: float
    subTotal: float


class EducationSectorDTO(DataTransferObject):
    header: Union[Dict, EducationSectorHeaderDTO]
    details: Union[List[Dict], List[EducationSectorDetailDTO]]
