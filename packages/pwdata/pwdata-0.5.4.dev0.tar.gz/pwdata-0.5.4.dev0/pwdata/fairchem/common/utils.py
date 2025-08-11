"""
Copyright (c) Meta, Inc. and its affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from __future__ import annotations

import ast
import collections
import copy
import errno
import importlib
import itertools
import json
import logging
import os
import subprocess
import sys
import time
from bisect import bisect
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
from itertools import product
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

# copied from https://stackoverflow.com/questions/33490870/parsing-yaml-in-python-detect-duplicated-keys
# prevents loading YAMLS where keys have been overwritten
class UniqueKeyLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = set()
        for key_node, _ in node.value:
            each_key = self.construct_object(key_node, deep=deep)
            if each_key in mapping:
                raise ValueError(
                    f"Duplicate Key: {each_key!r} is found in YAML File.\n"
                    f"Error File location: {key_node.end_mark}"
                )
            mapping.add(each_key)
        return super().construct_mapping(node, deep)


def pyg2_data_transform(data):
    """
    if we're on the new pyg (2.0 or later) and if the Data stored is in older format
    we need to convert the data to the new format
    """
    return data


multitask_required_keys = {
    "tasks",
    "datasets",
    "combined_dataset",
    "model",
    "optim",
}

def warmup_lr_lambda(current_step: int, optim_config):
    """Returns a learning rate multiplier.
    Till `warmup_steps`, learning rate linearly increases to `initial_lr`,
    and then gets multiplied by `lr_gamma` every time a milestone is crossed.
    """

    # keep this block for older configs that have warmup_epochs instead of warmup_steps
    # and lr_milestones are defined in epochs
    if (
        any(x < 100 for x in optim_config["lr_milestones"])
        or "warmup_epochs" in optim_config
    ):
        raise Exception(
            "ConfigError: please define lr_milestones in steps not epochs and define warmup_steps instead of warmup_epochs"
        )

    if current_step <= optim_config["warmup_steps"]:
        alpha = current_step / float(optim_config["warmup_steps"])
        return optim_config["warmup_factor"] * (1.0 - alpha) + alpha
    else:
        idx = bisect(optim_config["lr_milestones"], current_step)
        return pow(optim_config["lr_gamma"], idx)


def conditional_grad(dec):
    "Decorator to enable/disable grad depending on whether force/energy predictions are being made"

    # Adapted from https://stackoverflow.com/questions/60907323/accessing-class-property-as-decorator-argument
    def decorator(func):
        @wraps(func)
        def cls_method(self, *args, **kwargs):
            f = func
            if self.regress_forces and not getattr(self, "direct_forces", 0):
                f = dec(func)
            return f(self, *args, **kwargs)

        return cls_method

    return decorator

def collate(data_list):
    keys = data_list[0].keys
    data = data_list[0].__class__()

    for key in keys:
        data[key] = []
    slices = {key: [0] for key in keys}

    for item, key in product(data_list, keys):
        data[key].append(item[key])
        if isinstance(item[key], (int, float)):
            s = slices[key][-1] + 1
        else:
            raise ValueError("Unsupported attribute type")
        slices[key].append(s)

    if hasattr(data_list[0], "__num_nodes__"):
        data.__num_nodes__ = []
        for item in data_list:
            data.__num_nodes__.append(item.num_nodes)

    for key in keys:
        pass
    return data, slices


def _import_local_file(path: Path, *, project_root: Path) -> None:
    """
    Imports a Python file as a module

    :param path: The path to the file to import
    :type path: Path
    :param project_root: The root directory of the project (i.e., the "ocp" folder)
    :type project_root: Path
    """

    path = path.absolute()
    project_root = project_root.parent.absolute()

    module_name = ".".join(
        path.absolute().relative_to(project_root.absolute()).with_suffix("").parts
    )
    logging.debug(f"Resolved module name of {path} to {module_name}")
    importlib.import_module(module_name)


def setup_experimental_imports(project_root: Path) -> None:
    """
    Import selected directories of modules from the "experimental" subdirectory.

    If a file named ".include" is present in the "experimental" subdirectory,
    this will be read as a list of experimental subdirectories whose module
    (including in any subsubdirectories) should be imported.

    :param project_root: The root directory of the project (i.e., the "ocp" folder)
    """
    experimental_dir = (project_root / "experimental").absolute()
    if not experimental_dir.exists() or not experimental_dir.is_dir():
        return

    experimental_files = []
    include_file = experimental_dir / ".include"

    if include_file.exists():
        with open(include_file) as f:
            include_dirs = [line.rstrip("\n") for line in f.readlines() if line.strip()]

        for inc_dir in include_dirs:
            experimental_files.extend(
                f.absolute() for f in (experimental_dir / inc_dir).rglob("*.py")
            )

    for f in experimental_files:
        _import_local_file(f, project_root=project_root)


def _get_project_root() -> Path:
    """
    Gets the root folder of the project (the "ocp" folder)
    :return: The absolute path to the project root.
    """
    from fairchem.core.common.registry import registry

    # Automatically load all of the modules, so that
    # they register with registry
    root_folder = registry.get("fairchem_core_root", no_warning=True)

    if root_folder is not None:
        assert isinstance(root_folder, str), "fairchem_core_root must be a string"
        root_folder = Path(root_folder).resolve().absolute()
        assert root_folder.exists(), f"{root_folder} does not exist"
        assert root_folder.is_dir(), f"{root_folder} is not a directory"
    else:
        root_folder = Path(__file__).resolve().absolute().parent.parent

    # root_folder is the "ocpmodes" folder, so we need to go up one more level
    return root_folder.parent


# Copied from https://github.com/facebookresearch/mmf/blob/master/mmf/utils/env.py#L89.
def setup_imports(config: dict | None = None) -> None:
    from fairchem.core.common.registry import registry

    skip_experimental_imports = (config or {}).get("skip_experimental_imports", False)

    # First, check if imports are already setup
    has_already_setup = registry.get("imports_setup", no_warning=True)
    if has_already_setup:
        return

    try:
        project_root = _get_project_root()
        logging.info(f"Project root: {project_root}")
        importlib.import_module("fairchem.core.common.logger")

        import_keys = ["trainers", "datasets", "models", "tasks"]
        for key in import_keys:
            for f in (project_root / "core" / key).rglob("*.py"):
                _import_local_file(f, project_root=project_root)

        if not skip_experimental_imports:
            setup_experimental_imports(project_root)
    finally:
        registry.register("imports_setup", True)


def dict_set_recursively(dictionary, key_sequence, val) -> None:
    top_key = key_sequence.pop(0)
    if len(key_sequence) == 0:
        dictionary[top_key] = val
    else:
        if top_key not in dictionary:
            dictionary[top_key] = {}
        dict_set_recursively(dictionary[top_key], key_sequence, val)


def parse_value(value):
    """
    Parse string as Python literal if possible and fallback to string.
    """
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        # Use as string if nothing else worked
        return value


def create_dict_from_args(args: list, sep: str = "."):
    """
    Create a (nested) dictionary from console arguments.
    Keys in different dictionary levels are separated by sep.
    """
    return_dict = {}
    for arg in args:
        keys_concat, val = arg.removeprefix("--").split("=")
        val = parse_value(val)
        key_sequence = keys_concat.split(sep)
        dict_set_recursively(return_dict, key_sequence, val)
    return return_dict


# given a filename and set of paths , return the full file path
def find_relative_file_in_paths(filename, include_paths):
    if os.path.exists(filename):
        return filename
    for path in include_paths:
        include_filename = os.path.join(path, filename)
        if os.path.exists(include_filename):
            return include_filename
    raise ValueError(f"Cannot find include YML {filename}")


def load_config(
    path: str,
    files_previously_included: list | None = None,
    include_paths: list | None = None,
):
    """
    Load a given config with any defined imports

    When imports are present this is a recursive function called on imports.
    To prevent any cyclic imports we keep track of already imported yml files
    using files_previously_included
    """
    if include_paths is None:
        include_paths = []
    if files_previously_included is None:
        files_previously_included = []
    path = Path(path)
    if path in files_previously_included:
        raise ValueError(
            f"Cyclic config include detected. {path} included in sequence {files_previously_included}."
        )
    files_previously_included = [*files_previously_included, path]

    with open(path) as fp:
        current_config = yaml.load(fp, Loader=UniqueKeyLoader)

    # Load config from included files.
    includes_listed_in_config = (
        current_config.pop("includes") if "includes" in current_config else []
    )
    if not isinstance(includes_listed_in_config, list):
        raise AttributeError(
            f"Includes must be a list, '{type(includes_listed_in_config)}' provided"
        )

    config_from_includes = {}
    duplicates_warning = []
    duplicates_error = []
    for include in includes_listed_in_config:
        include_filename = find_relative_file_in_paths(
            include, [os.path.dirname(path), *include_paths]
        )
        include_config, inc_dup_warning, inc_dup_error = load_config(
            include_filename, files_previously_included
        )
        duplicates_warning += inc_dup_warning
        duplicates_error += inc_dup_error

        # Duplicates between includes causes an error
        config_from_includes, merge_dup_error = merge_dicts(
            config_from_includes, include_config
        )
        duplicates_error += merge_dup_error

    # Duplicates between included and main file causes warnings
    config_from_includes, merge_dup_warning = merge_dicts(
        config_from_includes, current_config
    )
    duplicates_warning += merge_dup_warning
    return config_from_includes, duplicates_warning, duplicates_error


def build_config(args, args_override, include_paths=None):
    config, duplicates_warning, duplicates_error = load_config(
        args.config_yml, include_paths=include_paths
    )
    if len(duplicates_warning) > 0:
        logging.warning(
            f"Overwritten config parameters from included configs "
            f"(non-included parameters take precedence): {duplicates_warning}"
        )
    if len(duplicates_error) > 0:
        raise ValueError(
            f"Conflicting (duplicate) parameters in simultaneously "
            f"included configs: {duplicates_error}"
        )

    # Some other flags.
    config["mode"] = args.mode
    config["identifier"] = args.identifier
    config["timestamp_id"] = args.timestamp_id
    config["seed"] = args.seed
    config["is_debug"] = args.debug
    config["run_dir"] = args.run_dir
    config["print_every"] = args.print_every
    config["amp"] = args.amp
    config["checkpoint"] = args.checkpoint
    config["cpu"] = args.cpu
    # Submit
    config["submit"] = args.submit
    config["summit"] = args.summit
    # Distributed
    config["world_size"] = args.num_nodes * args.num_gpus
    config["distributed_backend"] = "gloo" if args.cpu else "nccl"
    config["gp_gpus"] = args.gp_gpus

    # Check for overridden parameters.
    if args_override != []:
        overrides = create_dict_from_args(args_override)
        config, _ = merge_dicts(config, overrides)

    return config


def create_grid(base_config, sweep_file: str):
    def _flatten_sweeps(sweeps, root_key: str = "", sep: str = "."):
        flat_sweeps = []
        for key, value in sweeps.items():
            new_key = root_key + sep + key if root_key else key
            if isinstance(value, collections.MutableMapping):
                flat_sweeps.extend(_flatten_sweeps(value, new_key).items())
            else:
                flat_sweeps.append((new_key, value))
        return collections.OrderedDict(flat_sweeps)

    def _update_config(config, keys, override_vals, sep: str = "."):
        for key, value in zip(keys, override_vals):
            key_path = key.split(sep)
            child_config = config
            for name in key_path[:-1]:
                child_config = child_config[name]
            child_config[key_path[-1]] = value
        return config

    with open(sweep_file) as fp:
        sweeps = yaml.load(fp, Loader=UniqueKeyLoader)

    flat_sweeps = _flatten_sweeps(sweeps)
    keys = list(flat_sweeps.keys())
    values = list(itertools.product(*flat_sweeps.values()))

    configs = []
    for i, override_vals in enumerate(values):
        config = copy.deepcopy(base_config)
        config = _update_config(config, keys, override_vals)
        config["identifier"] = config["identifier"] + f"_run{i}"
        configs.append(config)
    return configs


def save_experiment_log(args, jobs, configs):
    log_file = args.logdir / "exp" / time.strftime("%Y-%m-%d-%I-%M-%S%p.log")
    log_file.parent.mkdir(exist_ok=True, parents=True)
    with open(log_file, "w") as f:
        for job, config in zip(jobs, configs):
            print(
                json.dumps(
                    {
                        "config": config,
                        "slurm_id": job.job_id,
                        "timestamp": time.strftime("%I:%M:%S%p %Z %b %d, %Y"),
                    }
                ),
                file=f,
            )
    return log_file

def merge_dicts(dict1: dict, dict2: dict):
    """Recursively merge two dictionaries.
    Values in dict2 override values in dict1. If dict1 and dict2 contain a dictionary as a
    value, this will call itself recursively to merge these dictionaries.
    This does not modify the input dictionaries (creates an internal copy).
    Additionally returns a list of detected duplicates.
    Adapted from https://github.com/TUM-DAML/seml/blob/master/seml/utils.py

    Parameters
    ----------
    dict1: dict
        First dict.
    dict2: dict
        Second dict. Values in dict2 will override values from dict1 in case they share the same key.

    Returns
    -------
    return_dict: dict
        Merged dictionaries.
    """
    if not isinstance(dict1, dict):
        raise ValueError(f"Expecting dict1 to be dict, found {type(dict1)}.")
    if not isinstance(dict2, dict):
        raise ValueError(f"Expecting dict2 to be dict, found {type(dict2)}.")

    return_dict = copy.deepcopy(dict1)
    duplicates = []

    for k, v in dict2.items():
        if k not in dict1:
            return_dict[k] = v
        else:
            if isinstance(v, dict) and isinstance(dict1[k], dict):
                return_dict[k], duplicates_k = merge_dicts(dict1[k], dict2[k])
                duplicates += [f"{k}.{dup}" for dup in duplicates_k]
            else:
                return_dict[k] = dict2[k]
                duplicates.append(k)

    return return_dict, duplicates


class SeverityLevelBetween(logging.Filter):
    def __init__(self, min_level: int, max_level: int) -> None:
        super().__init__()
        self.min_level = min_level
        self.max_level = max_level

    def filter(self, record) -> bool:
        return self.min_level <= record.levelno < self.max_level


def setup_logging() -> None:
    root = logging.getLogger()

    # Perform setup only if logging has not been configured
    if not root.hasHandlers():
        root.setLevel(logging.INFO)

        log_formatter = logging.Formatter(
            "%(asctime)s (%(levelname)s): %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Send INFO to stdout
        handler_out = logging.StreamHandler(sys.stdout)
        handler_out.addFilter(SeverityLevelBetween(logging.INFO, logging.WARNING))
        handler_out.setFormatter(log_formatter)
        root.addHandler(handler_out)

        # Send WARNING (and higher) to stderr
        handler_err = logging.StreamHandler(sys.stderr)
        handler_err.setLevel(logging.WARNING)
        handler_err.setFormatter(log_formatter)
        root.addHandler(handler_err)

def check_traj_files(batch, traj_dir) -> bool:
    if traj_dir is None:
        return False
    traj_dir = Path(traj_dir)
    sid_list =  batch.sid
    traj_files = [traj_dir / f"{sid}.traj" for sid in sid_list]
    return all(fl.exists() for fl in traj_files)


@contextmanager
def new_trainer_context(*, config: dict[str, Any]):
    from fairchem.core.common import distutils, gp_utils
    from fairchem.core.common.registry import registry

    if TYPE_CHECKING:
        from fairchem.core.tasks.task import BaseTask
        from fairchem.core.trainers import BaseTrainer

    @dataclass
    class _TrainingContext:
        config: dict[str, Any]
        task: BaseTask
        trainer: BaseTrainer

    setup_logging()
    original_config = config
    config = copy.deepcopy(original_config)

    distutils.setup(config)
    if config["gp_gpus"] is not None:
        gp_utils.setup_gp(config)
    try:
        setup_imports(config)
        trainer_name = config.get("trainer", "ocp")
        # backwards compatibility for older configs
        if trainer_name in ["forces", "equiformerv2_forces"]:
            task_name = "s2ef"
        elif trainer_name in ["energy", "equiformerv2_energy"]:
            task_name = "is2re"
        elif "multitask" in trainer_name:
            task_name = "multitask"
        else:
            task_name = "ocp"

        trainer_cls = registry.get_trainer_class(trainer_name)
        assert trainer_cls is not None, "Trainer not found"

        trainer_config = {
            "model": config["model"],
            "optimizer": config["optim"],
            "identifier": config["identifier"],
            "timestamp_id": config.get("timestamp_id", None),
            "run_dir": config.get("run_dir", "./"),
            "is_debug": config.get("is_debug", False),
            "print_every": config.get("print_every", 10),
            "seed": config.get("seed", 0),
            "logger": config.get("logger", "wandb"),
            "local_rank": config["local_rank"],
            "amp": config.get("amp", False),
            "cpu": config.get("cpu", False),
            "slurm": config.get("slurm", {}),
            "name": task_name,
            "gp_gpus": config.get("gp_gpus"),
        }

        if task_name == "multitask":
            trainer_config.update(
                {
                    "tasks": config.get("tasks", {}),
                    "dataset_configs": config["datasets"],
                    "combined_dataset_config": config.get("combined_dataset", {}),
                    "evaluations": config.get("evaluations", {}),
                }
            )
        else:
            trainer_config.update(
                {
                    "task": config.get("task", {}),
                    "outputs": config.get("outputs", {}),
                    "dataset": config["dataset"],
                    "loss_functions": config.get("loss_functions", {}),
                    "evaluation_metrics": config.get("evaluation_metrics", {}),
                }
            )
        trainer = trainer_cls(**trainer_config)

        task_cls = registry.get_task_class(config["mode"])
        assert task_cls is not None, "Task not found"
        task = task_cls(config)
        start_time = time.time()
        ctx = _TrainingContext(config=original_config, task=task, trainer=trainer)
        yield ctx
        distutils.synchronize()
        if distutils.is_master():
            logging.info(f"Total time taken: {time.time() - start_time}")
    finally:
        distutils.cleanup()


def irreps_sum(ang_mom: int) -> int:
    """
    Returns the sum of the dimensions of the irreps up to the specified angular momentum.

    :param ang_mom: max angular momenttum to sum up dimensions of irreps
    """
    total = 0
    for i in range(ang_mom + 1):
        total += 2 * i + 1

    return total


def update_config(base_config):
    """
    Configs created prior to FAIRChem/OCP 2.0 are organized a little different than they
    are now. Update old configs to fit the new expected structure.
    """
    ### TODO: better format check for older configs
    # some configs have a loss_functions key with an empty dictionary, those need to be updated as well
    if len(base_config.get("loss_functions", {})) > 0:
        return base_config

    logging.warning(
        "Detected old config, converting to new format. Consider updating to avoid potential incompatibilities."
    )

    # do we need a copy?
    config = copy.deepcopy(base_config)

    # initial fairchem/ocp 2.0 configs renamed loss_functions -> loss_fns and evaluation_metrics -> eval_metrics
    # so some checkpoints may have configs in new format with the exception of renamed loss_funs and eval_metrics
    if "loss_fns" in config:
        config["loss_functions"] = config.pop("loss_fns")
        if "eval_metrics" in config:
            config["evaluation_metrics"] = config.pop("eval_metrics")
        return config

    # If config["dataset"]["format"] is missing, get it from the task (legacy location).
    # If it is not there either, default to LMDB.
    config["dataset"]["format"] = config["dataset"].get(
        "format", config["task"].get("dataset", "lmdb")
    )

    ### Read task based off config structure, similar to OCPCalculator.
    if config["task"]["dataset"] in [
        "trajectory_lmdb",
        "lmdb",
        "trajectory_lmdb_v2",
        "oc22_lmdb",
        "ase_read",
        "ase_read_multi",
        "ase_db",
    ]:
        task = "s2ef"
    elif config["task"]["dataset"] == "single_point_lmdb":
        task = "is2re"
    else:
        raise NotImplementedError

    if task == "is2re":
        ### Define loss functions
        _loss_fns = [
            {
                "energy": {
                    "fn": config["optim"].get("loss_energy", "mae"),
                    "coefficient": config["optim"].get("energy_coefficient", 1),
                },
            }
        ]
        ### Define evaluation metrics
        _eval_metrics = {
            "metrics": {"energy": ["mae", "mse", "energy_within_threshold"]},
        }
        if "primary_metric" in config["task"]:
            _eval_metrics["primary_metric"] = config["task"]["primary_metric"]
        ### Define outputs
        _outputs = {"energy": {"level": "system"}}
        ### Define key mapping
        config["dataset"]["key_mapping"] = {"y_relaxed": "energy"}
    elif task == "s2ef":
        ### Define loss functions
        _loss_fns = [
            {
                "energy": {
                    "fn": config["optim"].get("loss_energy", "mae"),
                    "coefficient": config["optim"].get("energy_coefficient", 1),
                },
            },
            {
                "forces": {
                    "fn": config["optim"].get("loss_forces", "l2mae"),
                    "coefficient": config["optim"].get("force_coefficient", 30),
                },
            },
        ]
        ### Define evaluation metrics
        _eval_metrics = {
            "metrics": {
                "misc": ["energy_forces_within_threshold"],
                "energy": ["mae"],
                "forces": [
                    "forcesx_mae",
                    "forcesy_mae",
                    "forcesz_mae",
                    "mae",
                    "cosine_similarity",
                    "magnitude_error",
                ],
            },
        }
        if "primary_metric" in config["task"]:
            _eval_metrics["primary_metric"] = config["task"]["primary_metric"]
        elif "eval_metrics" in config and "primary_metric" in config["eval_metrics"]:
            _eval_metrics["primary_metric"] = config["eval_metrics"]["primary_metric"]
        ### Define outputs
        _outputs = {
            "energy": {"level": "system"},
            "forces": {
                "level": "atom",
                "train_on_free_atoms": (
                    config["task"].get("train_on_free_atoms", False)
                ),
                "eval_on_free_atoms": (config["task"].get("eval_on_free_atoms", True)),
            },
        }
        ### Define key mapping
        config["dataset"]["key_mapping"] = {"y": "energy", "force": "forces"}

    if config["dataset"].get("normalize_labels", False):
        normalizer = {
            "energy": {
                "mean": config["dataset"].get("target_mean", 0),
                "stdev": config["dataset"].get("target_std", 1),
            },
            "forces": {
                "mean": config["dataset"].get("grad_target_mean", 0),
                "stdev": config["dataset"].get("grad_target_std", 1),
            },
        }

        transforms = config["dataset"].get("transforms", {})
        transforms["normalizer"] = normalizer
        config["dataset"]["transforms"] = transforms

    ### Update config
    config.update({"loss_functions": _loss_fns})
    config.update({"evaluation_metrics": _eval_metrics})
    config.update({"outputs": _outputs})

    return config
