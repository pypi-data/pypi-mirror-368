from typing import Callable, Dict, List, Union

from sincpro_siat_soap.logger import logger
from sincpro_siat_soap.shared.core_exceptions import SIATException


def generate_message_based_on_list(message_list: List[Dict]) -> Union[str, None]:
    error_message = ""
    if message_list is None:
        return None

    if isinstance(message_list, list):
        for index, message in enumerate(message_list):
            codigo = message["codigo"]
            description = message["descripcion"]
            error_message = (
                f"{error_message} \n {index + 1}: Codigo [{codigo}] - {description}"
            )

    return error_message


def siat_exception_builder(raw_response: Dict) -> Callable[[], SIATException]:
    message = "Error"
    logger.exception(f"{raw_response}")
    if raw_response["mensajesList"]:
        error_message = generate_message_based_on_list(raw_response["mensajesList"])
        if error_message:
            message = f"{message}\n {error_message}"

    def call_error_fn():
        raise SIATException(message)

    return call_error_fn
