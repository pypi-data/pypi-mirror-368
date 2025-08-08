from sincpro_siat_soap import Feature, siat_soap_sdk
from sincpro_siat_soap.global_definitions import SIAT_WSDL

from .shared import BaseRequestSynchronization, BaseSIATResponse


class CommandGetSectorDocument(BaseRequestSynchronization):
    pass


class ResponseGetSectorDocument(BaseSIATResponse):
    pass


@siat_soap_sdk.feature(CommandGetSectorDocument)
class GetSectorDocument(Feature):

    def execute(self, dto: CommandGetSectorDocument) -> ResponseGetSectorDocument:
        response = self.soap_client(
            SIAT_WSDL.SINCRONIZACION_DE_DATOS
        ).service.sincronizarListaActividadesDocumentoSector(
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
        for sector_document in response["listaActividadesDocumentoSector"]:
            if sector_document["codigoDocumentoSector"] not in response_dict.keys():
                response_dict[str(sector_document["codigoDocumentoSector"])] = (
                    sector_document["tipoDocumentoSector"]
                )

        return ResponseGetSectorDocument(raw_response=response, comparison_data=response_dict)
