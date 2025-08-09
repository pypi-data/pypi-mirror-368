import datetime
from enum import IntEnum
from typing import TYPE_CHECKING

from .base import SsasEditableRecord

if TYPE_CHECKING:
    from .role import Role


class MemberType(IntEnum):
    Auto = 1
    User = 2
    Group = 3


class RoleMembership(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/dbecc1f4-142b-4765-8374-a4d4dc51313b)
    """

    identity_provider: str
    member_id: str
    member_name: str
    member_type: MemberType
    role_id: int

    modified_time: datetime.datetime

    def role(self) -> "Role":
        return self.tabular_model.roles.find(self.role_id)
