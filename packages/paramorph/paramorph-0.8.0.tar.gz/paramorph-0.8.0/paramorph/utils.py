# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from pathlib import Path

from libinephany.pydantic_models.configs.hyperparameter_configs import HParamConfig, HParamConfigs
from libinephany.pydantic_models.states.hyperparameter_states import Hyperparameter, HyperparameterStates
from libinephany.utils import agent_utils, directory_utils, enums, exceptions
from libinephany.utils.constants import (
    AGENT_PREFIX_BETA_ONE,
    AGENT_PREFIX_BETA_TWO,
    AGENT_PREFIX_CLIPPING,
    AGENT_PREFIX_DROPOUT,
    AGENT_PREFIX_EPS,
    AGENT_PREFIX_LR,
    AGENT_PREFIX_WD,
)

from paramorph.paramorph_config import InitialHyperparametersConfig, ParamorphConfig

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class ParamorphConfigurationError(exceptions.CustomException):
    pass


# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================


def _add_new_agent_ids(current_ids: set[str], agent_prefix: str, agent_modules: dict[str, str]) -> set[str]:
    """
    :param current_ids: Current set of agent IDs.
    :param agent_prefix: Prefix given to the agent type being created.
    :param agent_modules: Dictionary mapping modules in the target NN to the type of those modules.
    :return: Updated set of agent IDs.
    """

    for module_name in agent_modules:
        current_ids.add(agent_utils.create_agent_id(layer_name=module_name, prefix=agent_prefix, suffix=None))

    return current_ids


def create_agent_ids(paramorph_config: ParamorphConfig) -> set[str]:
    """
    :param paramorph_config: ParamorphConfig used to form the agent IDs determined by which agents are active.
    :return: Set of agent IDs.
    """

    agent_modules = paramorph_config.agent_modules
    agent_ids: set[str] = set()

    if paramorph_config.agent_config.use_learning_rate_agents:
        agent_ids = _add_new_agent_ids(current_ids=agent_ids, agent_prefix=AGENT_PREFIX_LR, agent_modules=agent_modules)

    if paramorph_config.agent_config.use_weight_decay_agents:
        agent_ids = _add_new_agent_ids(current_ids=agent_ids, agent_prefix=AGENT_PREFIX_WD, agent_modules=agent_modules)

    if paramorph_config.agent_config.use_dropout_agents:
        agent_ids = _add_new_agent_ids(
            current_ids=agent_ids, agent_prefix=AGENT_PREFIX_DROPOUT, agent_modules=agent_modules
        )

    if paramorph_config.agent_config.use_grad_clip_agents:
        agent_ids = _add_new_agent_ids(
            current_ids=agent_ids, agent_prefix=AGENT_PREFIX_CLIPPING, agent_modules=agent_modules
        )

    if paramorph_config.agent_config.use_adam_beta_one_agents:
        agent_ids = _add_new_agent_ids(
            current_ids=agent_ids, agent_prefix=AGENT_PREFIX_BETA_ONE, agent_modules=agent_modules
        )

    if paramorph_config.agent_config.use_adam_beta_two_agents:
        agent_ids = _add_new_agent_ids(
            current_ids=agent_ids, agent_prefix=AGENT_PREFIX_BETA_TWO, agent_modules=agent_modules
        )

    if paramorph_config.agent_config.use_adam_eps_agents:
        agent_ids = _add_new_agent_ids(
            current_ids=agent_ids, agent_prefix=AGENT_PREFIX_EPS, agent_modules=agent_modules
        )

    return agent_ids


def create_hyperparameter_config_mapping(
    agent_ids: set[str],
    hyperparameter_configs: HParamConfigs,
) -> dict[str, HParamConfig]:
    """
    :param agent_ids: Set of agent IDs to create hyperparameter config mapping for.
    :param hyperparameter_configs: Config of all hyperparameters.
    :return: Dictionary mapping agent IDs to the HParamConfig for the hyperparameter that agent controls.
    """

    return {
        agent_id: hyperparameter_configs.get_hyperparameter_config_from_agent_type(
            agent_type=enums.AgentTypes(agent_utils.extract_agent_type(agent_id=agent_id))
        )
        for agent_id in agent_ids
    }


def create_hyperparameter_mapping(
    agent_ids: set[str], hyperparameter_states: HyperparameterStates
) -> dict[str, Hyperparameter]:
    """
    :param agent_ids: Set of agent IDs to create hyperparameter mapping for.
    :param hyperparameter_states: Object that maintains the states of all hyperparameters.
    :return: Dictionary mapping agent IDs to the hyperparameter that agent controls.
    """

    hyperparameter_mapping: dict[str, Hyperparameter] = {}

    for agent_id in agent_ids:
        parameter_group_name = agent_utils.extract_parameter_group_name(agent_id=agent_id)
        agent_type = agent_utils.extract_agent_type(agent_id=agent_id)
        group_hparams = hyperparameter_states[parameter_group_name]
        hyperparameter = group_hparams.get_hyperparameter_by_name(name=enums.AgentTypes(agent_type))

        hyperparameter_mapping[agent_id] = hyperparameter

    return hyperparameter_mapping


def set_initial_hyperparameters(
    hparam_configs: HParamConfigs,
    initial_hparams_config: InitialHyperparametersConfig,
) -> HParamConfigs:
    """
    :param hparam_configs: Config of all hyperparameters.
    :param initial_hparams_config: Config of initial hyperparameters.
    :return: Updated HParamConfigs with initial values set.
    """

    hparam_configs.learning_rate_config.initial_value = initial_hparams_config.initial_learning_rate

    if initial_hparams_config.initial_weight_decay is not None:
        hparam_configs.weight_decay_config.initial_value = initial_hparams_config.initial_weight_decay

    if initial_hparams_config.initial_dropout is not None:
        hparam_configs.dropout_config.initial_value = initial_hparams_config.initial_dropout

    if initial_hparams_config.initial_grad_norm_clip is not None:
        hparam_configs.gradient_norm_clipping_config.initial_value = initial_hparams_config.initial_grad_norm_clip

    if initial_hparams_config.initial_adam_beta_one is not None:
        hparam_configs.adam_beta_one_config.initial_value = initial_hparams_config.initial_adam_beta_one

    if initial_hparams_config.initial_adam_beta_two is not None:
        hparam_configs.adam_beta_two_config.initial_value = initial_hparams_config.initial_adam_beta_two

    if initial_hparams_config.initial_adam_eps is not None:
        hparam_configs.adam_eps_config.initial_value = initial_hparams_config.initial_adam_eps

    return hparam_configs


def retrieve_from_loss_cache(
    loss_cache: list[float], step: int, tuning_frequency: int, step_offset: int = 0
) -> tuple[float | None, list[float]]:
    """
    :param loss_cache: List of loss values to retrieve from.
    :param step: Current step.
    :param tuning_frequency: Tuning frequency.
    :param step_offset: Offset to add to the step.
    :return: Tuple containing the average loss value from the list and the updated loss cache.
    """

    if not (step + step_offset) % tuning_frequency and loss_cache:
        loss = round(sum(loss_cache) / len(loss_cache), 4)
        loss_cache = []

    else:
        loss = loss_cache[-1] if loss_cache else None

    return loss, loss_cache


def build_config(paramorph_config_path: str | Path) -> ParamorphConfig:
    """
    :param paramorph_config_path: Path to the paramorph config file.
    :return: Loaded Paramorph config object.
    """

    config_as_dict = directory_utils.load_yaml(yaml_path=paramorph_config_path)
    config = ParamorphConfig(**config_as_dict)

    return config
