/**
 * Utility Functions for NBQueue Extension
 * 
 * Provides helper functions for loading and processing extension settings.
 */

import { ISettingRegistry } from '@jupyterlab/settingregistry';
import _ from 'lodash';

/**
 * Loads the rendering folder setting from the extension configuration
 * 
 * @param setting - The loaded settings instance for this extension
 * @returns The configured rendering folder path as a string
 */
export function loadSetting(setting: ISettingRegistry.ISettings): string {
  // Extract rendering folder from composite settings
  let renderingFolder = setting.get('renderingFolder').composite as string;
  console.log(`Rendering Folder Loading Settings = ${renderingFolder}`);
  return renderingFolder;
}
