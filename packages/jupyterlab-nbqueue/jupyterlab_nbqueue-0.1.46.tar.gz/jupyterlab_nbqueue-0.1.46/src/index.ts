/**
 * JupyterLab NBQueue Extension
 * 
 * This extension provides functionality to queue notebook executions
 * in Kubernetes environments through a sidebar interface and context menu.
 */

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { runIcon } from '@jupyterlab/ui-components';
import { NBQueueWidget } from "./widgets/NBQueueWidget";
import { Widget } from '@lumino/widgets';
import { IDisposable, DisposableDelegate } from '@lumino/disposable';
import { ICommandPalette, MainAreaWidget, Notification, ToolbarButton } from '@jupyterlab/apputils';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import {
  NotebookPanel,
  INotebookModel,
} from '@jupyterlab/notebook';
import { NBQueueSideBarWidget } from './widgets/NBQueueSideBarWidget';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { loadSetting } from './utils';
import _ from 'lodash'

/** Plugin identifier for settings and registration */
const PLUGIN_ID = 'jupyterlab-nbqueue:plugin'

/**
 * Activates the NBQueue extension
 * @param app - The JupyterLab application instance
 * @param factory - File browser factory for file operations
 * @param palette - Command palette for registering commands
 * @param mainMenu - Main menu for adding menu items
 * @param settings - Settings registry for configuration
 */
const activate = async (app: JupyterFrontEnd, factory: IFileBrowserFactory, palette: ICommandPalette, mainMenu: IMainMenu, settings: ISettingRegistry) => {
  console.log('JupyterLab extension jupyterlab-nbqueue is activated!');
  
  // Initialize user service and log user information for debugging
  const user = app.serviceManager.user;
  user.ready.then(() => {
     console.debug("Identity:", user.identity);
     console.debug("Permissions:", user.permissions);
  });  
  
  // Load rendering folder configuration from settings
  let renderingFolder = ''
  await Promise.all([settings.load(PLUGIN_ID)])
    .then(([setting]) => {
      renderingFolder = loadSetting(setting);
    }).catch((reason) => {
      console.error(
        `Something went wrong when getting the current rendering folder.\n${reason}`
      );
    });

  // Validate rendering folder configuration
  if (_.isEqual(renderingFolder, "")) {
    Notification.warning('Rendering Folder is not configured')
    return;
  }

  // Create and configure the sidebar widget for job management
  const sideBarContent = new NBQueueSideBarWidget(renderingFolder);
  const sideBarWidget = new MainAreaWidget<NBQueueSideBarWidget>({
    content: sideBarContent
  });
  // Configure sidebar widget appearance and add to shell
  sideBarWidget.toolbar.hide();
  sideBarWidget.title.icon = runIcon;
  sideBarWidget.title.caption = 'NBQueue job list';
  app.shell.add(sideBarWidget, 'right', { rank: 501 });

  // Register command for sending notebooks to queue via context menu
  app.commands.addCommand('jupyterlab-nbqueue:open', {
    label: 'NBQueue: Send to queue',
    caption: "Send selected notebook to execution queue",
    icon: runIcon,
    execute: async () => {
      // Reload settings to ensure we have the latest configuration
      await Promise.all([settings.load(PLUGIN_ID)])
        .then(([setting]) => {
          renderingFolder = loadSetting(setting);
        }).catch((reason) => {
          console.error(
            `Something went wrong when getting the current rendering folder.\n${reason}`
          );
        });

      // Validate configuration before proceeding
      if (_.isEqual(renderingFolder, "")) {
        Notification.warning('Rendering Folder is not configured')
        return;
      }

      // Get the currently selected file from file browser
      const file = factory.tracker.currentWidget
        ?.selectedItems()
        .next().value;

      if (file) {
        // Create and display the job submission widget
        const widget = new NBQueueWidget(file, renderingFolder);
        widget.title.label = "NBQueue metadata";
        Widget.attach(widget, document.body);
      }
    }
  });

  // Add context menu item for notebook files
  app.contextMenu.addItem({
    command: 'jupyterlab-nbqueue:open',
    selector: ".jp-DirListing-item[data-file-type=\"notebook\"]",
    rank: 0
  });

  // Add toolbar button extension to notebook panels
  app.docRegistry.addWidgetExtension('Notebook', new ButtonExtension(settings));
}

/**
 * Main plugin configuration object
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-nbqueue:plugin',
  description: 'A JupyterLab extension for queuing notebook executions in Kubernetes.',
  autoStart: true,
  requires: [IFileBrowserFactory, ICommandPalette, IMainMenu, ISettingRegistry],
  activate
};

/**
 * Document registry extension that adds a toolbar button to notebook panels
 * for quick access to NBQueue functionality
 */
export class ButtonExtension
  implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel> {

  settings: ISettingRegistry
  
  constructor(settings: ISettingRegistry) {
    this.settings = settings;
  }

  /**
   * Creates a new toolbar button for the notebook panel
   * @param panel - The notebook panel to extend
   * @param context - The document context
   * @returns Disposable for cleanup
   */
  createNew(
    panel: NotebookPanel,
    context: DocumentRegistry.IContext<INotebookModel>
  ): IDisposable {
    
    /**
     * Handler for sending the current notebook to queue
     */
    const sendToQueue = async () => {
      let renderingFolder = ''
      
      // Load current settings
      await Promise.all([this.settings.load(PLUGIN_ID)])
        .then(([setting]) => {
          renderingFolder = loadSetting(setting);
          console.log(renderingFolder);
        }).catch((reason) => {
          console.error(
            `Something went wrong when getting the current rendering folder.\n${reason}`
          );
        });

      // Validate configuration
      if (_.isEqual(renderingFolder, "")) {
        Notification.warning('Rendering Folder is not configured')
        return;
      }

      // Create and show the job submission widget
      const widget = new NBQueueWidget(context.contentsModel, renderingFolder);
      widget.title.label = "NBQueue metadata";
      Widget.attach(widget, document.body);
    };
    
    // Create the toolbar button
    const button = new ToolbarButton({
      className: 'nbqueue-submit',
      label: 'NBQueue: Send to queue',
      onClick: sendToQueue,
      tooltip: 'Send notebook to execution queue',
    });

    // Insert button into toolbar
    panel.toolbar.insertItem(10, 'clearOutputs', button);
    
    // Return disposable for cleanup
    return new DisposableDelegate(() => {
      button.dispose();
    });
  }
}

export default plugin;
