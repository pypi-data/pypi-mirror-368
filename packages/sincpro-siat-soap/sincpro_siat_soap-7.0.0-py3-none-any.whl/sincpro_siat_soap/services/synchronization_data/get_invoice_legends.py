from sincpro_siat_soap import Feature, siat_soap_sdk
from sincpro_siat_soap.global_definitions import SIAT_WSDL

from .shared import BaseRequestSynchronization, BaseSIATResponse


class CommandGetInvoiceLegends(BaseRequestSynchronization):
    pass


class ResponseGetInvoiceLegends(BaseSIATResponse):
    pass


@siat_soap_sdk.feature(CommandGetInvoiceLegends)
class GetInvoiceLegends(Feature):

    def execute(self, dto: CommandGetInvoiceLegends) -> ResponseGetInvoiceLegends:
        response = self.soap_client(
            SIAT_WSDL.SINCRONIZACION_DE_DATOS
        ).service.sincronizarListaLeyendasFactura(
            SolicitudSincronizacion={
                "codigoAmbiente": dto.environment,
                "codigoPuntoVenta": dto.point_of_sale,
                "codigoSistema": dto.system_code,
                "codigoSucursal": dto.branch_office,
                "cuis": dto.cuis,
                "nit": dto.nit,
            }
        )
        legends = {legend["descripcionLeyenda"] for legend in response["listaLeyendas"]}
        generated_ids = range(len(legends))
        dict_legends = dict(zip(map(str, generated_ids), legends))

        return ResponseGetInvoiceLegends(raw_response=response, comparison_data=dict_legends)
