# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import os
from http import HTTPStatus

# ======================================================================================================================
#
# CONSTANTS
#
# ======================================================================================================================

PARAMORPH_URL_EVAR = "PARAMORPH_URL"
PARAMORPH_URL = os.environ.get(PARAMORPH_URL_EVAR, "https://api.paramorph.ai")

RETRY_FORCE_LIST = (
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.BAD_GATEWAY,
    HTTPStatus.SERVICE_UNAVAILABLE,
    HTTPStatus.GATEWAY_TIMEOUT,
    HTTPStatus.TOO_MANY_REQUESTS,
    HTTPStatus.REQUEST_TIMEOUT,
)
HTTPS = "https://"
