from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Literal, TypedDict

from sincpro_siat_soap import ApplicationService, DataTransferObject, siat_soap_sdk
from sincpro_siat_soap.domain import SIATEnvironment
from sincpro_siat_soap.services.synchronization_data import (
    BaseSIATResponse,
    CommandGetInvoiceLegends,
    CommandGetSectorDocument,
    CommandMessageServiceList,
    CommandOriginCountry,
    CommandReasonCancellation,
    CommandSearchCompanyActivities,
    CommandSearchProductsAndServices,
    CommandSignificantEvents,
    CommandTypeBilling,
    CommandTypeCI,
    CommandTypeCurrency,
    CommandTypeEmission,
    CommandTypePaymentMethod,
    CommandTypePointOfSale,
    CommandTypeRoom,
    CommandTypeSectorDocument,
    CommandTypeUOM,
)


class CommandGenerateSyncDataDict(DataTransferObject):
    nit: str | int
    cuis: str
    system_code: str
    environment: SIATEnvironment
    point_of_sale: int = 0  # DEFAULT
    branch_office: int = 0  # DEFAULT


SyncProperties = Literal[
    "actividades",
    "productos_y_servicios",
    "tipos_habitacion",
    "tipos_documentos",
    "tipos_punto_venta",
    "actividades_documento_sector",
    "leyendas",
    "eventos_significativos",
    "mensajes_servicios",
    "paises",
    "unidades_de_medida",
    "tipos_moneda",
    "tipos_facturas",
    "tipo_emision",
    "razon_cancelacion",
    "tipo_metodo_pago",
    "tipo_documento_sector",
]


class ResponseGenerateSyncDataDict(TypedDict):
    actividades: dict
    productos_y_servicios: dict
    tipos_habitacion: dict
    tipos_documentos: dict
    tipos_punto_venta: dict
    actividades_documento_sector: dict
    leyendas: dict
    eventos_significativos: dict
    mensajes_servicios: dict
    paises: dict
    unidades_de_medida: dict
    tipos_moneda: dict
    tipos_facturas: dict
    tipo_emision: dict
    razon_cancelacion: dict
    tipo_metodo_pago: dict
    tipo_documento_sector: dict


@siat_soap_sdk.app_service(CommandGenerateSyncDataDict)
class GenerateSyncDataDict(ApplicationService):

    def execute(self, dto: CommandGenerateSyncDataDict) -> ResponseGenerateSyncDataDict:
        commads = self.prepare_command(dto)
        self.response: ResponseGenerateSyncDataDict = dict()
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for c in commads:
                params = c + (self.response,)
                futures.append(executor.submit(self.thread_pool_function, *params))

            for future in as_completed(futures):
                future.result()

        return self.response

    def prepare_command(self, command: CommandGenerateSyncDataDict):
        constructor_dict = {
            "nit": command.nit,
            "cuis": command.cuis,
            "branch_office": command.branch_office,
            "system_code": command.system_code,
            "point_of_sale": command.point_of_sale,
            "environment": command.environment,
        }
        # the second file in the tuple are the keys to map in the dictionary
        commands = [
            (CommandSearchCompanyActivities(**constructor_dict), "actividades"),
            (CommandSearchProductsAndServices(**constructor_dict), "productos_y_servicios"),
            (CommandTypeRoom(**constructor_dict), "tipos_habitacion"),
            (CommandTypeCI(**constructor_dict), "tipos_documentos"),
            (CommandTypePointOfSale(**constructor_dict), "tipos_punto_venta"),
            (CommandGetSectorDocument(**constructor_dict), "actividades_documento_sector"),
            (CommandGetInvoiceLegends(**constructor_dict), "leyendas"),
            (CommandSignificantEvents(**constructor_dict), "eventos_significativos"),
            (CommandMessageServiceList(**constructor_dict), "mensajes_servicios"),
            (CommandOriginCountry(**constructor_dict), "paises"),
            (CommandTypeUOM(**constructor_dict), "unidades_de_medida"),
            (CommandTypeCurrency(**constructor_dict), "tipos_moneda"),
            (CommandTypeBilling(**constructor_dict), "tipos_facturas"),
            (CommandTypeEmission(**constructor_dict), "tipo_emision"),
            (CommandReasonCancellation(**constructor_dict), "razon_cancelacion"),
            (CommandTypePaymentMethod(**constructor_dict), "tipo_metodo_pago"),
            (CommandTypeSectorDocument(**constructor_dict), "tipo_documento_sector"),
        ]
        return commands

    def thread_pool_function(self, command: DataTransferObject, key, shared_structure_dict):
        response = self.feature_bus.execute(command, BaseSIATResponse)
        shared_structure_dict[key] = response.comparison_data
