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

import React, { useRef, useState } from 'react';
import { SchedulerWidget } from '../../controls/SchedulerWidget';
import { JupyterLab } from '@jupyterlab/application';
import { IThemeManager } from '@jupyterlab/apputils';
import ListVertexScheduler from '../vertex/ListVertexScheduler';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import {
  IActivePaginationVariables,
  ICreatePayload,
  ISchedulerData
} from './VertexInterfaces';
import VertexExecutionHistory from './VertexExecutionHistory';

const VertexScheduleJobs = ({
  app,
  createCompleted,
  setCreateCompleted,
  region,
  setRegion,
  setSubNetworkList,
  setEditMode,
  setJobNameSelected,
  setExecutionPageFlag,
  setIsApiError,
  setApiError,
  setExecutionPageListFlag,
  setVertexScheduleDetails,
  setApiEnableUrl,
  setListingScreenFlag,
  createMode
}: {
  app: JupyterLab;
  themeManager: IThemeManager;
  createCompleted?: boolean;
  setCreateCompleted: (value: boolean) => void;
  region: string;
  setRegion: (value: string) => void;
  setSubNetworkList: (value: { name: string; link: string }[]) => void;
  setEditMode: (value: boolean) => void;
  setJobNameSelected?: (value: string) => void;
  setExecutionPageFlag: (value: boolean) => void;
  setIsApiError: (value: boolean) => void;
  setApiError: (value: string) => void;
  setExecutionPageListFlag: (value: boolean) => void;
  setVertexScheduleDetails: (value: ICreatePayload) => void;
  setApiEnableUrl: any;
  setListingScreenFlag: (value: boolean) => void;
  createMode: boolean;
}): React.JSX.Element => {
  const [showExecutionHistory, setShowExecutionHistory] =
    useState<boolean>(false);
  const [schedulerData, setSchedulerData] = useState<ISchedulerData>();
  const [scheduleName, setScheduleName] = useState('');
  const abortControllers = useRef<any>([]); // Array of API signals to abort
  const [activePaginationVariables, setActivePaginationVariables] = useState<
    IActivePaginationVariables | null | undefined
  >();

  /**
   * Handles the back button click event.
   * @param paginationVariables
   * @param region
   */
  const handleBackButton = (
    paginationVariables: React.SetStateAction<
      IActivePaginationVariables | null | undefined
    >,
    regionToLoad: string
  ) => {
    setShowExecutionHistory(false);
    setExecutionPageFlag(true);
    setActivePaginationVariables(paginationVariables);
    setRegion(regionToLoad);
    abortApiCall();
  };

  /**
   * Handles the selection of a DAG ID and updates the state with the selected scheduler data.
   * @param schedulerData
   * @param scheduleName
   * @param paginationVariables
   * @param region
   */
  const handleScheduleIdSelection = (
    schedulerData: any,
    scheduleName: string,
    paginationVariables: IActivePaginationVariables | null | undefined,
    regionToLoad: string
  ) => {
    setShowExecutionHistory(true);
    setScheduleName(scheduleName);
    setSchedulerData(schedulerData);
    setActivePaginationVariables(paginationVariables);
    setRegion(regionToLoad);
  };

  /**
   * Abort Api calls while moving away from page.
   */
  const abortApiCall = () => {
    abortControllers.current.forEach((controller: any) => controller.abort());
    abortControllers.current = [];
  };

  return (
    <>
      {showExecutionHistory ? (
        <VertexExecutionHistory
          region={region}
          setRegion={setRegion}
          schedulerData={schedulerData}
          scheduleName={scheduleName}
          handleBackButton={handleBackButton}
          setExecutionPageFlag={setExecutionPageFlag}
          setExecutionPageListFlag={setExecutionPageListFlag}
          abortControllers={abortControllers}
          abortApiCall={abortApiCall}
          activePaginationVariables={activePaginationVariables}
        />
      ) : (
        <ListVertexScheduler
          region={region}
          setRegion={setRegion}
          app={app}
          createCompleted={createCompleted}
          setCreateCompleted={setCreateCompleted}
          setSubNetworkList={setSubNetworkList}
          setEditMode={setEditMode}
          setJobNameSelected={setJobNameSelected!}
          handleScheduleIdSelection={handleScheduleIdSelection}
          setIsApiError={setIsApiError}
          setApiError={setApiError}
          abortControllers={abortControllers}
          abortApiCall={abortApiCall}
          activePaginationVariables={activePaginationVariables}
          setActivePaginationVariables={setActivePaginationVariables}
          setApiEnableUrl={setApiEnableUrl}
          setVertexScheduleDetails={setVertexScheduleDetails}
          setListingScreenFlag={setListingScreenFlag}
          createMode={createMode}
        />
      )}
    </>
  );
};

export class NotebookJobs extends SchedulerWidget {
  app: JupyterLab;
  settingRegistry: ISettingRegistry;
  setExecutionPageFlag: (value: boolean) => void;
  setCreateCompleted: (value: boolean) => void;
  region: string;
  setRegion: (value: string) => void;
  setSubNetworkList: (value: { name: string; link: string }[]) => void;
  setEditMode: (value: boolean) => void;
  setIsApiError: (value: boolean) => void;
  setApiError: (value: string) => void;
  setExecutionPageListFlag: (value: boolean) => void;
  setVertexScheduleDetails: (value: ICreatePayload) => void;
  setApiEnableUrl: any;
  setListingScreenFlag: (value: boolean) => void;
  createMode: boolean;

  constructor(
    app: JupyterLab,
    settingRegistry: ISettingRegistry,
    themeManager: IThemeManager,
    setExecutionPageFlag: (value: boolean) => void,
    setCreateCompleted: (value: boolean) => void,
    region: string,
    setRegion: (value: string) => void,
    setSubNetworkList: (value: { name: string; link: string }[]) => void,
    setEditMode: (value: boolean) => void,
    setIsApiError: (value: boolean) => void,
    setApiError: (value: string) => void,
    setExecutionPageListFlag: (value: boolean) => void,
    setVertexScheduleDetails: (value: ICreatePayload) => void,
    setApiEnableUrl: any,
    setListingScreenFlag: (value: boolean) => void,
    createMode: boolean
  ) {
    super(themeManager);
    this.app = app;
    this.settingRegistry = settingRegistry;
    this.setExecutionPageFlag = setExecutionPageFlag;
    this.setCreateCompleted = setCreateCompleted;
    this.region = region;
    this.setRegion = setRegion;
    this.setSubNetworkList = setSubNetworkList;
    this.setEditMode = setEditMode;
    this.setExecutionPageFlag = setExecutionPageFlag;
    this.setIsApiError = setIsApiError;
    this.setApiError = setApiError;
    this.setExecutionPageListFlag = setExecutionPageListFlag;
    this.setVertexScheduleDetails = setVertexScheduleDetails;
    this.setApiEnableUrl = setApiEnableUrl;
    this.setListingScreenFlag = setListingScreenFlag;
    this.createMode = createMode;
  }
  renderInternal(): React.JSX.Element {
    return (
      <VertexScheduleJobs
        app={this.app}
        themeManager={this.themeManager}
        setCreateCompleted={this.setCreateCompleted}
        region={this.region}
        setRegion={this.setRegion}
        setSubNetworkList={this.setSubNetworkList}
        setEditMode={this.setEditMode}
        setExecutionPageFlag={this.setExecutionPageFlag}
        setIsApiError={this.setIsApiError}
        setApiError={this.setApiError}
        setExecutionPageListFlag={this.setExecutionPageListFlag}
        setVertexScheduleDetails={this.setVertexScheduleDetails}
        setApiEnableUrl={this.setApiEnableUrl}
        setListingScreenFlag={this.setListingScreenFlag}
        createMode={this.createMode}
      />
    );
  }
}

export default VertexScheduleJobs;
