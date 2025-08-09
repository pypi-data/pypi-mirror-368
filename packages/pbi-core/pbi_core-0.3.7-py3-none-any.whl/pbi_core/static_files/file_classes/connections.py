from uuid import UUID

from ._base import BaseFileModel


class RemoteArtifact(BaseFileModel):
    DatasetId: UUID
    ReportId: UUID


class Connections(BaseFileModel):
    Version: int
    RemoteArtifacts: list[RemoteArtifact]
