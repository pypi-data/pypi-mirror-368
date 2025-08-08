import gzip
import itertools
import tarfile
import tempfile
import uuid
import zipfile
from typing import Any, List, Union

from pydantic import Field

from sincpro_siat_soap import DataTransferObject, Feature, siat_soap_sdk

NAME_FILE = "facturaElectronica"


class CommandCompressFile(DataTransferObject):
    string_file: Union[str, List[str]] = Field(repr=False)


class ResponseCompressFile(DataTransferObject):
    zip_file: Any = Field(repr=False)


@siat_soap_sdk.feature(CommandCompressFile)
class CompressFile(Feature):
    def execute(self, dto: CommandCompressFile) -> ResponseCompressFile:
        # binary_file = param_object.string_file.encode('utf-8')
        orignal_named_function = tempfile._get_candidate_names
        tempfile._get_candidate_names = lambda: itertools.repeat(NAME_FILE)
        response = None
        if isinstance(dto.string_file, str):
            response = CompressFile.compress_one(dto.string_file)

        if isinstance(dto.string_file, list):
            response = CompressFile.compress_many_to_targz(dto.string_file)

        tempfile._get_candidate_names = orignal_named_function
        return ResponseCompressFile(zip_file=response)

    @staticmethod
    def compress_one(string_file: str):
        with tempfile.NamedTemporaryFile(suffix=".xml", prefix="") as file:
            siat_soap_sdk.logger.debug(f"Creating XML file: {file.name}")
            siat_soap_sdk.logger.debug(f"Dumping the string into a temporary XML file")
            file.write(string_file.encode("utf-8"))
            file.seek(0)
            xml_file = file.read()

        temporary_file_for_zip = tempfile.NamedTemporaryFile(suffix=".zip", prefix="")
        siat_soap_sdk.logger.debug(f"Creating zip file: {temporary_file_for_zip.name}")

        with temporary_file_for_zip as zip_file:
            with gzip.GzipFile(fileobj=zip_file, mode="w") as compress:
                siat_soap_sdk.logger.debug("Compressing the XML file in [ZIP]")
                compress.write(xml_file)

            siat_soap_sdk.logger.debug("The compression was executed SUCCESSFULL")
            zip_file.seek(0)

            return zip_file.read()

    @staticmethod
    def compress_many(string_files: List[str]):
        with tempfile.NamedTemporaryFile(suffix=".zip", prefix="") as zipped_files:
            siat_soap_sdk.logger.debug(f"Creating zip file: {zipped_files.name}")
            with zipfile.ZipFile(
                file=zipped_files, mode="w", compression=zipfile.ZIP_DEFLATED
            ) as zip_func:
                for index, string_file in enumerate(string_files):
                    with tempfile.NamedTemporaryFile(
                        suffix=".xml", prefix=str(index)
                    ) as xml_file:
                        zip_func.writestr(xml_file.name.split("/")[-1], string_file)
            zipped_files.seek(0)
            return zipped_files.read()

    @staticmethod
    def compress_many_to_targz(string_files: List[str]):
        # Create a temporary file
        # TODO: In paralallel execution this for some reaso this once can override the another file of the thread
        with tempfile.TemporaryDirectory(
            suffix="", prefix=f"{uuid.uuid4()}", dir="/tmp"
        ) as temporary_folder:
            siat_soap_sdk.logger.debug(
                f"Creating temporary folder for invioces: {temporary_folder}"
            )

            # Creating a temporary xml file for every invoice
            xml_files = []
            for index, string_file in enumerate(string_files):
                with tempfile.NamedTemporaryFile(
                    prefix=str(index), suffix=".xml", dir=temporary_folder, delete=False
                ) as temp_xml:
                    siat_soap_sdk.logger.debug(f"Creating temporary xml: {temp_xml.name}")
                    temp_xml.write(string_file.encode("utf-8"))
                    only_name_file = temp_xml.name.split("/")[-1]
                    # Add tuple with xml information: (Absolute path, file name) ie: (/tmp/facturaElectronica/1facturaElectronica.xml, 1facturaElectronica.xml)
                    xml_files.append((temp_xml.name, only_name_file))

            path_tar_file = f"{temporary_folder}/{NAME_FILE}.tar.gz"

            with tarfile.open(path_tar_file, mode="w:gz") as compress_tar_funcs:
                for xml_file in xml_files:
                    siat_soap_sdk.logger.debug(
                        f"Adding xml file: [{xml_file[0]}-{xml_file[1]}]"
                    )
                    compress_tar_funcs.add(xml_file[0], xml_file[1])

            with open(path_tar_file, "rb") as tmp_targz_file:
                siat_soap_sdk.logger.debug(
                    f"Read/get binary from temporary file [{path_tar_file}]"
                )
                return tmp_targz_file.read()
