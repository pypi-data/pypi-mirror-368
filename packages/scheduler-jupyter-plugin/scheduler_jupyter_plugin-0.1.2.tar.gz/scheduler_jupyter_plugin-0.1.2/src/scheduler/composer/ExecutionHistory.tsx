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

import React, { useEffect, useState } from 'react';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { PickersDayProps } from '@mui/x-date-pickers/PickersDay';
import { DateCalendar } from '@mui/x-date-pickers/DateCalendar';
import dayjs, { Dayjs } from 'dayjs';
import ListDagRuns from './ListDagRuns';
import { LabIcon } from '@jupyterlab/ui-components';
import LeftArrowIcon from '../../../style/icons/left_arrow_icon.svg';
import ListDagTaskInstances from './ListDagTaskInstances';
import { Box, LinearProgress } from '@mui/material';
import { handleDebounce } from '../../utils/Config';
import CustomDate from '../common/CustomDate';

const iconLeftArrow = new LabIcon({
  name: 'launcher:left-arrow-icon',
  svgstr: LeftArrowIcon
});

const ExecutionHistory = ({
  composerName,
  dagId,
  handleBackButton,
  bucketName,
  setExecutionPageFlag,
  projectId,
  region
}: {
  composerName: string;
  dagId: string;
  handleBackButton: () => void;
  bucketName: string;
  setExecutionPageFlag: (value: boolean) => void;
  projectId: string;
  region: string;
}): JSX.Element => {
  const [dagRunId, setDagRunId] = useState('');
  const currentDate = new Date().toLocaleDateString();
  const [selectedDate, setSelectedDate] = useState<Dayjs | null>(null);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [greyListDates, setGreyListDates] = useState<string[]>([]);
  const [redListDates, setRedListDates] = useState<string[]>([]);
  const [greenListDates, setGreenListDates] = useState<string[]>([]);
  const [darkGreenListDates, setDarkGreenListDates] = useState<string[]>([]);

  const [height, setHeight] = useState(window.innerHeight - 145);

  function handleUpdateHeight() {
    const updateHeight = window.innerHeight - 145;
    setHeight(updateHeight);
  }

  // Debounce the handleUpdateHeight function
  const debouncedHandleUpdateHeight = handleDebounce(handleUpdateHeight, 500);

  // Add event listener for window resize using useEffect
  useEffect(() => {
    window.addEventListener('resize', debouncedHandleUpdateHeight);

    // Cleanup function to remove event listener on component unmount
    return () => {
      window.removeEventListener('resize', debouncedHandleUpdateHeight);
    };
  }, []);

  const handleDateSelection = (selectedValue: any) => {
    setDagRunId('');
    setSelectedDate(selectedValue);
  };

  const CustomDay = (props: PickersDayProps<Dayjs>) => {
    const { day, isFirstVisibleCell, isLastVisibleCell } = props;
    if (isFirstVisibleCell) {
      setStartDate(new Date(day.toDate()).toISOString());
    }
    if (isLastVisibleCell) {
      setEndDate(day.toDate().toISOString());
    }

    return (
      <CustomDate
        selectedDate={selectedDate}
        greyListDates={greyListDates}
        redListDates={redListDates}
        greenListDates={greenListDates}
        darkGreenListDates={darkGreenListDates}
        dateProps={props}
      />
    );
  };

  useEffect(() => {
    setSelectedDate(dayjs(currentDate));
    setExecutionPageFlag(false);
  }, []);

  return (
    <>
      <div className="execution-history-header">
        <div
          role="button"
          className="scheduler-back-arrow-icon"
          onClick={() => handleBackButton()}
        >
          <iconLeftArrow.react
            tag="div"
            className="icon-white logo-alignment-style"
          />
        </div>
        <div className="create-job-scheduler-title">
          Execution History: {dagId}
        </div>
      </div>
      <div
        className="execution-history-main-wrapper"
        style={{ height: height }}
      >
        <div className="execution-history-left-wrapper">
          <LocalizationProvider dateAdapter={AdapterDayjs}>
            {isLoading ? (
              <div className="spin-loader-main-execution-history">
                <Box sx={{ width: '100%' }}>
                  <LinearProgress />
                </Box>
              </div>
            ) : (
              <div
                className="spin-loader-main-execution-history"
                style={{ height: '4px' }}
              ></div>
            )}
            <DateCalendar
              minDate={dayjs().year(2024).startOf('year')}
              maxDate={dayjs(currentDate)}
              referenceDate={dayjs(currentDate)}
              onChange={newValue => handleDateSelection(newValue)}
              slots={{
                day: CustomDay
              }}
            />
          </LocalizationProvider>
          {startDate !== '' && endDate !== '' && (
            <ListDagRuns
              composerName={composerName}
              dagId={dagId}
              startDate={startDate}
              endDate={endDate}
              setDagRunId={setDagRunId}
              selectedDate={selectedDate}
              setGreyListDates={setGreyListDates}
              setRedListDates={setRedListDates}
              setGreenListDates={setGreenListDates}
              setDarkGreenListDates={setDarkGreenListDates}
              bucketName={bucketName}
              setIsLoading={setIsLoading}
              isLoading={isLoading}
              projectId={projectId}
              region={region}
            />
          )}
        </div>
        <div className="execution-history-right-wrapper">
          {dagRunId !== '' && (
            <ListDagTaskInstances
              composerName={composerName}
              dagId={dagId}
              dagRunId={dagRunId}
              projectId={projectId}
              region={region}
            />
          )}
        </div>
      </div>
    </>
  );
};

export default ExecutionHistory;
