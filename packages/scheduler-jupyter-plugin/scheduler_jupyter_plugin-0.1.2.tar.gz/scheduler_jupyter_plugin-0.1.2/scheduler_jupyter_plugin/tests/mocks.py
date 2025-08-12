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
import aiohttp
from google.cloud import jupyter_config

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


async def mock_config(field_name):
    return None


class MockResponse:
    def __init__(self, json, status=200, text=None):
        self._json = json
        self._text = text
        self.status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        return

    async def json(self):
        return self._json

    async def text(self, encoding=None):
        return self._text or json.dumps(self._json)


class MockClientSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        return

    def get(self, api_endpoint, headers=None):
        return MockResponse(
            {
                "api_endpoint": api_endpoint,
                "headers": headers,
            }
        )

    def post(self, api_endpoint, headers=None, json=None):
        return MockResponse(
            {
                "results": [
                    {
                        "api_endpoint": api_endpoint,
                        "headers": headers,
                        "json": json,
                    }
                ]
            }
        )


def patch_mocks(monkeypatch):
    monkeypatch.setattr(credentials, "get_cached", mock_credentials)
    monkeypatch.setattr(jupyter_config, "async_get_gcloud_config", mock_config)
    monkeypatch.setattr(aiohttp, "ClientSession", MockClientSession)


class MockGetScheduleClientSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        return

    def get(self, api_endpoint, headers=None):
        return MockResponse(
            {"createNotebookExecutionJobRequest": {"notebookExecutionJob": {}}}
        )


class MockPostClientSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        return

    def post(self, api_endpoint, headers=None):
        return MockResponse({})


class MockDeleteSchedulesClientSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        return

    def delete(self, api_endpoint, headers=None):
        return MockResponse({"name": "mock-name", "done": True})


class MockListUIConfigClientSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        return

    def get(self, api_endpoint, headers=None):
        return MockResponse(
            {
                "notebookRuntimeConfig": {
                    "machineConfigs": [
                        {
                            "machineType": "value1",
                            "acceleratorConfigs": [],
                            "ramBytes": 206158430208,
                            "cpuCount": 2,
                        },
                        {
                            "machineType": "value12",
                            "acceleratorConfigs": [],
                            "ramBytes": 1005022347264,
                            "cpuCount": 1,
                        },
                    ]
                }
            }
        )


class MockListNotebookExecutionJobsClientSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        return

    def get(self, api_endpoint, headers=None):
        return MockResponse(
            {"notebookExecutionJobs": [{"name": "mock-name"}, {"name": "mock-name1"}]}
        )


class MockListSchedulesClientSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        return

    def get(self, api_endpoint, headers=None):
        return MockResponse(
                {
                 "schedules": [
                     {
                        "createTime": None,
                        "displayName": None,
                        "lastScheduledRunResponse": None,
                        "name": None,
                        "nextRunTime": None,
                        "cron": "* * * * *",  # cron string, will be parsed by parse_schedule
                        "state": None,        # maps to "status" in formatted output
                        "createNotebookExecutionJobRequest": {
                            "notebookExecutionJob": {
                                "kernelName": "python3",  # at least one of these must be present
                                # "workbenchRuntime": {},
                                # "customEnvironmentSpec": {},
                            }
                         },
                     },
                 ]
             }
        )


class MockTriggerSchedulesClientSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        return

    def post(self, api_endpoint, headers=None, json={}):
        return MockResponse({"name": "mock-name"})
