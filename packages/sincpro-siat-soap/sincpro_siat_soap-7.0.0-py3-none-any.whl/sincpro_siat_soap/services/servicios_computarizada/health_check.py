from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.global_definitions import SIAT_WSDL


class CommandCheckHealthComputarizada(DataTransferObject):
    pass


class ResponseCheckHealthComputarizada(DataTransferObject):
    is_up: bool


@siat_soap_sdk.feature(CommandCheckHealthComputarizada)
class CheckHealth(Feature):

    def execute(
        self, dto: CommandCheckHealthComputarizada
    ) -> ResponseCheckHealthComputarizada:
        if self.soap_client(SIAT_WSDL.SERVICIOS_COMPUTARIZADA) is None:
            return ResponseCheckHealthComputarizada(is_up=False)

        response = self.soap_client(
            SIAT_WSDL.SERVICIOS_COMPUTARIZADA
        ).service.verificarComunicacion()
        return ResponseCheckHealthComputarizada(is_up=response["transaccion"])
