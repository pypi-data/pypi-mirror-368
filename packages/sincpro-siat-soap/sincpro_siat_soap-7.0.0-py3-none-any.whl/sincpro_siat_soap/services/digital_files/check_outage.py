"""Check Outage Service"""

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk


class CmdCheckOutage(DataTransferObject):
    pass


class ResCheckOutage(DataTransferObject):
    is_up: bool


@siat_soap_sdk.feature(CmdCheckOutage)
class CheckOutage(Feature):

    def execute(self, dto: CmdCheckOutage) -> ResCheckOutage:
        if self.proxy_siat.is_outage_services():
            siat_soap_sdk.logger.warning("Outage detected in SIAT services")
            return ResCheckOutage(is_up=False)

        return ResCheckOutage(is_up=True)
