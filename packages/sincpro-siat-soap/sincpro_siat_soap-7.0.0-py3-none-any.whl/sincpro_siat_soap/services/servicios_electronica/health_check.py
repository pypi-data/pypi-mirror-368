from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.global_definitions import SIAT_WSDL


class CommandCheckHealthElectronica(DataTransferObject):
    pass


class ResponseCheckHealthElectronica(DataTransferObject):
    is_up: bool


@siat_soap_sdk.feature(CommandCheckHealthElectronica)
class CheckHealth(Feature):
    def execute(self, dto: CommandCheckHealthElectronica) -> ResponseCheckHealthElectronica:
        if self.soap_client(SIAT_WSDL.SERVICIOS_ELECTRONICA) is None:
            return ResponseCheckHealthElectronica(is_up=False)

        response = self.soap_client(
            SIAT_WSDL.SERVICIOS_ELECTRONICA
        ).service.verificarComunicacion()
        return ResponseCheckHealthElectronica(is_up=response["transaccion"])
