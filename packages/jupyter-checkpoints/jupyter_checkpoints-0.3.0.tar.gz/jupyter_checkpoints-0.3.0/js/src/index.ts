import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { INotebookTracker } from '@jupyterlab/notebook';
import { IEditorTracker } from '@jupyterlab/fileeditor';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { ToolbarButton, Dialog, showDialog } from '@jupyterlab/apputils';
import { IDisposable } from '@lumino/disposable';
import { Contents } from '@jupyterlab/services';
import { Widget } from '@lumino/widgets';

/**
 * The plugin registration information.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupytercheckpoints:revert-button',
  description: 'A JupyterLab extension adding a revert button to the toolbar.',
  autoStart: true,
  requires: [INotebookTracker, IEditorTracker, IDocumentManager],
  activate: activateRevertButton
};

/**
 * Format the checkpoint date for display
 */
function formatCheckpointDate(date: string): string {
  const d = new Date(date);
  return d.toLocaleString();
}

/**
 * Format checkpoint ID to be more user-friendly
 */
function formatCheckpointId(id: string): string {
  // If the ID is a UUID-like string, shorten it
  if (id.length > 8) {
    return id.substring(0, 8);
  }
  return id;
}

/**
 * Create a more descriptive label for a checkpoint
 */
function createCheckpointLabel(checkpoint: Contents.ICheckpointModel): string {
  const id = formatCheckpointId(checkpoint.id);
  const date = formatCheckpointDate(checkpoint.last_modified);

  // Calculate time difference
  const now = new Date();
  const checkpointDate = new Date(checkpoint.last_modified);
  const diffMs = now.getTime() - checkpointDate.getTime();
  const diffMins = Math.round(diffMs / 60000);
  const diffHours = Math.round(diffMs / 3600000);
  const diffDays = Math.round(diffMs / 86400000);

  let timeAgo;
  if (diffMins < 60) {
    timeAgo = `${diffMins} 分钟前`;
  } else if (diffHours < 24) {
    timeAgo = `${diffHours} 小时前`;
  } else {
    timeAgo = `${diffDays} 天前`;
  }

  return `[id: ${id}] ${date} (${timeAgo})`;
}

/**
 * A simple widget to display HTML content in a dialog
 */
class HTMLDialogContent extends Widget {
  constructor(content: HTMLElement) {
    super();
    this.addClass('jp-RevertCheckpoint-dialog');
    this.node.appendChild(content);
  }
}

/**
 * Activate the revert button extension.
 */
function activateRevertButton(
  app: JupyterFrontEnd,
  notebookTracker: INotebookTracker,
  editorTracker: IEditorTracker,
  docManager: IDocumentManager
): void {
  console.log('JupyterLab extension jupytercheckpoints:revert-button is activated!');

  // Track the toolbar items we create for each widget
  const toolbarItems: { [id: string]: IDisposable } = {};

  // Add the toolbar button to each notebook and file editor
  function addToolbarButton(widget: any): void {
    const context = docManager.contextForWidget(widget);
    if (!context) {
      return;
    }

    // Check if we already added a button for this widget
    if (toolbarItems[context.path]) {
      return;
    }

    // Create the toolbar button
    const button = new ToolbarButton({
      className: 'jp-RevertCheckpoint-button jp-mod-styled',
      icon: 'fa fa-undo',  // use undo icon
      label: 'Revert Checkpoint',  // add text label
      tooltip: 'Revert file to previous checkpoint state',
      onClick: async () => {
        try {
          // Get the list of checkpoints
          const checkpoints = await context.listCheckpoints();

          if (checkpoints.length === 0) {
            void showDialog({
              title: '没有检查点',
              body: '当前文件没有可用的检查点。',
              buttons: [Dialog.okButton()]
            });
            return;
          }

          // Create a dialog with a dropdown to select a checkpoint
          const body = document.createElement('div');
          const label = document.createElement('label');
          label.textContent = '选择要恢复的检查点：';
          body.appendChild(label);

          const select = document.createElement('select');
          select.style.width = '100%';
          select.style.marginTop = '10px';

          // Add options for each checkpoint
          checkpoints.forEach((checkpoint) => {
            const option = document.createElement('option');
            option.value = checkpoint.id;
            option.text = createCheckpointLabel(checkpoint);
            select.appendChild(option);
          });

          body.appendChild(select);

          // Show the dialog
          const result = await showDialog({
            title: '选择一个检查点',
            body: new HTMLDialogContent(body),
            buttons: [Dialog.cancelButton(), Dialog.okButton()]
          });

          if (result.button.accept) {
            const selectedId = select.value;
            const selectedCheckpoint = checkpoints.find(cp => cp.id === selectedId);

            if (!selectedCheckpoint) {
              return;
            }

            // get file name (remove path)
            const fileName = context.path.split('/').pop() || context.path;

            // create confirmation dialog content
            const confirmBody = document.createElement('div');

            // add warning text
            const warningText = document.createElement('p');
            const fileType = fileName.endsWith('.ipynb') ? 'Notebook' : '文件';
            warningText.innerHTML = `您确定要将${fileType} <strong>${fileName}</strong> 恢复到检查点状态吗？<strong>此操作无法撤消。</strong>`;
            confirmBody.appendChild(warningText);

            // add checkpoint time information
            const timeInfo = document.createElement('p');
            const checkpointDate = new Date(selectedCheckpoint.last_modified);
            const now = new Date();
            const diffMs = now.getTime() - checkpointDate.getTime();

            // show different time format based on time difference
            let timeAgo: string;
            const diffMins = Math.round(diffMs / 60000);
            const diffHours = Math.round(diffMs / 3600000);
            const diffDays = Math.round(diffMs / 86400000);

            if (diffMins < 60) {
              timeAgo = `${diffMins} 分钟前`;
            } else if (diffHours < 24) {
              timeAgo = `${diffHours} 小时前`;
            } else {
              timeAgo = `${diffDays} 天前`;
            }

            timeInfo.innerHTML = `检查点最后更新时间：`;
            const timeDetail = document.createElement('p');
            timeDetail.style.textAlign = 'center';
            timeDetail.textContent = `${formatCheckpointDate(selectedCheckpoint.last_modified)} (${timeAgo})`;
            timeInfo.appendChild(timeDetail);

            confirmBody.appendChild(timeInfo);

            // show confirmation dialog
            const confirmResult = await showDialog({
              title: `恢复${fileType}到检查点`,
              body: new HTMLDialogContent(confirmBody),
              buttons: [
                Dialog.cancelButton({ label: '取消' }),
                Dialog.warnButton({ label: '恢复' })
              ]
            });

            if (confirmResult.button.accept) {
              try {
                // show loading state
                const busySignal = document.createElement('div');
                busySignal.className = 'jp-Dialog-busy';
                document.body.appendChild(busySignal);

                try {
                  // first restore checkpoint (server-side operation)
                  await context.restoreCheckpoint(selectedId);

                  // mark model as non-dirty to ensure correct refresh
                  context.model.dirty = false;

                  // get updated content from server and refresh frontend display
                  await context.revert();
                } finally {
                  // remove loading state regardless of success or failure
                  if (busySignal && busySignal.parentNode) {
                    busySignal.parentNode.removeChild(busySignal);
                  }
                }
              } catch (error) {
                console.error('Error restoring checkpoint:', error);
                void showDialog({
                  title: '恢复检查点失败',
                  body: `恢复检查点时出错: ${error}`,
                  buttons: [Dialog.okButton()]
                });
              }
            }
          }
        } catch (error) {
          console.error('Error listing or restoring checkpoints:', error);
          void showDialog({
            title: '错误',
            body: `获取或恢复检查点时出错: ${error}`,
            buttons: [Dialog.okButton()]
          });
        }
      }
    });

    // Add the button to the toolbar
    widget.toolbar.insertItem(10, 'revertCheckpoint', button);

    // Keep track of the button for disposal
    toolbarItems[context.path] = button;
  }

  // Add the button to existing notebooks and editors
  notebookTracker.forEach(addToolbarButton);
  editorTracker.forEach(addToolbarButton);

  // Add the button to new notebooks and editors
  notebookTracker.widgetAdded.connect((sender, widget) => {
    addToolbarButton(widget);
  });

  editorTracker.widgetAdded.connect((sender, widget) => {
    addToolbarButton(widget);
  });


  // Clean up when widgets are disposed
  // Set up a periodic cleanup to check for disposed widgets
  setInterval(() => {
    Object.keys(toolbarItems).forEach(path => {
      const widget = notebookTracker.find(w => docManager.contextForWidget(w)?.path === path) ||
                    editorTracker.find(w => docManager.contextForWidget(w)?.path === path);

      if (!widget) {
        // Widget is no longer in the tracker, dispose the button
        if (toolbarItems[path]) {
          toolbarItems[path].dispose();
          delete toolbarItems[path];
        }
      }
    });
  }, 5000); // Check every 5 seconds

  // Clean up the interval when the app is disposed
}

/**
 * Export the plugin as default.
 */
export default plugin;
