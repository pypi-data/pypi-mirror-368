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
import { SchedulerLoggingService, LOG_LEVEL } from './LoggingService';
import { handleErrorToast } from '../utils/ErrorUtils';

export class IamServices {
  static readonly serviceAccountAPIService = (
    setServiceAccountList: (
      value: { displayName: string; email: string }[]
    ) => void,
    setServiceAccountLoading: (value: boolean) => void,
    setErrorMessage: (value: string) => void
  ) => {
    setServiceAccountLoading(true);
    requestAPI('api/iam/listServiceAccount')
      .then((formattedResponse: any) => {
        if (formattedResponse.length > 0) {
          const serviceAccountList = formattedResponse.map((account: any) => ({
            displayName: account.displayName,
            email: account.email
          }));
          serviceAccountList.sort();
          setServiceAccountList(serviceAccountList);
        } else if (formattedResponse.error) {
          setErrorMessage(formattedResponse.error);
          setServiceAccountList([]);
        } else {
          setServiceAccountList([]);
        }
        setServiceAccountLoading(false);
      })
      .catch(error => {
        setServiceAccountList([]);
        setServiceAccountLoading(false);
        SchedulerLoggingService.log(
          `Error listing service accounts : ${error}`,
          LOG_LEVEL.ERROR
        );
        const errorResponse = `Failed to fetch service accounts list : ${error}`;
        handleErrorToast({
          error: errorResponse
        });
      });
  };
}
