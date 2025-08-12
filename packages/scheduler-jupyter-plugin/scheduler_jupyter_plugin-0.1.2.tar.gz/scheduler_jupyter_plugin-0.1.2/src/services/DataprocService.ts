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

import { authenticatedFetch } from '../utils/Config';
import { HTTP_METHOD } from '../utils/Const';

export class DataprocService {
  static readonly listClustersDataprocAPIService = async () => {
    try {
      const queryParams = new URLSearchParams({ pageSize: '100' });
      const response = await authenticatedFetch({
        uri: 'clusters',
        method: HTTP_METHOD.GET,
        regionIdentifier: 'regions',
        queryParams: queryParams
      });
      const formattedResponse = await response.json();
      return formattedResponse;
    } catch (error) {
      return error;
    }
  };
}
