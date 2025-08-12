import React, { useEffect, useState } from 'react';
import { VertexServices } from '../../services/Vertex';
import { iconDownload } from '../../utils/Icons';
import { CircularProgress } from '@mui/material';
import { StorageServices } from '../../services/Storage';

const VertexExecutionHistoryActions = ({
  data,
  jobRunId,
  state,
  gcsUrl,
  fileName,
  scheduleName,
  abortControllers
}: {
  data: { id: string; status: string };
  jobRunId?: string;
  state?: string;
  gcsUrl?: string;
  fileName?: string;
  scheduleName: string;
  abortControllers: any;
}) => {
  const [jobDownloadLoading, setJobDownloadLoading] = useState(false);
  const [
    downloadOutputVertexScheduleRunId,
    setDownloadOutputVertexScheduleRunId
  ] = useState<string | undefined>('');
  const [isLoading, setIsLoading] = useState<boolean>(state === 'failed');
  const [fileExists, setFileExists] = useState<boolean>(false);
  const bucketName = gcsUrl?.split('//')[1];

  const outPutFileExistsApi = async () => {
    await VertexServices.outputFileExists(
      bucketName,
      jobRunId,
      fileName,
      setIsLoading,
      setFileExists,
      abortControllers
    );
  };

  /**
   * Handles the download of a job's output by triggering the download API service.
   * @param {Object} data - The data related to the job run and output.
   * @param {string} data.id - The optional ID of the job run.
   * @param {string} data.status - The optional status of the job run.
   * @param {string} data.jobRunId - The optional job run ID associated with the job output.
   * @param {string} data.state - The optional state of the job run.
   * @param {string} data.gcsUrl - The URL of the output file in Google Cloud Storage (GCS).
   * @param {string} data.fileName - The name of the file to be downloaded.
   */
  const handleDownloadOutput = async (data: {
    id?: string;
    status?: string;
    jobRunId?: string;
    state?: string;
    gcsUrl?: string;
    fileName?: string;
  }) => {
    setDownloadOutputVertexScheduleRunId(data.jobRunId);
    await StorageServices.downloadJobAPIService(
      data.gcsUrl,
      data.fileName,
      data.jobRunId,
      setJobDownloadLoading,
      scheduleName
    );
  };

  useEffect(() => {
    if (state === 'failed') {
      outPutFileExistsApi();
    }
  }, []);

  return (
    <div className="action-btn-execution">
      {isLoading ||
      (jobDownloadLoading && jobRunId === downloadOutputVertexScheduleRunId) ? (
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
          className={
            state === 'succeeded' || fileExists
              ? 'icon-buttons-style sub-title-heading'
              : 'icon-buttons-style-disable sub-title-heading'
          }
          title="Download Output"
          data-dag-run-id={data}
          onClick={
            state === 'succeeded' || fileExists
              ? e => handleDownloadOutput(data)
              : undefined
          }
        >
          <iconDownload.react tag="div" />
        </div>
      )}
    </div>
  );
};

export default VertexExecutionHistoryActions;
