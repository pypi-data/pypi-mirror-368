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

export interface ISessionTemplateRoot {
  error: {
    code: number;
    message: string;
  };
  sessionTemplates: ISessionTemplate[];
  nextPageToken: string;
}

export interface ISessionTemplate {
  name: string;
  createTime: string;
  jupyterSession: IJupyterSession;
  creator: string;
  labels: ILabels;
  environmentConfig: IEnvironmentConfig;
  description: string;
  updateTime: string;
}

export interface IJupyterSession {
  kernel: string;
  displayName: string;
}

export interface ILabels {
  purpose: string;
}

export interface IEnvironmentConfig {
  executionConfig: IExecutionConfig;
}

export interface IExecutionConfig {
  subnetworkUri: string;
}

export interface ISessionTemplateDisplay {
  name: string;
  owner: string;
  description: string;
  lastModified: string;
  id: string;
}
