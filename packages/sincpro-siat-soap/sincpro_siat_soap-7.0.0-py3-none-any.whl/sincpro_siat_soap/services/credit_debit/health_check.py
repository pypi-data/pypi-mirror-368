from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk
from sincpro_siat_soap.global_definitions import SIAT_WSDL


class CmdCheckHealthCreditDebit(DataTransferObject):
    pass


class ResCheckHealthCreditDebit(DataTransferObject):
    is_up: bool


@siat_soap_sdk.feature(CmdCheckHealthCreditDebit)
class CheckHealthCreditDebit(Feature):

    def execute(self, dto: CmdCheckHealthCreditDebit) -> ResCheckHealthCreditDebit:
        response = self.soap_client(SIAT_WSDL.NOTA_DE_CREDITO).service.verificarComunicacion()
        return ResCheckHealthCreditDebit(is_up=response["transaccion"])
