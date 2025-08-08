"""Get significant events from SIAT based on date."""

from datetime import date, datetime
from typing import Any

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.domain import SIATEnvironment, SIATSignificantEvent
from sincpro_siat_soap.domain.codes import SignificantEventModel
from sincpro_siat_soap.global_definitions import SIAT_WSDL


class CommandGetRegisteredSignificantEvents(DataTransferObject):
    point_of_sale: int
    system_code: str
    branch_office: int
    event_date: str | date
    cufd: str
    cuis: str
    nit: int | str
    enviroment: SIATEnvironment


class ResponseGetRegisteredSignificantEvents(DataTransferObject):
    raw_response: Any
    list_significant_events: list[SignificantEventModel]


@siat_soap_sdk.app_service(CommandGetRegisteredSignificantEvents)
class GetRegisteredSignificantEvents(Feature):

    def execute(
        self, dto: CommandGetRegisteredSignificantEvents
    ) -> ResponseGetRegisteredSignificantEvents:
        _date = dto.event_date
        if isinstance(dto.event_date, date):
            _date = _date.isoformat()

        response = self.soap_client(
            SIAT_WSDL.OPERACIONES
        ).service.consultaEventoSignificativo(
            SolicitudConsultaEvento={
                "codigoAmbiente": dto.enviroment,
                "codigoPuntoVenta": dto.point_of_sale,
                "codigoSistema": dto.system_code,
                "codigoSucursal": dto.branch_office,
                "cufd": dto.cufd,
                "cuis": dto.cuis,
                "nit": dto.nit,
                "fechaEvento": dto.event_date,
            }
        )

        return ResponseGetRegisteredSignificantEvents(
            raw_response=response,
            list_significant_events=[
                SignificantEventModel(
                    event_type=SIATSignificantEvent(event["codigoEvento"]),
                    significant_event_code=event["codigoRecepcionEventoSignificativo"],
                    description=event["descripcion"],
                    start_datetime_event=datetime.fromisoformat(event["fechaInicio"]),
                    end_datetime_event=datetime.fromisoformat(event["fechaFin"]),
                )
                for event in response["listaCodigos"]
            ],
        )
