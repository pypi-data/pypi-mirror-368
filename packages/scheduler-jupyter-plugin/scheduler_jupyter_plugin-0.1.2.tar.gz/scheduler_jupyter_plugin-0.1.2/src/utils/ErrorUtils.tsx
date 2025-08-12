import React from 'react';
import { toast } from 'react-toastify';
import { Notification } from '@jupyterlab/apputils';
import ExpandToastMessage from '../scheduler/common/ExpandToastMessage';
import { toastifyCustomStyle, toastifyCustomWidth } from './Config';

// Recursively search for a 'message' key in an object
function findMessage(obj: any): string | undefined {
  if (!obj || typeof obj !== 'object') {
    return undefined;
  }
  if ('message' in obj && typeof obj.message === 'string') {
    return obj.message;
  }
  for (const key of Object.keys(obj)) {
    const found = findMessage(obj[key]);
    if (found) {
      return found;
    }
  }
  return undefined;
}

// Extract URLs from a string using regex
export function extractUrls(text: string): string[] {
  if (!text) {
    return [];
  }
  /* eslint-disable */
  const urlPattern =
    /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/g;
  return text.match(urlPattern) || [];
}

/**
 * Handles error for toast and URL extraction.
 * @param error - error string or object
 * @param toast - toast function (e.g., toast.error)
 * @param toastifyCustomStyle - style for toast
 * @param toastifyCustomWidth - style for long messages
 * @param setApiEnableUrl - function to set URLs (optional)
 */
export function handleErrorToast({
  error,
  setApiEnableUrl
}: {
  error: any;
  setApiEnableUrl?: (urls: string[]) => void;
}) {
  let errorMessage: string | undefined;
  const errorStr = typeof error === 'string' ? error : JSON.stringify(error);

  // Try to parse JSON if error is a string and looks like JSON
  let errorObj: any = error;
  if (typeof error === 'string') {
    try {
      // Try to extract JSON substring if present
      const jsonStart = error.indexOf('{');
      const jsonEnd = error.lastIndexOf('}');
      if (jsonStart !== -1 && jsonEnd !== -1) {
        const jsonStr = error.slice(jsonStart, jsonEnd + 1);
        errorObj = JSON.parse(jsonStr);
      }
    } catch {
      // ignore parse errors
    }
  }

  // Recursively find a message
  errorMessage = findMessage(errorObj);

  // Fallback to the whole error string if no message found
  const displayMessage = errorMessage || errorStr;

  // Extract URLs
  const urls = extractUrls(errorStr);
  if (setApiEnableUrl && urls.length > 0) {
    setApiEnableUrl(urls);
  }

  // Show toast or Notification
  if (typeof displayMessage === 'string' && displayMessage.length < 140) {
    Notification.error(displayMessage, { autoClose: false });
  } else if (
    typeof displayMessage === 'string' &&
    displayMessage.length < 500
  ) {
    toast.error(displayMessage, toastifyCustomStyle);
  } else {
    toast.error(
      <ExpandToastMessage message={displayMessage} />,
      toastifyCustomWidth
    );
  }
}
