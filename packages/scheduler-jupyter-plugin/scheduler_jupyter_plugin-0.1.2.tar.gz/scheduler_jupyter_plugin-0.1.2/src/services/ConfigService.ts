/**
 * @license
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { requestAPI } from '../handler/Handler';
import 'react-toastify/dist/ReactToastify.css';
import { IGcpUrlResponseData } from '../utils/SchedulerJupyterInterfaces';

export class ConfigService {
  static readonly gcpServiceUrlsAPI = async () => {
    const data = (await requestAPI('getGcpServiceUrls')) as IGcpUrlResponseData;
    const storage_url = new URL(data.storage_url);
    const storage_upload_url = new URL(data.storage_url);

    if (
      !storage_url.pathname ||
      storage_url.pathname === '' ||
      storage_url.pathname === '/'
    ) {
      // If the overwritten  storage_url doesn't contain a path, add it.
      storage_url.pathname = 'storage/v1/';
    }
    storage_upload_url.pathname = 'upload/storage/v1/';

    return {
      DATAPROC: data.dataproc_url + 'v1',
      COMPUTE: data.compute_url,
      METASTORE: data.metastore_url + 'v1',
      CLOUD_KMS: data.cloudkms_url + 'v1',
      CLOUD_RESOURCE_MANAGER: data.cloudresourcemanager_url + 'v1/projects',
      REGION_URL: data.compute_url + '/projects',
      CATALOG: data.datacatalog_url + 'v1/catalog:search',
      COLUMN: data.datacatalog_url + 'v1/',
      STORAGE: storage_url.toString(),
      STORAGE_UPLOAD: storage_upload_url.toString()
    };
  };
}
