"""Contains global definitions for SIAT SOAP API"""

import os
from enum import IntEnum, StrEnum

from sincpro_siat_soap.domain import (
    SIATEmissionType,
    SIATEnvironment,
    SIATInvoiceType,
    SIATModality,
    SIATSignificantEvent,
    SignificantEventModel,
)


class SIAT_FIELD_WIDTH:
    NIT: int = 13
    DATETIME: int = 17
    BRANCH_OFFICE: int = 4
    DOCUMENT_TYPE: int = 2
    INVOICE_NUMBER: int = 10
    POINT_OF_SALE: int = 4


# fmt: off
MAP_DESCRIPTION_SIGNIFICANT_EVENT: dict[SIATSignificantEvent | int, str] = {
    SIATSignificantEvent.CORTE_INTERNET: "CORTE DEL SERVICIO DE INTERNET",
    SIATSignificantEvent.ADMINISTRACION_TRIBUTARIA: "INACCESIBILIDAD AL SERVICIO WEB DE LA ADMINISTRACIÓN TRIBUTARIA",
    SIATSignificantEvent.DEPLIEGUE_A_ZONAS_SIN_INTERNET: "INGRESO A ZONAS SIN INTERNET POR DESPLIEGUE DE PUNTO DE VENTA EN VEHICULOS AUTOMOTORES",
    SIATSignificantEvent.ZONAS_SIN_INTERNET: "VENTA EN LUGARES SIN INTERNET",
    SIATSignificantEvent.CORTE_ELECTRICIDAD: "CORTE DE SUMINISTRO DE ENERGIA ELECTRICA",
    SIATSignificantEvent.VIRUS_INFORMATICO: "VIRUS INFORMÁTICO O FALLA DE SOFTWARE",
    SIATSignificantEvent.FALLA_HARDWARE: "CAMBIO DE INFRAESTRUCTURA DEL SISTEMA INFORMÁTICO DE FACTURACIÓN O FALLA DE HARDWARE",
}
# fmt: on


# ----------------------------------------------------------------------------------------------------------------------
# Approved digital documents
# ----------------------------------------------------------------------------------------------------------------------
class SIATApprovedDocumentId(IntEnum):
    """Approved documents"""

    COMPRA_VENTA = 1
    ALQUILER_DE_BIENES = 2
    SECTOR_EDUCATIVO = 11
    HOTELES = 16
    HOSPITALES_CLINICA = 17
    PREVALORADA = 23
    NOTA_DE_CREDITO_DEBITO = 24
    PREVALORADA_SIN_DERECHO_CREDITO_FISCAL = 36


class XMLRootName(StrEnum):
    """Root name for XML files"""

    COMPRA_VENTA_ELECTRONICA = "facturaElectronicaCompraVenta"
    COMPRA_VENTA_COMPUTARIZADA = "facturaComputarizadaCompraVenta"
    ALQUILER_DE_BIENES_ELECTRONICA = "facturaElectronicaAlquilerBienInmueble"
    ALQUILER_DE_BIENES_COMPUTARIZADA = "facturaComputarizadaAlquilerBienInmueble"
    SECTOR_EDUCATIVO_ELECTRONICA = "facturaElectronicaSectorEducativo"
    SECTOR_EDUCATIVO_COMPUTARIZADA = "facturaComputarizadaSectorEducativo"
    HOTELES_ELECTRONICA = "facturaElectronicaHotel"
    HOTELES_COMPUTARIZADA = "facturaComputarizadaHotel"
    HOSPITALES_CLINICA_ELECTRONICA = "facturaElectronicaHospitalClinica"
    HOSPITALES_CLINICA_COMPUTARIZADA = "facturaComputarizadaHospitalClinica"
    PREVALORADA_ELECTRONICA = "facturaElectronicaPrevalorada"
    PREVALORADA_COMPUTARIZADA = "facturaComputarizadaPrevalorada"
    NOTA_CREDITO_DEBITO_ELECTRONICA = "notaFiscalElectronicaCreditoDebito"
    NOTA_CREDITO_DEBITO_COMPUTARIZADA = "notaFiscalComputarizadaCreditoDebito"
    PREVALORADA_SIN_DERECHO_CREDITO_FISCAL_ELECTRONICA = "facturaElectronicaPrevaloradaSD"
    PREVALORADA_SIN_DERECHO_CREDITO_FISCAL_COMPUTARIZADA = "facturaComputarizadaPrevaloradaSD"


# fmt: off
def get_root_name_by_document_id(document_id: SIATApprovedDocumentId, modality: SIATModality) -> XMLRootName:
    """Get the root name for XML files based on document id and modality"""
    match document_id, modality:
        case SIATApprovedDocumentId.COMPRA_VENTA, SIATModality.ELECTRONICA:
            return XMLRootName.COMPRA_VENTA_ELECTRONICA
        case SIATApprovedDocumentId.COMPRA_VENTA, SIATModality.COMPUTARIZADA:
            return XMLRootName.COMPRA_VENTA_COMPUTARIZADA
        case SIATApprovedDocumentId.ALQUILER_DE_BIENES, SIATModality.ELECTRONICA:
            return XMLRootName.ALQUILER_DE_BIENES_ELECTRONICA
        case SIATApprovedDocumentId.ALQUILER_DE_BIENES, SIATModality.COMPUTARIZADA:
            return XMLRootName.ALQUILER_DE_BIENES_COMPUTARIZADA
        case SIATApprovedDocumentId.SECTOR_EDUCATIVO, SIATModality.ELECTRONICA:
            return XMLRootName.SECTOR_EDUCATIVO_ELECTRONICA
        case SIATApprovedDocumentId.SECTOR_EDUCATIVO, SIATModality.COMPUTARIZADA:
            return XMLRootName.SECTOR_EDUCATIVO_COMPUTARIZADA
        case SIATApprovedDocumentId.HOTELES, SIATModality.ELECTRONICA:
            return XMLRootName.HOTELES_ELECTRONICA
        case SIATApprovedDocumentId.HOTELES, SIATModality.COMPUTARIZADA:
            return XMLRootName.HOTELES_COMPUTARIZADA
        case SIATApprovedDocumentId.HOSPITALES_CLINICA, SIATModality.ELECTRONICA:
            return XMLRootName.HOSPITALES_CLINICA_ELECTRONICA
        case SIATApprovedDocumentId.HOSPITALES_CLINICA, SIATModality.COMPUTARIZADA:
            return XMLRootName.HOSPITALES_CLINICA_COMPUTARIZADA
        case SIATApprovedDocumentId.PREVALORADA, SIATModality.ELECTRONICA:
            return XMLRootName.PREVALORADA_ELECTRONICA
        case SIATApprovedDocumentId.PREVALORADA, SIATModality.COMPUTARIZADA:
            return XMLRootName.PREVALORADA_COMPUTARIZADA
        case SIATApprovedDocumentId.NOTA_DE_CREDITO_DEBITO, SIATModality.ELECTRONICA:
            return XMLRootName.NOTA_CREDITO_DEBITO_ELECTRONICA
        case SIATApprovedDocumentId.NOTA_DE_CREDITO_DEBITO, SIATModality.COMPUTARIZADA:
            return XMLRootName.NOTA_CREDITO_DEBITO_COMPUTARIZADA
        case SIATApprovedDocumentId.PREVALORADA_SIN_DERECHO_CREDITO_FISCAL, SIATModality.ELECTRONICA:
            return XMLRootName.PREVALORADA_SIN_DERECHO_CREDITO_FISCAL_ELECTRONICA
        case SIATApprovedDocumentId.PREVALORADA_SIN_DERECHO_CREDITO_FISCAL, SIATModality.COMPUTARIZADA:
            return XMLRootName.PREVALORADA_SIN_DERECHO_CREDITO_FISCAL_COMPUTARIZADA

# fmt: on


# ----------------------------------------------------------------------------------------------------------------------
# Version: 3.0
# ----------------------------------------------------------------------------------------------------------------------
class SIAT_WSDL:
    OBTENCION_CODIGO = "OBTERCION_CODIGO"
    SINCRONIZACION_DE_DATOS = "SINCRONIZACION_DE_DATOS"
    OPERACIONES = "OPERACIONES"
    COMPRAS = "COMPRAS"
    NOTA_DE_CREDITO = "NOTA_DE_CREDITO"
    FACTURA_COMPRA_VENTA = "FACTURA_COMPRA_VENTA"
    SERVICIOS_ELECTRONICA = "SERVICIOS_ELECTRONICA"
    SERVICIOS_COMPUTARIZADA = "SERVICIOS_COMPUTARIZADA"


WSDL_SERVICE_LIST = [
    SIAT_WSDL.OBTENCION_CODIGO,
    SIAT_WSDL.SINCRONIZACION_DE_DATOS,
    SIAT_WSDL.OPERACIONES,
    SIAT_WSDL.COMPRAS,
    SIAT_WSDL.NOTA_DE_CREDITO,
    SIAT_WSDL.FACTURA_COMPRA_VENTA,
    SIAT_WSDL.SERVICIOS_ELECTRONICA,
    SIAT_WSDL.SERVICIOS_COMPUTARIZADA,
]


# ----------------------------------------------------------------------------------------------------------------------
# Shared Endpoints for ELECTRINICA and COMPUTARIZADA
# ----------------------------------------------------------------------------------------------------------------------

SIAT_TESTING_ENDPOINTS = {
    SIAT_WSDL.OBTENCION_CODIGO: "https://pilotosiatservicios.impuestos.gob.bo/v2/FacturacionCodigos?wsdl",
    SIAT_WSDL.SINCRONIZACION_DE_DATOS: "https://pilotosiatservicios.impuestos.gob.bo/v2/FacturacionSincronizacion?wsdl",
    SIAT_WSDL.OPERACIONES: "https://pilotosiatservicios.impuestos.gob.bo/v2/FacturacionOperaciones?wsdl",
    SIAT_WSDL.COMPRAS: "https://pilotosiatservicios.impuestos.gob.bo/v2/ServicioRecepcionCompras?wsdl",
    SIAT_WSDL.NOTA_DE_CREDITO: "https://pilotosiatservicios.impuestos.gob.bo/v2/ServicioFacturacionDocumentoAjuste?wsdl",
    SIAT_WSDL.FACTURA_COMPRA_VENTA: "https://pilotosiatservicios.impuestos.gob.bo/v2/ServicioFacturacionCompraVenta?wsdl",
    SIAT_WSDL.SERVICIOS_ELECTRONICA: "https://pilotosiatservicios.impuestos.gob.bo/v2/ServicioFacturacionElectronica?wsdl",
    SIAT_WSDL.SERVICIOS_COMPUTARIZADA: "https://pilotosiatservicios.impuestos.gob.bo/v2/ServicioFacturacionComputarizada?wsdl",
}

SIAT_PRODUCTION_ENDPOINTS = {
    SIAT_WSDL.OBTENCION_CODIGO: "https://siatrest.impuestos.gob.bo/v2/FacturacionCodigos?wsdl",
    SIAT_WSDL.SINCRONIZACION_DE_DATOS: "https://siatrest.impuestos.gob.bo/v2/FacturacionSincronizacion?wsdl",
    SIAT_WSDL.OPERACIONES: "https://siatrest.impuestos.gob.bo/v2/FacturacionOperaciones?wsdl",
    SIAT_WSDL.COMPRAS: "https://siatrest.impuestos.gob.bo/v2/ServicioRecepcionCompras?wsdl",
    SIAT_WSDL.NOTA_DE_CREDITO: "https://siatrest.impuestos.gob.bo/v2/ServicioFacturacionDocumentoAjuste?wsdl",
    SIAT_WSDL.FACTURA_COMPRA_VENTA: "https://siatrest.impuestos.gob.bo/v2/ServicioFacturacionCompraVenta?wsdl",
    SIAT_WSDL.SERVICIOS_ELECTRONICA: "https://siatrest.impuestos.gob.bo/v2/ServicioFacturacionElectronica?wsdl",
    SIAT_WSDL.SERVICIOS_COMPUTARIZADA: "https://siatrest.impuestos.gob.bo/v2/ServicioFacturacionComputarizada?wsdl",
}


WSDL_DIR = os.path.join(os.path.dirname(__file__)) + "/resources/wsdl"
WSDL_TESTING_DIR = WSDL_DIR + "/testing"
WSDL_PRODUCTION_DIR = WSDL_DIR + "/production"

__all__ = [
    "SIAT_FIELD_WIDTH",
    "MAP_DESCRIPTION_SIGNIFICANT_EVENT",
    "SIATApprovedDocumentId",
    "XMLRootName",
    "get_root_name_by_document_id",
    "SIAT_WSDL",
    "SIAT_TESTING_ENDPOINTS",
    "SIAT_PRODUCTION_ENDPOINTS",
    "SIATEnvironment",
    "SIATInvoiceType",
    "SIATEmissionType",
    "SignificantEventModel",
    "WSDL_SERVICE_LIST",
]
