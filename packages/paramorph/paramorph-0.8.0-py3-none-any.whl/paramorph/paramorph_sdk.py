# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import os
import secrets
from typing import Any, Callable

import requests
from libinephany.pydantic_models.configs.hyperparameter_configs import HParamConfig
from libinephany.pydantic_models.schemas.request_schemas import (
    AgentScheduleRequest,
    ClientPolicySchemaRequest,
    ClientScheduleRequest,
)
from libinephany.pydantic_models.schemas.response_schemas import (
    AgentScheduleResponse,
    ClientPolicySchemaResponse,
    ClientScheduleResponse,
)
from libinephany.pydantic_models.states.hyperparameter_states import Hyperparameter
from libinephany.utils import agent_utils
from libinephany.utils.constants import KEY_HEADER_CASE
from libinephany.utils.transforms import transform_and_sort_hparam_values
from libinephany.web_apps.web_app_utils import SCHEDULE_ENDPOINT, SCHEMA_ENDPOINT
from loguru import logger
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from paramorph.constants import HTTPS, PARAMORPH_URL, RETRY_FORCE_LIST
from paramorph.paramorph_config import ParamorphConfig

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class ParamorphSDK:

    API_KEY_ENV_VAR = "PARAMORPH_API_KEY"

    def __init__(self, config: ParamorphConfig) -> None:
        """
        :param config: Paramorph specific config options.
        """

        self.config = config
        self.sdk_config = config.sdk_config

        self._session = requests.Session()
        self._run_slug = secrets.randbits(16)

        self._base_url = PARAMORPH_URL if self.sdk_config.url_override is None else self.sdk_config.url_override
        self._schedule_url = self._form_url(self._base_url, SCHEDULE_ENDPOINT)
        self._schema_url = self._form_url(self._base_url, SCHEMA_ENDPOINT)

        self._add_backoff_adapter()

    @staticmethod
    def _extract_agent_types(agent_ids: set[str] | list[str]) -> list[str]:
        """
        :param agent_ids: List of agent IDs to extract the various types from.
        :return: List of all agent types in the given list of agent IDs.
        """

        return list(set([agent_utils.extract_agent_type(agent_id=agent_id) for agent_id in agent_ids]))

    @staticmethod
    def _send_request(
        method: Callable[..., requests.Response], url: str, json: dict[str, Any], headers: dict[str, Any]
    ) -> dict[str, Any]:
        """
        :param method: Method of the internal session object to call in order to conduct the request.
        :param url: URL to send the request to.
        :param json: JSON to send in the request.
        :param headers: Dictionary of HTTP headers.
        :return: JSON response from the API.
        """

        response = method(url=url, json=json, headers=headers)
        response.raise_for_status()

        return response.json()

    @staticmethod
    def _form_url(base_url: str, endpoint: str) -> str:
        """
        :param base_url: Base URL to send the request to.
        :param endpoint: Endpoint to send the request to.
        :return: Formed URL.
        """

        if base_url.endswith("/"):
            base_url = base_url[:-1]

        if endpoint.startswith("/"):
            endpoint = endpoint[1:]

        if endpoint.endswith("/"):
            endpoint = endpoint[:-1]

        return f"{base_url}/{endpoint}"

    def _add_backoff_adapter(self) -> None:
        """
        Adds an exponential backoff adapter to retry requests that fail with the specified status codes.
        """

        retries = Retry(
            total=self.sdk_config.max_retries,
            backoff_factor=self.sdk_config.backoff_factor,
            backoff_max=self.sdk_config.max_backoff,
            status_forcelist=RETRY_FORCE_LIST,
        )

        adapter = HTTPAdapter(max_retries=retries)

        self._session.mount(prefix=HTTPS, adapter=adapter)

    def _create_schedule_request(
        self,
        observations: dict[str, list[int | float]],
        current_hyperparameters: dict[str, Hyperparameter],
        hyperparameter_configs: dict[str, HParamConfig],
    ) -> ClientScheduleRequest:
        """
        :param observations: Dictionary mapping agent IDs to the corresponding agent's observation vector.
        :param current_hyperparameters: Dictionary mapping agent IDs to the corresponding agent's hyperparameter.
        :param hyperparameter_configs: Dictionary mapping agent IDs to the hyperparameter config for the type of
        hyperparameter they control.
        :return: Formed client schedule request.
        """

        agent_schedule_requests = {}

        for agent_id, observation_vector in observations.items():
            agent_type = agent_utils.extract_agent_type(agent_id=agent_id)

            current_hyperparameter = current_hyperparameters[agent_id]
            hparam_config = hyperparameter_configs[agent_id]

            min_hparam_internal_value, max_hparam_internal_value = transform_and_sort_hparam_values(
                current_hyperparameter.transform.to_internal,
                hparam_config.min_hparam_value,
                hparam_config.max_hparam_value,
            )
            agent_schedule_requests[agent_id] = AgentScheduleRequest(
                observations=observation_vector,
                agent_type=agent_type,
                hyperparameter_internal_value=current_hyperparameter.internal_value,
                max_hyperparameter_internal_value=max_hparam_internal_value,
                min_hyperparameter_internal_value=min_hparam_internal_value,
                transform_type=current_hyperparameter.transform_type.value,
            )

        return ClientScheduleRequest(
            run_slug=str(self._run_slug),
            inephany_model_id=self.config.inephany_model_id,
            observations=agent_schedule_requests,
        )

    def _get_auth_headers(self) -> dict[str, Any]:
        """
        :return: HTTP headers containing the API auth key.
        """

        api_key = os.environ.get(self.API_KEY_ENV_VAR, None)

        if api_key is None:
            raise KeyError(f"No API key found. API key must be in environment variable {self.API_KEY_ENV_VAR}.")

        return {KEY_HEADER_CASE: api_key}

    def get_schema(self, agent_ids: set[str] | list[str]) -> ClientPolicySchemaResponse:
        """
        :param agent_ids: List of agent IDs to extract agent types from and get agent observer configs for.
        :return: ClientPolicySchemaResponse from the API containing details on hyperparameter configuration,
        observer configuration and other miscellaneous items.
        """

        schema_request = ClientPolicySchemaRequest(
            inephany_model_id=self.config.inephany_model_id,
            agent_types=self._extract_agent_types(agent_ids=agent_ids),
        )

        schema_as_json = self._send_request(
            method=self._session.post,
            url=self._schema_url,
            json=schema_request.model_dump(),
            headers=self._get_auth_headers(),
        )

        as_model = ClientPolicySchemaResponse(**schema_as_json)

        return as_model

    def schedule(
        self,
        observations: dict[str, list[int | float]],
        current_hyperparameters: dict[str, Hyperparameter],
        hyperparameter_configs: dict[str, HParamConfig],
    ) -> dict[str, AgentScheduleResponse]:
        """
        :param observations: Dictionary mapping agent IDs to the corresponding agent's observation vector.
        :param current_hyperparameters: Dictionary mapping agent IDs to the corresponding agent's hyperparameter.
        :param hyperparameter_configs: Dictionary mapping agent IDs to the hyperparameter config for the type of
        hyperparameter they control.
        """

        logger.debug("Sending request to Paramorph API...")

        schedule_request = self._create_schedule_request(
            observations=observations,
            current_hyperparameters=current_hyperparameters,
            hyperparameter_configs=hyperparameter_configs,
        )

        result = self._send_request(
            method=self._session.post,
            url=self._schedule_url,
            json=schedule_request.model_dump(),
            headers=self._get_auth_headers(),
        )

        as_model = ClientScheduleResponse(**result)

        logger.debug(
            f"Finished schedule request after "
            f"{round(as_model.response_time, 3) if as_model.response_time is not None else None} seconds."
        )

        return as_model.actions
