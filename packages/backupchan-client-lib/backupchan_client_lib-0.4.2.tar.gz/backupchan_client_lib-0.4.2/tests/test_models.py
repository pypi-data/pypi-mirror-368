import datetime
from backupchan.models import Backup, BackupType, BackupRecycleAction, BackupRecycleCriteria, BackupTarget, Stats

def test_target_from_dict():
    json_target = {
        "id": "deadbeef-dead-beef-dead-beefdeadbeef",
        "name": "touhoku kiritest",
        "target_type": "multi",
        "recycle_criteria": "count",
        "recycle_value": 13,
        "recycle_action": "recycle",
        "location": "/var/backups/touhoku",
        "name_template": "$I_kiritanpo",
        "deduplicate": False,
        "alias": None
    }

    target = BackupTarget.from_dict(json_target)
    assert target.id == json_target["id"]
    assert target.name == json_target["name"]
    assert target.target_type == BackupType.MULTI
    assert target.recycle_criteria == BackupRecycleCriteria.COUNT
    assert target.recycle_value == json_target["recycle_value"]
    assert target.recycle_action == BackupRecycleAction.RECYCLE
    assert target.location == json_target["location"]
    assert target.name_template == json_target["name_template"]
    assert target.deduplicate == json_target["deduplicate"]
    assert target.alias == json_target["alias"]

def test_backup_from_dict():
    created_at = datetime.datetime.now()
    json_backup = {
        "id": "d0d0caca-d0d0-caca-d0d0-cacad0d0caca",
        "target_id": "deadbeef-dead-beef-dead-beefdeadbeef",
        "created_at": created_at.isoformat(),
        "manual": False,
        "is_recycled": True,
        "filesize": 123456
    }

    backup = Backup.from_dict(json_backup)
    assert backup.id == json_backup["id"]
    assert backup.target_id == json_backup["target_id"]
    assert backup.created_at == created_at
    assert backup.manual == json_backup["manual"]
    assert backup.is_recycled == json_backup["is_recycled"]
    assert backup.filesize == json_backup["filesize"]

def test_stats_from_dict():
    json_stats = {
        "program_version": "1.1.0",
        "total_target_size": 123456,
        "total_recycle_bin_size": 654321,
        "total_targets": 4,
        "total_backups": 43,
        "total_recycled_backups": 11
    }

    stats = Stats.from_dict(json_stats)
    assert stats.program_version == json_stats["program_version"]
    assert stats.total_target_size == json_stats["total_target_size"]
    assert stats.total_recycle_bin_size == json_stats["total_recycle_bin_size"]
    assert stats.total_targets == json_stats["total_targets"]
    assert stats.total_backups == json_stats["total_backups"]
    assert stats.total_recycled_backups == json_stats["total_recycled_backups"]
