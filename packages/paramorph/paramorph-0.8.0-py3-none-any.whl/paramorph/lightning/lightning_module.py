# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import math
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import lightning as L
import torch
import torch.nn as nn
import torch.optim as optim
from libinephany.utils import optim_utils, torch_utils
from lightning.pytorch.utilities.types import STEP_OUTPUT, OptimizerLRScheduler

from paramorph import utils
from paramorph.core import Paramorph
from paramorph.paramorph_callbacks import ParamorphCallbacks
from paramorph.paramorph_config import ParamorphConfig

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class ParamorphLightningModule(L.LightningModule, ABC):

    SCHEDULER = "scheduler"
    INTERVAL = "interval"
    STEP = "step"
    LOSS = "loss"

    def __init__(
        self,
        paramorph_config: ParamorphConfig | str | Path,
        optimizer_type: type[optim.Optimizer] | None,
        optimizer_kwargs: dict[str, Any] | None,
        use_paramorph: bool = True,
        steps_to_verify_paramorph: int = 10,
        **kwargs,
    ) -> None:
        """
        :param paramorph_config: Configuration object for Paramorph hyperparameter tuning.
        :param optimizer_type: Type of optimizer to use for training. If None, must be overridden in subclasses.
        :param optimizer_kwargs: Keyword arguments to pass to the optimizer constructor.
        :param use_paramorph: Whether to enable Paramorph hyperparameter tuning.
        :param steps_to_verify_paramorph: Number of steps to wait before verifying Paramorph is properly configured.
        :param kwargs: Additional arguments passed to the parent LightningModule.
        """

        super().__init__(**kwargs)

        self._training_loss_cache: list[float] = []
        self._validation_loss_cache: list[float] = []
        self._previous_paramorph_step: int | None = None

        self._use_paramorph = use_paramorph
        self._steps_to_verify_paramorph = steps_to_verify_paramorph

        self.paramorph_config = self._load_paramorph_config(paramorph_config=paramorph_config)

        self.paramorph: Paramorph | None = None

        self.paramorph_optimizer: optim.Optimizer | None = None
        self.no_op_lr_scheduler: torch_utils.NoOpLRScheduler | None = None
        self.optimizer_type = optimizer_type
        self.optimizer_kwargs = optimizer_kwargs

    @property
    @abstractmethod
    def model_for_paramorph(self) -> nn.Module:
        """
        :return: The neural network model that Paramorph will tune hyperparameters for.

        This property must be implemented by subclasses to specify which model
        Paramorph should operate on.
        """

        ...

    @property
    def use_paramorph(self) -> bool:
        """
        :return: Whether Paramorph hyperparameter tuning is currently enabled.
        """

        return self._use_paramorph

    @use_paramorph.setter
    def use_paramorph(self, use_paramorph: bool) -> None:
        """
        :param use_paramorph: Whether to enable or disable Paramorph hyperparameter tuning.
        """

        self._use_paramorph = use_paramorph

    @property
    def optimizer_type_for_paramorph(self) -> type[optim.Optimizer]:
        """
        :return: The optimizer type to use for Paramorph.

        :raises ValueError: If optimizer_type is not set during initialization and not overridden.
        """

        optimizer_type = self.optimizer_type

        if self.optimizer_type is None:
            raise ValueError(
                f"Optimizer type is not set. If you do not pass an optimizer type to the "
                f"{self.__class__.__name__} on initialization, you must override this property instead."
            )

        return optimizer_type

    @property
    def paramorph_callback_override(self) -> type[ParamorphCallbacks]:
        """
        :return: The callback class to use for Paramorph operations.

        Subclasses can override this to provide custom callback behavior.
        """

        return ParamorphCallbacks

    @staticmethod
    def _load_paramorph_config(paramorph_config: ParamorphConfig | str | Path) -> ParamorphConfig:
        """
        :param paramorph_config: Either a loaded ParamorphConfig object or a path to a config file to load.
        :return: Loaded ParamorphConfig object.
        """

        if isinstance(paramorph_config, ParamorphConfig):
            return paramorph_config

        return utils.build_config(paramorph_config_path=paramorph_config)

    def configure_optimizers(self) -> OptimizerLRScheduler:
        """
        :return: Tuple containing the list of optimizers and learning rate schedulers for Lightning.

        Configures the Paramorph optimizer and scheduler, initializes the Paramorph instance,
        and returns the optimizer and scheduler configuration expected by Lightning.
        """

        self.paramorph_optimizer = optim_utils.build_optimizer(
            model=self.model_for_paramorph,
            agent_controlled_modules=self.paramorph_config.agent_modules,
            inner_model_optimizer=self.optimizer_type_for_paramorph,
            initial_learning_rate=self.paramorph_config.initial_hyperparameters_config.initial_learning_rate,
            initial_weight_decay=self.paramorph_config.initial_hyperparameters_config.initial_weight_decay,
            optimizer_kwargs=self.optimizer_kwargs or {},
        )
        self.no_op_lr_scheduler = torch_utils.NoOpLRScheduler(optimizer=self.paramorph_optimizer)

        self.paramorph = Paramorph(
            model=self.model_for_paramorph,
            optimizer=self.paramorph_optimizer,
            config=self.paramorph_config,
            callbacks=self.paramorph_callback_override,
        )

        return [self.paramorph_optimizer], [{self.SCHEDULER: self.no_op_lr_scheduler, self.INTERVAL: self.STEP}]  # type: ignore

    def validate_paramorph(self) -> None:
        """
        Validates that Paramorph is properly configured and being used correctly.

        :raises ValueError: If gradient clipping is enabled when Paramorph gradient clipping agents are active.
        :raises ParamorphConfigurationError: If on_before_zero_grad is not called within the expected number of steps.
        """

        if self.paramorph_config.agent_config.use_grad_clip_agents and self.trainer.gradient_clip_val is not None:
            raise ValueError(
                "Gradient clipping is not supported when Paramorph gradient cliping agents are active. "
                "Please set gradient_clip_val to None when Paramorph gradient cliping agents are active."
            )

        if self.global_step > self._steps_to_verify_paramorph and self._previous_paramorph_step is None:
            raise utils.ParamorphConfigurationError(
                f"on_train_batch_end was called more than {self._steps_to_verify_paramorph} times before "
                f"on_before_zero_grad was called. Please manually call on_before_zero_grad after optimizer.step but "
                f"before optimizer.zero_grad is called when automatic_optimization is False."
            )

    def on_train_batch_end(self, outputs: STEP_OUTPUT, batch: Any, batch_idx: int) -> None:
        """
        :param outputs: Output from the training step, expected to contain loss information.
        :param batch: The batch of data that was processed.
        :param batch_idx: Index of the current batch.

        Called at the end of each training batch. Caches the loss for Paramorph and validates
        the Paramorph configuration. Also prints current learning rates and weight decay values.
        """

        if self.use_paramorph and outputs is not None:
            loss = outputs[self.LOSS] if not isinstance(outputs, torch.Tensor) else outputs
            self._training_loss_cache.append(loss.detach().item())

            self.validate_paramorph()

    def on_validation_batch_end(
        self, outputs: STEP_OUTPUT, batch: Any, batch_idx: int, dataloader_idx: int = 0
    ) -> None:
        """
        :param outputs: Output from the validation step, expected to contain loss information.
        :param batch: The batch of data that was processed.
        :param batch_idx: Index of the current batch.
        :param dataloader_idx: Index of the current dataloader.
        """

        if self.use_paramorph and outputs is not None:
            loss = outputs[self.LOSS] if not isinstance(outputs, torch.Tensor) else outputs
            self._validation_loss_cache.append(loss.detach().item())

    def on_before_zero_grad(self, optimizer: optim.Optimizer) -> None:
        """
        :param optimizer: The optimizer that is about to have its gradients zeroed.

        Called before optimizer.zero_grad() is called. This is where Paramorph performs
        its hyperparameter tuning step. Validates that this method is not called multiple
        times per step and triggers Paramorph's step method with the cached loss information.

        :raises ParamorphConfigurationError: If called more than once in a single step.
        """

        if self.use_paramorph:
            if self.global_step == self._previous_paramorph_step:
                raise utils.ParamorphConfigurationError(
                    "on_before_zero_grad was called more than once in a single step. Paramorph does not yet support "
                    "multiple optimizers. Please use a single optimizer while Paramorph is active."
                )

            if not self._training_loss_cache and self.global_step == 0:
                return

            self._previous_paramorph_step = self.global_step

            training_loss, self._training_loss_cache = utils.retrieve_from_loss_cache(
                loss_cache=self._training_loss_cache,
                step=self.global_step,
                tuning_frequency=self.paramorph_config.scheduling_config.tuning_frequency,
                step_offset=1,
            )
            validation_loss, self._validation_loss_cache = utils.retrieve_from_loss_cache(
                loss_cache=self._validation_loss_cache,
                step=self.global_step,
                tuning_frequency=self.paramorph_config.scheduling_config.tuning_frequency,
                step_offset=1,
            )

            if self.trainer.max_steps is not None and self.trainer.max_steps > 0:
                training_progress = self.global_step / self.trainer.max_steps
            else:
                training_progress = self.current_epoch / self.trainer.max_epochs

            self.paramorph.step(
                training_loss=training_loss,
                validation_loss=validation_loss,
                training_score=math.exp(training_loss) if training_loss is not None else None,
                validation_score=math.exp(validation_loss) if validation_loss is not None else None,
                training_progress=training_progress,
                current_epoch=self.current_epoch,
            )
