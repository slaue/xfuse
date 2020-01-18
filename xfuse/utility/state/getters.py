from typing import Any, Callable, Optional

import pyro
import torch

from .state import __MODULES, __STATE_DICT
from ...session import get


def get_module(
    name: str, module: Optional[Callable[[], torch.nn.Module]] = None
) -> torch.nn.Module:
    r"""
    Retrieves :class:`~torch.nn.Module` by name or creates it if it doesn't
    exist.

    :param name: Module name
    :param module: Module to register if it doesn't already exist. The module
    should be "quoted" by encapsulating it in a `Callable` in order to lazify
    its creation.

    :returns: The module
    :raises RuntimeError: If there is no module named `name` and `module` is
    `None`.
    """
    try:
        module_ = pyro.module(name, __MODULES[name])
    except KeyError:
        if module is None:
            raise RuntimeError(f'Module "{name}" does not exist')
        module_ = pyro.module(name, module(), update_module_params=True)
        if name in __STATE_DICT.modules:
            module_.load_state_dict(__STATE_DICT.modules[name])
        __MODULES[name] = module_
    return module_.train(not get("eval"))


def get_param(
    name: str,
    default_value: Optional[Callable[[], torch.Tensor]] = None,
    **kwargs: Any,
) -> torch.Tensor:
    r"""
    Retrieves learnable :class:`~torch.Tensor` (non-module parameter) by
    name or creates it if it doesn't exist.

    :param name: Parameter name
    :param default_value: Default value if parameter doesn't exist. The value
    should be "quoted" by encapsulating it in a `Callable` in order to lazify
    its creation.
    :param kwargs: Arguments passed to :func:`~pyro.sample`.

    :returns: The parameter
    :raises RuntimeError: If there is no parameter named `name` and
    `default_value` is `None`.
    """
    try:
        param = pyro.param(name, __STATE_DICT.params[name], **kwargs)
    except KeyError:
        if default_value is None:
            raise RuntimeError(f'Parameter "{name}" does not exist')
        param = pyro.param(name, default_value(), **kwargs)
        __STATE_DICT.params[name] = param.detach()
    if get("eval"):
        return param.detach()
    return param
