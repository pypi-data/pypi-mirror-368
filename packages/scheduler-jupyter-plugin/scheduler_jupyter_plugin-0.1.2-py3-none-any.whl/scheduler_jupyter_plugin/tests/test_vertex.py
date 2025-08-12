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
import unittest
from unittest.mock import MagicMock, patch
import aiohttp

import pytest

from scheduler_jupyter_plugin.services import vertex
from scheduler_jupyter_plugin.tests.mocks import (
    MockDeleteSchedulesClientSession,
    MockGetScheduleClientSession,
    MockListNotebookExecutionJobsClientSession,
    MockListSchedulesClientSession,
    MockListUIConfigClientSession,
    MockPostClientSession,
    MockTriggerSchedulesClientSession,
)


@pytest.mark.parametrize(
    "returncode, expected_result",
    [(0, {"createNotebookExecutionJobRequest": {"notebookExecutionJob": {}}})],
)
async def test_get_schedule(monkeypatch, returncode, expected_result, jp_fetch):
    monkeypatch.setattr(aiohttp, "ClientSession", MockGetScheduleClientSession)

    mock_region_id = "mock-region-id"
    mock_schedule_id = "mock-project-id"

    response = await jp_fetch(
        "scheduler-plugin",
        "api/vertex/getSchedule",
        params={"region_id": mock_region_id, "schedule_id": mock_schedule_id},
    )
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == expected_result


@pytest.mark.parametrize("returncode, expected_result", [(0, {})])
async def test_resume_schedule(monkeypatch, returncode, expected_result, jp_fetch):
    monkeypatch.setattr(aiohttp, "ClientSession", MockPostClientSession)

    mock_region_id = "mock-region-id"
    mock_schedule_id = "mock-project-id"

    response = await jp_fetch(
        "scheduler-plugin",
        "api/vertex/resumeSchedule",
        method="POST",
        allow_nonstandard_methods=True,
        params={"region_id": mock_region_id, "schedule_id": mock_schedule_id},
    )
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == expected_result


@pytest.mark.parametrize("returncode, expected_result", [(0, {})])
async def test_pause_schedule(monkeypatch, returncode, expected_result, jp_fetch):
    monkeypatch.setattr(aiohttp, "ClientSession", MockPostClientSession)

    mock_region_id = "mock-region-id"
    mock_schedule_id = "mock-project-id"

    response = await jp_fetch(
        "scheduler-plugin",
        "api/vertex/pauseSchedule",
        method="POST",
        allow_nonstandard_methods=True,
        params={"region_id": mock_region_id, "schedule_id": mock_schedule_id},
    )
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == expected_result


@pytest.mark.parametrize(
    "returncode, expected_result", [(0, {"name": "mock-name", "done": True})]
)
async def test_delete_schedule(monkeypatch, returncode, expected_result, jp_fetch):
    monkeypatch.setattr(aiohttp, "ClientSession", MockDeleteSchedulesClientSession)

    mock_region_id = "mock-region-id"
    mock_schedule_id = "mock-project-id"

    response = await jp_fetch(
        "scheduler-plugin",
        "api/vertex/deleteSchedule",
        method="DELETE",
        params={"region_id": mock_region_id, "schedule_id": mock_schedule_id},
    )
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == expected_result


@pytest.mark.parametrize(
    "returncode, expected_result",
    [
        (
            0,
            [
                {
                    "machineType": "value1 (2 CPUs, 206.16 GB RAM)",
                    "acceleratorConfigs": [],
                },
                {
                    "machineType": "value12 (1 CPUs, 1005.02 GB RAM)",
                    "acceleratorConfigs": [],
                },
            ],
        )
    ],
)
async def test_list_uiconfig(monkeypatch, returncode, expected_result, jp_fetch):
    monkeypatch.setattr(aiohttp, "ClientSession", MockListUIConfigClientSession)

    mock_region_id = "mock-region-id"

    response = await jp_fetch(
        "scheduler-plugin",
        "api/vertex/uiConfig",
        params={"region_id": mock_region_id},
    )
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == expected_result


@pytest.mark.parametrize(
    "returncode, expected_result",
    [
        (
            0,
            [{"name": "mock-name"}, {"name": "mock-name1"}],
        )
    ],
)
async def test_list_notebook_execution_jobs(
    monkeypatch, returncode, expected_result, jp_fetch
):
    monkeypatch.setattr(
        aiohttp, "ClientSession", MockListNotebookExecutionJobsClientSession
    )

    mock_region_id = "mock-region-id"
    mock_schedule_id = "mock-project-id"
    mock_order_by = "mock-order-by"

    response = await jp_fetch(
        "scheduler-plugin",
        "api/vertex/listNotebookExecutionJobs",
        params={
            "region_id": mock_region_id,
            "schedule_id": mock_schedule_id,
            "order_by": mock_order_by,
        },
    )
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == expected_result


@pytest.mark.parametrize(
    "returncode, expected_result",
    [
        (
            0,
            {
                "schedules": [
                    {
                        "createTime": None,
                        "displayName": None,
                        "lastScheduledRunResponse": None,
                        "name": None,
                        "nextRunTime": None,
                        "schedule": "Every 5 minutes",
                        "status": None,
                    },
                ],
            },
        )
    ],
)
async def test_list_schedules(monkeypatch, returncode, expected_result, jp_fetch):
    def mock_get_description(*args, **kwargs):
        return "Every 5 minutes"

    monkeypatch.setattr(vertex.Client, "parse_schedule", mock_get_description)
    monkeypatch.setattr(aiohttp, "ClientSession", MockListSchedulesClientSession)

    mock_region_id = "mock-region-id"
    mock_page_size = "mock-page-size"

    response = await jp_fetch(
        "scheduler-plugin",
        "api/vertex/listSchedules",
        params={"region_id": mock_region_id, "page_size": mock_page_size},
    )
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == expected_result


@pytest.mark.parametrize("returncode, expected_result", [(0, {"name": "mock-name"})])
async def test_trigger_schedule(monkeypatch, returncode, expected_result, jp_fetch):
    async def mock_get_schedule(*args, **kwargs):
        return {"createNotebookExecutionJobRequest": {"notebookExecutionJob": {}}}

    monkeypatch.setattr(vertex.Client, "get_schedule", mock_get_schedule)

    monkeypatch.setattr(aiohttp, "ClientSession", MockTriggerSchedulesClientSession)

    mock_region_id = "mock-region-id"
    mock_schedule_id = "mock-project-id"

    response = await jp_fetch(
        "scheduler-plugin",
        "api/vertex/triggerSchedule",
        method="POST",
        allow_nonstandard_methods=True,
        params={"region_id": mock_region_id, "schedule_id": mock_schedule_id},
    )
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == expected_result


class TestCreateJobScheduleMethod(unittest.TestCase):
    def setUp(self):
        self.instance = vertex.Client
        self.input_data = {
            "cloud_storage_bucket": "test_cloud_storage_bucket",
            "display_name": "test_display_name",
            "input_filename": "test_input_file",
        }

    @patch("models.DescribeVertexJob")
    @patch("vertex.Client.upload_to_gcs")
    @patch("vertex.Client.create_schedule")
    async def test_create_job_schedule(
        self,
        mock_create_schedule,
        mock_upload_to_gcs,
        mock_describe_vertex_job,
    ):
        mock_job = MagicMock()
        mock_job.cloud_storage_bucket = "test_storage_bucket"
        mock_job.display_name = "test_job_name"
        mock_job.input_filename = "test_input_file"
        mock_describe_vertex_job.return_value = mock_job

        result = await self.instance.create_job_schedule(self.input_data)

        self.assertEqual(result, {})


class TestCreateNewBucketMethod(unittest.TestCase):
    def setUp(self):
        self.instance = vertex.Client
        self.input_data = {
            "bucket_name": "test_bucket_name",
        }

    @patch("models.DescribeBucketName")
    @patch("vertex.Client.create_gcs_bucket")
    async def test_create_new_bucket(
        self,
        mock_gcs_bucket,
        mock_describe_bucket_name,
    ):
        mock_data = MagicMock()
        mock_data.bucket_name = "test_bucket_name"
        mock_describe_bucket_name.return_value = mock_data

        result = await self.instance.create_new_bucket(self.input_data)

        self.assertEqual(result, {})
