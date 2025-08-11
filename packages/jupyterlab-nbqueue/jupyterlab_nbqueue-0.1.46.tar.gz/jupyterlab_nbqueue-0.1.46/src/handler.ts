/**
 * API Handler for NBQueue Extension
 * 
 * Provides utility functions for making HTTP requests to the NBQueue backend API.
 * Handles authentication, error processing, and response formatting.
 */

import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';

/**
 * Makes authenticated requests to the NBQueue API extension
 * 
 * @param endPoint - API REST endpoint for the extension (default: '')
 * @param init - Initial values for the request (headers, method, body, etc.)
 * @returns Promise resolving to the parsed response body
 * @throws {ServerConnection.NetworkError} When network request fails
 * @throws {ServerConnection.ResponseError} When server returns error response
 */
export async function requestAPI<T>(
  endPoint = '',
  init: RequestInit = {}
): Promise<T> {
  // Build request URL using Jupyter server settings
  const settings = ServerConnection.makeSettings();
  const requestUrl = URLExt.join(
    settings.baseUrl,
    'jupyterlab-nbqueue', // API namespace for this extension
    endPoint
  );

  let response: Response;
  try {
    // Make authenticated request through Jupyter server connection
    response = await ServerConnection.makeRequest(requestUrl, init, settings);
  } catch (error) {
    throw new ServerConnection.NetworkError(error as any);
  }

  // Parse response body as text first, then try JSON parsing
  let data: any = await response.text();

  if (data.length > 0) {
    try {
      data = JSON.parse(data);
    } catch (error) {
      console.log('Not a JSON response body.', response);
    }
  }

  // Check for HTTP error status codes
  if (!response.ok) {
    throw new ServerConnection.ResponseError(response, data.message || data);
  }

  return data;
}
