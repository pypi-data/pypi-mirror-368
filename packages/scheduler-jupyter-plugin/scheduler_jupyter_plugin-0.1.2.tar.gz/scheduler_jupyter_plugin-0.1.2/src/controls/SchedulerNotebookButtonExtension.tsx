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
import { JupyterLab } from '@jupyterlab/application';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { IDisposable } from '@lumino/disposable';
import { LabIcon } from '@jupyterlab/ui-components';
import { NotebookPanel, INotebookModel } from '@jupyterlab/notebook';
import {
  ToolbarButton,
  MainAreaWidget,
  IThemeManager
} from '@jupyterlab/apputils';
import notebookSchedulerIcon from '../../style/icons/scheduler_calendar_month.svg';
import { NotebookScheduler } from '../scheduler/NotebookScheduler';
import { ISettingRegistry } from '@jupyterlab/settingregistry';

const iconNotebookScheduler = new LabIcon({
  name: 'launcher:notebook-scheduler-icon',
  svgstr: notebookSchedulerIcon
});

/**
 * A disposable class to track the toolbar widget for a single notebook.
 */
class NotebookButtonExtensionPoint {
  // IDisposable required.
  isDisposed: boolean;
  private readonly notebookSchedulerButton: ToolbarButton;

  constructor(
    private readonly panel: NotebookPanel,
    private readonly context: DocumentRegistry.IContext<INotebookModel>,
    private readonly app: JupyterLab,
    private readonly settingRegistry: ISettingRegistry,
    private readonly themeManager: IThemeManager
  ) {
    this.isDisposed = false;

    this.notebookSchedulerButton = new ToolbarButton({
      icon: iconNotebookScheduler,
      onClick: () => {
        this.onNotebookSchedulerClick();
      },
      tooltip: 'Job Scheduler',
      className: 'dark-theme-logs'
    });

    this.panel.toolbar.insertItem(
      1000,
      'notebook-scheduler',
      this.notebookSchedulerButton
    );
  }

  dispose(): void {
    if (this.isDisposed) {
      return;
    }
    this.notebookSchedulerButton.dispose();
    this.isDisposed = true;
  }

  private readonly onNotebookSchedulerClick = () => {
    const content = new NotebookScheduler(
      this.app as JupyterLab,
      this.themeManager,
      this.settingRegistry as ISettingRegistry,
      this.context
    );
    const widget = new MainAreaWidget<NotebookScheduler>({ content });
    widget.title.label = 'Job Scheduler';
    widget.title.icon = iconNotebookScheduler;
    this.app.shell.add(widget, 'main');
  };
}

export class SchedulerNotebookButtonExtension
  implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel>
{
  constructor(
    private app: JupyterLab,
    private settingRegistry: ISettingRegistry,
    private themeManager: IThemeManager
  ) {}

  createNew(
    panel: NotebookPanel,
    context: DocumentRegistry.IContext<INotebookModel>
  ): IDisposable {
    return new NotebookButtonExtensionPoint(
      panel,
      context,
      this.app,
      this.settingRegistry,
      this.themeManager
    );
  }
}
