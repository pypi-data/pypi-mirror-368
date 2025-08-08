"""Config SDK"""

import os
from typing import Literal

from sincpro_framework.sincpro_conf import SincproConfig, build_config_obj

from sincpro_siat_soap.domain.sector_document import SIATEnvironment

DEFAULT_PRODUCTION_FILE_PATH = "/home/odoo/soap_siat.ini"
if not os.path.exists(DEFAULT_PRODUCTION_FILE_PATH):
    DEFAULT_PRODUCTION_FILE_PATH = os.path.dirname(__file__) + "/conf/soap_siat.yml"

ENV_CONFIG_PATH = os.getenv("SOAP_SIAT_CONFIG_FILE_2", None)

if ENV_CONFIG_PATH and not ENV_CONFIG_PATH.startswith("/"):
    ENV_CONFIG_PATH = os.path.dirname(__file__) + "/" + ENV_CONFIG_PATH


class SIATSoapConfigSDK(SincproConfig):
    """Configuration for SIAT Soap"""

    logging_level: Literal["INFO", "DEBUG"] = "DEBUG"
    token: str | None = None
    sign_password: str | None = None
    environment: SIATEnvironment = SIATEnvironment.TEST


settings = build_config_obj(
    SIATSoapConfigSDK,
    ENV_CONFIG_PATH or DEFAULT_PRODUCTION_FILE_PATH,
    "sincpro_soap_sdk",
)

from sincpro_framework.sincpro_logger import configure_global_logging
from sincpro_framework.sincpro_logger import settings as framework_settings

framework_settings.sincpro_framework_log_level = settings.logging_level
configure_global_logging(settings.logging_level)
