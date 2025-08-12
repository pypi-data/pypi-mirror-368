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

import React, { useState, useEffect } from 'react';
import 'react-toastify/dist/ReactToastify.css';
import { IExpandableToastProps } from './SchedulerInteface';

const ExpandToastMessage: React.FC<IExpandableToastProps> = ({
  message,
  ...rest
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [truncatedMessage, setTruncatedMessage] = useState('');
  const [showExpandButton, setShowExpandButton] = useState(false);
  const truncateLength = 50; // Adjust as needed

  useEffect(() => {
    if (message.length > truncateLength) {
      setTruncatedMessage(message.substring(0, truncateLength) + '  ');
      setShowExpandButton(true);
    } else {
      setTruncatedMessage(message);
      setShowExpandButton(false);
    }
  }, [message, truncateLength]);

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className="cursor-icon">
      {isExpanded ? message : truncatedMessage}
      {showExpandButton && !isExpanded && (
        <span className="expand-btn" onClick={toggleExpand}>
          {' '}
          Show more
        </span>
      )}
      {showExpandButton && isExpanded && (
        <span className="expand-btn" onClick={toggleExpand}>
          {' '}
          Show less
        </span>
      )}
    </div>
  );
};

export default ExpandToastMessage;
