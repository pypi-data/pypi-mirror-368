# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================
# type: ignore

from pathlib import Path

import torch.nn as nn
import torch.optim as optim
from libinephany.utils import optim_utils, torch_utils

from paramorph.core import Paramorph
from paramorph.huggingface.callbacks import ParamorphHFCallbacks
from paramorph.huggingface.trainer import ParamorphHFTrainer
from paramorph.lightning import ParamorphLightningModule
from paramorph.paramorph_callbacks import ParamorphCallbacks
from paramorph.utils import build_config

# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================


def build(
    model: nn.Module,
    optimizer_type: type[optim.Optimizer],
    paramorph_config_path: str | Path,
    paramorph_callback_override: type[ParamorphCallbacks] = ParamorphCallbacks,
    **optimizer_kwargs,
) -> tuple[optim.Optimizer, Paramorph]:
    """
    :param model: Model the client is training.
    :param optimizer_type: Type of optimizer the client is using.
    :param paramorph_config_path: Path to the paramorph config file.
    :param paramorph_callback_override: ParamorphCallbacks class to use during operation. A client can subclass
    ParamorphCallbacks to override certain behaviours as necessary.
    :param optimizer_kwargs: Keyword arguments for the given optimizer.
    :return: Tuple of:
        - Optimizer built for operation under Paramorph.
        - Paramorph object which schedules hyperparameters.
    """

    config = build_config(paramorph_config_path=paramorph_config_path)
    optimizer = optim_utils.build_optimizer(
        model=model,
        agent_controlled_modules=config.agent_modules,
        inner_model_optimizer=optimizer_type,
        initial_learning_rate=config.initial_hyperparameters_config.initial_learning_rate,
        initial_weight_decay=config.initial_hyperparameters_config.initial_weight_decay,
        optimizer_kwargs=optimizer_kwargs,
    )

    paramorph = Paramorph(model=model, optimizer=optimizer, config=config, callbacks=paramorph_callback_override)

    return optimizer, paramorph


def build_for_huggingface(
    model: nn.Module,
    optimizer_type: type[optim.Optimizer],
    paramorph_config_path: str | Path,
    paramorph_callback_override: type[ParamorphCallbacks] = ParamorphCallbacks,
    **optimizer_kwargs,
) -> tuple[ParamorphHFCallbacks, optim.Optimizer, torch_utils.NoOpLRScheduler, type[ParamorphHFTrainer]]:
    """
    :param model: Model the client is training.
    :param optimizer_type: Type of optimizer the client is using.
    :param paramorph_config_path: Path to the paramorph config file.
    :param paramorph_callback_override: ParamorphCallbacks class to use during operation. A client can subclass
    ParamorphCallbacks to override certain behaviours as necessary.
    :param optimizer_kwargs: Keyword arguments for the given optimizer.
    :return: Tuple of:
        - Formed callback to use in the Huggingface trainer.
        - Optimizer built for operation under Paramorph.
        - No Op learning rate scheduler to use with the HF trainer.
        - Paramorph Huggingface trainer. It is a minimal subclass which alters the trainer so that certain metrics
          and behaviours can be captured. A client can choose not to use it so long as their Huggingface trainer
          is modified to do the same things as the Paramorph version.
    """

    config = build_config(paramorph_config_path=paramorph_config_path)
    optimizer = optim_utils.build_optimizer(
        model=model,
        agent_controlled_modules=config.agent_modules,
        inner_model_optimizer=optimizer_type,
        initial_learning_rate=config.initial_hyperparameters_config.initial_learning_rate,
        initial_weight_decay=config.initial_hyperparameters_config.initial_weight_decay,
        optimizer_kwargs=optimizer_kwargs,
    )

    hf_callback = ParamorphHFCallbacks(
        model=model, optimizer=optimizer, config=config, callbacks=paramorph_callback_override
    )

    lr_scheduler = torch_utils.NoOpLRScheduler(optimizer=optimizer)

    return hf_callback, optimizer, lr_scheduler, ParamorphHFTrainer


def build_for_lightning(
    lightning_module: type[ParamorphLightningModule],
    paramorph_config_path: str | Path,
    optimizer_type: type[optim.Optimizer],
    use_paramorph: bool = True,
    **optimizer_kwargs,
) -> ParamorphLightningModule:
    """
    :param lightning_module: Type of Lightning module to use for training. Should be a subclass
    of ParamorphLightningModule.
    :param paramorph_config_path: Path to the paramorph config file.
    :param optimizer_type: Type of optimizer the client is using.
    :param use_paramorph: Whether to use Paramorph hyperparameter tuning.
    :param optimizer_kwargs: Keyword arguments for the given optimizer.
    :return: ParamorphLightningModule instance.
    """

    if ParamorphLightningModule is None:
        raise ImportError(
            "Lightning is not installed. Please ensure Paramorph dependencies have "
            "been correctly installed with `python -m pip install paramorph[lightning]`."
        )

    return lightning_module(
        paramorph_config=paramorph_config_path,
        optimizer_type=optimizer_type,
        optimizer_kwargs=optimizer_kwargs,
        use_paramorph=use_paramorph,
    )
