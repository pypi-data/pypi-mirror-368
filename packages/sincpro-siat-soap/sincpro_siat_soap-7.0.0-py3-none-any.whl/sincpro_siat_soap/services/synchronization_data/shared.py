from typing import Any

from pydantic import Field

from sincpro_siat_soap import DataTransferObject
from sincpro_siat_soap.domain import SIATEnvironment


class BaseRequestSynchronization(DataTransferObject):
    nit: str | int
    cuis: str
    branch_office: int
    system_code: str
    point_of_sale: int
    environment: SIATEnvironment


class BaseRequestCommonSyncServices(BaseRequestSynchronization):
    service: str


class BaseSIATResponse(DataTransferObject):
    raw_response: Any = Field(repr=False)
    comparison_data: Any
