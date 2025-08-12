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

import React, { useState, useEffect, useMemo, useRef } from 'react';
import { Notification } from '@jupyterlab/apputils';
import { useTable, usePagination } from 'react-table';
import TableData from '../../utils/TableData';
import { PaginationComponent } from '../../utils/PaginationComponent';
import { IVertexCellProps } from '../../utils/Config';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { CircularProgress, Button } from '@mui/material';
import DeletePopup from '../../utils/DeletePopup';
import { VERTEX_REGIONS, VERTEX_SCHEDULE } from '../../utils/Const';
import { RegionDropdown } from '../../controls/RegionDropdown';
import { iconDash } from '../../utils/Icons';
import { authApi } from '../../utils/Config';
import {
  iconActive,
  iconDelete,
  iconEditDag,
  iconEditNotebook,
  iconFailed,
  iconListCompleteWithError,
  iconListPause,
  iconPause,
  iconPlay,
  iconSuccess,
  iconTrigger,
  iconPending
} from '../../utils/Icons';
import { VertexServices } from '../../services/Vertex';
import {
  IVertexScheduleList,
  IActivePaginationVariables,
  ICreatePayload
} from './VertexInterfaces';
import dayjs from 'dayjs';
import ErrorMessage from '../common/ErrorMessage';

function ListVertexScheduler({
  region,
  setRegion,
  app,
  createCompleted,
  setCreateCompleted,
  setSubNetworkList,
  setEditMode,
  handleScheduleIdSelection,
  setIsApiError,
  setApiError,
  abortControllers,
  abortApiCall,
  activePaginationVariables,
  setActivePaginationVariables,
  setApiEnableUrl,
  setVertexScheduleDetails,
  setListingScreenFlag,
  createMode
}: {
  region: string;
  setRegion: (value: string) => void;
  app: JupyterFrontEnd;
  createCompleted?: boolean;
  setCreateCompleted: (value: boolean) => void;
  setSubNetworkList: (value: { name: string; link: string }[]) => void;
  setEditMode: (value: boolean) => void;
  setJobNameSelected: (value: string) => void;
  handleScheduleIdSelection: (
    scheduleId: any,
    scheduleName: string,
    activePaginationVariables: IActivePaginationVariables | null | undefined,
    region: string
  ) => void;
  setIsApiError: (value: boolean) => void;
  setApiError: (value: string) => void;
  abortControllers: any;
  abortApiCall: () => void;
  activePaginationVariables: IActivePaginationVariables | null | undefined;
  setActivePaginationVariables: (
    value: IActivePaginationVariables | null | undefined
  ) => void;
  setApiEnableUrl: any;
  setVertexScheduleDetails: (value: ICreatePayload) => void;
  setListingScreenFlag: (value: boolean) => void;
  createMode: boolean;
}) {
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [vertexScheduleList, setScheduleList] = useState<IVertexScheduleList[]>(
    []
  );
  const data = vertexScheduleList;
  const [deletePopupOpen, setDeletePopupOpen] = useState<boolean>(false);
  const [editScheduleLoading, setEditScehduleLoading] = useState('');
  const [triggerLoading, setTriggerLoading] = useState('');
  const [resumeLoading, setResumeLoading] = useState('');
  const [inputNotebookFilePath, setInputNotebookFilePath] =
    useState<string>('');
  const [editNotebookLoading, setEditNotebookLoading] = useState<string>('');
  const [deletingSchedule, setDeletingSchedule] = useState<boolean>(false);
  const [projectId, setProjectId] = useState<string>('');
  const [uniqueScheduleId, setUniqueScheduleId] = useState<string>('');
  const [scheduleDisplayName, setScheduleDisplayName] = useState<string>('');
  const isPreview = false;

  const [scheduleListPageLength, setScheduleListPageLength] =
    useState<number>(25); // size of each page with pagination
  const [totalCount, setTotalCount] = useState<number>(0); // size of each page with pagination
  const [pageTokenList, setPageTokenList] = useState<string[]>([]);
  const [canNextPage, setCanNextPage] = useState<boolean>(false);
  const [canPreviousPage, setCanPreviousPage] = useState<boolean>(false);
  const [nextPageToken, setNextPageToken] = useState<string | null>(null);
  const [fetchPreviousPage, setFetchPreviousPage] = useState<boolean>(false);
  const [resetToCurrentPage, setResetToCurrentPage] = useState<boolean>(false);
  const previousScheduleList = useRef(vertexScheduleList);
  const previousNextPageToken = useRef(nextPageToken);
  const [regionDisable, setRegionDisable] = useState<boolean>(false);
  const [loaderRegion, setLoaderRegion] = useState<boolean>(false);
  const [pageNumber, setPageNumber] = useState<number>(1); // Track current page number
  const [fetchNextPage, setFetchNextPage] = useState<boolean>(false);

  const columns = useMemo(
    () => [
      {
        Header: 'Schedule Name',
        accessor: 'displayName'
      },
      {
        Header: 'Frequency',
        accessor: 'schedule'
      },
      {
        Header: 'Next Run Date',
        accessor: 'nextRunTime'
      },
      {
        Header: 'Created',
        accessor: 'createTime'
      },
      {
        Header: 'Latest Execution Jobs',
        accessor: 'jobState'
      },
      {
        Header: 'Status',
        accessor: 'status'
      },
      {
        Header: 'Actions',
        accessor: 'actions'
      }
    ],
    []
  );

  /**
   * Get list of schedules
   */
  const listVertexScheduleInfoAPI = async (
    nextToken: string | null | undefined
  ) => {
    setIsLoading(true);

    await VertexServices.listVertexSchedules(
      setScheduleList,
      region,
      setIsLoading,
      setIsApiError,
      setApiError,
      setNextPageToken,
      nextToken,
      setCanNextPage,
      setApiEnableUrl,
      scheduleListPageLength,
      abortControllers
    );
    setRegionDisable(false);
    setIsLoading(false);
  };

  /**
   * For applying pagination
   */
  useEffect(() => {
    const hasListChanged = previousScheduleList.current !== vertexScheduleList;
    const hasNextPageTokenChanged =
      previousNextPageToken.current !== nextPageToken;
    // Reset pagination variables only if the list has changed or next page token has changed
    // or if the resetToCurrentPage is true.
    if (resetToCurrentPage || (hasListChanged && hasNextPageTokenChanged)) {
      setPaginationVariables();

      if (hasListChanged && hasNextPageTokenChanged) {
        previousScheduleList.current = vertexScheduleList;
        previousNextPageToken.current = nextPageToken;
      }
    }
    setActivePaginationVariables(null); // reset once api has loaded the active pagination variables on return back
  }, [nextPageToken, vertexScheduleList, scheduleListPageLength]);
  /**
   * Pagination variables
   */
  const setPaginationVariables = () => {
    let updatedPageTokenList = [...pageTokenList];
    let currentPageNumber = pageNumber;
    let resetFlag = resetToCurrentPage;
    if (fetchPreviousPage) {
      // True only in case of clicking for previous page
      if (updatedPageTokenList.length > 0) {
        updatedPageTokenList = updatedPageTokenList.slice(0, -1); // Remove the token for accessing current page
      }
      setFetchPreviousPage(false);
      currentPageNumber = Math.max(1, currentPageNumber - 1);
    } else if (resetToCurrentPage) {
      //Logic to refresh or reset current page. In case of Actions/ refresh
      if (updatedPageTokenList.length > 0 && nextPageToken) {
        updatedPageTokenList = updatedPageTokenList.slice(0, -1); // remove nextpage's token if not in last page
      }
      setResetToCurrentPage(false); // to make sure ttoken list is not refreshed again.
      resetFlag = false;
    } else if (fetchNextPage) {
      //only if incrementing to next page
      currentPageNumber += 1;
      setFetchNextPage(false);
    }

    let hasNextPage = false;

    if (nextPageToken) {
      hasNextPage = true;
      // add new token after getting paginated token list; and has set Previous flag.; if new nextPageToken is available
      if (
        !updatedPageTokenList.includes(nextPageToken) &&
        previousNextPageToken.current !== nextPageToken &&
        !resetFlag
      ) {
        // to make sure the token is added only once and is not the one deleted during refresh.
        updatedPageTokenList = [...updatedPageTokenList, nextPageToken]; // set paginated token list and the new token list.
      }
    }
    setCanNextPage(hasNextPage);
    const hasPreviousPage = hasNextPage
      ? updatedPageTokenList.length > 1
      : updatedPageTokenList.length > 0; // hasPreviousPage is true if there are more than 1 tokens in the list, which means there is a previous page available.
    setCanPreviousPage(hasPreviousPage); // false only on first page
    setPageTokenList([...updatedPageTokenList]); // set the updated token list after pagination

    setPageNumber(currentPageNumber);
    if (!hasNextPage) {
      setTotalCount(currentPageNumber); // Total count is found when we reach the final page
    }
  };

  /**
   * Handles next page navigation
   */
  const handleNextPage = async () => {
    abortApiCall(); //Abort last run execution api call
    setFetchNextPage(true);
    const nextTokenToFetch =
      pageTokenList.length > 0 ? pageTokenList[pageTokenList.length - 1] : null;

    await listVertexScheduleInfoAPI(nextTokenToFetch); // call API with the last item in token list.
  };

  /**
   * Handles previous page navigation
   */
  const handlePreviousPage = async () => {
    abortApiCall(); //Abort last run execution api call
    setFetchPreviousPage(true);
    if (pageTokenList.length > 0) {
      setIsLoading(true); // Indicate loading during page transition
      let updatedTokens = [...pageTokenList];
      if (nextPageToken) {
        updatedTokens = updatedTokens.slice(0, -1); // removing next page's token if available
        setPageTokenList(updatedTokens);
      }
      if (updatedTokens.length > 0) {
        updatedTokens = updatedTokens.slice(0, -1); // removing current page's token
        const nextTokenToFetch = updatedTokens[updatedTokens.length - 1]; //Reading last element (previous page's token to fetch) for fetching
        await listVertexScheduleInfoAPI(nextTokenToFetch); // Step 3 API call
      } else {
        await listVertexScheduleInfoAPI(null); // In case there are no more tokens after popping, fetch first page.
      }
    } else {
      // when there is no more tokens and should fetch first page.
      await listVertexScheduleInfoAPI(null);
    }
  };

  /**
   *
   * @param pageTokenListToLoad available only in case navigating  back from another screen
   * @param nextPageTokenToLoad available only in case navigating back from another screen
   */
  const handleCurrentPageRefresh = async (
    pageTokenListToLoad: string[] | undefined | null,
    nextPageTokenToLoad: string | null | undefined
  ) => {
    setRegionDisable(true);
    abortApiCall(); //Abort last run execution api call
    setResetToCurrentPage(true);
    //fetching the current page token from token list: on the last page its the last element, null if on first page, 2nd last element on other pages.
    let currentPageToken = null;
    if (pageTokenListToLoad) {
      // if navigating back, load the same page.
      currentPageToken = nextPageTokenToLoad
        ? pageTokenListToLoad.length > 1
          ? pageTokenListToLoad[pageTokenListToLoad.length - 2]
          : null
        : pageTokenListToLoad.length > 0
          ? pageTokenListToLoad[pageTokenListToLoad.length - 1]
          : null;
    } else {
      // in case of a simple same page refresh.
      currentPageToken = nextPageToken
        ? pageTokenList.length > 1
          ? pageTokenList[pageTokenList.length - 2]
          : null
        : pageTokenList.length > 0
          ? pageTokenList[pageTokenList.length - 1]
          : null;
    }
    listVertexScheduleInfoAPI(currentPageToken);
  };
  /**
   * Handle resume and pause
   * @param {string} scheduleId unique ID for schedule
   * @param {string} is_status_paused modfied status of schedule
   * @param {string} displayName name of schedule
   */
  const handleUpdateScheduler = async (
    scheduleId: string,
    is_status_paused: string,
    displayName: string,
    newPageToken: string | null | undefined
  ) => {
    if (is_status_paused === 'ACTIVE') {
      await VertexServices.handleUpdateSchedulerPauseAPIService(
        scheduleId,
        region,
        displayName,
        setResumeLoading,
        abortControllers
      );
    } else {
      await VertexServices.handleUpdateSchedulerResumeAPIService(
        scheduleId,
        region,
        displayName,
        setResumeLoading,
        abortControllers
      );
    }
    handleCurrentPageRefresh(null, null);
  };

  /**
   * Trigger a job immediately
   * @param {React.ChangeEvent<HTMLInputElement>} e - event triggered by the trigger button.
   * @param {string} displayName name of schedule
   */
  const handleTriggerSchedule = async (
    event: React.MouseEvent,
    displayName: string
  ) => {
    const scheduleId = event.currentTarget.getAttribute('data-scheduleId');
    if (scheduleId !== null) {
      await VertexServices.triggerSchedule(
        region,
        scheduleId,
        displayName,
        setTriggerLoading,
        abortControllers
      );
    }

    handleCurrentPageRefresh(null, null);
  };

  /**
   * Delete pop up
   * @param {string} schedule_id Id of schedule
   * @param {string} displayName name of schedule
   */
  const handleDeletePopUp = (schedule_id: string, displayName: string) => {
    setUniqueScheduleId(schedule_id);
    setScheduleDisplayName(displayName);
    setDeletePopupOpen(true);
  };

  /**
   * Cancel delete pop up
   */
  const handleCancelDelete = () => {
    setDeletePopupOpen(false);
  };

  /**
   * Handles the deletion of a scheduler by invoking the API service to delete it.
   */
  const handleDeleteScheduler = async (
    newPageToken: string | null | undefined
  ) => {
    setDeletingSchedule(true);
    resetPaginationVariables(true); // Reset pagination variables to fetch the first page after deletion
    const deleteResponse = await VertexServices.handleDeleteSchedulerAPIService(
      region,
      uniqueScheduleId,
      scheduleDisplayName
    );
    if (deleteResponse && deleteResponse.done) {
      await listVertexScheduleInfoAPI(null); // Refresh the list after deletion
      Notification.success(
        `Deleted job ${scheduleDisplayName}. It might take a few minutes for the job to be deleted from the list of jobs.`,
        {
          autoClose: false
        }
      );
    } else {
      Notification.error(`Failed to delete the ${scheduleDisplayName}`, {
        autoClose: false
      });
    }
    setDeletePopupOpen(false);
    setDeletingSchedule(false);
  };

  /**
   * Handles the editing of a vertex by triggering the editVertexSchedulerService.
   * @param {React.ChangeEvent<HTMLInputElement>} event - event triggered by the edit vertex button.
   */
  const handleEditVertex = async (event: React.MouseEvent) => {
    const scheduleId = event.currentTarget.getAttribute('data-scheduleId');
    if (scheduleId !== null) {
      await VertexServices.editVertexSchedulerService(
        scheduleId,
        region,
        setInputNotebookFilePath,
        setEditNotebookLoading
      );
    }
  };

  /**
   * Edit job
   * @param {React.ChangeEvent<HTMLInputElement>} e - event triggered by the edit job button.
   */
  const handleEditJob = async (
    event: React.MouseEvent,
    displayName: string
  ) => {
    abortApiCall();
    const job_id = event.currentTarget.getAttribute('data-jobid');

    if (job_id !== null) {
      await VertexServices.editVertexSJobService(
        job_id,
        region,
        setEditScehduleLoading,
        setCreateCompleted,
        setRegion,
        setSubNetworkList,
        setEditMode,
        abortControllers,
        setVertexScheduleDetails
      );
    }
  };
  /**
   * Function that redirects to Job Execution History
   * @param schedulerData schedule data to be retrieved
   * @param scheduleName name of the schedule
   * @param paginationVariables current page details (to be restored when user clicks back to Schedule Listing)
   * @param region selected region for the job (to be reatianed when user clicks back to Schedule Listing)
   */
  const handleScheduleIdSelectionFromList = (
    schedulerData: any,
    scheduleName: string
  ) => {
    abortApiCall();
    handleScheduleIdSelection(
      schedulerData,
      scheduleName,
      saveActivePaginationVariables(),
      region
    );
  };
  /**
   * Function that stores all paginationtion related data for future restoration.
   */
  const saveActivePaginationVariables = () => {
    const currentPaginationVariables: IActivePaginationVariables | undefined = {
      scheduleListPageLength: scheduleListPageLength,
      totalCount: totalCount,
      pageTokenList: pageTokenList,
      nextPageToken: nextPageToken,
      pageNumber: pageNumber
    };
    return currentPaginationVariables;
  };

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow,
    page
  } = useTable(
    {
      //@ts-expect-error react-table 'columns' which is declared here on type 'TableOptions<IDagList>'
      columns,
      data,
      autoResetPage: false,
      initialState: { pageSize: scheduleListPageLength },
      manualPagination: true
    },
    usePagination
  );

  const renderActions = (data: any) => {
    const is_status_paused = data.status;
    return (
      <div className="actions-icon-btn">
        {data.name === resumeLoading ? (
          <div className="icon-buttons-style">
            <CircularProgress
              size={18}
              aria-label="Loading Spinner"
              data-testid="loader"
            />
          </div>
        ) : (
          <div
            role="button"
            className="icon-buttons-style"
            title={
              is_status_paused === 'COMPLETED'
                ? 'Completed'
                : is_status_paused === 'PAUSED'
                  ? 'Resume'
                  : 'Pause'
            }
            onClick={e => {
              is_status_paused !== 'COMPLETED' &&
                handleUpdateScheduler(
                  data.name,
                  is_status_paused,
                  data.displayName,
                  null
                );
            }}
          >
            {is_status_paused === 'COMPLETED' ? (
              <iconPlay.react
                tag="div"
                className="icon-buttons-style-disable disable-complete-btn"
              />
            ) : is_status_paused === 'PAUSED' ? (
              <iconPlay.react
                tag="div"
                className="icon-white logo-alignment-style"
              />
            ) : (
              <iconPause.react
                tag="div"
                className="icon-white logo-alignment-style"
              />
            )}
          </div>
        )}
        {data.name === triggerLoading ? (
          <div className="icon-buttons-style">
            <CircularProgress
              size={18}
              aria-label="Loading Spinner"
              data-testid="loader"
            />
          </div>
        ) : (
          <div
            role="button"
            className="icon-buttons-style"
            title="Trigger the job"
            data-scheduleId={data.name}
            onClick={e => handleTriggerSchedule(e, data.displayName)}
          >
            <iconTrigger.react
              tag="div"
              className="icon-white logo-alignment-style"
            />
          </div>
        )}
        {is_status_paused === 'COMPLETED' ? (
          <iconEditNotebook.react
            tag="div"
            className="icon-buttons-style-disable"
          />
        ) : data.name === editScheduleLoading ? (
          <div className="icon-buttons-style">
            <CircularProgress
              size={18}
              aria-label="Loading Spinner"
              data-testid="loader"
            />
          </div>
        ) : (
          <div
            role="button"
            className="icon-buttons-style"
            title="Edit Schedule"
            data-jobid={data.name}
            onClick={e => handleEditJob(e, data.displayName)}
          >
            <iconEditNotebook.react
              tag="div"
              className="icon-white logo-alignment-style"
            />
          </div>
        )}
        {isPreview &&
          (data.name === editNotebookLoading ? (
            <div className="icon-buttons-style">
              <CircularProgress
                size={18}
                aria-label="Loading Spinner"
                data-testid="loader"
              />
            </div>
          ) : (
            <div
              role="button"
              className="icon-buttons-style"
              title="Edit Notebook"
              data-scheduleId={data.name}
              onClick={e => handleEditVertex(e)}
            >
              <iconEditDag.react
                tag="div"
                className="icon-white logo-alignment-style"
              />
            </div>
          ))}
        <div
          role="button"
          className="icon-buttons-style"
          title="Delete"
          onClick={() => handleDeletePopUp(data.name, data.displayName)}
        >
          <iconDelete.react
            tag="div"
            className="icon-white logo-alignment-style"
          />
        </div>
      </div>
    );
  };

  const tableDataCondition = (cell: IVertexCellProps) => {
    if (cell.column.Header === 'Actions') {
      return (
        <td
          {...cell.getCellProps()}
          className="clusters-table-data table-cell-overflow"
        >
          {renderActions(cell.row.original)}
        </td>
      );
    } else if (cell.column.Header === 'Schedule Name') {
      return (
        <td
          {...cell.getCellProps()}
          className="clusters-table-data table-cell-overflow"
        >
          <span
            onClick={() =>
              handleScheduleIdSelectionFromList(cell.row.original, cell.value)
            }
          >
            {cell.value}
          </span>
        </td>
      );
    } else if (cell.column.Header === 'Created') {
      return (
        <td
          {...cell.getCellProps()}
          className="clusters-table-data table-cell-overflow"
        >
          {dayjs(cell.row.original.createTime).format('MMM DD, YYYY h:mm A')}
        </td>
      );
    } else if (cell.column.Header === 'Next Run Date') {
      return (
        <td
          {...cell.getCellProps()}
          className="clusters-table-data table-cell-overflow"
        >
          {cell.row.original.status === 'COMPLETED' ||
          cell.row.original.status === 'PAUSED' ? (
            <iconDash.react tag="div" />
          ) : (
            dayjs(cell.row.original.nextRunTime).format('lll')
          )}
        </td>
      );
    } else if (cell.column.Header === 'Latest Execution Jobs') {
      return (
        <td
          {...cell.getCellProps()}
          className="clusters-table-data table-cell-overflow"
        >
          {cell.row.original.jobState ? (
            cell.row.original.jobState.length > 0 ? (
              <div className="execution-history-main-wrapper">
                {cell.row.original.jobState.map(job => {
                  return (
                    <>
                      {job === 'JOB_STATE_SUCCEEDED' ? (
                        <iconSuccess.react
                          tag="div"
                          title={job}
                          className="icon-white logo-alignment-style success_icon icon-size icon-completed"
                        />
                      ) : job === 'JOB_STATE_FAILED' ||
                        job === 'JOB_STATE_EXPIRED' ||
                        job === 'JOB_STATE_PARTIALLY_SUCCEEDED' ? (
                        <iconFailed.react
                          tag="div"
                          title={job}
                          className="logo-alignment-style success_icon icon-size icon-completed"
                        />
                      ) : (
                        <iconPending.react
                          tag="div"
                          title={job}
                          className="logo-alignment-style success_icon icon-size icon-completed"
                        />
                      )}
                    </>
                  );
                })}
              </div>
            ) : (
              <iconPending.react
                tag="div"
                title="No Job State Found"
                className="logo-alignment-style success_icon icon-size icon-completed"
              />
            )
          ) : (
            <CircularProgress
              className="spin-loader-custom-style"
              size={18}
              aria-label="Loading Spinner"
              data-testid="loader"
            />
          )}
        </td>
      );
    } else {
      const alignIcon =
        cell.row.original.status === 'ACTIVE' ||
        cell.row.original.status === 'PAUSED' ||
        cell.row.original.status === 'COMPLETED';

      const { status, lastScheduledRunResponse } = cell.row.original;
      const runResponse = lastScheduledRunResponse
        ? lastScheduledRunResponse.runResponse
        : '';

      const getStatusIcon = () => {
        type StatusKey = 'ACTIVE' | 'PAUSED' | 'COMPLETED';
        const allowedStatuses: ReadonlyArray<StatusKey> = [
          'ACTIVE',
          'PAUSED',
          'COMPLETED'
        ];
        const iconMap: {
          [key in StatusKey | 'default']: () => React.ReactElement;
        } = {
          ACTIVE: () => (
            <iconActive.react
              tag="div"
              title="ACTIVE"
              className="icon-white logo-alignment-style success_icon icon-size-status"
            />
          ),
          PAUSED: () => (
            <iconListPause.react
              tag="div"
              title="PAUSE"
              className="icon-white logo-alignment-style success_icon icon-size"
            />
          ),
          COMPLETED: () => {
            if (!lastScheduledRunResponse) {
              return (
                <div>
                  <iconSuccess.react
                    tag="div"
                    title="COMPLETED"
                    className="icon-white logo-alignment-style success_icon icon-size icon-completed"
                  />
                </div>
              );
            }
            if (runResponse !== 'OK') {
              return (
                <div>
                  <iconListCompleteWithError.react
                    tag="div"
                    title={runResponse}
                    className="icon-white logo-alignment-style success_icon icon-size-status"
                  />
                </div>
              );
            }
            return (
              <div>
                <iconSuccess.react
                  tag="div"
                  title="COMPLETED"
                  className="icon-white logo-alignment-style success_icon icon-size icon-completed"
                />
              </div>
            );
          },
          default: () => (
            <div>
              <iconFailed.react
                tag="div"
                title={!lastScheduledRunResponse ? 'Not started' : runResponse}
                className="icon-white logo-alignment-style success_icon icon-size"
              />
            </div>
          )
        };

        return allowedStatuses.includes(status as StatusKey)
          ? iconMap[status as StatusKey]()
          : iconMap.default();
      };

      return (
        <td
          {...cell.getCellProps()}
          className={
            cell.column.Header === 'Schedule'
              ? 'clusters-table-data table-cell-overflow'
              : 'clusters-table-data'
          }
        >
          {cell.column.Header === 'Status' ? (
            <>
              <div className="execution-history-main-wrapper">
                {getStatusIcon()}
                <div className={alignIcon ? 'text-icon' : ''}>
                  {cell.render('Cell')}
                </div>
              </div>
            </>
          ) : (
            <div className="cell-width-listing">{cell.render('Cell')}</div>
          )}
        </td>
      );
    }
  };

  const openEditVertexNotebookFile = async () => {
    const filePath = inputNotebookFilePath.replace('gs://', 'gs:');
    const openNotebookFile = await app.commands.execute('docmanager:open', {
      path: filePath
    });
    setInputNotebookFilePath('');
    if (openNotebookFile) {
      setEditNotebookLoading('');
    }
  };

  useEffect(() => {
    if (inputNotebookFilePath !== '') {
      openEditVertexNotebookFile();
    }
  }, [inputNotebookFilePath]);

  useEffect(() => {
    setListingScreenFlag(true);
    window.scrollTo(0, 0);
    return () => {
      abortApiCall(); // Abort any ongoing requests on component unmount
      setListingScreenFlag(false);
    };
  }, []);

  useEffect(() => {
    if (region !== '') {
      if (activePaginationVariables) {
        setBackPaginationVariables();
      } else {
        resetPaginationVariables(true);
      }
      handleCurrentPageRefresh(
        activePaginationVariables?.pageTokenList,
        activePaginationVariables?.nextPageToken
      );
    }
  }, [region]);

  useEffect(() => {
    setLoaderRegion(true);
    authApi()
      .then(credentials => {
        if (credentials && credentials?.region_id && credentials.project_id) {
          if (!createMode && !activePaginationVariables) {
            setLoaderRegion(false);
            if (!region) {
              setRegion(credentials.region_id);
            }
          }
          setProjectId(credentials.project_id);
        }
      })
      .catch(error => {
        console.error(error);
      });
  }, [projectId]);

  /**
   * Setting back pagination variables.
   */
  const setBackPaginationVariables = () => {
    setScheduleListPageLength(
      activePaginationVariables?.scheduleListPageLength ??
        scheduleListPageLength
    );
    setTotalCount(activePaginationVariables?.totalCount ?? totalCount);
    setPageTokenList(activePaginationVariables?.pageTokenList ?? pageTokenList);
    setNextPageToken(activePaginationVariables?.nextPageToken ?? nextPageToken);
    setPageNumber(activePaginationVariables?.pageNumber ?? pageNumber);
    previousNextPageToken.current =
      activePaginationVariables?.nextPageToken ?? nextPageToken;
  };

  /**
   *
   * @param reloadPagination parameter specifies if the page has to refresh.
   * Function resets all variables except nextPageToken
   * which would be automatically taken care during rendering.
   */
  const resetPaginationVariables = (reloadPagination: boolean) => {
    setActivePaginationVariables(null); //
    setIsLoading(true);
    setResetToCurrentPage(reloadPagination);
    setCanPreviousPage(false);
    setCanNextPage(false);
    setPageNumber(1);
    setTotalCount(0);
    setPageTokenList([]);
  };

  return (
    <div>
      <div className="select-text-overlay-scheduler">
        <div className="enable-text-label">
          <div className="create-scheduler-form-element content-pd-space ">
            <RegionDropdown
              projectId={projectId}
              region={region}
              onRegionChange={region => setRegion(region)}
              regionsList={VERTEX_REGIONS}
              regionDisable={regionDisable}
              fromPage={VERTEX_SCHEDULE}
              loaderRegion={loaderRegion}
            />
            {!isLoading && !region && (
              <ErrorMessage message="Region is required" showIcon={false} />
            )}
          </div>
        </div>

        <div className="btn-refresh">
          <Button
            disabled={isLoading}
            className="btn-refresh-text"
            variant="outlined"
            aria-label="cancel Batch"
            onClick={() => {
              handleCurrentPageRefresh(null, null);
            }}
          >
            <div>REFRESH</div>
          </Button>
        </div>
      </div>

      {vertexScheduleList.length > 0 || nextPageToken ? (
        <>
          <div className="notebook-templates-list-tabl e-parent vertex-list-table-parent table-space-around scroll-list">
            <TableData
              getTableProps={getTableProps}
              headerGroups={headerGroups}
              getTableBodyProps={getTableBodyProps}
              isLoading={isLoading}
              rows={rows}
              page={page}
              prepareRow={prepareRow}
              tableDataCondition={tableDataCondition}
              fromPage="Vertex schedulers"
            />
            {vertexScheduleList.length > 0 && (
              <PaginationComponent
                canPreviousPage={canPreviousPage}
                canNextPage={canNextPage}
                pageNumber={pageNumber}
                handleNextPage={handleNextPage}
                handlePreviousPage={handlePreviousPage}
                isLoading={isLoading}
                totalCount={totalCount}
              />
            )}
            {deletePopupOpen && (
              <DeletePopup
                onCancel={() => handleCancelDelete()}
                onDelete={() => handleDeleteScheduler(null)}
                deletePopupOpen={deletePopupOpen}
                DeleteMsg={`This will delete ${scheduleDisplayName} and cannot be undone.`}
                deletingSchedule={deletingSchedule}
              />
            )}
          </div>
        </>
      ) : (
        <div>
          {isLoading && (
            <div className="spin-loader-main spin-loader-listing">
              <CircularProgress
                className="spin-loader-custom-style"
                size={18}
                aria-label="Loading Spinner"
                data-testid="loader"
              />
              Loading Vertex Schedules
            </div>
          )}
          {!isLoading && (
            <div className="no-data-style">No schedules available</div>
          )}
        </div>
      )}
    </div>
  );
}

export default ListVertexScheduler;
