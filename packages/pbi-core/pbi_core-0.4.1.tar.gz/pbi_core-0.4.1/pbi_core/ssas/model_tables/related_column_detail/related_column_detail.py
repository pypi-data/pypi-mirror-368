from pbi_core.ssas.model_tables.base import SsasTable


class RelatedColumnDetail(SsasTable):
    """TBD.

    SSAS spec:
    """

    @classmethod
    def _db_type_name(cls) -> str:
        return "RelatedColumnDetails"
