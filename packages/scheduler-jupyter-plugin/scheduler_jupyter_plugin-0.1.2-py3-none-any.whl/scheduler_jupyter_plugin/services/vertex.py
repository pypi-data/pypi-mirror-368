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


import aiohttp
import json
from cron_descriptor import get_description

import google.oauth2.credentials as oauth2
from google.cloud import storage

from scheduler_jupyter_plugin.commons.constants import (
    CONTENT_TYPE,
    HTTP_STATUS_OK,
    HTTP_STATUS_FORBIDDEN,
    HTTP_STATUS_NO_CONTENT,
)
from scheduler_jupyter_plugin.models.models import (
    DescribeVertexJob,
    DescribeBucketName,
    DescribeUpdateVertexJob,
)


class Client:
    client_session = aiohttp.ClientSession()

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

    async def create_gcs_bucket(self, bucket_name):
        try:
            if not bucket_name:
                raise ValueError("Bucket name cannot be empty")
            credentials = oauth2.Credentials(token=self._access_token)
            storage_client = storage.Client(credentials=credentials, project=self.project_id)
            storage_client.create_bucket(bucket_name)
        except Exception as error:
            self.log.exception(f"Error in creating Bucket: {error}")
            raise IOError(f"Error in creating Bucket: {error}")

    async def upload_to_gcs(self, bucket_name, file_path, job_name):
        input_notebook = file_path.split("/")[-1]
        credentials = oauth2.Credentials(self._access_token)
        storage_client = storage.Client(credentials=credentials, project=self.project_id)
        bucket = storage_client.bucket(bucket_name)
        blob_name = None

        if "gs:" not in file_path:
            # uploading the input file
            blob_name = f"{job_name}/{input_notebook}"
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(file_path)
            self.log.info(f"File {input_notebook} uploaded to gcs successfully")

            # creating json file containing the input file path
            metadata = {"inputFilePath": f"gs://{bucket_name}/{blob_name}"}
        else:
            metadata = {"inputFilePath": file_path}

        json_file_name = f"{job_name}.json"

        with open(json_file_name, "w") as f:
            json.dump(metadata, f, indent=4)

        # uploading json file containing the input file path
        json_blob_name = f"{job_name}/{json_file_name}"
        json_blob = bucket.blob(json_blob_name)
        json_blob.upload_from_filename(json_file_name)

        return blob_name if blob_name else file_path

    async def create_schedule(self, job, file_path, bucket_name):
        try:
            schedule_value = (
                "* * * * *" if job.schedule_value == "" else job.schedule_value
            )
            cron = (
                schedule_value
                if job.time_zone == "UTC"
                else f"TZ={job.time_zone} {schedule_value}"
            )
            machine_type = job.machine_type.split(" ", 1)[0]
            disk_type = job.disk_type.split(" ", 1)[0]

            # getting list of strings from UI, the api accepts dictionary, so converting it
            parameters = {
                param.split(":")[0]: param.split(":")[1] for param in job.parameters
            }

            notebook_source = (
                file_path if "gs://" in file_path else f"gs://{bucket_name}/{file_path}"
            )

            api_endpoint = f"https://{job.region}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{job.region}/schedules"
            headers = self.create_headers()
            payload = {
                "displayName": job.display_name,
                "cron": cron,
                "maxConcurrentRunCount": "1",
                "createNotebookExecutionJobRequest": {
                    "parent": f"projects/{self.project_id}/locations/{job.region}",
                    "notebookExecutionJob": {
                        "displayName": job.display_name,
                        "parameters": parameters,
                        "labels": {
                            "aiplatform.googleapis.com/colab_enterprise_entry_service": "workbench",
                        },
                        "customEnvironmentSpec": {
                            "machineSpec": {
                                "machineType": machine_type,
                                "acceleratorType": job.accelerator_type,
                                "acceleratorCount": job.accelerator_count,
                            },
                            "persistentDiskSpec": {
                                "diskType": disk_type,
                                "diskSizeGb": job.disk_size,
                            },
                            "networkSpec": {}
                        },
                        "gcsNotebookSource": {"uri": notebook_source},
                        "gcsOutputUri": job.cloud_storage_bucket,
                        "serviceAccount": job.service_account,
                        "kernelName": job.kernel_name,
                        "workbenchRuntime": {},
                    },
                },
            }
            if job.max_run_count:
                payload["maxRunCount"] = job.max_run_count
            if job.start_time:
                payload["startTime"] = job.start_time
            if job.end_time:
                payload["endTime"] = job.end_time
            if job.network:
                payload["createNotebookExecutionJobRequest"]["notebookExecutionJob"][
                    "customEnvironmentSpec"
                ]["networkSpec"]["network"] = job.network
                payload["createNotebookExecutionJobRequest"]["notebookExecutionJob"][
                    "customEnvironmentSpec"
                ]["networkSpec"]["enableInternetAccess"] = "TRUE"
            if job.subnetwork and job.network:
                payload["createNotebookExecutionJobRequest"]["notebookExecutionJob"][
                    "customEnvironmentSpec"
                ]["networkSpec"]["subnetwork"] = job.subnetwork

            async with self.client_session.post(
                api_endpoint, headers=headers, json=payload
            ) as response:
                if response.status == HTTP_STATUS_OK:
                    resp = await response.json()
                    return resp
                else:
                    self.log.exception("Error creating the schedule")
                    raise Exception(f"{response.reason} {await response.text()}")
        except Exception as e:
            self.log.exception(f"Error creating schedule: {str(e)}")
            raise Exception(f"Error creating schedule: {str(e)}")

    async def create_job_schedule(self, input_data):
        try:
            job = DescribeVertexJob(**input_data)
            storage_bucket = job.cloud_storage_bucket.split("//")[-1]

            if "gs://" in job.input_filename:
                input_filename = job.input_filename
            elif "gs:" in job.input_filename:
                input_filename = job.input_filename.replace("gs:", "gs://", 1)
            else:
                input_filename = job.input_filename

            file_path = await self.upload_to_gcs(
                storage_bucket, input_filename, job.display_name
            )
            res = await self.create_schedule(job, file_path, storage_bucket)
            return res
        except Exception as e:
            return {"error": str(e)}

    async def create_new_bucket(self, input_data):
        try:
            data = DescribeBucketName(**input_data)
            res = await self.create_gcs_bucket(data.bucket_name)
            return res
        except Exception as e:
            return {"error": str(e)}

    async def list_uiconfig(self, region_id):
        try:
            uiconfig = []
            api_endpoint = f"https://{region_id}-aiplatform.googleapis.com/ui/projects/{self.project_id}/locations/{region_id}/uiConfig"

            headers = self.create_headers()
            async with self.client_session.get(
                api_endpoint, headers=headers
            ) as response:
                if response.status == HTTP_STATUS_OK:
                    resp = await response.json()
                    if not resp:
                        return uiconfig
                    else:
                        if (
                            "notebookRuntimeConfig" in resp
                            and "machineConfigs" in resp["notebookRuntimeConfig"]
                        ):
                            for machineconfig in resp["notebookRuntimeConfig"][
                                "machineConfigs"
                            ]:
                                ramBytes_in_gb = round(
                                    int(machineconfig.get("ramBytes")) / 1000000000, 2
                                )
                                formatted_config = {
                                    "machineType": f"{machineconfig.get('machineType')} ({machineconfig.get('cpuCount')} CPUs, {ramBytes_in_gb} GB RAM)",
                                    "acceleratorConfigs": machineconfig.get(
                                        "acceleratorConfigs"
                                    ),
                                }
                                uiconfig.append(formatted_config)
                        return uiconfig
                elif response.status == HTTP_STATUS_FORBIDDEN:
                    resp = await response.json()
                    return resp
                else:
                    self.log.exception(
                        f"Error getting vertex ui config: {response.reason} {await response.text()}"
                    )
                    raise Exception(
                        f"Error getting vertex ui config: {response.reason} {await response.text()}"
                    )
        except Exception as e:
            self.log.exception(f"Error fetching ui config: {str(e)}")
            return {"Error fetching ui config": str(e)}

    def parse_schedule(self, cron):
        return get_description(cron)

    async def list_schedules(self, region_id, page_size=100, next_page_token=None):
        try:
            result = {}

            if next_page_token:
                api_endpoint = f"https://{region_id}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{region_id}/schedules?orderBy=createTime desc&pageToken={next_page_token}&pageSize={page_size}&filter=createNotebookExecutionJobRequest:*"

            else:
                api_endpoint = f"https://{region_id}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{region_id}/schedules?orderBy=createTime desc&pageSize={page_size}&filter=createNotebookExecutionJobRequest:*"

            headers = self.create_headers()
            async with self.client_session.get(
                api_endpoint, headers=headers
            ) as response:
                if response.status == HTTP_STATUS_OK:
                    resp = await response.json()
                    if not resp:
                        return result
                    else:
                        schedule_list = []
                        schedules = resp.get("schedules")
                        for schedule in schedules:
                            # filter for a workbench schedule 
                            # ie atleast any one of the following is not available.
                            # workbenchRuntime or kernel or customEnvironmentSpec
                            if schedule.get("createNotebookExecutionJobRequest").get("notebookExecutionJob") is None:
                                continue
                            notebook_execution_job = schedule.get("createNotebookExecutionJobRequest").get("notebookExecutionJob")
                            if (
                                notebook_execution_job.get("workbenchRuntime") is None
                                and notebook_execution_job.get("kernelName") is None
                                and notebook_execution_job.get("customEnvironmentSpec") is None
                            ):
                                continue
                            max_run_count = schedule.get("maxRunCount")
                            cron = schedule.get("cron")
                            cron_value = (
                                cron.split(" ", 1)[1]
                                if (cron and "TZ" in cron)
                                else cron
                            )
                            if max_run_count == "1" and cron_value == "* * * * *":
                                schedule_value = "run once"
                            else:
                                schedule_value = self.parse_schedule(cron)

                            formatted_schedule = {
                                "name": schedule.get("name"),
                                "displayName": schedule.get("displayName"),
                                "schedule": schedule_value,
                                "status": schedule.get("state"),
                                "createTime": schedule.get("createTime"),
                                "nextRunTime": schedule.get("nextRunTime"),
                                "lastScheduledRunResponse": schedule.get(
                                    "lastScheduledRunResponse"
                                ),
                            }
                            schedule_list.append(formatted_schedule)
                        resp["schedules"] = schedule_list
                        result.update(resp)
                        return result
                elif response.status == HTTP_STATUS_FORBIDDEN:
                    resp = await response.json()
                    return resp
                else:
                    self.log.exception(
                        f"Error listing schedules: {response.reason} {await response.text()}"
                    )
                    raise Exception(
                        f"Error listing schedules: {response.reason} {await response.text()}"
                    )
        except Exception as e:
            self.log.exception(f"Error fetching schedules: {str(e)}")
            return {"Error fetching schedules": str(e)}

    async def pause_schedule(self, region_id, schedule_id):
        try:
            api_endpoint = (
                f"https://{region_id}-aiplatform.googleapis.com/v1/{schedule_id}:pause"
            )

            headers = self.create_headers()
            async with self.client_session.post(
                api_endpoint, headers=headers
            ) as response:
                if response.status == HTTP_STATUS_OK:
                    return await response.json()
                elif response.status == HTTP_STATUS_NO_CONTENT:
                    return {"message": "Schedule paused successfully"}
                else:
                    self.log.exception(
                        f"Error pausing the schedule: {response.reason} {await response.text()}"
                    )
                    raise Exception(
                        f"Error pausing the schedule: {response.reason} {await response.text()}"
                    )
        except Exception as e:
            self.log.exception(f"Error pausing schedule: {str(e)}")
            return {"Error pausing schedule": str(e)}

    async def resume_schedule(self, region_id, schedule_id):
        try:
            api_endpoint = (
                f"https://{region_id}-aiplatform.googleapis.com/v1/{schedule_id}:resume"
            )

            headers = self.create_headers()
            async with self.client_session.post(
                api_endpoint, headers=headers
            ) as response:
                if response.status == HTTP_STATUS_OK:
                    return await response.json()
                elif response.status == HTTP_STATUS_NO_CONTENT:
                    return {"message": "Schedule resumed successfully"}
                else:
                    self.log.exception(
                        f"Error resuming the schedule: {response.reason} {await response.text()}"
                    )
                    raise Exception(
                        f"Error resuming the schedule: {response.reason} {await response.text()}"
                    )
        except Exception as e:
            self.log.exception(f"Error resuming schedule: {str(e)}")
            return {"Error resuming schedule": str(e)}

    async def delete_schedule(self, region_id, schedule_id):
        try:
            api_endpoint = (
                f"https://{region_id}-aiplatform.googleapis.com/v1/{schedule_id}"
            )

            headers = self.create_headers()
            async with self.client_session.delete(
                api_endpoint, headers=headers
            ) as response:
                if response.status == HTTP_STATUS_OK:
                    return await response.json()
                elif response.status == HTTP_STATUS_NO_CONTENT:
                    return {"message": "Schedule deleted successfully"}
                else:
                    self.log.exception(
                        f"Error deleting the schedule: {response.reason} {await response.text()}"
                    )
                    raise Exception(
                        f"Error deleting the schedule: {response.reason} {await response.text()}"
                    )
        except Exception as e:
            self.log.exception(f"Error deleting schedule: {str(e)}")
            return {"Error deleting schedule": str(e)}

    async def get_schedule(self, region_id, schedule_id):
        try:
            api_endpoint = (
                f"https://{region_id}-aiplatform.googleapis.com/v1/{schedule_id}"
            )

            headers = self.create_headers()
            async with self.client_session.get(
                api_endpoint, headers=headers
            ) as response:
                if response.status == HTTP_STATUS_OK:
                    return await response.json()
                else:
                    self.log.exception(
                        f"Error getting the schedule: {response.reason} {await response.text()}"
                    )
                    raise Exception(
                        f"Error getting the schedule: {response.reason} {await response.text()}"
                    )
        except Exception as e:
            self.log.exception(f"Error getting schedule: {str(e)}")
            return {"Error getting schedule": str(e)}

    async def trigger_schedule(self, region_id, schedule_id):
        try:
            data = await self.get_schedule(region_id, schedule_id)
            api_endpoint = f"https://{region_id}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{region_id}/notebookExecutionJobs"

            headers = self.create_headers()

            payload = data.get("createNotebookExecutionJobRequest", {}) \
                .get("notebookExecutionJob", {})
            
            payload["scheduleResourceName"] = data.get("name")
            async with self.client_session.post(
                api_endpoint, headers=headers, json=payload
            ) as response:
                if response.status == HTTP_STATUS_OK:
                    return await response.json()
                else:
                    self.log.exception(
                        f"Error triggering the schedule: {response.reason} {await response.text()}"
                    )
                    raise Exception(
                        f"Error triggering the schedule: {response.reason} {await response.text()}"
                    )
        except Exception as e:
            self.log.exception(f"Error triggering schedule: {str(e)}")
            return {"Error triggering schedule": str(e)}

    async def update_schedule(self, region_id, schedule_id, input_data):
        try:
            data = DescribeUpdateVertexJob(**input_data)
            custom_environment_spec = {}
            notebook_execution_job = {
                "displayName": data.display_name,
                "gcsNotebookSource": {"uri": data.gcs_notebook_source},
                "customEnvironmentSpec": custom_environment_spec,
                "labels": {
                    "aiplatform.googleapis.com/colab_enterprise_entry_service": "workbench",
                },
                "workbenchRuntime": {},
            }
            schedule_value = (
                "* * * * *" if data.schedule_value == "" else data.schedule_value
            )
            cron = (
                schedule_value
                if data.time_zone == "UTC"
                else f"TZ={data.time_zone} {schedule_value}"
            )
            # getting list of strings from UI, the api accepts dictionary, so converting it
            parameters = {
                param.split(":")[0]: param.split(":")[1] for param in data.parameters
            }

            if data.kernel_name:
                notebook_execution_job["kernelName"] = data.kernel_name
            if data.service_account:
                notebook_execution_job["serviceAccount"] = data.service_account
            if data.cloud_storage_bucket:
                notebook_execution_job["gcsOutputUri"] = data.cloud_storage_bucket
            if data.parameters:
                notebook_execution_job["parameters"] = parameters
            if data.machine_type:
                custom_environment_spec["machineSpec"] = {
                    "machineType": data.machine_type.split(" ", 1)[0],
                    "acceleratorType": data.accelerator_type,
                    "acceleratorCount": data.accelerator_count,
                }
            if data.network or data.subnetwork:
                custom_environment_spec["networkSpec"] = {
                    "network": data.network,
                    "subnetwork": data.subnetwork,
                }
            if data.disk_size or data.disk_type:
                custom_environment_spec["persistentDiskSpec"] = {
                    "diskSizeGb": data.disk_size,
                    "diskType": data.disk_type.split(" ", 1)[0],
                }

            payload = {
                "displayName": data.display_name,
                "maxConcurrentRunCount": "1",
                "cron": cron,
                "createNotebookExecutionJobRequest": {
                    "parent": f"projects/{self.project_id}/locations/{region_id}",
                    "notebookExecutionJob": notebook_execution_job,
                },
            }

            if data.start_time:
                payload["startTime"] = data.start_time
            if data.end_time:
                payload["endTime"] = data.end_time

            if data.max_run_count:
                payload["maxRunCount"] = data.max_run_count

            keys = payload.keys()
            keys_to_filter = ["displayName", "maxConcurrentRunCount"]
            filtered_keys = [
                item for item in keys if not any(key in item for key in keys_to_filter)
            ]
            update_mask = ",".join(filtered_keys)
            api_endpoint = f"https://{region_id}-aiplatform.googleapis.com/v1/{schedule_id}?updateMask={update_mask}"

            headers = self.create_headers()
            async with self.client_session.patch(
                api_endpoint, headers=headers, json=payload
            ) as response:
                if response.status == HTTP_STATUS_OK:
                    return await response.json()
                else:
                    self.log.exception(
                        f"Error updating the schedule: {response.reason} {await response.text()}"
                    )
                    raise Exception(
                        f"Error updating the schedule: {response.reason} {await response.text()}"
                    )
        except Exception as e:
            self.log.exception(f"Error updating schedule: {str(e)}")
            return {"error": str(e)}

    async def list_notebook_execution_jobs(
        self, region_id, schedule_id, order_by, page_size=None, start_date=None
    ):
        try:
            execution_jobs = []
            if page_size:
                api_endpoint = f"https://{region_id}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{region_id}/notebookExecutionJobs?filter=schedule={schedule_id}&pageSize={page_size}&orderBy={order_by}"
            else:
                api_endpoint = f"https://{region_id}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{region_id}/notebookExecutionJobs?filter=schedule={schedule_id}&orderBy={order_by}"

            headers = self.create_headers()
            async with self.client_session.get(
                api_endpoint, headers=headers
            ) as response:
                if response.status == HTTP_STATUS_OK:
                    resp = await response.json()
                    if not resp:
                        return execution_jobs
                    else:
                        jobs = resp.get("notebookExecutionJobs")
                        for job in jobs:
                            if start_date:
                                # getting only the jobs whose create time is equal to start date
                                # splitting it in order to get only the date part from the values which is in zulu format (2011-08-12T20:17:46.384Z)
                                if (
                                    start_date.rsplit("-", 1)[0]
                                    == job.get("createTime").rsplit("-", 1)[0]
                                ):
                                    execution_jobs.append(job)
                            else:
                                execution_jobs.append(job)
                        return execution_jobs
                else:
                    self.log.exception(
                        f"Error fetching notebook execution jobs: {response.reason} {await response.text()}"
                    )
                    raise Exception(
                        f"Error fetching notebook execution jobs: {response.reason} {await response.text()}"
                    )
        except Exception as e:
            self.log.exception(
                f"Error fetching list of notebook execution jobs: {str(e)}"
            )
            return {"Error fetching list of notebook execution jobs": str(e)}
