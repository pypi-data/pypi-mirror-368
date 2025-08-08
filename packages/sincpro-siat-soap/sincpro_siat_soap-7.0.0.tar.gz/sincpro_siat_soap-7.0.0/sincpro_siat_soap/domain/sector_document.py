"""All the classes related to the Sector Document."""

from enum import IntEnum, StrEnum


class SIATEnvironment(IntEnum):
    """SIAT Environment"""

    PRODUCTION = 1
    TEST = 2


class SIATModality(IntEnum):
    """SIAT Modality"""

    ELECTRONICA = 1
    COMPUTARIZADA = 2


class SIATEmissionType(IntEnum):
    """Emission type"""

    ONLINE = 1
    OFFLINE = 2
    MASSIVE = 3


class SIATInvoiceType(IntEnum):
    """Invoice type"""

    CREDITO_FISCAL = 1
    SIN_CREDITO_FISCAL = 2
    DOCUMENTO_DE_AJUSTE = 3


class SectorDocumentState(StrEnum):
    """State of the Sector Document"""

    CONFIRMED = "VALIDADA"
    VALID = "VALIDA"
    REJECTED = "RECHAZADA"
    CANCELLED = "ANULADA"
    OBSERVED = "OBSERVADA"
    PENDING = "PENDIENTE"
