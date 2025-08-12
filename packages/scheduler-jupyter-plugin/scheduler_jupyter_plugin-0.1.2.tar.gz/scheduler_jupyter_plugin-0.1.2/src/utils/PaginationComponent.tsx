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

import React from 'react';
import { iconPrevious, iconNext } from './Icons';
import { IPaginationViewProps } from '../scheduler/vertex/VertexInterfaces';

export const PaginationComponent = ({
  canPreviousPage,
  canNextPage,
  pageNumber,
  handleNextPage,
  handlePreviousPage,
  isLoading,
  totalCount
}: IPaginationViewProps) => {
  return (
    <div>
      {isLoading ? null : (
        <div className="pagination-parent-view-main">
          <div className="pagination-numbers" aria-disabled={isLoading}>
            Page {pageNumber} of {totalCount !== 0 ? totalCount : 'Many'}
          </div>

          <div
            role={!canPreviousPage || isLoading ? undefined : 'button'}
            onClick={() =>
              !canPreviousPage || isLoading ? undefined : handlePreviousPage()
            }
            aria-disabled={!canPreviousPage || isLoading}
          >
            {canPreviousPage && !isLoading ? (
              <iconPrevious.react
                tag="div"
                className="logo-alignment-style cursor-icon"
              />
            ) : (
              <iconPrevious.react
                tag="div"
                className="icon-buttons-style-disable disable-complete-btn"
              />
            )}
          </div>

          <div
            role={!canNextPage || isLoading ? undefined : 'button'}
            onClick={() =>
              !canNextPage || isLoading ? undefined : handleNextPage()
            }
            aria-disabled={!canNextPage || isLoading}
          >
            {canNextPage && !isLoading ? (
              <iconNext.react
                tag="div"
                className="logo-alignment-style cursor-icon"
              />
            ) : (
              <iconNext.react
                tag="div"
                className="icon-buttons-style-disable disable-complete-btn" // Optional class for further styling
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
};
