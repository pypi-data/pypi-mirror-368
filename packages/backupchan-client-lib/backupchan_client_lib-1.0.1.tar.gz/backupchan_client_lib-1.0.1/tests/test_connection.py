import uuid
import io
import pytest
import requests_mock
from backupchan import Connection

# example responses all taken straight from the api docs

NULL_UUID = "00000000-0000-0000-0000-000000000000"

def check_request(mock: requests_mock.Mocker, conn: Connection, method: str, payload: None | dict = None):
    last_request = mock.last_request
    assert mock.called
    assert last_request.method == method
    assert last_request.headers["Authorization"] == conn.headers()["Authorization"]

    if payload is not None:
        if "application/json" in last_request.headers["Content-Type"]:
            assert last_request.json() == payload
        else:
            assert last_request.text is not None

def test_get(conn):
    mock_response = {
        "success": True,
        "targets": [
            {
                "id": NULL_UUID,
                "name": "My backup",
                "target_type": "multi",
                "recycle_criteria": "count",
                "recycle_value": 10,
                "recycle_action": "recycle",
                "location": "/var/backups/MyBackup",
                "name_template": "backup-$I-$D"
            }
        ]
    }

    with requests_mock.Mocker() as m:
        m.get("http://localhost:5000/api/target", json=mock_response, status_code=200)

        response = conn.get("target")

        check_request(m, conn, "GET")

        assert response.status_code == 200
        assert response.json_body["success"] is True
        assert len(response.json_body["targets"]) == 1
        assert response.json_body["targets"][0]["name"] == "My backup"

def test_post(conn):
    mock_response = {
        "success": True,
        "id": NULL_UUID
    }

    with requests_mock.Mocker() as m:
        m.post("http://localhost:5000/api/target", json=mock_response, status_code=201)

        payload = {
            "name": "Backupy",
            "backup_type": "multi",
            "recycle_criteria": "count",
            "recycle_value": 10,
            "recycle_action": "recycle",
            "location": "/bakupy",
            "name_template": "bkp-$I"
        }

        response = conn.post("target", payload)

        check_request(m, conn, "POST", payload)

        assert response.status_code == 201
        assert response.json_body["success"] is True
        assert response.json_body["id"] == NULL_UUID

def test_post_form(conn):
    mock_response = {
        "success": True,
        "id": NULL_UUID
    }

    test_uuid = str(uuid.uuid4())

    with requests_mock.Mocker() as m:
        m.post(f"http://localhost:5000/api/target/{test_uuid}/upload", json=mock_response, status_code=200)
        
        payload = {
            "manual": False
        }

        files = {
            "backup_file": io.BytesIO(b"i am file")
        }

        response = conn.post_form(f"target/{test_uuid}/upload", data=payload, files=files)

        last_request = m.last_request
        check_request(m, conn, "POST", payload)
        assert "multipart/form-data" in last_request.headers["Content-Type"]

        assert response.status_code == 200
        assert response.json_body["success"] is True
        assert response.json_body["id"] == NULL_UUID

def test_delete(conn):
    mock_response = {
        "success": True
    }

    with requests_mock.Mocker() as m:
        m.delete(f"http://localhost:5000/api/target/{NULL_UUID}", json=mock_response, status_code=200)

        payload = {
            "delete_files": True
        }

        response = conn.delete(f"target/{NULL_UUID}", data=payload)

        check_request(m, conn, "DELETE", payload)

        assert response.status_code == 200
        assert response.json_body["success"] is True

def test_patch(conn):
    mock_response = {
        "success": True
    }

    with requests_mock.Mocker() as m:
        m.patch(f"http://localhost:5000/api/backup/{NULL_UUID}", json=mock_response, status_code=200)

        payload = {
            "is_recycled": True
        }

        response = conn.patch(f"backup/{NULL_UUID}", data=payload)

        check_request(m, conn, "PATCH", payload)

        assert response.status_code == 200
        assert response.json_body["success"] is True
