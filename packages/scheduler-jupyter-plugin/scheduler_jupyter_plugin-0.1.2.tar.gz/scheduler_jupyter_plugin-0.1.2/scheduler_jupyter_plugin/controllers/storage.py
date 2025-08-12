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

import tornado
from jupyter_server.base.handlers import APIHandler

from scheduler_jupyter_plugin import credentials
from scheduler_jupyter_plugin.services import storage


class DownloadOutputController(APIHandler):
    @tornado.web.authenticated
    async def post(self):
        try:
            bucket_name = self.get_argument("bucket_name")
            job_run_id = self.get_argument("job_run_id")
            file_name = self.get_argument("file_name")
            client = storage.Client(await credentials.get_cached(), self.log)
            download_result = await client.download_output(
                bucket_name, file_name, job_run_id
            )
            self.finish(
                json.dumps(
                    {
                        "status": download_result.get("status"),
                        "downloaded_filename": download_result.get(
                            "downloaded_filename"
                        ),
                    }
                )
            )
        except Exception as e:
            self.log.exception({"Error in downloading output file": str(e)})
            self.finish({"Error in downloading output file": str(e)})


class CloudStorageController(APIHandler):
    @tornado.web.authenticated
    async def get(self):
        """Returns cloud storage bucket"""
        try:
            storage_client = storage.Client(await credentials.get_cached(), self.log)
            csb = await storage_client.list_bucket()
            self.finish(json.dumps(csb))
        except Exception as e:
            self.log.exception(f"Error fetching cloud storage bucket: {str(e)}")
            self.finish({"error": str(e)})


class OutputFileExistsController(APIHandler):
    @tornado.web.authenticated
    async def get(self):
        """Checks output file exists or not"""
        try:
            bucket_name = self.get_argument("bucket_name")
            job_run_id = self.get_argument("job_run_id")
            file_name = self.get_argument("file_name")
            client = storage.Client(await credentials.get_cached(), self.log)
            result = await client.output_file_exists(bucket_name, file_name, job_run_id)
            self.finish(json.dumps(result))
        except Exception as e:
            self.log.exception({"Error in checking output file": str(e)})
            self.finish({"Error in checking output file": str(e)})
