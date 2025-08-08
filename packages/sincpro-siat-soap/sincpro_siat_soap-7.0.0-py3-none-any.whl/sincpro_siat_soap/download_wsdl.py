import os

import requests

from sincpro_siat_soap import logger
from sincpro_siat_soap.global_definitions import (
    SIAT_PRODUCTION_ENDPOINTS,
    SIAT_TESTING_ENDPOINTS,
    WSDL_DIR,
    WSDL_PRODUCTION_DIR,
    WSDL_TESTING_DIR,
)


def download_wsdl():
    """
    Download WSDL files for SIAT SOAP services and save them in the resources directory.
    """

    os.makedirs(WSDL_DIR, exist_ok=True)
    os.makedirs(WSDL_TESTING_DIR, exist_ok=True)
    os.makedirs(WSDL_PRODUCTION_DIR, exist_ok=True)

    for name, url in SIAT_TESTING_ENDPOINTS.items():
        logger.info(f"Downloading WSDL for {name} from {url}")
        resp = requests.get(url)
        resp.raise_for_status()
        with open(os.path.join(WSDL_TESTING_DIR, f"{name}.wsdl"), "wb") as f:
            f.write(resp.content)

    for name, url in SIAT_PRODUCTION_ENDPOINTS.items():
        logger.info(f"Downloading WSDL for {name} from {url}")
        resp = requests.get(url)
        resp.raise_for_status()
        with open(os.path.join(WSDL_PRODUCTION_DIR, f"{name}.wsdl"), "wb") as f:
            f.write(resp.content)


if __name__ == "__main__":
    download_wsdl()
    logger.info("WSDL files downloaded successfully.")
