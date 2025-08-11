from __future__ import annotations

# with suppress(ImportError):
#     # TODO remove this in favor of a better solution
#     # We should never be importing * from a module
#     from fairchem.experimental.foundation_models.multi_task_dataloader.transforms.data_object import *  # noqa


class DataTransforms:
    def __init__(self, config) -> None:
        self.config = config

    def __call__(self, data_object):
        if not self.config:
            return data_object

        for transform_fn in self.config:
            # TODO: Normalization information used in the trainers. Ignore here for now
            # TODO: if we dont use them here, these should not be defined as "transforms" in the config
            # TODO: add them as another entry under dataset, maybe "standardize"?
            if transform_fn in ("normalizer", "element_references"):
                continue

            data_object = eval(transform_fn)(data_object, self.config[transform_fn])

        return data_object


def decompose_tensor(data_object, config):
    tensor_key = config["tensor"]
    rank = config["rank"]

    if tensor_key not in data_object:
        return data_object

    if rank != 2:
        raise NotImplementedError
    return data_object
