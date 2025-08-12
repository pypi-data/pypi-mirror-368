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
import { Notification } from '@jupyterlab/apputils';
import { requestAPI } from '../handler/Handler';
import { SchedulerLoggingService, LOG_LEVEL } from './LoggingService';
import path from 'path';
import { handleErrorToast } from '../utils/ErrorUtils';

export class StorageServices {
  static readonly cloudStorageAPIService = (
    setCloudStorageList: (value: string[]) => void,
    setCloudStorageLoading: (value: boolean) => void,
    setErrorMessageBucket: (value: string) => void
  ) => {
    setCloudStorageLoading(true);
    requestAPI('api/storage/listBucket')
      .then((formattedResponse: any) => {
        if (formattedResponse.length > 0) {
          setCloudStorageList(formattedResponse);
        } else if (formattedResponse.error) {
          setErrorMessageBucket(formattedResponse.error);
          setCloudStorageList([]);
        } else {
          setCloudStorageList([]);
        }
        setCloudStorageLoading(false);
      })
      .catch(error => {
        setCloudStorageList([]);
        setCloudStorageLoading(false);
        SchedulerLoggingService.log(
          `Error listing cloud storage bucket : ${error}`,
          LOG_LEVEL.ERROR
        );
        const errorResponse = `Failed to fetch cloud storage bucket : ${error}`;
        handleErrorToast({
          error: errorResponse
        });
      });
  };
  static readonly newCloudStorageAPIService = (
    bucketName: string,
    setIsCreatingNewBucket: (value: boolean) => void,
    setBucketError: (value: string) => void
  ) => {
    const payload = {
      bucket_name: bucketName
    };
    setIsCreatingNewBucket(true);
    requestAPI('api/storage/createNewBucket', {
      body: JSON.stringify(payload),
      method: 'POST'
    })
      .then((formattedResponse: any) => {
        if (formattedResponse === null) {
          Notification.success('Bucket created successfully', {
            autoClose: false
          });
          setBucketError('');
        } else if (formattedResponse?.error) {
          setBucketError(formattedResponse.error);
        }
        setIsCreatingNewBucket(false);
      })
      .catch(error => {
        setIsCreatingNewBucket(false);
        SchedulerLoggingService.log(
          `Error creating the cloud storage bucket ${error}`,
          LOG_LEVEL.ERROR
        );
      });
  };

  static readonly downloadJobAPIService = async (
    gcsUrl: string | undefined,
    fileName: string | undefined,
    jobRunId: string | undefined,
    setJobDownloadLoading: (value: boolean) => void,
    scheduleName: string
  ) => {
    try {
      const bucketName = gcsUrl?.split('//')[1];
      setJobDownloadLoading(true);
      const formattedResponse: any = await requestAPI(
        `api/storage/downloadOutput?bucket_name=${bucketName}&job_run_id=${jobRunId}&file_name=${fileName}`,
        {
          method: 'POST'
        }
      );
      if (formattedResponse.status === 0) {
        const base_filename = path.basename(
          formattedResponse.downloaded_filename
        );
        Notification.success(
          `${base_filename} has been successfully downloaded from the ${scheduleName} job history`,
          {
            autoClose: false
          }
        );
      } else {
        SchedulerLoggingService.log(
          'Error in downloading the job history',
          LOG_LEVEL.ERROR
        );
        Notification.error('Error in downloading the job history', {
          autoClose: false
        });
      }
      setJobDownloadLoading(false);
    } catch (error) {
      setJobDownloadLoading(false);
      SchedulerLoggingService.log(
        'Error in downloading the job history',
        LOG_LEVEL.ERROR
      );
      Notification.error('Error in downloading the job history', {
        autoClose: false
      });
    }
  };
}
