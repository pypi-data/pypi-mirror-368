from collections import OrderedDict

from sincpro_siat_soap import Feature, siat_soap_sdk
from sincpro_siat_soap.global_definitions import SIAT_WSDL

from .shared import BaseRequestCommonSyncServices, BaseSIATResponse


class CommandMessageServiceList(BaseRequestCommonSyncServices):
    service: str = "sincronizarListaMensajesServicios"


class CommandSignificantEvents(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaEventosSignificativos"


class CommandReasonCancellation(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaMotivoAnulacion"


class CommandOriginCountry(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaPaisOrigen"


class CommandTypeCI(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaTipoDocumentoIdentidad"


class CommandTypeSectorDocument(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaTipoDocumentoSector"


class CommandTypeEmission(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaTipoEmision"


class CommandTypeRoom(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaTipoHabitacion"


class CommandTypePaymentMethod(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaTipoMetodoPago"


class CommandTypeCurrency(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaTipoMoneda"


class CommandTypePointOfSale(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaTipoPuntoVenta"


class CommandTypeBilling(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaTiposFactura"


class CommandTypeUOM(BaseRequestCommonSyncServices):
    service: str = "sincronizarParametricaUnidadMedida"


@siat_soap_sdk.feature(
    [
        CommandMessageServiceList,
        CommandSignificantEvents,
        CommandTypeUOM,
        CommandTypeCurrency,
        CommandOriginCountry,
        CommandTypeEmission,
        CommandReasonCancellation,
        CommandTypeBilling,
        CommandTypeCI,
        CommandTypePaymentMethod,
        CommandTypePointOfSale,
        CommandTypeRoom,
        CommandTypeSectorDocument,
    ]
)
class ExecuteCommonSyncService(Feature):
    def wsdl(self) -> str:
        return SIAT_WSDL.SINCRONIZACION_DE_DATOS

    def execute(self, param_object: BaseRequestCommonSyncServices) -> BaseSIATResponse:
        service = getattr(
            self.soap_client(SIAT_WSDL.SINCRONIZACION_DE_DATOS).service, param_object.service
        )
        response = service(
            SolicitudSincronizacion={
                "codigoAmbiente": param_object.environment,
                "codigoPuntoVenta": param_object.point_of_sale,
                "codigoSistema": param_object.system_code,
                "codigoSucursal": param_object.branch_office,
                "cuis": param_object.cuis,
                "nit": param_object.nit,
            }
        )

        response_dict = OrderedDict()
        ordered_list_by_description = sorted(
            response["listaCodigos"], key=lambda x: x["descripcion"]
        )

        for sync in ordered_list_by_description:
            if sync["codigoClasificador"] not in response_dict.keys():
                response_dict[str(sync["codigoClasificador"])] = sync["descripcion"]

        return BaseSIATResponse(raw_response=response, comparison_data=response_dict)
