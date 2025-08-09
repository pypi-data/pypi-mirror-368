from pbi_core.ruff.base_rule import BaseRule


class LargeImages(BaseRule):
    id = "GEN-003"
    name = "Overly Large Images"
    description = (
        "Flags cases where images are used that are larger than 500KB. Large images can significantly "
        "impact report performance and load times. It's recommended to optimize images to be under "
        "500KB for better performance."
    )
