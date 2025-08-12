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


import os
from google.cloud import storage
import google.oauth2.credentials as oauth2
import aiofiles
import time


class Client:
    def __init__(self, credentials, log):
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

    async def download_output(self, bucket_name, file_name, job_run_id):
        try:
            credentials = oauth2.Credentials(self._access_token)
            storage_client = storage.Client(
                credentials=credentials, project=self.project_id
            )
            blob_name = f"{job_run_id}/{file_name}"
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            original_file_name = os.path.basename(blob_name)

            timestamp = time.strftime("%H%M%S")
            base_name, extension = os.path.splitext(original_file_name)
            unique_file_name = f"{base_name}_{job_run_id}_{timestamp}{extension}"
            destination_file_name = os.path.join(".", unique_file_name)

            async with aiofiles.open(destination_file_name, "wb") as f:
                file_data = blob.download_as_bytes()
                await f.write(file_data)
            self.log.info(
                f"Output notebook file '{unique_file_name}' downloaded successfully"
            )
            return {"status": 0, "downloaded_filename": destination_file_name}
        except Exception as error:
            self.log.exception(f"Error downloading output notebook file: {str(error)}")
            return {"error": str(error)}

    async def list_bucket(self):
        try:
            cloud_storage_buckets = []
            credentials = oauth2.Credentials(self._access_token)
            storage_client = storage.Client(
                credentials=credentials, project=self.project_id
            )
            buckets = storage_client.list_buckets()
            for bucket in buckets:
                cloud_storage_buckets.append(bucket.name)
            return cloud_storage_buckets

        except Exception as e:
            self.log.exception(f"Error fetching cloud storage buckets: {str(e)}")
            return {"error": str(e)}

    async def output_file_exists(self, bucket_name, file_name, job_run_id):
        try:
            credentials = oauth2.Credentials(self._access_token)
            storage_client = storage.Client(
                credentials=credentials, project=self.project_id
            )
            blob_name = f"{job_run_id}/{file_name}"
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            if blob.exists():
                return "true"
            else:
                return "false"
        except Exception as error:
            self.log.exception(f"Error checking output notebook file: {str(error)}")
            return {"error": str(error)}
