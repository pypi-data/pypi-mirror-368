import datetime
from enum import IntEnum, StrEnum
from typing import TYPE_CHECKING, Any, Literal

import pydantic
from pydantic_extra_types.semantic_version import SemanticVersion

from pbi_core.lineage import LineageNode
from pbi_core.pydantic import BaseValidation
from pbi_core.ssas.model_tables.base import SsasEditableRecord
from pbi_core.ssas.server._commands import BaseCommands
from pbi_core.ssas.server.utils import SsasCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.culture import Culture


class ContentType(IntEnum):
    Xml = 0
    Json = 1


class EntityDefinitionBinding(BaseValidation):
    ConceptualEntity: str
    ConceptualProperty: str | None = None
    VariationSource: str | None = None
    VariationSet: str | None = None
    Hierarchy: str | None = None
    HierarchyLevel: str | None = None


class EntityDefinition(BaseValidation):
    Binding: EntityDefinitionBinding


class TermSourceType(StrEnum):
    External = "External"


class TermSource(BaseValidation):
    Type: TermSourceType | None = None
    Agent: str


class TermDefinitionState(StrEnum):
    Suggested = "Suggested"
    Generated = "Generated"
    Deleted = "Deleted"


class TermDefinitionType(StrEnum):
    Noun = "Noun"


class TermDefinition(BaseValidation):
    State: TermDefinitionState | None = None
    Source: TermSource | None = None
    Weight: float | None = None
    Type: TermDefinitionType | None = None
    LastModified: datetime.datetime | None = None


class VisibilityValue(StrEnum):
    Hidden = "Hidden"


class VisibilityState(StrEnum):
    Authored = "Authored"


class VisibilityType(BaseValidation):
    Value: VisibilityValue
    State: VisibilityState | None = None


class NameTypeType(StrEnum):
    Identifier = "Identifier"
    Name = "Name"


class LinguisticMetadataEntity(BaseValidation):
    Weight: float | None = None
    State: TermDefinitionState
    Terms: list[dict[str, TermDefinition]] | None = None
    Definition: EntityDefinition | None = None
    Binding: EntityDefinitionBinding | None = None
    SemanticType: str | None = None
    Visibility: VisibilityType | None = None
    Hidden: bool = False
    NameType: NameTypeType | None = None
    Units: list[str] = []


class RelationshipBinding(BaseValidation):
    ConceptualEntity: str


class PhrasingAttributeRole(BaseValidation):
    Role: str


class RelationshipPhrasingState(StrEnum):
    Generated = "Generated"


# TODO: Subtype
class PhrasingAttribute(BaseValidation):
    model_config = pydantic.ConfigDict(
        extra="forbid",
    )
    Adjective: PhrasingAttributeRole | None = None
    Measurement: PhrasingAttributeRole | None = None
    Object: PhrasingAttributeRole | None = None
    Subject: PhrasingAttributeRole | None = None
    Name: PhrasingAttributeRole | None = None

    PrepositionalPhrases: list[dict[str, Any]] = []
    Adjectives: list[dict[str, TermDefinition]] = []
    Antonyms: list[dict[str, TermDefinition]] = []
    Prepositions: list[dict[str, TermDefinition]] = []
    Verbs: list[dict[str, TermDefinition]] = []
    Nouns: list[dict[str, TermDefinition]] = []


class RelationshipPhrasing(BaseValidation):
    Name: PhrasingAttribute | None = None
    Attribute: PhrasingAttribute | None = None
    Verb: PhrasingAttribute | None = None
    Adjective: PhrasingAttribute | None = None
    Preposition: PhrasingAttribute | None = None
    DynamicAdjective: PhrasingAttribute | None = None
    State: RelationshipPhrasingState | None = None
    Weight: float | None = None


class RelationshipRoleEntity(BaseValidation):
    Entity: str


class RelationshipRole(BaseValidation):
    Target: RelationshipRoleEntity
    Nouns: Any | None = None


class SemanticSlot(BaseValidation):
    Where: PhrasingAttributeRole | None = None
    When: PhrasingAttributeRole | None = None


class ConditionOperator(StrEnum):
    Equals = "Equals"
    GreaterThan = "GreaterThan"


class Condition(BaseValidation):
    Target: PhrasingAttributeRole
    Operator: ConditionOperator
    Value: dict[str, list[int | str]]


class LinguisticMetadataRelationship(BaseValidation):
    Binding: RelationshipBinding
    Phrasings: list[RelationshipPhrasing] = []
    Roles: dict[str, RelationshipRole | int]
    State: str | None = None
    SemanticSlots: SemanticSlot | None = None
    Conditions: list[Condition] | None = None


class LinguisticMetadataContent(BaseValidation):
    Version: SemanticVersion
    Language: str
    DynamicImprovement: str | None = None
    Relationships: dict[str, LinguisticMetadataRelationship] | None = None
    Entities: dict[str, LinguisticMetadataEntity] | None = None
    Examples: list[dict[str, dict[str, str]]] | None = None


class LinguisticMetadata(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/f8924a45-70da-496a-947a-84b8d5beaae6)
    """

    content: pydantic.Json[LinguisticMetadataContent]
    content_type: ContentType
    culture_id: int

    modified_time: datetime.datetime

    _commands: BaseCommands = pydantic.PrivateAttr(default_factory=lambda: SsasCommands.linguistic_metadata)

    def culture(self) -> "Culture":
        return self.tabular_model.cultures.find({"id": self.culture_id})

    def pbi_core_name(self) -> str:
        """Returns the name displayed in the PBIX report."""
        return self.culture().pbi_core_name()

    @classmethod
    def _db_command_obj_name(cls) -> str:
        return "LinguisticMetadata"

    def get_lineage(self, lineage_type: Literal["children", "parents"]) -> LineageNode:
        if lineage_type == "children":
            return LineageNode(self, lineage_type)
        return LineageNode(self, lineage_type, [self.culture().get_lineage(lineage_type)])
