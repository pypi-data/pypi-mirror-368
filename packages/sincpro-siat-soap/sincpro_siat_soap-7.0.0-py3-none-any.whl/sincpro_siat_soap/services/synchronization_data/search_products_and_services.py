from typing import Dict, List, TypedDict

from sincpro_siat_soap import Feature, siat_soap_sdk
from sincpro_siat_soap.global_definitions import SIAT_WSDL

from .shared import BaseRequestSynchronization, BaseSIATResponse


class CommandSearchProductsAndServices(BaseRequestSynchronization):
    pass


class ResponseSearchProductsAndServices(BaseSIATResponse):
    pass


class SoapResponse(TypedDict):
    codigoActividad: str
    codigoProducto: str
    descripcionProducto: str
    nandina: str


@siat_soap_sdk.feature(CommandSearchProductsAndServices)
class SearchProductsAndServices(Feature):

    def execute(
        self, dto: CommandSearchProductsAndServices
    ) -> ResponseSearchProductsAndServices:
        response = self.soap_client(
            SIAT_WSDL.SINCRONIZACION_DE_DATOS
        ).service.sincronizarListaProductosServicios(
            SolicitudSincronizacion={
                "codigoAmbiente": dto.environment,
                "codigoPuntoVenta": dto.point_of_sale,
                "codigoSistema": dto.system_code,
                "codigoSucursal": dto.branch_office,
                "cuis": dto.cuis,
                "nit": dto.nit,
            }
        )
        comparison_data = self.remove_duplicated_products_and_services(
            response["listaCodigos"]
        )
        return ResponseSearchProductsAndServices(
            raw_response=response, comparison_data=comparison_data
        )

    def remove_duplicated_products_and_services(
        self, code_list: List[SoapResponse]
    ) -> Dict[str, str]:
        response_dict = dict()

        for product in code_list:
            if product["codigoProducto"] not in response_dict.keys():
                # Tuple as key, because python allow
                key = f"({product['codigoProducto']}, {product['codigoActividad']})"
                response_dict[key] = (
                    f'{product["codigoActividad"]} - {product["descripcionProducto"]}'
                )

        return response_dict
