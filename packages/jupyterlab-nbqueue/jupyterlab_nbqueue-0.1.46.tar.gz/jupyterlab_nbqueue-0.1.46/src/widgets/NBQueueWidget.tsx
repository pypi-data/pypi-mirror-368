/**
 * NBQueue Widget
 * 
 * A ReactWidget wrapper for the NBQueueComponent that provides
 * a styled container for the job submission dialog.
 */

import { ReactWidget } from "@jupyterlab/apputils";
import React from 'react';
import NBQueueComponent from "../components/NBQueueComponent";

/**
 * Widget class for NBQueue job submission
 * 
 * Wraps the NBQueueComponent in a JupyterLab ReactWidget
 * with appropriate styling and dimensions.
 */
export class NBQueueWidget extends ReactWidget {
  file
  renderingFolder
  
  /**
   * Constructor for NBQueueWidget
   * @param file - File object containing notebook information
   * @param renderingFolder - Output folder path for job results
   */
  constructor(file: any, renderingFolder: string) {
    super()
    this.file = file
    this.renderingFolder = renderingFolder
  }

  /**
   * Renders the widget content
   * @returns JSX element with styled container and NBQueueComponent
   */
  render(): JSX.Element {
    return (
      <div
        style={{
          width: '400px',
          minWidth: '400px',
          display: 'flex',
          flexDirection: 'column',
          background: 'var(--jp-layout-color1)'
        }}
      >
        <NBQueueComponent file={this.file} renderingFolder={this.renderingFolder} />
      </div>
    )
  }
}