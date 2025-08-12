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
from google.cloud import compute_v1

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
async def test_list_region(monkeypatch, returncode, expected_result, jp_fetch):
    mock_regions = MagicMock()

    mock_compute_client = MagicMock()
    mock_compute_client.ListRegionsRequest.return_value = mock_regions
    monkeypatch.setattr(credentials, "get_cached", mock_credentials)
    monkeypatch.setattr(
        compute_v1,
        "RegionsClient",
        lambda credentials=None, project=None: mock_compute_client,
    )

    response = await jp_fetch(
        "scheduler-plugin",
        "api/compute/region",
        method="GET",
        allow_nonstandard_methods=True,
    )
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == expected_result


@pytest.mark.parametrize("returncode, expected_result", [(0, [])])
async def test_get_network(monkeypatch, returncode, expected_result, jp_fetch):
    mock_network = MagicMock()

    mock_compute_client = MagicMock()
    mock_compute_client.list.return_value = mock_network
    monkeypatch.setattr(credentials, "get_cached", mock_credentials)
    monkeypatch.setattr(
        compute_v1,
        "NetworksClient",
        lambda credentials=None, project=None: mock_compute_client,
    )

    response = await jp_fetch(
        "scheduler-plugin",
        "api/compute/network",
        method="GET",
        allow_nonstandard_methods=True,
    )
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == expected_result


@pytest.mark.parametrize("returncode, expected_result", [(0, [])])
async def test_get_subnetwork(monkeypatch, returncode, expected_result, jp_fetch):
    mock_sub_network = MagicMock()

    mock_compute_client = MagicMock()
    mock_compute_client.list.return_value = mock_sub_network
    monkeypatch.setattr(credentials, "get_cached", mock_credentials)
    monkeypatch.setattr(
        compute_v1,
        "SubnetworksClient",
        lambda credentials=None, project=None, region=None: mock_compute_client,
    )

    mock_region_id = "mock-region"
    mock_network_id = "mock-network"

    response = await jp_fetch(
        "scheduler-plugin",
        "api/compute/subNetwork",
        params={
            "region_id": mock_region_id,
            "network_id": mock_network_id,
        },
        method="GET",
        allow_nonstandard_methods=True,
    )
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == expected_result


@pytest.mark.parametrize("returncode, expected_result", [(0, [])])
async def test_get_shared_network(monkeypatch, returncode, expected_result, jp_fetch):
    mock_shared_network = MagicMock()

    mock_compute_client = MagicMock()
    mock_compute_client.list_usable.return_value = mock_shared_network
    monkeypatch.setattr(credentials, "get_cached", mock_credentials)
    monkeypatch.setattr(
        compute_v1,
        "SubnetworksClient",
        lambda credentials=None, project=None: mock_compute_client,
    )

    mock_project_id = "mock-project"
    mock_region_id = "mock-region"

    response = await jp_fetch(
        "scheduler-plugin",
        "api/compute/sharedNetwork",
        params={
            "project_id": mock_project_id,
            "region_id": mock_region_id,
        },
        method="GET",
        allow_nonstandard_methods=True,
    )
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == expected_result
