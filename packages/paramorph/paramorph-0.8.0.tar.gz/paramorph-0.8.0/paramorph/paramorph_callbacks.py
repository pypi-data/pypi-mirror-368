# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from collections import defaultdict
from typing import Any, DefaultDict

import torch
import torch.nn as nn
import torch.optim as optim
from libinephany.pydantic_models.configs.hyperparameter_configs import HParamConfigs
from libinephany.pydantic_models.states.hyperparameter_states import UpdateCallbacks
from libinephany.utils import dropout_utils
from libinephany.utils.constants import SCHEDULER_GROUP_NAME
from libinephany.utils.dropout_utils import DropoutLayer

from paramorph.paramorph_config import ParamorphConfig

# ======================================================================================================================
#
# CONSTANTS
#
# ======================================================================================================================

LEARNING_RATE_KEY = "lr"
WEIGHT_DECAY_KEY = "weight_decay"
ADAM_BETAS_KEY = "betas"
ADAM_EPS_KEY = "eps"
SGD_MOMENTUM_KEY = "momentum"

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class ParamorphCallbacks:
    """
    :todo: Add optimizer type checks to adam-specific and sgd-specific hparams with log once warnings and ability to
    :todo: override.
    """

    def __init__(
        self,
        model: nn.Module,
        optimizer: optim.Optimizer,
        config: ParamorphConfig,
        hyperparameter_configs: HParamConfigs,
    ):
        """
        :param model: Client's neural network that is being trained.
        :param optimizer: Optimizer used to train the client's network.
        :param config: Paramorph specific config options.
        :param hyperparameter_configs: Hyperparameter configs from the policy schema.
        """

        self.model = model
        self.optimizer = optimizer
        self.config = config
        self.hyperparameter_configs = hyperparameter_configs

        self.dropout_mapping = self.create_dropout_mapping()
        self.grad_clip_mapping: DefaultDict[str, float] = defaultdict(
            lambda: self.hyperparameter_configs.gradient_norm_clipping_config.initial_value
        )

    def clip_gradients(self, parameters: list[torch.Tensor], clipping_threshold: float) -> None:
        """
        :param parameters: List of parameters to clip the gradient norms of.
        :param clipping_threshold: Clipping threshold for to use on these parameters.
        """

        torch.nn.utils.clip_grad_norm_(parameters, clipping_threshold)

    def create_dropout_mapping(self) -> dict[str, list[nn.Module | DropoutLayer]]:
        """
        :return: Dropout mapping which maps parameter group names to the list of dropout layers present in that
        parameter group.
        """

        return dropout_utils.create_torch_dropout_mapping(
            model=self.model, parameter_group_names=list(self.config.agent_modules.keys())
        )

    def get_parameter_group(self, parameter_group_name: str) -> dict[str, Any]:
        """
        :param parameter_group_name: Name of the parameter group to retrieve. The group's name should be stored under
        SCHEDULER_GROUP_NAME in the parameter group dictionary.

        :return: Requested parameter group.

        :raises KeyError: If the parameter group with the given name cannot be found.
        """

        for parameter_group in self.optimizer.param_groups:
            group_name = parameter_group.get(SCHEDULER_GROUP_NAME, None)

            if group_name is not None and group_name == parameter_group_name:
                return parameter_group

        raise KeyError(f"Unknown parameter group {parameter_group_name}.")

    def set_learning_rate(self, parameter_group_name: str, value: float) -> None:
        """
        :param parameter_group_name: Name of the parameter group whose hyperparameter is being changed.
        :param value: New value to set the hyperparameter to.
        """

        parameter_group = self.get_parameter_group(parameter_group_name=parameter_group_name)

        parameter_group[LEARNING_RATE_KEY] = value

    def set_weight_decay(self, parameter_group_name: str, value: float) -> None:
        """
        :param parameter_group_name: Name of the parameter group whose hyperparameter is being changed.
        :param value: New value to set the hyperparameter to.
        """

        parameter_group = self.get_parameter_group(parameter_group_name=parameter_group_name)

        parameter_group[WEIGHT_DECAY_KEY] = value

    def set_dropout(self, parameter_group_name: str, value: float) -> None:
        """
        :param parameter_group_name: Name of the parameter group whose hyperparameter is being changed.
        :param value: New value to set the hyperparameter to.
        """

        dropout_utils.set_torch_dropout(
            dropout_layer_mapping=self.dropout_mapping, parameter_group_name=parameter_group_name, dropout=value
        )

    def set_grad_clip_norm(self, parameter_group_name: str, value: float) -> None:
        """
        :param parameter_group_name: Name of the parameter group whose hyperparameter is being changed.
        :param value: New value to set the hyperparameter to.
        """

        self.grad_clip_mapping[parameter_group_name] = value

    def set_adam_beta_one(self, parameter_group_name: str, value: float) -> None:
        """
        :param parameter_group_name: Name of the parameter group whose hyperparameter is being changed.
        :param value: New value to set the hyperparameter to.
        """

        parameter_group = self.get_parameter_group(parameter_group_name=parameter_group_name)

        beta_two = parameter_group[ADAM_BETAS_KEY][1]
        parameter_group[ADAM_BETAS_KEY] = (value, beta_two)

    def set_adam_beta_two(self, parameter_group_name: str, value: float) -> None:
        """
        :param parameter_group_name: Name of the parameter group whose hyperparameter is being changed.
        :param value: New value to set the hyperparameter to.
        """

        parameter_group = self.get_parameter_group(parameter_group_name=parameter_group_name)

        beta_one = parameter_group[ADAM_BETAS_KEY][0]
        parameter_group[ADAM_BETAS_KEY] = (beta_one, value)

    def set_adam_eps(self, parameter_group_name: str, value: float) -> None:
        """
        :param parameter_group_name: Name of the parameter group whose hyperparameter is being changed.
        :param value: New value to set the hyperparameter to.
        """

        parameter_group = self.get_parameter_group(parameter_group_name=parameter_group_name)

        parameter_group[ADAM_EPS_KEY] = value

    def set_sgd_momentum(self, parameter_group_name: str, value: float) -> None:
        """
        :param parameter_group_name: Name of the parameter group whose hyperparameter is being changed.
        :param value: New value to set the hyperparameter to.
        """

        parameter_group = self.get_parameter_group(parameter_group_name=parameter_group_name)

        parameter_group[SGD_MOMENTUM_KEY] = value

    def form_update_callbacks(self) -> UpdateCallbacks:
        """
        :return: Created UpdateCallbacks object used by the HyperparameterStates within the scheduler to know what
        method to call when setting a particular hyperparameter.
        """

        return UpdateCallbacks(
            learning_rate=self.set_learning_rate,
            weight_decay=self.set_weight_decay,
            dropout=self.set_dropout,
            grad_norm_clip=self.set_grad_clip_norm,
            adam_beta_one=self.set_adam_beta_one,
            adam_beta_two=self.set_adam_beta_two,
            adam_eps=self.set_adam_eps,
            sgd_momentum=self.set_sgd_momentum,
            batch_size=None,
            epochs=None,
            gradient_accumulation=None,
        )

    def log_new_hyperparameters(self, new_values: dict[str, float | int]) -> None:
        """
        :param new_values: Dictionary mapping agent IDs to the new value for that agent's hyperparameter.
        """

        pass
