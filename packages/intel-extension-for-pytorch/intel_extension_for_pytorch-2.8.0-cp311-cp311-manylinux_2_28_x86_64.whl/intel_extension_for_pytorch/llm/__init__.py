import warnings
from .frontend import optimize
from . import modules
from . import functional
from . import quantization

try:
    from . import generation
except ImportError as e:
    pass

try:
    from .utils import (
        _get_relative_imports,
        _gradient_checkpointing_disable,
        _gradient_checkpointing_enable,
        _get_class_from_dynamic_module,
        _get_cached_module_file,
        _get_imports,
        _pad,
        load_low_precision_checkpoint,
        shard_low_precision_checkpoint,
    )
    import transformers

    transformers.dynamic_module_utils.get_relative_imports = _get_relative_imports
    transformers.dynamic_module_utils.get_imports = _get_imports
    transformers.dynamic_module_utils.get_cached_module_file = _get_cached_module_file
    transformers.dynamic_module_utils.get_class_from_dynamic_module = (
        _get_class_from_dynamic_module
    )
    from packaging import version

    if version.parse(transformers.__version__) < version.parse("4.36"):
        transformers.modeling_utils.PreTrainedModel.gradient_checkpointing_disable = (
            _gradient_checkpointing_disable
        )
        transformers.modeling_utils.PreTrainedModel.gradient_checkpointing_enable = (
            _gradient_checkpointing_enable
        )
    transformers.tokenization_utils_base.PreTrainedTokenizerBase.pad = _pad
    if version.parse(transformers.__version__) >= version.parse(
        "4.48"
    ) and version.parse(transformers.__version__) <= version.parse("4.48.1"):
        import torch

        parsed_torch_version_base = version.parse(
            version.parse(torch.__version__).base_version
        )
        transformers.pytorch_utils.is_torch_greater_or_equal_than_2_0 = (
            parsed_torch_version_base >= version.parse("2.0")
        )
        transformers.pytorch_utils.is_torch_greater_or_equal_than_1_13 = (
            parsed_torch_version_base >= version.parse("1.13")
        )
        transformers.pytorch_utils.is_torch_greater_or_equal_than_1_12 = (
            parsed_torch_version_base >= version.parse("1.12")
        )
except ImportError:
    pass
