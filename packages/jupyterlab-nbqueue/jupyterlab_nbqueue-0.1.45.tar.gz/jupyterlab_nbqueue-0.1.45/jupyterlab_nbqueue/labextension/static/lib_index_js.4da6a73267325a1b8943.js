"use strict";
(self["webpackChunkjupyterlab_nbqueue"] = self["webpackChunkjupyterlab_nbqueue"] || []).push([["lib_index_js"],{

/***/ "./lib/common/types.js":
/*!*****************************!*\
  !*** ./lib/common/types.js ***!
  \*****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   isJobSubmissionSuccess: () => (/* binding */ isJobSubmissionSuccess),
/* harmony export */   validateJobSubmissionRequest: () => (/* binding */ validateJobSubmissionRequest),
/* harmony export */   validateNotebookFile: () => (/* binding */ validateNotebookFile)
/* harmony export */ });
/**
 * Job submission interfaces for API validation
 */
/**
 * Validation utilities for API requests
 */
/** Validates that a NotebookFile has the required fields */
function validateNotebookFile(file) {
    return file &&
        typeof file.name === 'string' &&
        typeof file.path === 'string' &&
        file.name.endsWith('.ipynb');
}
/** Validates that a JobSubmissionRequest has all required fields */
function validateJobSubmissionRequest(request) {
    if (!request)
        return false;
    const requiredFields = ['notebook_file', 'output_path', 'cpu', 'ram'];
    for (const field of requiredFields) {
        if (!request[field])
            return false;
    }
    // Validate notebook_file structure
    if (!validateNotebookFile(request.notebook_file))
        return false;
    // Validate CPU is a valid number
    const cpu = parseFloat(String(request.cpu));
    if (isNaN(cpu) || cpu <= 0)
        return false;
    // Validate RAM format (number optionally followed by unit)
    const ramPattern = /^\d+(\.\d+)?(Gi|G|Mi|M)?$/;
    if (!ramPattern.test(String(request.ram).trim()))
        return false;
    return true;
}
/** Type guard to check if response is a successful job submission */
function isJobSubmissionSuccess(response) {
    return response &&
        typeof response.success === 'boolean' &&
        typeof response.job_id === 'string' &&
        typeof response.kubectl_output === 'string';
}


/***/ }),

/***/ "./lib/components/NBQueueComponent.js":
/*!********************************************!*\
  !*** ./lib/components/NBQueueComponent.js ***!
  \********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material_Autocomplete__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @mui/material/Autocomplete */ "./node_modules/@mui/material/Autocomplete/Autocomplete.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../handler */ "./lib/handler.js");
/* harmony import */ var _common_types__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../common/types */ "./lib/common/types.js");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__);
/**
 * NBQueue Job Submission Component
 *
 * React component that provides a dialog interface for submitting notebooks
 * to the execution queue with configurable parameters (CPU, RAM, container image, etc.).
 */






/**
 * Main component for job submission dialog
 *
 * Renders a Material-UI dialog with form fields for configuring
 * notebook execution parameters and submitting to the queue.
 */
const NBQueueComponent = (props) => {
    // Dialog state management
    const [open, setOpen] = react__WEBPACK_IMPORTED_MODULE_1___default().useState(true);
    const [file] = react__WEBPACK_IMPORTED_MODULE_1___default().useState(props.file);
    const [renderingFolder] = react__WEBPACK_IMPORTED_MODULE_1___default().useState(props.renderingFolder);
    const [fullWidth] = react__WEBPACK_IMPORTED_MODULE_1___default().useState(true);
    const [maxWidth] = react__WEBPACK_IMPORTED_MODULE_1___default().useState('md');
    const [selectedOutputPath, setSelectedOutputPath] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(null);
    // State for accessible directories
    const [accessibleDirectories, setAccessibleDirectories] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)([]);
    const [showAdvanced, setShowAdvanced] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(false);
    // New state variables for container image and conda environment
    const [containerImage, setContainerImage] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)('');
    const [condaEnv, setCondaEnv] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)('');
    const [condaEnvError, setCondaEnvError] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(false);
    (0,react__WEBPACK_IMPORTED_MODULE_1__.useEffect)(() => {
        // Fetch accessible directories from the handler
        const fetchDirectories = async () => {
            try {
                const response = await (0,_handler__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('accessible-directories', {
                    method: 'POST',
                    body: JSON.stringify({ root_path: renderingFolder }),
                });
                // Map response to extract paths as strings
                const directoryPaths = response.accessible_directories.map(dir => dir.path);
                setAccessibleDirectories(directoryPaths);
            }
            catch (error) {
                console.error('Error fetching accessible directories:', error);
            }
        };
        fetchDirectories();
    }, [renderingFolder]);
    /** Closes the dialog */
    const handleClose = () => {
        setOpen(false);
    };
    return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement((react__WEBPACK_IMPORTED_MODULE_1___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Dialog, { open: open, onClose: handleClose, fullWidth: fullWidth, maxWidth: maxWidth, PaperProps: {
                component: 'form',
                onSubmit: async (event) => {
                    event.preventDefault();
                    const formData = new FormData(event.currentTarget);
                    const formJson = Object.fromEntries(formData.entries());
                    // Validación: si container-image tiene valor, conda-environment es obligatorio
                    if (containerImage && !condaEnv) {
                        setCondaEnvError(true);
                        return;
                    }
                    // Build payload for API request
                    const payload = {
                        notebook_file: file,
                        image: containerImage || formJson['container-image'],
                        conda_env: condaEnv || formJson['conda-environment'],
                        output_path: selectedOutputPath !== null && selectedOutputPath !== void 0 ? selectedOutputPath : '',
                        cpu: formJson['cpu-number'],
                        ram: formJson['ram-number']
                    };
                    // Validate payload before sending
                    if (!(0,_common_types__WEBPACK_IMPORTED_MODULE_4__.validateJobSubmissionRequest)(payload)) {
                        console.error('Invalid job submission payload:', payload);
                        return;
                    }
                    // Submit job with progress notifications
                    _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__.Notification.promise((0,_handler__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('job', {
                        method: 'POST',
                        body: JSON.stringify(payload),
                    }), {
                        pending: {
                            message: 'Sending info to gRPC server',
                        },
                        success: {
                            message: (result) => {
                                const response = result;
                                if ((0,_common_types__WEBPACK_IMPORTED_MODULE_4__.isJobSubmissionSuccess)(response)) {
                                    return response.success ?
                                        (response.kubectl_output || 'Job submitted successfully') :
                                        (response.error_message || 'Job submission failed');
                                }
                                return 'Job submitted successfully';
                            },
                            options: { autoClose: 3000 },
                        },
                        error: {
                            message: (reason) => `Error sending info. Reason: ${typeof reason === 'object' && reason.error ? reason.error : reason}`,
                            options: { autoClose: 3000 },
                        },
                    });
                    handleClose();
                }
            } },
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.DialogTitle, null, "Parameters"),
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.DialogContent, null,
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.DialogContentText, null, "Please fill the form with your parameters."),
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.TextField, { required: true, id: "cpu-number", name: "cpu-number", defaultValue: "1", label: "CPU", type: "number", variant: "standard", margin: "dense", fullWidth: true, autoFocus: true, inputProps: { min: 1, max: 32, step: 1 } }),
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.TextField, { required: true, id: "ram-number", name: "ram-number", defaultValue: "1", label: "RAM", type: "number", variant: "standard", margin: "dense", fullWidth: true, inputProps: { min: 1, max: 32, step: 1 } }),
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material_Autocomplete__WEBPACK_IMPORTED_MODULE_5__["default"], { id: "output-path", options: accessibleDirectories, value: selectedOutputPath, onChange: (_, newValue) => setSelectedOutputPath(newValue), renderInput: (params) => (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.TextField, { ...params, label: "Output Path", variant: "standard", margin: "dense", fullWidth: true, required: true })) }),
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Button, { onClick: () => setShowAdvanced((prev) => !prev), color: "primary", style: { marginTop: 16, marginBottom: 8 } }, showAdvanced ? 'Hide Advanced Options' : 'Show Advanced Options'),
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Collapse, { in: showAdvanced },
                    react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", null,
                        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.TextField, { id: "container-image", name: "container-image", label: "Container Image", variant: "standard", margin: "dense", fullWidth: true, style: { marginTop: 8 }, value: containerImage, onChange: e => {
                                setContainerImage(e.target.value);
                                setCondaEnvError(false);
                            } }),
                        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.TextField, { id: "conda-environment", name: "conda-environment", label: "Conda environment", variant: "standard", margin: "dense", fullWidth: true, style: { marginTop: 8 }, value: condaEnv, onChange: e => {
                                setCondaEnv(e.target.value);
                                setCondaEnvError(false);
                            }, error: condaEnvError, helperText: condaEnvError ? 'Conda environment is required if container image is set.' : '' })))),
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.DialogActions, null,
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Button, { onClick: handleClose }, "Cancel"),
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Button, { type: "submit" }, "Send")))));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (NBQueueComponent);


/***/ }),

/***/ "./lib/components/NBQueueSideBarComponent.js":
/*!***************************************************!*\
  !*** ./lib/components/NBQueueSideBarComponent.js ***!
  \***************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_icons_material_Refresh__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @mui/icons-material/Refresh */ "./node_modules/@mui/icons-material/Refresh.js");
/* harmony import */ var _mui_icons_material_DeleteSweep__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @mui/icons-material/DeleteSweep */ "./node_modules/@mui/icons-material/DeleteSweep.js");
/* harmony import */ var _mui_icons_material_Done__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @mui/icons-material/Done */ "./node_modules/@mui/icons-material/Done.js");
/* harmony import */ var _mui_icons_material_Error__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @mui/icons-material/Error */ "./node_modules/@mui/icons-material/Error.js");
/* harmony import */ var _mui_icons_material_Pending__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @mui/icons-material/Pending */ "./node_modules/@mui/icons-material/Pending.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../handler */ "./lib/handler.js");
/**
 * NBQueue Sidebar Component
 *
 * React component that provides a sidebar interface for managing and monitoring
 * workflow jobs in the NBQueue system. Displays job status, logs, and provides
 * controls for job management (refresh, view logs, delete, download).
 */






// import Close from '@mui/icons-material/Close';


/**
 * Main sidebar component for workflow management
 *
 * Provides a comprehensive interface for viewing, managing, and monitoring
 * NBQueue workflows including status indicators and job controls.
 */
const NBQueueSideBarComponent = (props) => {
    // Component state management
    const [dense] = react__WEBPACK_IMPORTED_MODULE_1___default().useState(true);
    const [jobs, setJobs] = react__WEBPACK_IMPORTED_MODULE_1___default().useState([]);
    //     const [selectedJob, setSelectedJob] = React.useState<JobHistory | null>(null);
    //     const [scroll, setScroll] = React.useState<DialogProps['scroll']>('paper');
    //     const [open, setOpen] = React.useState(false);
    //     const [contentLog, setContentLog] = React.useState('');
    /**
     * Renders appropriate status icon based on workflow status
     * @param status - Current workflow status
     * @returns JSX element with appropriate status icon
     */
    function AvatarStatusIcon({ status }) {
        switch (status) {
            case 'Succeeded':
                return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_icons_material_Done__WEBPACK_IMPORTED_MODULE_2__["default"], null));
            case 'Running':
                return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_icons_material_Pending__WEBPACK_IMPORTED_MODULE_3__["default"], null));
            case 'Failed':
                return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_icons_material_Error__WEBPACK_IMPORTED_MODULE_4__["default"], null));
            case 'Pending':
                return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_icons_material_Pending__WEBPACK_IMPORTED_MODULE_3__["default"], null));
            default:
                return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_icons_material_Error__WEBPACK_IMPORTED_MODULE_4__["default"], null));
        }
    }
    /**
     * Fetches the list of workflows from the API
     * Updates the component state with the retrieved workflows
     */
    // Fetch job history from /job-history endpoint
    const getJobHistory = async () => {
        try {
            const jobs = await (0,_handler__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('jobs', { method: 'GET' });
            setJobs(jobs);
        }
        catch (error) {
            console.error('Error fetching job history:', error);
        }
    };
    // Fetch job status from /job endpoint
    //     const getJobStatus = async (job_id: string) => {
    //         try {
    //             const status = await requestAPI<any>(`job?job_id=${job_id}`, { method: 'GET' });
    //             return status;
    //         } catch (error) {
    //             console.error('Error fetching job status:', error);
    //             return null;
    //         }
    //     };
    // Dialog state for job deletion (removed custom dialog, use window.confirm for consistency)
    // Delete job from /job endpoint
    const deleteJob = async (job_id) => {
        try {
            const result = await (0,_handler__WEBPACK_IMPORTED_MODULE_5__.requestAPI)(`job?job_id=${job_id}`, { method: 'DELETE' });
            getJobHistory(); // Refresh list after delete
            return result;
        }
        catch (error) {
            console.error('Error deleting job:', error);
            return null;
        }
    };
    /**
     * Retrieves logs for a specific workflow
     * @param workflowName - Name of the workflow to get logs for
     * @param bucket - Bucket identifier
     * @returns Promise resolving to workflow logs
     */
    // Consultar estatus y detalles de un job
    //     const getJobStatus = async (job_id: string) => {
    //         try {
    //             const status = await requestAPI<any>(`job-status?job_id=${job_id}`, { method: 'GET' });
    //             return status;
    //         } catch (error) {
    //             console.error('Error fetching job status:', error);
    //             return null;
    //         }
    //     };
    /**
     * Deletes a specific workflow
     * @param workflowName - Name of the workflow to delete
     * @param bucket - Bucket identifier
     * @returns Promise resolving to deletion result
     */
    // Delete all jobs using the jobs handler DELETE endpoint
    const deleteAllJobs = async () => {
        try {
            const result = await (0,_handler__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('jobs', { method: 'DELETE' });
            getJobHistory(); // Refresh list after delete
            console.log(result);
            return result;
        }
        catch (error) {
            console.error('Error deleting all jobs:', error);
            return null;
        }
    };
    /**
     * Downloads workflow logs
     * @param workflowName - Name of the workflow to download logs for
     * @param bucket - Bucket identifier
     * @returns Promise resolving to download data
     */
    // const downloadWorkflowLog = async (workflowName: string, bucket: string) => {
    //      const logs = await requestAPI<Blob | string>('workflow/download?workflow_name=' + workflowName + '&bucket=' + bucket, {
    //           method: 'GET'
    //      })
    //      console.log(logs)
    //      return logs
    // };
    /**
     * Handles refresh button click to reload workflows
     */
    // const handleRefreshClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    //      getWorkflows()
    // };
    /**
     * Handles log view button click
     * Opens dialog with workflow logs
     * @param scrollType - Dialog scroll behavior
     * @param workflowName - Name of workflow to view logs for
     * @param bucket - Bucket identifier
     */
    // Mostrar detalles/estatus de un job en el dialog
    //     const handleJobClick = (scrollType: DialogProps['scroll'], job: JobHistory) => async () => {
    //         const status = await getJobStatus(job.job_id);
    //         setSelectedJob(job);
    //         setContentLog(JSON.stringify(status, null, 2));
    //         setOpen(true);
    //         setScroll(scrollType);
    //     };
    /**
     * Handles download button click for workflow logs
     * @param scrollType - Dialog scroll behavior
     * @param workflowName - Name of workflow to download
     * @param bucket - Bucket identifier
     */
    // const handleDownloadClick = (scrollType: DialogProps['scroll'], workflowName: string, bucket: string) => async () => {
    //      try {
    //           console.log('handleDownloadClick');
    //           const logs = await downloadWorkflowLog(workflowName, bucket)
    //           console.log(`Endpoint Workflow log Result => ${logs}`)
    //      } catch (error) {
    //           console.log(`Error => ${JSON.stringify(error, null, 2)}`)
    //      }
    //      console.log(`Workflow Name => ${workflowName}`)
    // };
    // const handleDeleteClick = (scrollType: DialogProps['scroll'], workflowName: string, bucket: string) => async () => {
    //      try {
    //           console.log('handleDeleteClick');
    //           const logs = await deleteWorkflowLog(workflowName, bucket)
    //           console.log(`Endpoint Workflow log Result => ${logs}`)
    //      } catch (error) {
    //           console.log(`Error => ${JSON.stringify(error, null, 2)}`)
    //      }
    //      console.log(`Workflow Name => ${workflowName}`)
    //      getWorkflows()
    // };
    // const handleClose = () => {
    //      setOpen(false);
    // };
    // const descriptionElementRef = React.useRef<HTMLElement>(null);
    // React.useEffect(() => {
    //      if (open) {
    //           const { current: descriptionElement } = descriptionElementRef;
    //           if (descriptionElement !== null) {
    //                descriptionElement.focus();
    //           }
    //      }
    // }, [open]);
    react__WEBPACK_IMPORTED_MODULE_1___default().useEffect(() => {
        getJobHistory();
    }, []);
    return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement((react__WEBPACK_IMPORTED_MODULE_1___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.AppBar, null,
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Toolbar, null,
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Typography, { variant: "h6", component: "div", sx: { flexGrow: 1 } }, "NBQueue job history"),
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.IconButton, { "aria-label": "refresh", onClick: getJobHistory, color: "inherit" },
                    react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_icons_material_Refresh__WEBPACK_IMPORTED_MODULE_6__["default"], null)),
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.IconButton, { "aria-label": "delete-all", onClick: () => {
                        if (window.confirm('¿Seguro que deseas borrar todo el historial de jobs?')) {
                            deleteAllJobs();
                        }
                    }, color: "inherit" },
                    react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_icons_material_DeleteSweep__WEBPACK_IMPORTED_MODULE_7__["default"], null)))),
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Toolbar, null),
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Container, { sx: {
                height: '100%',
                overflowY: 'auto',
                paddingBottom: 5
            } },
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Grid, { container: true, direction: "row", justifyContent: "space-between", alignItems: "flex-start", rowSpacing: 1, columnSpacing: { xs: 1, sm: 2, md: 3 } },
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Grid, { item: true, xs: 12 },
                    react__WEBPACK_IMPORTED_MODULE_1___default().createElement("nav", { "aria-label": "job history list" },
                        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.List, { dense: dense },
                            jobs.map(job => (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.ListItem, { key: job.job_id, button: true, secondaryAction: react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.IconButton, { edge: "end", "aria-label": "delete", onClick: async () => {
                                        if (window.confirm(`¿Seguro que deseas borrar el job?\nJob ID: ${job.job_id}`)) {
                                            await deleteJob(job.job_id);
                                        }
                                    } },
                                    react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_icons_material_Error__WEBPACK_IMPORTED_MODULE_4__["default"], null)) },
                                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.ListItemAvatar, null,
                                    react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Avatar, { color: job.status },
                                        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(AvatarStatusIcon, { status: job.status }))),
                                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.ListItemText, { primary: job.job_id, secondary: react__WEBPACK_IMPORTED_MODULE_1___default().createElement((react__WEBPACK_IMPORTED_MODULE_1___default().Fragment), null,
                                        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Typography, { sx: { display: 'inline' }, component: "span", variant: "body2", color: "text.primary" }, job.start_time ? `Started: ${job.start_time}` : ''),
                                        ` — ${job.status}`,
                                        job.error_message ? ` — Error: ${job.error_message}` : '') })))),
                            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.ListItem, null,
                                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.ListItemText, null)))))))));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (NBQueueSideBarComponent);


/***/ }),

/***/ "./lib/handler.js":
/*!************************!*\
  !*** ./lib/handler.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   requestAPI: () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);
/**
 * API Handler for NBQueue Extension
 *
 * Provides utility functions for making HTTP requests to the NBQueue backend API.
 * Handles authentication, error processing, and response formatting.
 */


/**
 * Makes authenticated requests to the NBQueue API extension
 *
 * @param endPoint - API REST endpoint for the extension (default: '')
 * @param init - Initial values for the request (headers, method, body, etc.)
 * @returns Promise resolving to the parsed response body
 * @throws {ServerConnection.NetworkError} When network request fails
 * @throws {ServerConnection.ResponseError} When server returns error response
 */
async function requestAPI(endPoint = '', init = {}) {
    // Build request URL using Jupyter server settings
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 'jupyterlab-nbqueue', // API namespace for this extension
    endPoint);
    let response;
    try {
        // Make authenticated request through Jupyter server connection
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    // Parse response body as text first, then try JSON parsing
    let data = await response.text();
    if (data.length > 0) {
        try {
            data = JSON.parse(data);
        }
        catch (error) {
            console.log('Not a JSON response body.', response);
        }
    }
    // Check for HTTP error status codes
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message || data);
    }
    return data;
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ButtonExtension: () => (/* binding */ ButtonExtension),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/filebrowser */ "webpack/sharing/consume/default/@jupyterlab/filebrowser");
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/mainmenu */ "webpack/sharing/consume/default/@jupyterlab/mainmenu");
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _widgets_NBQueueWidget__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ./widgets/NBQueueWidget */ "./lib/widgets/NBQueueWidget.js");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _widgets_NBQueueSideBarWidget__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./widgets/NBQueueSideBarWidget */ "./lib/widgets/NBQueueSideBarWidget.js");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _utils__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./utils */ "./lib/utils.js");
/* harmony import */ var lodash__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! lodash */ "webpack/sharing/consume/default/lodash/lodash");
/* harmony import */ var lodash__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(lodash__WEBPACK_IMPORTED_MODULE_7__);
/**
 * JupyterLab NBQueue Extension
 *
 * This extension provides functionality to queue notebook executions
 * in Kubernetes environments through a sidebar interface and context menu.
 */











/** Plugin identifier for settings and registration */
const PLUGIN_ID = 'jupyterlab-nbqueue:plugin';
/**
 * Activates the NBQueue extension
 * @param app - The JupyterLab application instance
 * @param factory - File browser factory for file operations
 * @param palette - Command palette for registering commands
 * @param mainMenu - Main menu for adding menu items
 * @param settings - Settings registry for configuration
 */
const activate = async (app, factory, palette, mainMenu, settings) => {
    console.log('JupyterLab extension jupyterlab-nbqueue is activated!');
    // Initialize user service and log user information for debugging
    const user = app.serviceManager.user;
    user.ready.then(() => {
        console.debug("Identity:", user.identity);
        console.debug("Permissions:", user.permissions);
    });
    // Load rendering folder configuration from settings
    let renderingFolder = '';
    await Promise.all([settings.load(PLUGIN_ID)])
        .then(([setting]) => {
        renderingFolder = (0,_utils__WEBPACK_IMPORTED_MODULE_8__.loadSetting)(setting);
    }).catch((reason) => {
        console.error(`Something went wrong when getting the current rendering folder.\n${reason}`);
    });
    // Validate rendering folder configuration
    if (lodash__WEBPACK_IMPORTED_MODULE_7___default().isEqual(renderingFolder, "")) {
        _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Notification.warning('Rendering Folder is not configured');
        return;
    }
    // Create and configure the sidebar widget for job management
    const sideBarContent = new _widgets_NBQueueSideBarWidget__WEBPACK_IMPORTED_MODULE_9__.NBQueueSideBarWidget(renderingFolder);
    const sideBarWidget = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.MainAreaWidget({
        content: sideBarContent
    });
    // Configure sidebar widget appearance and add to shell
    sideBarWidget.toolbar.hide();
    sideBarWidget.title.icon = _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__.runIcon;
    sideBarWidget.title.caption = 'NBQueue job list';
    app.shell.add(sideBarWidget, 'right', { rank: 501 });
    // Register command for sending notebooks to queue via context menu
    app.commands.addCommand('jupyterlab-nbqueue:open', {
        label: 'NBQueue: Send to queue',
        caption: "Send selected notebook to execution queue",
        icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__.runIcon,
        execute: async () => {
            var _a;
            // Reload settings to ensure we have the latest configuration
            await Promise.all([settings.load(PLUGIN_ID)])
                .then(([setting]) => {
                renderingFolder = (0,_utils__WEBPACK_IMPORTED_MODULE_8__.loadSetting)(setting);
            }).catch((reason) => {
                console.error(`Something went wrong when getting the current rendering folder.\n${reason}`);
            });
            // Validate configuration before proceeding
            if (lodash__WEBPACK_IMPORTED_MODULE_7___default().isEqual(renderingFolder, "")) {
                _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Notification.warning('Rendering Folder is not configured');
                return;
            }
            // Get the currently selected file from file browser
            const file = (_a = factory.tracker.currentWidget) === null || _a === void 0 ? void 0 : _a.selectedItems().next().value;
            if (file) {
                // Create and display the job submission widget
                const widget = new _widgets_NBQueueWidget__WEBPACK_IMPORTED_MODULE_10__.NBQueueWidget(file, renderingFolder);
                widget.title.label = "NBQueue metadata";
                _lumino_widgets__WEBPACK_IMPORTED_MODULE_3__.Widget.attach(widget, document.body);
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
};
/**
 * Main plugin configuration object
 */
const plugin = {
    id: 'jupyterlab-nbqueue:plugin',
    description: 'A JupyterLab extension for queuing notebook executions in Kubernetes.',
    autoStart: true,
    requires: [_jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_0__.IFileBrowserFactory, _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.ICommandPalette, _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_1__.IMainMenu, _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_6__.ISettingRegistry],
    activate
};
/**
 * Document registry extension that adds a toolbar button to notebook panels
 * for quick access to NBQueue functionality
 */
class ButtonExtension {
    constructor(settings) {
        this.settings = settings;
    }
    /**
     * Creates a new toolbar button for the notebook panel
     * @param panel - The notebook panel to extend
     * @param context - The document context
     * @returns Disposable for cleanup
     */
    createNew(panel, context) {
        /**
         * Handler for sending the current notebook to queue
         */
        const sendToQueue = async () => {
            let renderingFolder = '';
            // Load current settings
            await Promise.all([this.settings.load(PLUGIN_ID)])
                .then(([setting]) => {
                renderingFolder = (0,_utils__WEBPACK_IMPORTED_MODULE_8__.loadSetting)(setting);
                console.log(renderingFolder);
            }).catch((reason) => {
                console.error(`Something went wrong when getting the current rendering folder.\n${reason}`);
            });
            // Validate configuration
            if (lodash__WEBPACK_IMPORTED_MODULE_7___default().isEqual(renderingFolder, "")) {
                _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Notification.warning('Rendering Folder is not configured');
                return;
            }
            // Create and show the job submission widget
            const widget = new _widgets_NBQueueWidget__WEBPACK_IMPORTED_MODULE_10__.NBQueueWidget(context.contentsModel, renderingFolder);
            widget.title.label = "NBQueue metadata";
            _lumino_widgets__WEBPACK_IMPORTED_MODULE_3__.Widget.attach(widget, document.body);
        };
        // Create the toolbar button
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.ToolbarButton({
            className: 'nbqueue-submit',
            label: 'NBQueue: Send to queue',
            onClick: sendToQueue,
            tooltip: 'Send notebook to execution queue',
        });
        // Insert button into toolbar
        panel.toolbar.insertItem(10, 'clearOutputs', button);
        // Return disposable for cleanup
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_4__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/utils.js":
/*!**********************!*\
  !*** ./lib/utils.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   loadSetting: () => (/* binding */ loadSetting)
/* harmony export */ });
/**
 * Utility Functions for NBQueue Extension
 *
 * Provides helper functions for loading and processing extension settings.
 */
/**
 * Loads the rendering folder setting from the extension configuration
 *
 * @param setting - The loaded settings instance for this extension
 * @returns The configured rendering folder path as a string
 */
function loadSetting(setting) {
    // Extract rendering folder from composite settings
    let renderingFolder = setting.get('renderingFolder').composite;
    console.log(`Rendering Folder Loading Settings = ${renderingFolder}`);
    return renderingFolder;
}


/***/ }),

/***/ "./lib/widgets/NBQueueSideBarWidget.js":
/*!*********************************************!*\
  !*** ./lib/widgets/NBQueueSideBarWidget.js ***!
  \*********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   NBQueueSideBarWidget: () => (/* binding */ NBQueueSideBarWidget)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components_NBQueueSideBarComponent__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../components/NBQueueSideBarComponent */ "./lib/components/NBQueueSideBarComponent.js");
/**
 * NBQueue Sidebar Widget
 *
 * A ReactWidget wrapper for the NBQueueSideBarComponent that provides
 * workflow management functionality in the JupyterLab sidebar.
 */



/**
 * Widget class for NBQueue sidebar
 *
 * Wraps the NBQueueSideBarComponent in a JupyterLab ReactWidget
 * for integration with the JupyterLab shell and sidebar area.
 */
class NBQueueSideBarWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ReactWidget {
    /**
     * Constructor for NBQueueSideBarWidget
     * @param bucket - Bucket identifier for workflow storage
     */
    constructor(bucket) {
        super();
        this.bucket = bucket;
    }
    /**
     * Renders the sidebar widget content
     * @returns JSX element with the NBQueueSideBarComponent
     */
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_components_NBQueueSideBarComponent__WEBPACK_IMPORTED_MODULE_2__["default"], { bucket: this.bucket }));
    }
}


/***/ }),

/***/ "./lib/widgets/NBQueueWidget.js":
/*!**************************************!*\
  !*** ./lib/widgets/NBQueueWidget.js ***!
  \**************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   NBQueueWidget: () => (/* binding */ NBQueueWidget)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components_NBQueueComponent__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../components/NBQueueComponent */ "./lib/components/NBQueueComponent.js");
/**
 * NBQueue Widget
 *
 * A ReactWidget wrapper for the NBQueueComponent that provides
 * a styled container for the job submission dialog.
 */



/**
 * Widget class for NBQueue job submission
 *
 * Wraps the NBQueueComponent in a JupyterLab ReactWidget
 * with appropriate styling and dimensions.
 */
class NBQueueWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ReactWidget {
    /**
     * Constructor for NBQueueWidget
     * @param file - File object containing notebook information
     * @param renderingFolder - Output folder path for job results
     */
    constructor(file, renderingFolder) {
        super();
        this.file = file;
        this.renderingFolder = renderingFolder;
    }
    /**
     * Renders the widget content
     * @returns JSX element with styled container and NBQueueComponent
     */
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { style: {
                width: '400px',
                minWidth: '400px',
                display: 'flex',
                flexDirection: 'column',
                background: 'var(--jp-layout-color1)'
            } },
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_components_NBQueueComponent__WEBPACK_IMPORTED_MODULE_2__["default"], { file: this.file, renderingFolder: this.renderingFolder })));
    }
}


/***/ }),

/***/ "./node_modules/@mui/icons-material/DeleteSweep.js":
/*!*********************************************************!*\
  !*** ./node_modules/@mui/icons-material/DeleteSweep.js ***!
  \*********************************************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {


"use client";

var _interopRequireDefault = __webpack_require__(/*! @babel/runtime/helpers/interopRequireDefault */ "./node_modules/@babel/runtime/helpers/interopRequireDefault.js");
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports["default"] = void 0;
var _createSvgIcon = _interopRequireDefault(__webpack_require__(/*! ./utils/createSvgIcon */ "./node_modules/@mui/icons-material/utils/createSvgIcon.js"));
var _jsxRuntime = __webpack_require__(/*! react/jsx-runtime */ "./node_modules/react/jsx-runtime.js");
var _default = exports["default"] = (0, _createSvgIcon.default)( /*#__PURE__*/(0, _jsxRuntime.jsx)("path", {
  d: "M15 16h4v2h-4zm0-8h7v2h-7zm0 4h6v2h-6zM3 18c0 1.1.9 2 2 2h6c1.1 0 2-.9 2-2V8H3zM14 5h-3l-1-1H6L5 5H2v2h12z"
}), 'DeleteSweep');

/***/ }),

/***/ "./node_modules/@mui/icons-material/Done.js":
/*!**************************************************!*\
  !*** ./node_modules/@mui/icons-material/Done.js ***!
  \**************************************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {


"use client";

var _interopRequireDefault = __webpack_require__(/*! @babel/runtime/helpers/interopRequireDefault */ "./node_modules/@babel/runtime/helpers/interopRequireDefault.js");
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports["default"] = void 0;
var _createSvgIcon = _interopRequireDefault(__webpack_require__(/*! ./utils/createSvgIcon */ "./node_modules/@mui/icons-material/utils/createSvgIcon.js"));
var _jsxRuntime = __webpack_require__(/*! react/jsx-runtime */ "./node_modules/react/jsx-runtime.js");
var _default = exports["default"] = (0, _createSvgIcon.default)( /*#__PURE__*/(0, _jsxRuntime.jsx)("path", {
  d: "M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"
}), 'Done');

/***/ }),

/***/ "./node_modules/@mui/icons-material/Error.js":
/*!***************************************************!*\
  !*** ./node_modules/@mui/icons-material/Error.js ***!
  \***************************************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {


"use client";

var _interopRequireDefault = __webpack_require__(/*! @babel/runtime/helpers/interopRequireDefault */ "./node_modules/@babel/runtime/helpers/interopRequireDefault.js");
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports["default"] = void 0;
var _createSvgIcon = _interopRequireDefault(__webpack_require__(/*! ./utils/createSvgIcon */ "./node_modules/@mui/icons-material/utils/createSvgIcon.js"));
var _jsxRuntime = __webpack_require__(/*! react/jsx-runtime */ "./node_modules/react/jsx-runtime.js");
var _default = exports["default"] = (0, _createSvgIcon.default)( /*#__PURE__*/(0, _jsxRuntime.jsx)("path", {
  d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2m1 15h-2v-2h2zm0-4h-2V7h2z"
}), 'Error');

/***/ }),

/***/ "./node_modules/@mui/icons-material/Pending.js":
/*!*****************************************************!*\
  !*** ./node_modules/@mui/icons-material/Pending.js ***!
  \*****************************************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {


"use client";

var _interopRequireDefault = __webpack_require__(/*! @babel/runtime/helpers/interopRequireDefault */ "./node_modules/@babel/runtime/helpers/interopRequireDefault.js");
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports["default"] = void 0;
var _createSvgIcon = _interopRequireDefault(__webpack_require__(/*! ./utils/createSvgIcon */ "./node_modules/@mui/icons-material/utils/createSvgIcon.js"));
var _jsxRuntime = __webpack_require__(/*! react/jsx-runtime */ "./node_modules/react/jsx-runtime.js");
var _default = exports["default"] = (0, _createSvgIcon.default)( /*#__PURE__*/(0, _jsxRuntime.jsx)("path", {
  d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2M7 13.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5m5 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5m5 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5"
}), 'Pending');

/***/ }),

/***/ "./node_modules/@mui/icons-material/Refresh.js":
/*!*****************************************************!*\
  !*** ./node_modules/@mui/icons-material/Refresh.js ***!
  \*****************************************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {


"use client";

var _interopRequireDefault = __webpack_require__(/*! @babel/runtime/helpers/interopRequireDefault */ "./node_modules/@babel/runtime/helpers/interopRequireDefault.js");
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports["default"] = void 0;
var _createSvgIcon = _interopRequireDefault(__webpack_require__(/*! ./utils/createSvgIcon */ "./node_modules/@mui/icons-material/utils/createSvgIcon.js"));
var _jsxRuntime = __webpack_require__(/*! react/jsx-runtime */ "./node_modules/react/jsx-runtime.js");
var _default = exports["default"] = (0, _createSvgIcon.default)( /*#__PURE__*/(0, _jsxRuntime.jsx)("path", {
  d: "M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4z"
}), 'Refresh');

/***/ }),

/***/ "./node_modules/@mui/icons-material/utils/createSvgIcon.js":
/*!*****************************************************************!*\
  !*** ./node_modules/@mui/icons-material/utils/createSvgIcon.js ***!
  \*****************************************************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {


'use client';

Object.defineProperty(exports, "__esModule", ({
  value: true
}));
Object.defineProperty(exports, "default", ({
  enumerable: true,
  get: function () {
    return _utils.createSvgIcon;
  }
}));
var _utils = __webpack_require__(/*! @mui/material/utils */ "./node_modules/@mui/material/utils/index.js");

/***/ })

}]);
//# sourceMappingURL=lib_index_js.4da6a73267325a1b8943.js.map