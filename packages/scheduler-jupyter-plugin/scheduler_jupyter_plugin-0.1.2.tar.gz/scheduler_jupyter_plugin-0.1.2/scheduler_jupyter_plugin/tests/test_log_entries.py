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
from google.cloud import logging

from scheduler_jupyter_plugin import credentials


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


@pytest.mark.parametrize("returncode, expected_result", [(0, [])])
async def test_list_log_entries(monkeypatch, returncode, expected_result, jp_fetch):
    mock_entries = MagicMock()

    mock_logging_client = MagicMock()
    mock_logging_client.list_entries.return_value = mock_entries
    monkeypatch.setattr(credentials, "get_cached", mock_credentials)
    monkeypatch.setattr(
        logging, "Client", lambda credentials=None, project=None: mock_logging_client
    )

    mock_filter_query = "mock-query"

    response = await jp_fetch(
        "scheduler-plugin",
        "api/logEntries/listEntries",
        params={
            "filter_query": mock_filter_query,
        },
        method="GET",
        allow_nonstandard_methods=True,
    )
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == expected_result
