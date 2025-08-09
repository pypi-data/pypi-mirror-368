/**
 * NBQueue Job Submission Component
 * 
 * React component that provides a dialog interface for submitting notebooks
 * to the execution queue with configurable parameters (CPU, RAM, container image, etc.).
 */

import {
     Button,
     Dialog,
     DialogActions,
     DialogContent,
     DialogContentText,
     DialogProps,
     DialogTitle,
     TextField,
     Collapse
} from '@mui/material';
import Autocomplete from '@mui/material/Autocomplete';
import React, { useEffect, useState } from 'react';
import { requestAPI } from '../handler';
import { 
     JobSubmissionRequest, 
     JobSubmissionResponse, 
     NotebookFile,
     validateJobSubmissionRequest,
     isJobSubmissionSuccess
} from '../common/types';
import { Notification } from '@jupyterlab/apputils';

/** Props interface for the NBQueueComponent */
interface NBQueueComponentProps {
     /** File object containing notebook information */
     file: NotebookFile;
     /** Output folder path for job results */
     renderingFolder: string;
}

/**
 * Main component for job submission dialog
 * 
 * Renders a Material-UI dialog with form fields for configuring
 * notebook execution parameters and submitting to the queue.
 */
const NBQueueComponent: React.FC<NBQueueComponentProps> = (
     props
): JSX.Element => {
     // Dialog state management
     const [open, setOpen] = React.useState(true);
     const [file] = React.useState(props.file);
     const [renderingFolder] = React.useState(props.renderingFolder);
     const [fullWidth] = React.useState(true);
     const [maxWidth] = React.useState<DialogProps['maxWidth']>('md');
     const [selectedOutputPath, setSelectedOutputPath] = useState<string | null>(null);

     // State for accessible directories
     const [accessibleDirectories, setAccessibleDirectories] = useState<string[]>([]);
     const [showAdvanced, setShowAdvanced] = useState(false);

     // New state variables for container image and conda environment
     const [containerImage, setContainerImage] = useState('');
     const [condaEnv, setCondaEnv] = useState('');
     const [condaEnvError, setCondaEnvError] = useState(false);

     useEffect(() => {
          // Fetch accessible directories from the handler
          const fetchDirectories = async () => {
               try {
                    const response = await requestAPI<{ accessible_directories: { path: string }[] }>('accessible-directories', {
                         method: 'POST',
                         body: JSON.stringify({ root_path: renderingFolder }),
                    });
                    // Map response to extract paths as strings
                    const directoryPaths = response.accessible_directories.map(dir => dir.path);
                    setAccessibleDirectories(directoryPaths);
               } catch (error) {
                    console.error('Error fetching accessible directories:', error);
               }
          };

          fetchDirectories();
     }, [renderingFolder]);

     /** Closes the dialog */
     const handleClose = () => {
          setOpen(false);
     };

     return (
          <React.Fragment>
               <Dialog
                    open={open}
                    onClose={handleClose}
                    fullWidth={fullWidth}
                    maxWidth={maxWidth}
                    PaperProps={{
                         component: 'form',
                         onSubmit: async (event: React.FormEvent<HTMLFormElement>) => {
                              event.preventDefault();
                              const formData = new FormData(event.currentTarget);
                              const formJson = Object.fromEntries((formData as any).entries());

                              // Validación: si container-image tiene valor, conda-environment es obligatorio
                              if (containerImage && !condaEnv) {
                                   setCondaEnvError(true);
                                   return;
                              }

                              // Build payload for API request
                              const payload: JobSubmissionRequest = {
                                   notebook_file: file,
                                   image: containerImage || formJson['container-image'],
                                   conda_env: condaEnv || formJson['conda-environment'],
                                   output_path: selectedOutputPath ?? '',
                                   cpu: formJson['cpu-number'],
                                   ram: formJson['ram-number']
                               };

                              // Validate payload before sending
                              if (!validateJobSubmissionRequest(payload)) {
                                   console.error('Invalid job submission payload:', payload);
                                   return;
                              }

                              // Submit job with progress notifications
                              Notification.promise(
                                   requestAPI<JobSubmissionResponse>('job', {
                                        method: 'POST',
                                        body: JSON.stringify(payload),
                                   }),
                                   {
                                        pending: {
                                             message: 'Sending info to gRPC server',
                                        },
                                        success: {
                                             message: (result: unknown) => {
                                                  const response = result as JobSubmissionResponse;
                                                  if (isJobSubmissionSuccess(response)) {
                                                       return response.success ? 
                                                            (response.kubectl_output || 'Job submitted successfully') :
                                                            (response.error_message || 'Job submission failed');
                                                  }
                                                  return 'Job submitted successfully';
                                             },
                                             options: { autoClose: 3000 },
                                        },
                                        error: {
                                             message: (reason: any) =>
                                                  `Error sending info. Reason: ${typeof reason === 'object' && reason.error ? reason.error : reason}`,
                                             options: { autoClose: 3000 },
                                        },
                                   }
                              );                              

                              handleClose();
                         }
                    }}
               >
                    <DialogTitle>Parameters</DialogTitle>
                    <DialogContent>
                         <DialogContentText>
                              Please fill the form with your parameters.
                         </DialogContentText>
                         
                         {/* CPU Configuration */}
                         <TextField
                              required
                              id="cpu-number"
                              name="cpu-number"
                              defaultValue="1"
                              label="CPU"
                              type="number"
                              variant="standard"
                              margin="dense"
                              fullWidth
                              autoFocus
                              inputProps={{ min: 1, max: 32, step: 1 }}
                         />
                         
                         {/* RAM Configuration */}
                         <TextField
                              required
                              id="ram-number"
                              name="ram-number"
                              defaultValue="1"
                              label="RAM"
                              type="number"
                              variant="standard"
                              margin="dense"
                              fullWidth
                              inputProps={{ min: 1, max: 32, step: 1 }}
                         />
                         
                         {/* Accessible Directories */}
                         <Autocomplete
                              id="output-path"
                              options={accessibleDirectories}
                              value={selectedOutputPath}
                              onChange={(_, newValue) => setSelectedOutputPath(newValue)}
                              renderInput={(params) => (
                                   <TextField
                                        {...params}
                                        label="Output Path"
                                        variant="standard"
                                        margin="dense"
                                        fullWidth
                                        required
                                   />
                              )}
                         />

                         {/* Advanced Options Toggle */}
                         <Button
                              onClick={() => setShowAdvanced((prev) => !prev)}
                              color="primary"
                              style={{ marginTop: 16, marginBottom: 8 }}
                         >
                              {showAdvanced ? 'Hide Advanced Options' : 'Show Advanced Options'}
                         </Button>
                         
                         {/* Advanced Options Fields */}
                         <Collapse in={showAdvanced}>
                              <div>
                                   {/* Container Image */}
                                   <TextField
                                        id="container-image"
                                        name="container-image"
                                        label="Container Image"
                                        variant="standard"
                                        margin="dense"
                                        fullWidth
                                        style={{ marginTop: 8 }}
                                        value={containerImage}
                                        onChange={e => {
                                             setContainerImage(e.target.value);
                                             setCondaEnvError(false);
                                        }}
                                   />
                                   
                                   {/* Conda Environment */}
                                   <TextField
                                        id="conda-environment"
                                        name="conda-environment"
                                        label="Conda environment"
                                        variant="standard"
                                        margin="dense"
                                        fullWidth
                                        style={{ marginTop: 8 }}
                                        value={condaEnv}
                                        onChange={e => {
                                             setCondaEnv(e.target.value);
                                             setCondaEnvError(false);
                                        }}
                                        error={condaEnvError}
                                        helperText={condaEnvError ? 'Conda environment is required if container image is set.' : ''}
                                   />
                              </div>
                         </Collapse>
                    </DialogContent>
                    <DialogActions>
                         <Button onClick={handleClose}>Cancel</Button>
                         <Button type="submit">Send</Button>
                    </DialogActions>
               </Dialog>
          </React.Fragment>
     );
};

export default NBQueueComponent;
