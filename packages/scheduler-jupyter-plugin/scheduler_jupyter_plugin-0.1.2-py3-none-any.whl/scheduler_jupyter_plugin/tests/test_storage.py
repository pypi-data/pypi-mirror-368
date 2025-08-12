# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from unittest.mock import MagicMock, Mock

import pytest
from google.cloud import storage

from scheduler_jupyter_plugin import credentials
from scheduler_jupyter_plugin.services import vertex


async def mock_credentials():
    return {
        "project_id": "credentials-project",
        "project_number": 12345,
        "region_id": "mock-region",
        "access_token": "mock-token",
        "config_error": 0,
        "login_error": 0,
    }


def mock_get(api_endpoint, headers=None):
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "api_endpoint": api_endpoint,
        "headers": headers,
    }
    return response


async def mock_config(field_name):
    return None


@pytest.mark.parametrize(
    "returncode, expected_result",
    [(0, {"status": 0, "downloaded_filename": "mock-file"})],
)
async def test_download_output(monkeypatch, returncode, expected_result, jp_fetch):

    async def mock_list_notebook_execution_jobs(*args, **kwargs):
        return None

    monkeypatch.setattr(
        vertex.Client, "list_notebook_execution_jobs", mock_list_notebook_execution_jobs
    )
    mock_blob = MagicMock()
    mock_blob.download_as_bytes.return_value = b"mock file content"

    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    mock_storage_client = MagicMock()
    mock_storage_client.bucket.return_value = mock_bucket
    monkeypatch.setattr(credentials, "get_cached", mock_credentials)
    monkeypatch.setattr(
        storage, "Client", lambda credentials=None, project=None: mock_storage_client
    )

    mock_bucket_name = "mock_bucket"
    mock_job_run_id = "258"
    mock_file_name = "mock-file"

    response = await jp_fetch(
        "scheduler-plugin",
        "api/storage/downloadOutput",
        params={
            "bucket_name": mock_bucket_name,
            "job_run_id": mock_job_run_id,
            "file_name": mock_file_name,
        },
        method="POST",
        allow_nonstandard_methods=True,
    )
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload["status"] == expected_result["status"]
    assert (
        payload["downloaded_filename"].find(expected_result["downloaded_filename"])
        != -1
    )


@pytest.mark.parametrize("returncode, expected_result", [(0, [])])
async def test_list_bucket(monkeypatch, returncode, expected_result, jp_fetch):
    mock_blob = MagicMock()
    mock_buckets = MagicMock()
    mock_buckets.blob.return_value = mock_blob

    mock_storage_client = MagicMock()
    mock_storage_client.list_buckets.return_value = mock_buckets

    monkeypatch.setattr(credentials, "get_cached", mock_credentials)
    monkeypatch.setattr(
        storage, "Client", lambda credentials=None, project=None: mock_storage_client
    )

    response = await jp_fetch(
        "scheduler-plugin",
        "api/storage/listBucket",
        method="GET",
        allow_nonstandard_methods=True,
    )
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == expected_result
