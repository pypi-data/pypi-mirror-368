# TODO: Probably remove this use only for test stand alone
"""Main source of truth for the synchronization object, this object is used to store the CUFD and the CUFD's history"""

import os
import pickle
import sys
from datetime import date, datetime, timedelta
from typing import Any, Dict, Tuple, Union

import pytz

from sincpro_siat_soap import ApplicationService, DataTransferObject, siat_soap_sdk
from sincpro_siat_soap.domain import SIATEnvironment, SIATModality
from sincpro_siat_soap.services.auth_permissions.generate_cufd import (
    CommandGenerateCUFD,
    ResponseGenerateCUFD,
)
from sincpro_siat_soap.shared.timeout import SincproTimeoutException, timeout


class HitoricalCUFD(DataTransferObject):
    control_code: str
    cufd: str
    address: str
    raw_cufd: Any


class SynchronizationObject:
    def __init__(
        self,
        nit,
        cuis,
        branch_office,
        system_code,
        point_of_sale,
        obj_binary_dir="/opt/siat/",
        modality=SIATModality.ELECTRONICA,
        environment=SIATEnvironment.TEST,
    ):
        self.nit: Union[int, str] = nit
        self.cuis: str = cuis
        self.branch_office: int = branch_office
        self.system_code: str = system_code
        self.point_of_sale: int = point_of_sale

        self.cufd_date: Union[date, None] = None
        self.cufd_response: Union[ResponseGenerateCUFD, None] = None
        self.cufd: Union[str, None] = None
        self.control_code: Union[str, None] = None
        self.address: Union[str, None] = None

        self.historical_cufd: Dict[Tuple[datetime, datetime], HitoricalCUFD] = dict()

        self.current_date: datetime = datetime.now()
        self.obj_binary_dir: str = obj_binary_dir
        self.modality: SIATModality = modality
        self.environment: SIATEnvironment = environment

        self.commands = []

    def sync(self):
        self.current_date: datetime = datetime.now()
        self.build_object_binary()

    def build_object_binary(self):
        file_name = f"{self.__class__.__name__}{self.point_of_sale}{self.branch_office}"
        siat_soap_sdk.logger.debug(
            f"Building/Serializing the SYNC OBJ in the path: [{self.obj_binary_dir}{file_name}]"
        )
        binary = pickle.dumps(self)
        with open(f"{self.obj_binary_dir}{file_name}", "wb") as file:
            file.write(binary)

    def request_new_cufd(self):
        # TODO: add timeout and if there is 3 attemps return the old
        siat_soap_sdk.logger.debug(
            f"Replacing old CUFD and generating a new one: {self.obj_binary_dir}"
        )
        self._store_old_cufd()
        command = CommandGenerateCUFD(
            nit=self.nit,
            system_code=self.system_code,
            point_of_sale=self.point_of_sale,
            branch_office=self.branch_office,
            cuis=self.cuis,
            environment=self.environment,
            billing_type=self.modality,
        )

        self.cufd_response = siat_soap_sdk(command)
        self.cufd_date = datetime.today().date()
        self.cufd = self.cufd_response.cufd
        self.control_code = self.cufd_response.control_code
        self.address = self.cufd_response.raw_response["direccion"]
        self.current_date = datetime.now()
        self.build_object_binary()
        return self.cufd_response

    def force_sync(self):
        siat_soap_sdk.logger.info(f"Force sync process")
        self.sync()

    def __str__(self):
        string_information = f"""
            point_of_sale: {self.point_of_sale}
            system_code: {self.system_code}
            nit: {self.nit}
            cuis: {self.cuis}
            branch_office: {self.branch_office}
            cufd: {self.cufd_response.cufd}    
            modality: {self.modality}
            environment: {self.environment}
        """
        return string_information

    def __repr__(self):
        return f"""
            point_of_sale: {self.point_of_sale}
            system_code: {self.system_code}
            nit: {self.nit}
            cuis: {self.cuis}
            branch_office: {self.branch_office}
            cufd: {self.cufd_response.cufd}    
            modality: {self.modality}
            environment: {self.environment}
        """

    @staticmethod
    def obj(
        binary_dir: str = "/opt/sincpro/storage",
        point_of_sale: int = 0,
        branch_office: int = 0,
    ) -> "SynchronizationObject":
        file_name = (
            f"{binary_dir}{SynchronizationObject.__name__}{point_of_sale}{branch_office}"
        )
        siat_soap_sdk.logger.debug(f"Loading sync obj from {file_name}")
        with open(f"{file_name}", "rb") as file:
            binary = file.read()
            siat_soap_sdk.logger.debug(f"Sync object Size: [{sys.getsizeof(binary)}]")
            sync_obj: SynchronizationObject = pickle.loads(binary)

            # TODO: add timeout and if there is 3 attemps return the old
            if (sync_obj.current_date + timedelta(hours=24)) < datetime.now():
                siat_soap_sdk.logger.info(
                    "Sync object out of date. building new sync obj and returning a new one "
                )
                sync_obj.request_new_cufd()
                sync_obj.sync()
                siat_soap_sdk.logger.debug(str(sync_obj))
                return sync_obj

            siat_soap_sdk.logger.debug("Returning current sync object")
            return sync_obj

    @staticmethod
    def old_obj(
        binary_dir: str = "/opt/sincpro/storage",
        point_of_sale: int = 0,
        branch_office: int = 0,
    ) -> "SynchronizationObject":
        file_name = (
            f"{binary_dir}{SynchronizationObject.__name__}{point_of_sale}{branch_office}"
        )
        siat_soap_sdk.logger.debug(f"Loading old sync obj from {file_name}")
        with open(f"{file_name}", "rb") as file:
            binary = file.read()
            siat_soap_sdk.logger.debug(f"Sync object Size: [{sys.getsizeof(binary)}]")
            sync_obj: SynchronizationObject = pickle.loads(binary)
        siat_soap_sdk.logger.debug("Returning current UNUPDATED Sync obj")
        return sync_obj

    def _store_old_cufd(self):
        siat_soap_sdk.logger.debug("Add CUFD to historical CUFDs")
        if not hasattr(self, "historical_cufd"):
            siat_soap_sdk.logger.debug("Historical CUFD is not defined, creating a new one")
            self.historical_cufd = dict()
        try:
            ttl_cufd = self.cufd_response.raw_response["fechaVigencia"]
            start_datetime = ttl_cufd - timedelta(days=1)
            end_datetime = datetime.now(tz=pytz.timezone("America/La_paz"))
            identifies = (start_datetime, end_datetime)
            self.historical_cufd[identifies] = HitoricalCUFD(
                control_code=self.control_code,
                cufd=self.cufd,
                address=self.address,
                raw_cufd=self.cufd_response,
            )
            if len(self.historical_cufd.keys()) > 30:
                list_keys = list(self.historical_cufd.keys())
                siat_soap_sdk.logger.debug(f"Removve the CUFD in dates {list_keys[0]}")
                del self.historical_cufd[list_keys[0]]

        except Exception:
            siat_soap_sdk.logger.exception(
                f"The CUFD was not stored in the historical CUFDs: {self.cufd}",
            )


class CommandCreateOrLoadSyncObj(DataTransferObject):
    nit: int | str
    cuis: str
    branch_office: int
    point_of_sale: int
    system_code: str
    path_serialized: str
    environment: SIATEnvironment
    modality: SIATModality


class ResponseCreateOrLoadSyncObj(DataTransferObject):
    sync_obj: SynchronizationObject


@siat_soap_sdk.app_service(CommandCreateOrLoadSyncObj)
class CreateOrLoadSyncObj(ApplicationService):
    def execute(self, dto: CommandCreateOrLoadSyncObj) -> ResponseCreateOrLoadSyncObj:
        try:
            timeout_value = os.getenv("SYNC_OBJ_TIMEOUT") or 10
            sync_obj_timeout_build_time = int(timeout_value)
            fn = timeout(sync_obj_timeout_build_time)
            return ResponseCreateOrLoadSyncObj(
                sync_obj=fn(SynchronizationObject.obj)(
                    dto.path_serialized,
                    dto.point_of_sale,
                    dto.branch_office,
                )
            )

        except SincproTimeoutException:
            siat_soap_sdk.logger.warning(
                "Timeout to rebuild the sync obj, returning the old one", exc_info=True
            )
            return ResponseCreateOrLoadSyncObj(
                sync_obj=SynchronizationObject.old_obj(
                    dto.path_serialized,
                    dto.point_of_sale,
                    dto.branch_office,
                )
            )

        except FileNotFoundError:
            siat_soap_sdk.logger.warning("Generating or creating a new sync object")
            sync_obj = SynchronizationObject(
                nit=dto.nit,
                cuis=dto.cuis,
                branch_office=dto.branch_office,
                system_code=dto.system_code,
                point_of_sale=dto.point_of_sale,
                obj_binary_dir=dto.path_serialized,
                environment=dto.environment,
                modality=dto.modality,
            )
            sync_obj.request_new_cufd()
            sync_obj.sync()
            siat_soap_sdk.logger.debug(str(sync_obj))
            return ResponseCreateOrLoadSyncObj(sync_obj=sync_obj)

        except Exception:
            siat_soap_sdk.logger.exception(
                "Error trying to build the sync obj",
                branch_office=dto.branch_office,
                point_of_sale=dto.point_of_sale,
                nit=dto.nit,
                cuis=dto.cuis,
                system_code=dto.system_code,
            )
