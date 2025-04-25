import { invoke } from "@tauri-apps/api/core";

/**
 * Call the Python backend using Tauri's py_api command.
 * @param {string} method - HTTP method (GET, POST, etc.)
 * @param {string} endpoint - API endpoint (e.g. "/greet")
 * @param {object} [payload={}] - JSON payload to send
 * @returns {Promise<any>} - JSON response from Python backend
 */
export function callPython(method, endpoint, payload = null) {

  return invoke('py_api', {
    method,
    endpoint,
    payload
  })}
  