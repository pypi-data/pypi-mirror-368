import io
import os
import tempfile
import uuid
import tarfile
from typing import Generator
from .connection import Connection, Response
from .models import Backup, BackupTarget, BackupRecycleCriteria, BackupRecycleAction, BackupType, Stats

class BackupchanAPIError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code

def check_success(response: Response) -> dict | Generator[bytes, None, None]:
    if isinstance(response.json_body, Generator):
        if response.status_code != 200:
            raise BackupchanAPIError(f"Server returned error (code {response.status_code})", response.status_code)
    elif not response.json_body.get("success", False):
        raise BackupchanAPIError(f"Server returned error: {response.json_body} (code {response.status_code})", response.status_code)
    return response.json_body

class API:
    def __init__(self, host: str, port: int, api_key: str):
        self.connection = Connection(host, port, api_key)

    def list_targets(self, page: int = 1) -> list[BackupTarget]:
        response = self.connection.get(f"target?page={page}")
        resp_json = check_success(response)
        targets = resp_json["targets"]
        return [BackupTarget.from_dict(target) for target in targets]

    def new_target(self, name: str, backup_type: BackupType, recycle_criteria: BackupRecycleCriteria, recycle_value: int, recycle_action: BackupRecycleAction, location: str, name_template: str, deduplicate: bool, alias: str | None) -> str:
        """
        Returns ID of new target.
        """
        data = {
            "name": name,
            "backup_type": backup_type,
            "recycle_criteria": recycle_criteria,
            "recycle_value": recycle_value,
            "recycle_action": recycle_action,
            "location": location,
            "name_template": name_template,
            "deduplicate": deduplicate,
            "alias": alias
        }
        resp_json = check_success(self.connection.post("target", data))
        return resp_json["id"]

    def upload_backup(self, target_id: str, file: io.IOBase, filename: str, manual: bool) -> str:
        """
        Returns ID of the job that uploads the backup.
        """
        data = {
            "manual": int(manual)
        }

        files = {
            "backup_file": (filename, file)
        }

        response = self.connection.post_form(f"target/{target_id}/upload", data=data, files=files)
        resp_json = check_success(response)
        return resp_json["job_id"]
    
    def upload_backup_folder(self, target_id: str, folder_path: str, manual: bool) -> str:
        if not os.path.isdir(folder_path):
            raise BackupchanAPIError("Cannot upload a single file in a directory upload")

        # Cannot upload a directory to a single-file target.
        target_type = self.get_target(target_id)[0].target_type
        if target_type == BackupType.SINGLE:
            raise BackupchanAPIError("Cannot upload directory to a single file target")

        # Make a temporary gzipped tarball containing the directory contents.
        temp_dir = tempfile.gettempdir()
        temp_tar_path = os.path.join(temp_dir, f"bakch-{uuid.uuid4().hex}.tar.gz")
        with tarfile.open(temp_tar_path, "w:gz") as tar:
            tar.add(folder_path, arcname=os.path.basename(folder_path))
        
        # Upload our new tar.
        with open(temp_tar_path, "rb") as tar:
            return self.upload_backup(target_id, tar, os.path.basename(folder_path) + ".tar.gz", manual)

    def download_backup(self, backup_id: str, output_directory: str) -> str:
        response = self.connection.get_stream(f"backup/{backup_id}/download")
        check_success(response)
        filename = response.headers["Content-Disposition"].split("filename=")[-1].strip('"')
        full_path = os.path.join(output_directory, filename)
        with open(full_path, "wb") as file:
            for chunk in response.json_body:
                file.write(chunk)
        return full_path

    def get_target(self, id: str) -> tuple[BackupTarget, list[Backup]]:
        response = self.connection.get(f"target/{id}")
        resp_json = check_success(response)
        return BackupTarget.from_dict(resp_json["target"]), [Backup.from_dict(backup) for backup in resp_json["backups"]]

    def edit_target(self, id: str, name: str, recycle_criteria: BackupRecycleCriteria, recycle_value: int, recycle_action: BackupRecycleAction, location: str, name_template: str, deduplicate: bool, alias: str | None):
        data = {
            "name": name,
            "recycle_criteria": recycle_criteria,
            "recycle_value": recycle_value,
            "recycle_action": recycle_action,
            "location": location,
            "name_template": name_template,
            "deduplicate": deduplicate,
            "alias": alias
        }
        response = self.connection.patch(f"target/{id}", data=data)
        check_success(response)

    def delete_target(self, id: str, delete_files: bool):
        data = {
            "delete_files": delete_files
        }
        response = self.connection.delete(f"target/{id}", data=data)
        check_success(response)

    def delete_target_backups(self, id: str, delete_files: bool):
        data = {
            "delete_files": delete_files
        }
        response = self.connection.delete(f"target/{id}/all", data=data)
        check_success(response)

    def delete_backup(self, id: str, delete_files: bool):
        data = {
            "delete_files": delete_files
        }
        response = self.connection.delete(f"backup/{id}", data=data)
        check_success(response)

    def recycle_backup(self, id: str, is_recycled: bool):
        data = {
            "is_recycled": is_recycled
        }
        response = self.connection.patch(f"backup/{id}", data=data)
        check_success(response)

    def list_recycled_backups(self) -> list[Backup]:
        response = self.connection.get("recycle_bin")
        resp_json = check_success(response)
        return [Backup.from_dict(backup) for backup in resp_json["backups"]]

    def clear_recycle_bin(self, delete_files: bool):
        data = {
            "delete_files": delete_files
        }
        response = self.connection.delete("recycle_bin", data=data)
        check_success(response)

    def get_log(self, tail: int) -> str:
        response = self.connection.get(f"log?tail={tail}")
        resp_json = check_success(response)
        return resp_json["log"]
    
    def view_stats(self) -> Stats:
        response = self.connection.get("stats")
        resp_json = check_success(response)
        return Stats.from_dict(resp_json)
