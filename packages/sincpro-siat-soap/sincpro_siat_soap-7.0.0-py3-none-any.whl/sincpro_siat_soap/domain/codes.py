from datetime import datetime
from enum import IntEnum

from sincpro_siat_soap import DataTransferObject


class SIATSignificantEvent(IntEnum):
    """Significant events"""

    CORTE_INTERNET = 1
    ADMINISTRACION_TRIBUTARIA = 2
    DEPLIEGUE_A_ZONAS_SIN_INTERNET = 3
    ZONAS_SIN_INTERNET = 4
    CORTE_ELECTRICIDAD = 5
    VIRUS_INFORMATICO = 6
    FALLA_HARDWARE = 7


class CUISModel(DataTransferObject):
    """Codigo Unico de Sistema SIAT"""

    cuis: str
    end_datetime: datetime


class CUFDModel(DataTransferObject):
    """Codigo Unico de Factura Diaria SIAT"""

    cufd: str
    control_code: str
    start_datetime: datetime
    end_datetime: datetime


class SignificantEventModel(DataTransferObject):
    """Evento Significativo SIAT"""

    event_type: SIATSignificantEvent
    significant_event_code: int
    description: str
    start_datetime_event: datetime
    end_datetime_event: datetime
