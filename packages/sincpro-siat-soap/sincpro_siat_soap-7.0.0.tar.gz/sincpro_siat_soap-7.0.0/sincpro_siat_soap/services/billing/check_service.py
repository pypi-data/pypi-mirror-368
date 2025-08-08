from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.global_definitions import SIAT_WSDL


class CommandCheckHealth(DataTransferObject):
    pass


class ResponseCheckHealth(DataTransferObject):
    is_up: bool


@siat_soap_sdk.feature(CommandCheckHealth)
class CheckHealth(Feature):

    def execute(self, dto: CommandCheckHealth) -> ResponseCheckHealth:
        response = self.soap_client(
            SIAT_WSDL.FACTURA_COMPRA_VENTA
        ).service.verificarComunicacion()
        return ResponseCheckHealth(is_up=response["transaccion"])
