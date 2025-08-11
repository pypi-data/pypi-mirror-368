/**
 * NBQueue Sidebar Component
 * 
 * React component that provides a sidebar interface for managing and monitoring
 * workflow jobs in the NBQueue system. Displays job status, logs, and provides
 * controls for job management (refresh, view logs, delete, download).
 */

import { AppBar, Avatar, Container, Grid, IconButton, List, ListItem, ListItemAvatar, ListItemText, Toolbar, Typography } from '@mui/material'
import Refresh from '@mui/icons-material/Refresh';
import DeleteSweep from '@mui/icons-material/DeleteSweep';
import Done from '@mui/icons-material/Done';
import Error from '@mui/icons-material/Error';
import Pending from '@mui/icons-material/Pending';
import { Delete } from '@mui/icons-material';
import { CircularProgress, Box } from '@mui/material';

// import Close from '@mui/icons-material/Close';

import React from 'react'
import { requestAPI } from '../handler';
// Eliminado import de WorkflowsResponse
// import { TransitionProps } from '@mui/material/transitions';

/** Interface for workflow data structure */
// Eliminada interfaz Workflow
interface JobHistory {
    job_id: string;
    status: string;
    start_time?: string;
    completion_time?: string;
    error_message?: string;
}

/** Transition component for dialog animations */
// const Transition = React.forwardRef(function Transition(
//      props: TransitionProps & {
//           children: React.ReactElement;
//      },
//      ref: React.Ref<unknown>,
// ) {
//      return <Slide direction="up" ref={ref} {...props} />;
// });

/** Props interface for the NBQueueSideBarComponent */
interface NBQueueSideBarComponentProps {
     bucket: string;
}

/**
 * Main sidebar component for workflow management
 * 
 * Provides a comprehensive interface for viewing, managing, and monitoring
 * NBQueue workflows including status indicators and job controls.
 */
const NBQueueSideBarComponent: React.FC<NBQueueSideBarComponentProps> = (props): JSX.Element => {
    // Estado para mostrar el spinner de carga
    const [loading, setLoading] = React.useState(false);
    // Escucha el evento global para forzar actualización del historial
    React.useEffect(() => {
        const handler = () => {
            getJobHistory(true);
        };
        window.addEventListener('nbqueue-job-submitted', handler);
        return () => {
            window.removeEventListener('nbqueue-job-submitted', handler);
        };
    }, []);
    // Component state management
    const [dense] = React.useState(true)
    const [jobs, setJobs] = React.useState<JobHistory[]>([])

    // Autorefresh progresivo
    const minDelay = 2000; // 2s
    const maxDelay = 30000; // 30s
    const [refreshDelay, setRefreshDelay] = React.useState(minDelay);
    const refreshTimeout = React.useRef<NodeJS.Timeout | null>(null);

    // Función para verificar si todos los jobs han finalizado
    const allJobsFinished = (jobs: JobHistory[]) =>
        jobs.length === 0 || jobs.every(job => {
            const status = job.status?.toLowerCase();
            return status === 'succeeded' || status === 'failed';
        });

    // Función principal de autorefresh
    const progressiveRefresh = async () => {
        await getJobHistory();
        if (!allJobsFinished(jobs)) {
            // Incrementa el delay progresivamente
            setRefreshDelay(prev => Math.min(prev * 2, maxDelay));
        } else {
            // Reinicia el delay si todos terminaron
            setRefreshDelay(minDelay);
        }
    };

    // Efecto para manejar el autorefresh progresivo
    React.useEffect(() => {
        // Limpia el timeout anterior
        if (refreshTimeout.current) {
            clearTimeout(refreshTimeout.current);
        }
        // Si no han terminado todos los jobs, programa el siguiente refresh
        if (!allJobsFinished(jobs)) {
            refreshTimeout.current = setTimeout(() => {
                progressiveRefresh();
            }, refreshDelay);
        }
        // Cleanup al desmontar
        return () => {
            if (refreshTimeout.current) {
                clearTimeout(refreshTimeout.current);
            }
        };
    }, [jobs, refreshDelay]);

    // Reinicia el ciclo de autorefresh al abrir el panel (cuando se monta)
    React.useEffect(() => {
        setRefreshDelay(minDelay);
        getJobHistory();
    }, []);
//     const [selectedJob, setSelectedJob] = React.useState<JobHistory | null>(null);
//     const [scroll, setScroll] = React.useState<DialogProps['scroll']>('paper');
//     const [open, setOpen] = React.useState(false);
//     const [contentLog, setContentLog] = React.useState('');

     /**
      * Renders appropriate status icon based on workflow status
      * @param status - Current workflow status
      * @returns JSX element with appropriate status icon
      */
    function AvatarStatusIcon({ status }: { status: string }) {
        switch (status?.toLowerCase()) {
            case 'running':
                return (<Pending color="primary" />);
            case 'pending':
                return (<Pending color="primary" />);
            case 'succeeded':
                return (<Done style={{ color: 'green' }} />);
            case 'failed':
                return (<Error color="error" />);
            default:
                return (<Error color="disabled" />);
        }
    }

     /**
      * Fetches the list of workflows from the API
      * Updates the component state with the retrieved workflows
      */

    // Fetch job history from /job-history endpoint
    const getJobHistory = async (resetDelay = false) => {
        setLoading(true);
        try {
            const jobs = await requestAPI<JobHistory[]>('jobs', { method: 'GET' });
            setJobs(jobs);
            if (resetDelay) setRefreshDelay(minDelay);
        } catch (error) {
            console.error('Error fetching job history:', error);
        } finally {
            setLoading(false);
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
    const deleteJob = async (job_id: string) => {
        try {
            const result = await requestAPI<any>(`job?job_id=${job_id}`, { method: 'DELETE' });
            getJobHistory(); // Refresh list after delete
            return result;
        } catch (error) {
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
            const result = await requestAPI<{success: boolean; deleted: number}>('jobs', { method: 'DELETE' });
            getJobHistory(); // Refresh list after delete
            console.log(result);
            return result;
        } catch (error) {
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

    React.useEffect(() => {
        getJobHistory();
    }, [])

    return (
        <React.Fragment>
            <AppBar>
                <Toolbar>
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                        NBQueue job history
                    </Typography>
                    <span title="Refresh job history">
                        <IconButton aria-label="refresh" onClick={() => getJobHistory(true)} color="inherit">
                            <Refresh />
                        </IconButton>
                    </span>
                    <span title="Delete all job history">
                        <IconButton aria-label="delete-all" onClick={() => {
                            if (window.confirm('Are you sure you want to delete all job history?')) {
                                deleteAllJobs();
                            }
                        }} color="inherit">
                            <DeleteSweep />
                        </IconButton>
                    </span>
                </Toolbar>
            </AppBar>
            <Toolbar />
            <Container sx={{
                height: '100%',
                overflowY: 'auto',
                paddingBottom: 5
            }}>
                {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
                        <CircularProgress />
                    </Box>
                ) : (
                    <Grid container direction="row" justifyContent="space-between" alignItems="flex-start" rowSpacing={1} columnSpacing={{ xs: 1, sm: 2, md: 3 }}>
                        <Grid item xs={12}>
                            <nav aria-label="job history list">
                                <List dense={dense}>
                                    {jobs.map(job => (
                                        <ListItem key={job.job_id} button
                                            secondaryAction={
                                                <span title={`Delete job ${job.job_id}`}>
                                                    <IconButton edge="end" aria-label="delete" onClick={async () => {
                                                        if (window.confirm(`Are you sure you want to delete this job?\nJob ID: ${job.job_id}`)) {
                                                            await deleteJob(job.job_id);
                                                        }
                                                    }}>
                                                        <Delete />
                                                    </IconButton>
                                                </span>
                                            }
                                            // onClick can be used for future details dialog, but no alert for delete
                                        >
                                            <ListItemAvatar>
                                                <Avatar sx={{ bgcolor: 'transparent', boxShadow: 'none' }}>
                                                    <AvatarStatusIcon status={job.status} />
                                                </Avatar>
                                            </ListItemAvatar>
                                            <ListItemText
                                                primary={job.job_id}
                                                secondary={
                                                    <React.Fragment>
                                                        <Typography
                                                            sx={{ display: 'inline' }}
                                                            component="span"
                                                            variant="body2"
                                                            color="text.primary"
                                                        >
                                                            {job.start_time ? `Started: ${job.start_time}` : ''}
                                                        </Typography>
                                                        {` — ${job.status}`}
                                                        {job.error_message ? ` — Error: ${job.error_message}` : ''}
                                                    </React.Fragment>
                                                }
                                            />
                                        </ListItem>
                                    ))}
                                    <ListItem>
                                        <ListItemText></ListItemText>
                                    </ListItem>
                                </List>
                            </nav>
                        </Grid>
                    </Grid>
                )}
            </Container>
            {/* Eliminado custom dialog, ahora ambos usan window.confirm para consistencia visual y UX */}
        </React.Fragment >
     );
}

export default NBQueueSideBarComponent;