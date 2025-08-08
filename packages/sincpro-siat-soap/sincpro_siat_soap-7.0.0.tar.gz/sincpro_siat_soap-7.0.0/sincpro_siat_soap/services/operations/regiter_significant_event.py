from datetime import datetime
from typing import Any

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.adapters.siat_exception_builder import siat_exception_builder
from sincpro_siat_soap.domain import CUFDModel, SIATEnvironment, SIATSignificantEvent
from sincpro_siat_soap.global_definitions import MAP_DESCRIPTION_SIGNIFICANT_EVENT, SIAT_WSDL
from sincpro_siat_soap.shared import core_exceptions
from sincpro_siat_soap.shared.fn_datetime import datetime_for_send_invoice


class CommandRegisterSignificantEvent(DataTransferObject):
    event_type: SIATSignificantEvent | int
    point_of_sale: int
    system_code: str
    branch_office: int
    cufd: str | CUFDModel
    cufd_event: str | CUFDModel  # Valor del CUFD que se uso en la contingencia.
    cuis: str
    nit: int | str
    start_datetime_event: datetime | str
    end_datetime_event: datetime | str
    enviroment: SIATEnvironment
    description: str | None = None


class ResponseRegisterSignificantEvent(DataTransferObject):
    raw_response: Any
    event_type: SIATSignificantEvent
    code_significant_event: int
    start_datetime_event: datetime
    end_datetime_event: datetime
    cuis: str
    cufd: str | CUFDModel
    nit: str | int
    system_code: str
    point_of_sale: int
    branch_office: int


@siat_soap_sdk.app_service(CommandRegisterSignificantEvent)
class RegisterSignificantEvent(Feature):

    def execute(
        self, dto: CommandRegisterSignificantEvent
    ) -> ResponseRegisterSignificantEvent:
        RegisterSignificantEvent.validate_cufd(dto)

        _description = dto.description
        if not _description:
            _description = MAP_DESCRIPTION_SIGNIFICANT_EVENT.get(
                dto.event_type, "Fuera de linea"
            )

        response = self.soap_client(
            SIAT_WSDL.OPERACIONES
        ).service.registroEventoSignificativo(
            SolicitudEventoSignificativo={
                "codigoAmbiente": dto.enviroment,
                "codigoMotivoEvento": dto.event_type,
                "codigoPuntoVenta": dto.point_of_sale,
                "codigoSistema": dto.system_code,
                "codigoSucursal": dto.branch_office,
                "cufd": RegisterSignificantEvent.get_CUFD_code(dto.cufd),
                "cufdEvento": RegisterSignificantEvent.get_CUFD_code(dto.cufd_event),
                "cuis": dto.cuis,
                "nit": dto.nit,
                "fechaHoraFinEvento": datetime_for_send_invoice(dto.end_datetime_event),
                "fechaHoraInicioEvento": datetime_for_send_invoice(dto.start_datetime_event),
                "descripcion": _description,
            }
        )

        if response["transaccion"] is False:
            fn_raise_exception = siat_exception_builder(response)
            fn_raise_exception()

        return ResponseRegisterSignificantEvent(
            start_datetime_event=dto.start_datetime_event,
            end_datetime_event=dto.end_datetime_event,
            event_type=dto.event_type,
            code_significant_event=response["codigoRecepcionEventoSignificativo"],
            raw_response=response,
            system_code=dto.system_code,
            point_of_sale=dto.point_of_sale,
            branch_office=dto.branch_office,
            cuis=dto.cuis,
            cufd=dto.cufd,
            nit=dto.nit,
        )

    @staticmethod
    def validate_cufd(dto: CommandRegisterSignificantEvent):
        """Validate if the CUFD model if meet the datetime"""
        if not isinstance(dto.cufd_event, CUFDModel):
            return

        if (
            dto.cufd_event.start_datetime < dto.start_datetime_event
            or dto.cufd_event.end_datetime > dto.end_datetime_event
        ):
            raise core_exceptions.SIATValidationError(
                f"El CUFD de evento acepta este rango de fechas {dto.start_datetime_event} -> {dto.end_datetime_event}. "
                f"Fecha enviada {dto.cufd_event.start_datetime} -> {dto.cufd_event.end_datetime}"
            )

    @staticmethod
    def get_CUFD_code(cufd: str | CUFDModel) -> str:
        """Legacy support without typing"""
        if isinstance(cufd, CUFDModel):
            return cufd.cufd
        return cufd
