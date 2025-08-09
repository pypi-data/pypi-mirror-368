/**
 * NBQueue Sidebar Widget
 * 
 * A ReactWidget wrapper for the NBQueueSideBarComponent that provides
 * workflow management functionality in the JupyterLab sidebar.
 */

import { ReactWidget } from "@jupyterlab/apputils";
import React from 'react';
import NBQueueSideBarComponent from "../components/NBQueueSideBarComponent";

/**
 * Widget class for NBQueue sidebar
 * 
 * Wraps the NBQueueSideBarComponent in a JupyterLab ReactWidget
 * for integration with the JupyterLab shell and sidebar area.
 */
export class NBQueueSideBarWidget extends ReactWidget {
  bucket
  
  /**
   * Constructor for NBQueueSideBarWidget
   * @param bucket - Bucket identifier for workflow storage
   */
  constructor(bucket: string) {
    super()
    this.bucket = bucket
  }

  /**
   * Renders the sidebar widget content
   * @returns JSX element with the NBQueueSideBarComponent
   */
  render(): JSX.Element {
    return (<NBQueueSideBarComponent bucket={this.bucket}/>)
  }
}