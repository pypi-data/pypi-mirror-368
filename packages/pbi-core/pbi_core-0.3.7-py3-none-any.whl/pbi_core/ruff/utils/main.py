from typing import Any

from pbi_core.static_files.layout.condition import Expression

MAX_FONTS = 2


def get_config_values(config: Any | dict) -> dict[tuple[str, str], Expression]:
    if config is None:
        return {}

    # Not all config objects are being converted to Pydantic models, so we need to handle both cases.
    if not isinstance(config, dict):
        config = config.model_dump()
    ret = {}
    for category, category_data in config.items():
        if category_data is None:
            continue
        category_data_element = category_data[0]
        if not isinstance(category_data_element, dict):
            category_data_element = category_data_element.model_dump()
        for field, field_data in category_data_element["properties"].items():
            ret[category, field] = field_data
    return ret
