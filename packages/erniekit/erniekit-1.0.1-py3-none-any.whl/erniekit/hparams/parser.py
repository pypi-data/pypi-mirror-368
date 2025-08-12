# Copyright (c) 2025 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# The file has been adapted from hiyouga LLaMA-Factory project
# Copyright (c) 2025 LLaMA-Factory
# Licensed under the Apache License - https://github.com/hiyouga/LLaMA-Factory/blob/main/LICENSE

import json
import sys
from pathlib import Path
from typing import Any, Optional, Union

import yaml
from omegaconf import OmegaConf
from paddleformers.trainer import PdArgumentParser

from ..utils.process import is_env_enabled
from .data_args import DataArguments
from .export_args import ExportArguments
from .finetuning_args import FinetuningArguments
from .generating_args import GeneratingArguments
from .model_args import ModelArguments
from .server_args import ServerArguments

_TRAIN_ARGS = [ModelArguments, DataArguments, GeneratingArguments, FinetuningArguments]
_TRAIN_CLS = tuple[ModelArguments, DataArguments, GeneratingArguments, FinetuningArguments]
_EVAL_ARGS = [ModelArguments, DataArguments, GeneratingArguments, FinetuningArguments]
_EVAL_CLS = tuple[ModelArguments, DataArguments, GeneratingArguments, FinetuningArguments]
_EXPORT_ARGS = [ModelArguments, DataArguments, GeneratingArguments, FinetuningArguments, ExportArguments]
_EXPORT_CLS = [ModelArguments, DataArguments, GeneratingArguments, FinetuningArguments, ExportArguments]
_SERVER_ARGS = [ModelArguments, GeneratingArguments, FinetuningArguments, ServerArguments]
_SERVER_CLS = tuple[ModelArguments, GeneratingArguments, FinetuningArguments, ServerArguments]


def read_args(args: Optional[Union[dict[str, Any], list[str]]] = None) -> Union[dict[str, Any], list[str]]:
    r"""Get arguments from the command line or a config file."""
    if args is not None:
        return args

    assert len(sys.argv) > 2, "Missing configuration files."

    if sys.argv[2].endswith(".yaml") or sys.argv[2].endswith(".yml"):
        override_config = OmegaConf.from_cli(sys.argv[3:])
        dict_config = yaml.safe_load(Path(sys.argv[2]).absolute().read_text())
        return OmegaConf.to_container(OmegaConf.merge(dict_config, override_config))
    elif sys.argv[2].endswith(".json"):
        override_config = OmegaConf.from_cli(sys.argv[3:])
        dict_config = json.loads(Path(sys.argv[2]).absolute().read_text())
        return OmegaConf.to_container(OmegaConf.merge(dict_config, override_config))
    elif sys.argv[2].endswith(".py"):
        raise ValueError('Config file only supports Yaml/Json/Arguments.')
    else:
        return sys.argv[2:]


def _parse_args(
    parser: "PdArgumentParser", args: Optional[Union[dict[str, Any], list[str]]] = None, allow_extra_keys: bool = False
) -> tuple[Any]:
    """_summary_

    Args:
        parser (PdArgumentParser): _description_
        args (Optional[Union[dict[str, Any], list[str]]], optional): _description_. Defaults to None.
        allow_extra_keys (bool, optional): _description_. Defaults to False.

    Raises:
        ValueError: _description_

    Returns:
        tuple[Any]: _description_
    """

    args = read_args(args)
    if isinstance(args, dict):
        return parser.parse_dict(args)

    (*parsed_args, unknown_args) = parser.parse_args_into_dataclasses(args=args, return_remaining_strings=True)

    if unknown_args and not allow_extra_keys:
        print(parser.format_help())
        print(f"Got unknown args, potentially deprecated arguments: {unknown_args}")
        raise ValueError(f"Some specified arguments are not used by the PdArgumentParser: {unknown_args}")

    return tuple(parsed_args)


def _parse_train_args(args: Optional[Union[dict[str, Any], list[str]]] = None) -> _TRAIN_CLS:
    """_summary_

    Args:
        args (Optional[Union[dict[str, Any], list[str]]], optional): _description_. Defaults to None.

    Returns:
        _TRAIN_CLS: _description_
    """
    parser = PdArgumentParser(_TRAIN_ARGS)
    allow_extra_keys = is_env_enabled("ALLOW_EXTRA_ARGS")
    return _parse_args(parser, args, allow_extra_keys=allow_extra_keys)


def _parse_eval_args(args: Optional[Union[dict[str, Any], list[str]]] = None) -> _EVAL_CLS:
    """_summary_

    Args:
        args (Optional[Union[dict[str, Any], list[str]]], optional): _description_. Defaults to None.

    Returns:
        _EVAL_CLS: _description_
    """
    parser = PdArgumentParser(_EVAL_ARGS)
    allow_extra_keys = is_env_enabled("ALLOW_EXTRA_ARGS")
    return _parse_args(parser, args, allow_extra_keys=allow_extra_keys)


def _parse_server_args(args: Optional[Union[dict[str, Any], list[str]]] = None) -> _SERVER_CLS:
    """_summary_

    Args:
        args (Optional[Union[dict[str, Any], list[str]]], optional): _description_. Defaults to None.

    Returns:
        _SERVER_CLS: _description_
    """
    parser = PdArgumentParser(_SERVER_ARGS)
    allow_extra_keys = is_env_enabled("ALLOW_EXTRA_ARGS")
    return _parse_args(parser, args, allow_extra_keys=allow_extra_keys)


def _parse_export_args(args: Optional[Union[dict[str, Any], list[str]]] = None) -> _SERVER_CLS:
    """_summary_

    Args:
        args (Optional[Union[dict[str, Any], list[str]]], optional): _description_. Defaults to None.

    Returns:
        _SERVER_CLS: _description_
    """
    parser = PdArgumentParser(_EXPORT_ARGS)
    allow_extra_keys = is_env_enabled("ALLOW_EXTRA_ARGS")
    return _parse_args(parser, args, allow_extra_keys=allow_extra_keys)


def get_train_args(args: Optional[Union[dict[str, Any], list[str]]] = None) -> _TRAIN_CLS:
    """_summary_

    Args:
        args (Optional[Union[dict[str, Any], list[str]]], optional): _description_. Defaults to None.

    Returns:
        _TRAIN_CLS: _description_
    """
    model_args, data_args, generating_args, finetuning_args = _parse_train_args(args)
    return model_args, data_args, generating_args, finetuning_args


def get_eval_args(args: Optional[Union[dict[str, Any], list[str]]] = None) -> _EVAL_CLS:
    """_summary_

    Args:
        args (Optional[Union[dict[str, Any], list[str]]], optional): _description_. Defaults to None.

    Returns:
        _EVAL_CLS: _description_
    """
    model_args, data_args, generating_args, finetuning_args = _parse_eval_args(args)
    return model_args, data_args, generating_args, finetuning_args


def get_server_args(args: Optional[Union[dict[str, Any], list[str]]] = None) -> _SERVER_CLS:
    """_summary_

    Args:
        args (Optional[Union[dict[str, Any], list[str]]], optional): _description_. Defaults to None.

    Returns:
        _SERVER_CLS: _description_
    """
    model_args, generating_args, finetuning_args, server_args = _parse_server_args(args)
    return model_args, generating_args, finetuning_args, server_args


def get_export_args(args: Optional[Union[dict[str, Any], list[str]]] = None) -> _EXPORT_CLS:
    """_summary_

    Args:
        args (Optional[Union[dict[str, Any], list[str]]], optional): _description_. Defaults to None.

    Returns:
        _EXPORT_CLS: _description_
    """
    model_args, data_args, generating_args, finetuning_args, export_args = _parse_export_args(args)
    return model_args, data_args, generating_args, finetuning_args, export_args
