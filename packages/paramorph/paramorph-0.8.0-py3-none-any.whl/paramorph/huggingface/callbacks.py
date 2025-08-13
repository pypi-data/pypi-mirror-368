# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import math
from typing import Any

import torch.nn as nn
import torch.optim as optim
from transformers import TrainerCallback, TrainerControl, TrainerState, TrainingArguments

from paramorph import utils
from paramorph.core import Paramorph
from paramorph.paramorph_callbacks import ParamorphCallbacks
from paramorph.paramorph_config import ParamorphConfig

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class ParamorphHFCallbacks(TrainerCallback):

    LOSS = "loss"
    VALIDATION_LOSS = "eval_loss"

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
        :param callbacks: Callbacks used by Paramorph to set hyperparameters and other miscellaneous tasks.
        """

        self._step = 0
        self._current_epoch = 0

        self._training_loss_cache: list[float] = []
        self._validation_loss_cache: list[float] = []

        self.config = config
        self.paramorph = Paramorph(
            model=model,
            optimizer=optimizer,
            config=config,
            callbacks=callbacks,
        )

    def on_log(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        logs: dict[str, Any] | None = None,
        **kwargs,
    ) -> None:
        """
        :param args: TrainingArguments used by the Huggingface Trainer.
        :param state: State of the training loop in the Huggingface Trainer.
        :param control: Controller which controls the flow through the training loop in the HuggingfaceTrainer.
        :param logs: Dictionary containing the loss values and other metrics.
        :param kwargs: Other keyword arguments from the callback controller.
        """

        if logs is not None and self.LOSS in logs:
            self._training_loss_cache.append(logs[self.LOSS])

        if logs is not None and self.VALIDATION_LOSS in logs:
            self._validation_loss_cache.append(logs[self.VALIDATION_LOSS])

    def on_optimizer_step(
        self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs
    ) -> None:
        """
        :param args: TrainingArguments used by the Huggingface Trainer.
        :param state: State of the training loop in the Huggingface Trainer.
        :param control: Controller which controls the flow through the training loop in the HuggingfaceTrainer.
        :param kwargs: Other keyword arguments from the callback controller.
        """

        self._step += 1

        training_loss, self._training_loss_cache = utils.retrieve_from_loss_cache(
            self._training_loss_cache, self._step, self.config.scheduling_config.tuning_frequency
        )
        validation_loss, self._validation_loss_cache = utils.retrieve_from_loss_cache(
            self._validation_loss_cache, self._step, self.config.scheduling_config.tuning_frequency
        )

        current_epoch = int(state.epoch)

        if state.max_steps is not None and state.max_steps > 0:
            training_progress = state.global_step / state.max_steps

        else:
            training_progress = state.epoch / args.num_train_epochs

        self.paramorph.step(
            training_loss=training_loss,
            validation_loss=validation_loss,
            training_score=math.exp(training_loss) if training_loss is not None else None,
            validation_score=math.exp(validation_loss) if validation_loss is not None else None,
            training_progress=training_progress,
            current_epoch=current_epoch,
        )
