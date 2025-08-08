from sincpro_siat_soap import Feature, siat_soap_sdk
from sincpro_siat_soap.global_definitions import SIAT_WSDL

from .shared import BaseRequestSynchronization, BaseSIATResponse


class CommandSearchCompanyActivities(BaseRequestSynchronization):
    pass


class ResponseSearchCompanyActivities(BaseSIATResponse):
    pass


@siat_soap_sdk.feature(CommandSearchCompanyActivities)
class SearchCompanyActivities(Feature):

    def execute(self, dto: CommandSearchCompanyActivities) -> ResponseSearchCompanyActivities:
        response = self.soap_client(
            SIAT_WSDL.SINCRONIZACION_DE_DATOS
        ).service.sincronizarActividades(
            SolicitudSincronizacion={
                "codigoAmbiente": dto.environment,
                "codigoPuntoVenta": dto.point_of_sale,
                "codigoSistema": dto.system_code,
                "codigoSucursal": dto.branch_office,
                "cuis": dto.cuis,
                "nit": dto.nit,
            }
        )

        response_dict = dict()

        for activity in response["listaActividades"]:
            if activity["codigoCaeb"] not in response_dict.keys():
                response_dict[activity["codigoCaeb"]] = activity["descripcion"]

        return ResponseSearchCompanyActivities(
            raw_response=response, comparison_data=response_dict
        )
