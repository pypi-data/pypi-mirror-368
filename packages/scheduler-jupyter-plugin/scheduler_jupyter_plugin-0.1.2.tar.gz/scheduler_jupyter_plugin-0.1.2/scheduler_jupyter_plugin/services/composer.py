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


from typing import List

from scheduler_jupyter_plugin import urls
from scheduler_jupyter_plugin.commons.constants import (
    COMPOSER_SERVICE_NAME,
    CONTENT_TYPE,
    HTTP_STATUS_OK,
    HTTP_STATUS_FORBIDDEN,
)
from scheduler_jupyter_plugin.models.models import ComposerEnvironment


class Client:
    def __init__(self, credentials, log, client_session):
        self.log = log
        if not (
            ("access_token" in credentials)
            and ("project_id" in credentials)
            and ("region_id" in credentials)
        ):
            self.log.exception("Missing required credentials")
            raise ValueError("Missing required credentials")
        self._access_token = credentials["access_token"]
        self.project_id = credentials["project_id"]
        self.region_id = credentials["region_id"]
        self.client_session = client_session

    def create_headers(self):
        return {
            "Content-Type": CONTENT_TYPE,
            "Authorization": f"Bearer {self._access_token}",
        }

    async def list_environments(
        self, project_id=None, region_id=None
    ) -> List[ComposerEnvironment]:
        try:
            environments = []
            composer_url = await urls.gcp_service_url(COMPOSER_SERVICE_NAME)
            if project_id and region_id:
                api_endpoint = f"{composer_url}/v1/projects/{project_id}/locations/{region_id}/environments"
            else:
                api_endpoint = f"{composer_url}/v1/projects/{self.project_id}/locations/{self.region_id}/environments"

            headers = self.create_headers()
            async with self.client_session.get(
                api_endpoint, headers=headers
            ) as response:
                if response.status == HTTP_STATUS_OK:
                    resp = await response.json()
                    if not resp:
                        return environments
                    else:
                        environment = resp.get("environments", [])
                        for env in environment:
                            path = env["name"]
                            name = env["name"].split("/")[-1]
                            state = env["state"]
                            pypi_packages = env.get("config", {}).get("softwareConfig", {}).get("pypiPackages", None)
                            environments.append(
                                ComposerEnvironment(
                                    name=name,
                                    label=name,
                                    description=f"Environment: {name}",
                                    state=state,
                                    file_extensions=["ipynb"],
                                    metadata={"path": path},
                                    pypi_packages=pypi_packages
                                )
                            )
                        return environments
                elif response.status == HTTP_STATUS_FORBIDDEN:
                    resp = await response.json()
                    return resp
                else:
                    self.log.exception("Error listing environments")
                    raise Exception(
                        f"Error getting composer list: {response.reason} {await response.text()}"
                    )
        except Exception as e:
            self.log.exception(f"Error fetching environments list: {str(e)}")
            return {"Error fetching environments list": str(e)}
        
    async def get_environment(
        self, env_name
    ) -> ComposerEnvironment:
        try:
            environment = {}
            composer_url = await urls.gcp_service_url(COMPOSER_SERVICE_NAME)
            api_endpoint = f"{composer_url}/v1/{env_name}"

            headers = self.create_headers()
            async with self.client_session.get(
                api_endpoint, headers=headers
            ) as response:
                if response.status == HTTP_STATUS_OK:
                    resp = await response.json()
                    if not resp:
                        return environment
                    else:
                        path = resp.get("name")
                        name = resp.get("name").split("/")[-1]
                        state = resp.get("state")
                        pypi_packages = resp.get("config", {}).get("softwareConfig", {}).get("pypiPackages", None)
                        environment = ComposerEnvironment(
                            name=name,
                            label=name,
                            description=f"Environment: {name}",
                            state=state,
                            file_extensions=["ipynb"],
                            metadata={"path": path},
                            pypi_packages=pypi_packages
                        )
                            
                        return environment
                elif response.status == HTTP_STATUS_FORBIDDEN:
                    resp = await response.json()
                    return resp
                else:
                    self.log.exception("Error fetching environment")
                    raise Exception(
                        f"Error getting composer: {response.reason} {await response.text()}"
                    )
        except Exception as e:
            self.log.exception(f"Error fetching environment: {str(e)}")
            return {"Error fetching environment": str(e)}
