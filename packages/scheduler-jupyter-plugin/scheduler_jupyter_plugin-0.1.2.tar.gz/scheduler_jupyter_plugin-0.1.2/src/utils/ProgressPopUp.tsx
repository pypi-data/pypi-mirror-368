import { CircularProgress } from '@mui/material';
import React from 'react';
import { ToastContentProps } from 'react-toastify';

export const ProgressPopUp = ({
  data
}: ToastContentProps<{ message: string }>) => {
  return (
    <div>
      <div className="progress-main">
        <span className="progress-message">{data!.message}</span>
        <span>
          <CircularProgress
            size={18}
            aria-label="Loading Spinner"
            data-testid="loader"
            className="spinner-loader-modal "
          />
        </span>
      </div>
    </div>
  );
};
