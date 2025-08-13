# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from libinephany.utils import import_utils

lightning = import_utils.try_import_lightning()

if lightning is not None:
    from paramorph.lightning.lightning_module import ParamorphLightningModule

else:
    ParamorphLightningModule = None  # type: ignore

__all__ = ["ParamorphLightningModule"]
