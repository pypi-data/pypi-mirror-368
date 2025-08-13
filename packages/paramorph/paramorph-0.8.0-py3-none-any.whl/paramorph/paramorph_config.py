# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from libinephany.utils.enums import ModuleTypes
from loguru import logger
from pydantic import BaseModel, field_validator

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class SDKConfig(BaseModel):
    max_retries: int = 10
    backoff_factor: float = 0.5
    max_backoff: float = 15.0
    url_override: str | None = None


class SchedulingConfig(BaseModel):
    nn_family: str | None = None
    tuning_frequency: int = 100

    can_nullify_gradients: bool = True
    max_statistic_cache_size: int = 3
    tensor_stats_downsample_percentage: float = 0.01
    statistic_sample_frequency: int = 10

    log_to_wandb: bool = True
    force_wandb_log_on_all_ranks: bool = False


class AgentConfig(BaseModel):
    use_learning_rate_agents: bool = True
    use_weight_decay_agents: bool = True
    use_dropout_agents: bool = True
    use_grad_clip_agents: bool = True
    use_adam_beta_one_agents: bool = True
    use_adam_beta_two_agents: bool = True
    use_adam_eps_agents: bool = True


class InitialHyperparametersConfig(BaseModel):
    initial_learning_rate: float = 3e-5
    initial_weight_decay: float | None = 0.001
    initial_dropout: float | None = 0.1
    initial_grad_norm_clip: float | None = 1.0
    initial_adam_beta_one: float | None = 0.9
    initial_adam_beta_two: float | None = 0.999
    initial_adam_eps: float | None = 1e-8


class ParamorphConfig(BaseModel):
    sdk_config: SDKConfig = SDKConfig()
    scheduling_config: SchedulingConfig = SchedulingConfig()
    agent_config: AgentConfig = AgentConfig()
    initial_hyperparameters_config: InitialHyperparametersConfig = InitialHyperparametersConfig()

    inephany_model_id: str = "alpha-v1"
    agent_modules: dict[str, str]

    @field_validator("agent_modules", mode="before")
    def validate_modules(cls, agent_modules: dict[str, str]) -> dict[str, str]:
        """
        :param agent_modules: Dictionary mapping layer names to the type of module the layer is.
        :return: Given dictionary, unedited.
        """

        unknown_types = []

        valid_module_types = {field.value for field in ModuleTypes}

        for layer, module_type in agent_modules.items():
            if module_type not in valid_module_types:
                unknown_types.append(module_type)

        if unknown_types:
            logger.warning(
                f"Unknown module types {unknown_types}. This will not cause errors but agent modules should be "
                f"labelled correctly where possible. Valid module types are {valid_module_types}."
            )

        return agent_modules
