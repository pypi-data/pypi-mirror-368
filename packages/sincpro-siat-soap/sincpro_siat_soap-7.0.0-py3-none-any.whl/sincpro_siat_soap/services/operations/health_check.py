from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.global_definitions import SIAT_WSDL


class CmdCheckHealthOperations(DataTransferObject):
    pass


class ResCheckHealthOperations(DataTransferObject):
    is_up: bool


@siat_soap_sdk.feature(CmdCheckHealthOperations)
class CheckHealth(Feature):

    def execute(self, dto: CmdCheckHealthOperations) -> ResCheckHealthOperations:
        response = self.soap_client(SIAT_WSDL.OPERACIONES).service.verificarComunicacion()
        return ResCheckHealthOperations(is_up=response["transaccion"])
