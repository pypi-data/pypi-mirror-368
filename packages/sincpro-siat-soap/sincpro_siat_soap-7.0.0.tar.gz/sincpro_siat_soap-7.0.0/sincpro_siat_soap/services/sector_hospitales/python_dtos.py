from typing import Dict, List, Optional, Union

from sincpro_siat_soap import DataTransferObject


class HospitalSectorHeaderDTO(DataTransferObject):
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
    modalidadServicio: str
    codigoMetodoPago: int
    numeroTarjeta: int | str | None
    montoTotal: float
    montoTotalSujetoIva: float
    codigoMoneda: int
    tipoCambio: int | float
    montoTotalMoneda: float
    montoGiftCard: Union[bool, None]
    descuentoAdicional: Union[float, None]
    codigoExcepcion: int | None
    cafc: Union[int, str, None]
    leyenda: str
    usuario: str | int
    codigoDocumentoSector: int


class HospitalSectorDetailDTO(DataTransferObject):
    actividadEconomica: int | str
    codigoProductoSin: int | str
    codigoProducto: int | str
    descripcion: str
    especialidad: Optional[str]  # Hospital -  Producto
    especialidadDetalle: Optional[str]  # Hospital  - Producto
    nroQuirofanoSalaOperaciones: int  # Hospital -  Producto
    especialidadMedico: Optional[str]  # Hospital - Medico Informacion
    nombreApellidoMedico: str  # Hospital - Medico Informacion
    nitDocumentoMedico: str  # Hospital  - Medico Informacion
    nroMatriculaMedico: Optional[str]  # Hospital  - Medico Informacion
    nroFacturaMedico: Optional[str]  # Hospital  - Medico Factura
    cantidad: float
    unidadMedida: int
    precioUnitario: float
    montoDescuento: float
    subTotal: float


class HospitalSectorDTO(DataTransferObject):
    header: Union[Dict, HospitalSectorHeaderDTO]
    details: Union[List[Dict], List[HospitalSectorDetailDTO]]
