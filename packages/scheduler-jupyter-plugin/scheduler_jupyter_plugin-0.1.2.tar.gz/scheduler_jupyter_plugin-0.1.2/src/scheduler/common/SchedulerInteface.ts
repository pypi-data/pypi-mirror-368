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

import { ToastOptions } from 'react-toastify';

export interface IPayload {
  input_filename: string;
  composer_environment_name: string;
  output_formats: string[];
  parameters: string[];
  cluster_name?: string;
  serverless_name?: Record<string, never>;
  mode_selected: string;
  retry_count: number | undefined;
  retry_delay: number | undefined;
  email_failure: boolean;
  email_delay: boolean;
  email: string[];
  name: string;
  schedule_value: string;
  stop_cluster: boolean;
  time_zone?: string;
  dag_id: string;
}

export interface IUpdateSchedulerAPIResponse {
  status: number;
  error: string;
}

export interface ISchedulerDagData {
  dag_id: string;
  timetable_description: string;
  is_paused: string;
  schedule_interval: null | {
    value: string;
  };
}
export interface IDagList {
  jobid: string;
  notebookname: string;
  schedule: string;
  scheduleInterval: string;
}

export interface IClusterAPIResponse {
  clusterName: string;
  clusterUuid: string;
  config: Record<string, never>;
  labels: Record<string, never>;
  metrics: Record<string, never>;
  projectId: string;
  status: Record<string, never>;
  statusHistory: [];
}

export interface IComposerAPIResponse {
  name: string | '';
  label: string;
  description: string;
  state: string;
  file_extensions: [];
  metadata: Record<string, never>;
  pypi_packages: Record<string, string> | undefined;
}

export interface IDagRunList {
  dagRunId: string;
  filteredDate: Date;
  state: string;
  date: Date;
  time: string;
}

export interface IExpandableToastProps extends ToastOptions {
  message: string;
}
