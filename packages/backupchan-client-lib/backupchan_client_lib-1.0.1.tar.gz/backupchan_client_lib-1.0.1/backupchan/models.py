from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

class BackupRecycleCriteria(str, Enum):
    NONE = "none"
    COUNT = "count"
    AGE = "age"

class BackupRecycleAction(str, Enum):
    DELETE = "delete"
    RECYCLE = "recycle"

class BackupType(str, Enum):
    SINGLE = "single"
    MULTI = "multi"

@dataclass
class BackupTarget:
    id: str
    name: str
    target_type: BackupType
    recycle_criteria: BackupRecycleCriteria
    recycle_value: Optional[int]
    recycle_action: BackupRecycleAction
    location: str
    name_template: str
    deduplicate: bool
    alias: str | None

    @staticmethod
    def from_dict(d: dict) -> "BackupTarget":
        return BackupTarget(d["id"], d["name"], d["target_type"], d["recycle_criteria"], d["recycle_value"], d["recycle_action"], d["location"], d["name_template"], d["deduplicate"], d["alias"])

@dataclass
class Backup:
    id: str
    target_id: str
    created_at: datetime
    manual: bool
    is_recycled: bool
    filesize: int

    def pretty_created_at(self) -> str:
        return self.created_at.strftime("%B %d, %Y %H:%M")

    @staticmethod
    def from_dict(d: dict) -> "Backup":
        return Backup(d["id"], d["target_id"], datetime.fromisoformat(d["created_at"]), d["manual"], d["is_recycled"], d["filesize"])

@dataclass
class Stats:
    program_version: str
    total_target_size: int
    total_recycle_bin_size: int
    total_targets: int
    total_backups: int
    total_recycled_backups: int

    @staticmethod
    def from_dict(d: dict) -> "Stats":
        return Stats(d["program_version"], d["total_target_size"], d["total_recycle_bin_size"], d["total_targets"], d["total_backups"], d["total_recycled_backups"])
