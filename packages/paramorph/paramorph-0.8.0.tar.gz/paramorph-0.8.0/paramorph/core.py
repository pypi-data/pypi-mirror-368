# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import torch.nn as nn
import torch.optim as optim
from libinephany.observations.pipeline_coordinator import ObserverPipelineCoordinator
from libinephany.observations.statistic_manager import StatisticManager
from libinephany.pydantic_models.configs.observer_config import AgentObserverConfig, ObserverConfig
from libinephany.pydantic_models.schemas.observation_models import ObservationInputs
from libinephany.pydantic_models.schemas.response_schemas import AgentScheduleResponse, ClientPolicySchemaResponse
from libinephany.pydantic_models.states.hyperparameter_states import HyperparameterStates
from libinephany.utils import agent_utils, import_utils, torch_distributed_utils
from loguru import logger

from paramorph import utils
from paramorph.paramorph_callbacks import ParamorphCallbacks
from paramorph.paramorph_config import ParamorphConfig
from paramorph.paramorph_sdk import ParamorphSDK

wandb = import_utils.try_import_wandb()

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class Paramorph:

    def __init__(
        self,
        model: nn.Module,
        optimizer: optim.Optimizer,
        config: ParamorphConfig,
        callbacks: type[ParamorphCallbacks] = ParamorphCallbacks,
    ) -> None:
        """
        :param model: Client's neural network that is being trained.
        :param optimizer: Optimizer used to train the client's network.
        :param config: Paramorph specific config options.
        :param callbacks: Type of callbacks used by Paramorph to set hyperparameters and other miscellaneous tasks.
        """

        self._step = 0
        self._agents = utils.create_agent_ids(paramorph_config=config)
        self._previous_actions: dict[str, float | int] = {}

        self.config = config
        self.force_wandb_log_on_all_ranks = self.config.scheduling_config.force_wandb_log_on_all_ranks
        self.log_to_wandb = self.config.scheduling_config.log_to_wandb

        self.model = model
        self.optimizer = optimizer

        self.paramorph_sdk = ParamorphSDK(config=self.config)
        self.policy_schema = self._get_policy_schema()

        self.callbacks = callbacks(
            model=self.model,
            optimizer=self.optimizer,
            config=self.config,
            hyperparameter_configs=self.policy_schema.hyperparameter_configs,
        )

        self.statistics_manager = StatisticManager(
            model=self.model,
            optimizer=self.optimizer,
            agent_modules=self.config.agent_modules,
            can_nullify_gradients=self.config.scheduling_config.can_nullify_gradients,
            max_statistic_cache_size=self.config.scheduling_config.max_statistic_cache_size,
            tensor_stats_downsample_percentage=self.config.scheduling_config.tensor_stats_downsample_percentage,
            statistic_sample_frequency=self.config.scheduling_config.statistic_sample_frequency,
        )
        self.observer_pipeline = ObserverPipelineCoordinator(observer_config=self._build_observer_config())
        self.observer_pipeline.infer()

        self.statistics_manager.build_trackers(required_trackers=self.observer_pipeline.get_required_trackers())

        self.hyperparameter_states = HyperparameterStates.build(
            hparam_configs=self.policy_schema.hyperparameter_configs,
            update_callbacks=self.callbacks.form_update_callbacks(),
            parameter_group_names=list(self.config.agent_modules.keys()),
        )
        self.hyperparameter_mapping = utils.create_hyperparameter_config_mapping(
            agent_ids=self._agents, hyperparameter_configs=self.policy_schema.hyperparameter_configs
        )

        self.hyperparameter_states.set_to_initial_values()

    def _create_agent_to_modules_mapping(self) -> list[tuple[AgentObserverConfig, dict[str, str | None]]]:
        """
        :return: List of tuples containing agent observer configs and a dictionary mapping agent IDs to the
        corresponding agent's parameter group.
        """

        agents_to_modules_by_type: dict[int, tuple[AgentObserverConfig, dict[str, str | None]]] = {}

        for agent_id in self._agents:
            agent_type = agent_utils.extract_agent_type(agent_id=agent_id)
            parameter_group_name = agent_utils.extract_parameter_group_name(agent_id=agent_id)
            observer_config = self.policy_schema.agent_observer_configs[agent_type]

            if id(observer_config) not in agents_to_modules_by_type:
                agents_to_modules_by_type[id(observer_config)] = (observer_config, {agent_id: parameter_group_name})

            else:
                agents_to_modules_by_type[id(observer_config)][1][agent_id] = parameter_group_name

        return list(agents_to_modules_by_type.values())

    def _build_observer_config(self) -> ObserverConfig:
        """
        :return: Config for the Observer pipeline.
        """

        return ObserverConfig(
            observation_clipping_threshold=self.policy_schema.observation_clipping_threshold,
            invalid_observation_threshold=self.policy_schema.invalid_observation_threshold,
            invalid_observation_replacement_value=self.policy_schema.invalid_observation_replacement_value,
            standardizer=self.policy_schema.standardizer,
            standardizer_arguments=self.policy_schema.standardizer_arguments,
            agent_modules=self.config.agent_modules,
            agents_to_modules_by_type=self._create_agent_to_modules_mapping(),
            optimizer_name=self.optimizer.__class__.__name__,
            nn_family_name=self.config.scheduling_config.nn_family,
        )

    def _get_policy_schema(self) -> ClientPolicySchemaResponse:
        """
        :return: The policy schema retrieved by the master rank, broadcast to all other ranks.
        """

        result: ClientPolicySchemaResponse | None = None

        if torch_distributed_utils.is_scheduler_master_rank():
            result = self.paramorph_sdk.get_schema(agent_ids=self._agents)

        result = torch_distributed_utils.broadcast_data(result)

        result.hyperparameter_configs = utils.set_initial_hyperparameters(
            hparam_configs=result.hyperparameter_configs,
            initial_hparams_config=self.config.initial_hyperparameters_config,
        )

        return result

    def _process_schedule_response(self, schedule_response: dict[str, AgentScheduleResponse]) -> dict[str, float | int]:
        """
        :param schedule_response: Dictionary mapping agent IDs to the schedule response for that agent.
        :return: Dictionary mapping agent IDs to the new value for that agent's hyperparameter.
        """

        self._previous_actions = {
            agent_id: agent_schedule_response.action for agent_id, agent_schedule_response in schedule_response.items()
        }

        return {
            agent_id: agent_schedule_response.hyperparameter_internal_value
            for agent_id, agent_schedule_response in schedule_response.items()
        }

    def set_new_hparam_values(self, new_internal_values: dict[str, float | int]) -> dict[str, float | int]:
        """
        :param new_values: Dictionary mapping agent IDs to new hyperparameter values for the hyperparameters they
        control.
        :return: Dictionary mapping agent IDs to new EXTERNAL hyperparameter values.

        :todo: Handle global agents not controlled on a per-parameter group basis.
        """

        external_values: dict[str, float | int] = {}

        for agent_id, new_hyperparameter_internal_value in new_internal_values.items():
            parameter_group_name = agent_utils.extract_parameter_group_name(agent_id=agent_id)
            agent_type = agent_utils.extract_agent_type(agent_id=agent_id)

            group_hparams = self.hyperparameter_states[parameter_group_name]
            hyperparameter = group_hparams.get_hyperparameter_by_name(name=agent_type)

            hyperparameter.internal_value = new_hyperparameter_internal_value
            external_values[agent_id] = hyperparameter.external_value

        return external_values

    def observe_and_update(self, observation_inputs: ObservationInputs) -> dict[str, float | int]:
        """
        :return: Dictionary mapping agent IDs to the new value for that agent's hyperparameter.

        Gathers tracked statistics from the client's model.
        """

        tracked_statistics = self.statistics_manager.compile()  # type: ignore
        new_hyperparameter_internal_values: dict[str, None | float | int] = {
            agent_id: None for agent_id in self._agents
        }

        if torch_distributed_utils.is_scheduler_master_rank():
            observations = self.observer_pipeline.observe(
                observation_inputs=observation_inputs,
                hyperparameter_states=self.hyperparameter_states,
                tracked_statistics=tracked_statistics,
                actions_taken=self._previous_actions,
            )

            hyperparameter_mapping = utils.create_hyperparameter_mapping(
                agent_ids=self._agents, hyperparameter_states=self.hyperparameter_states
            )

            try:
                schedule_response = self.paramorph_sdk.schedule(
                    observations=observations.agent_observations,
                    current_hyperparameters=hyperparameter_mapping,
                    hyperparameter_configs=self.hyperparameter_mapping,
                )
                new_hyperparameter_internal_values = self._process_schedule_response(
                    schedule_response=schedule_response
                )
            except Exception as e:
                logger.error(
                    f"Paramorph encountered {e.__class__.__name__}. Continuing without altering hyperparameters."
                )

        new_hyperparameter_internal_values = torch_distributed_utils.broadcast_data(
            data=new_hyperparameter_internal_values
        )

        if all(hparam is not None for hparam in new_hyperparameter_internal_values.values()):
            external_values = self.set_new_hparam_values(
                new_internal_values=new_hyperparameter_internal_values
            )  # type: ignore

        else:
            external_values = {}

        torch_distributed_utils.barrier()

        return external_values

    def log(self, new_values: dict[str, float | int]) -> None:
        """
        :param new_values: Dictionary mapping agent IDs to the new value for that agent's hyperparameter.

        Logs the hyperparameter schedules to Weights and Biases if a Weights and Biases run has been initialized.
        """

        self.callbacks.log_new_hyperparameters(new_values=new_values)

        rank_can_log = torch_distributed_utils.is_scheduler_master_rank() or self.force_wandb_log_on_all_ranks
        can_log_to_wandb = wandb is not None and wandb.run is not None and self.log_to_wandb

        if rank_can_log and can_log_to_wandb and new_values:
            wandb.log({f"Paramorph/{agent_id}": new_value for agent_id, new_value in new_values.items()})

    def step(
        self,
        training_loss: float,
        training_progress: float | None = None,
        current_epoch: int | None = None,
        validation_loss: float | None = None,
        training_score: float | None = None,
        validation_score: float | None = None,
    ) -> None:
        """
        :param training_loss: Training loss - average or not - of the client's training loop.
        :param training_progress: Progress through training as a percentage.
        :param current_epoch: Current epoch through the data the training loop is on.
        :param validation_loss: Most recent validation loss from the client's validation loop.
        :param training_score: Client's 'score' (perplexity, accuracy, etc.) on their training data.
        :param validation_score: Client's 'score' (perplexity, accuracy, etc.) on their validation data.
        """

        self.statistics_manager.on_optimizer_step(
            clipping_thresholds=self.callbacks.grad_clip_mapping,
            clipping_function=self.callbacks.clip_gradients if self.config.agent_config.use_grad_clip_agents else None,
        )
        self._step += 1

        if not self._step % self.config.scheduling_config.tuning_frequency:
            new_external_values = self.observe_and_update(
                observation_inputs=ObservationInputs(
                    training_loss=training_loss,
                    validation_loss=validation_loss,
                    training_score=training_score,
                    validation_score=validation_score,
                    training_progress=training_progress,
                    epochs_completed=current_epoch,
                )
            )
            self.log(new_values=new_external_values)
