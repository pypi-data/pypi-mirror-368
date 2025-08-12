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
import { IVertexScheduleRunList } from '../scheduler/vertex/VertexInterfaces';

export class LogEntriesServices {
  static readonly vertexJobTaskLogsListService = async (
    dagRunId: string | undefined,
    jobRunsData: IVertexScheduleRunList | undefined,
    setDagTaskInstancesList: (value: any) => void,
    setIsLoading: (value: boolean) => void
  ) => {
    setDagTaskInstancesList([]);
    setIsLoading(true);
    const start_date = encodeURIComponent(jobRunsData?.startDate ?? '');
    const end_date = encodeURIComponent(jobRunsData?.endDate ?? '');
    try {
      /* eslint-disable */
      const data: any = await requestAPI(
        `api/logEntries/listEntries?filter_query=timestamp >= \"${start_date}" AND timestamp <= \"${end_date}" AND SEARCH(\"${dagRunId}\") AND severity >= WARNING`
      );
      if (data.length > 0) {
        let transformDagRunTaskInstanceListData = [];
        transformDagRunTaskInstanceListData = data.map((dagRunTask: any) => {
          return {
            severity: dagRunTask.severity,
            textPayload: dagRunTask.summary,
            date: new Date(dagRunTask.timestamp).toDateString(),
            time: new Date(dagRunTask.timestamp).toTimeString().split(' ')[0],
            fullData: dagRunTask
          };
        });
        setDagTaskInstancesList(transformDagRunTaskInstanceListData);
      } else {
        setDagTaskInstancesList([]);
      }
      setIsLoading(false);
    } catch (reason) {
      setIsLoading(false);
      setDagTaskInstancesList([]);
    }
  };
}
