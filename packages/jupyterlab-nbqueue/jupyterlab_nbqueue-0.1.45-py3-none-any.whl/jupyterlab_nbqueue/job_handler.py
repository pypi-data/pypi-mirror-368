"""
MPI Job Handler for JupyterLab NBQueue Extension.

This module provides HTTP request handling for MPI job submission in JupyterLab.
It validates incoming requests, manages file organization, and communicates with
the backend gRPC service for job execution.

Main components:
- Pydantic models for request validation
- Hierarchical directory structure for job files
- gRPC communication for job submission
- Error handling and logging
"""

import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Job, Base
import os
import re
import shutil
import asyncio
from datetime import datetime
from shutil import which
from typing import Optional

import grpc
import tornado.web
from jupyter_server.base.handlers import APIHandler
from loguru import logger
from pydantic import BaseModel, ValidationError, field_validator, constr, conint, model_validator
from typing_extensions import Annotated

# Import proto modules and config in a try-catch to avoid circular imports
try:
    from .proto import service_pb2, service_pb2_grpc
    from .config import settings
    
    # Load configuration settings
    NBQUEUE_SERVER = settings.NBQUEUE_SERVER
    LOG_LEVEL = settings.LOG_LEVEL
    NBQUEUE_LOG_FILE_PATH = settings.NBQUEUE_LOG_FILE_PATH
    IS_DEV = LOG_LEVEL == "DEBUG"
except ImportError as e:
    # Fallback values if imports fail during initialization
    NBQUEUE_SERVER = "localhost:50051"
    LOG_LEVEL = "DEBUG"
    NBQUEUE_LOG_FILE_PATH = "logs/mpi_job_launcher.log"
    IS_DEV = True
    print(f"Warning: Could not import proto/config modules: {e}")
    # These will be imported later when actually needed
    service_pb2 = None
    service_pb2_grpc = None

# Configure logger
logger.remove()
logger.add(
    NBQUEUE_LOG_FILE_PATH,
    rotation="00:00",
    retention="7 days",
    compression="zip",
    level=LOG_LEVEL,
)

if IS_DEV:
    logger.add(lambda msg: print(msg, end=""), level=LOG_LEVEL)


# Pydantic models for request validation
class NotebookFileModel(BaseModel):
    """Model for notebook file metadata validation."""
    name: Annotated[str, constr(strip_whitespace=True, min_length=1, pattern=r".*\.ipynb$")]
    path: Annotated[str, constr(strip_whitespace=True, min_length=1)]


class JobRequestModel(BaseModel):
    """
    Model for validating job submission requests.
    
    Validates all required fields for notebook job execution including
    resource requirements, environment specifications, and file paths.
    """
    notebook_file: NotebookFileModel
    image: Optional[Annotated[str, constr(strip_whitespace=True, min_length=1)]] = None
    conda_env: Optional[Annotated[str, constr(strip_whitespace=True, min_length=1)]] = None
    output_path: Annotated[str, constr(strip_whitespace=True, min_length=1)]
    cpu: Annotated[int, conint(gt=0)]
    ram: Annotated[str, constr(strip_whitespace=True, min_length=1, pattern=r"^\d+(\.\d+)?(Gi|G|Mi|M)?$")]
    owner: Optional[str] = None
    nbqueue_job_name: Optional[str] = None

    @field_validator('output_path', mode='before')
    @classmethod
    def validate_not_empty(cls, v):
        """Ensure output_path is not empty after stripping whitespace."""
        if v is None or (isinstance(v, str) and v.strip() == ""):
            raise ValueError("Field cannot be empty.")
        return v

    @model_validator(mode="after")
    def validate_notebook_file(self):
        """Validate notebook file has correct extension."""
        nb_file = self.notebook_file
        if not nb_file or not nb_file.name.endswith('.ipynb'):
            raise ValueError('notebook_file.name must end with .ipynb')
        return self

    @field_validator('ram')
    @classmethod
    def validate_ram_format(cls, v):
        """Validate RAM format matches expected pattern with optional units."""
        if not re.match(r'^\d+(\.\d+)?(Gi|G|Mi|M)?$', v):
            raise ValueError("RAM must be a valid number optionally followed by unit (e.g., '4', '4Gi', '2048Mi').")
        return v

    @field_validator('cpu')
    @classmethod
    def validate_cpu_positive(cls, v):
        """Ensure CPU value is positive."""
        if v <= 0:
            raise ValueError('CPU value must be greater than 0.')
        return v

    class Config:
        extra = 'allow'

class JobHandler(APIHandler):
    @tornado.web.authenticated
    async def delete(self):
        """
        Delete a job from the job history by job_id.
        Expects job_id as a query parameter or in the JSON body.
        """
        job_id = self.get_argument("job_id", None)
        if not job_id:
            # Try to get from JSON body if not in query params
            try:
                json_body = self.get_json_body()
                job_id = json_body.get("job_id") if json_body else None
            except Exception:
                job_id = None
        if not job_id:
            self.set_status(400)
            self.finish(json.dumps({"error": "Missing job_id parameter"}))
            return
        session = self.SessionLocal()
        try:
            job = session.query(Job).filter_by(job_id=job_id).first()
            if not job:
                self.set_status(404)
                self.finish(json.dumps({"error": f"Job with id {job_id} not found"}))
                return
            session.delete(job)
            session.commit()
            self.write({"success": True, "message": f"Job {job_id} deleted"})
        except Exception as exc:
            session.rollback()
            self.set_status(500)
            self.finish(json.dumps({"error": str(exc)}))
        finally:
            session.close()
    # SQLite database initialization
    engine = create_engine(f"sqlite:///.nbqueue_jobs.db", echo=False, future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    @tornado.web.authenticated
    async def get(self):
        # Get job_id and namespace from GET parameters
        job_id = self.get_argument("job_id", None)
        namespace = self.get_argument("namespace", "default")
        if not job_id:
            self.set_status(400)
            self.finish(json.dumps({"error": "Missing job_id parameter"}))
            return
        # Query status from gRPC server
        try:
            with grpc.insecure_channel(os.environ.get("NBQUEUE_SERVER", "localhost:50051")) as channel:
                stub = service_pb2_grpc.NBQueueServiceStub(channel)
                request = service_pb2.JobStatusRequest(job_id=job_id, namespace=namespace)
                response = stub.GetJobStatus(request)
        except Exception as exc:
            self.set_status(500)
            self.finish(json.dumps({"error": str(exc)}))
            return
        # Save request and response in the database
        session = self.SessionLocal()
        try:
            job_record = Job(
                job_id=job_id,
                request_json=json.dumps({"job_id": job_id, "namespace": namespace}),
                response_json=json.dumps({
                    "success": getattr(response, "success", None),
                    "status": getattr(response, "status", None),
                    "job_json": getattr(response, "job_json", None),
                    "active_pods": getattr(response, "active_pods", None),
                    "succeeded_pods": getattr(response, "succeeded_pods", None),
                    "failed_pods": getattr(response, "failed_pods", None),
                    "start_time": getattr(response, "start_time", None),
                    "completion_time": getattr(response, "completion_time", None),
                    "error_message": getattr(response, "error_message", None)
                }),
                status=getattr(response, "status", None),
                error_message=getattr(response, "error_message", None)
            )
            session.add(job_record)
            session.commit()
        except Exception as db_exc:
            session.rollback()
        finally:
            session.close()
        # Build response
        response_data = {
            "success": getattr(response, "success", None),
            "status": getattr(response, "status", None),
            "job_json": getattr(response, "job_json", None),
            "active_pods": getattr(response, "active_pods", None),
            "succeeded_pods": getattr(response, "succeeded_pods", None),
            "failed_pods": getattr(response, "failed_pods", None),
            "start_time": getattr(response, "start_time", None),
            "completion_time": getattr(response, "completion_time", None)
        }
        if getattr(response, "error_message", None):
            response_data["error_message"] = getattr(response, "error_message", None)
        self.write(response_data)


    """
    Handler for MPI job submission requests.
    
    Processes notebook execution requests by:
    1. Validating input data using Pydantic models
    2. Creating organized directory structure for job files
    3. Copying notebook and conda environment files
    4. Submitting job to gRPC service
    5. Returning job status and metadata
    """

    async def _get_system_ids(self) -> tuple[str, str]:
        """
        Get system UID and GID using 'id' command asynchronously.
        
        Returns:
            tuple: (uid, gid) as strings, empty strings if failed
        """
        try:
            logger.debug("Getting uid and gid from system...")
            
            # Run uid command asynchronously
            uid_process = await asyncio.create_subprocess_exec(
                'id', '-u',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            uid_stdout, uid_stderr = await uid_process.communicate()
            
            # Run gid command asynchronously
            gid_process = await asyncio.create_subprocess_exec(
                'id', '-g',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            gid_stdout, gid_stderr = await gid_process.communicate()
            
            if uid_process.returncode == 0 and gid_process.returncode == 0:
                uid = uid_stdout.decode().strip()
                gid = gid_stdout.decode().strip()
                logger.debug("System uid: {}, gid: {}", uid, gid)
                return uid, gid
            else:
                logger.warning("Failed to get uid/gid from system. Using defaults.")
                return '', ''
                
        except Exception as e:
            logger.warning("Unexpected error getting uid/gid: {}. Using defaults.", e)
            return '', ''

    async def _generate_conda_environment_file(self, file_path: str) -> str:
        """
        Generate conda environment file using 'conda list --explicit' asynchronously.
        
        Args:
            file_path: Base path for the temporary conda file
            
        Returns:
            str: Path to the generated conda environment file
        """
        conda_env_file = f"{file_path}.txt"
        logger.info("Generating conda environment file at: {}", conda_env_file)
        
        try:
            conda_cmd = f"{which('conda')} list --explicit"
            
            # Run conda command asynchronously
            process = await asyncio.create_subprocess_shell(
                conda_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Write output to file
            with open(conda_env_file, "w") as f_obj:
                f_obj.write(stdout.decode())
            
            if process.returncode != 0:
                logger.warning("There were some errors creating the conda file: {}", stderr.decode())
            
        except Exception as e:
            logger.warning("Failed to generate conda environment file: {}", e)
            # Create empty file as fallback
            with open(conda_env_file, "w") as f_obj:
                f_obj.write("# Conda environment generation failed\n")
        
        return conda_env_file

    async def _create_job_directory_structure(self, output_path: str, owner: str, 
                                            file_name: str, timestamp: str) -> str:
        """
        Create hierarchical directory structure for job files asynchronously.
        
        Structure: /output_path/owner/notebook_name/notebook_name-timestamp/
        
        Args:
            output_path: Base output directory
            owner: Job owner/username
            file_name: Notebook name without extension
            timestamp: Unique timestamp for job
            
        Returns:
            str: Path to the created job directory
            
        Raises:
            ValueError: If directory creation fails
        """
        job_folder_name = f"{file_name}-{timestamp}"
        job_dir = os.path.join(output_path, file_name, job_folder_name)
        
        try:
            # Use asyncio thread pool for I/O operations
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: os.makedirs(job_dir, exist_ok=True))
            
            logger.info("Created job directory structure: {}", job_dir)
            return job_dir
        except Exception as e:
            logger.error("Failed to create job directory structure {}: {}", job_dir, e)
            raise ValueError(f"Cannot create job directory structure: {job_dir}")

    async def _copy_job_files(self, job_dir: str, notebook_path: str, notebook_file: str,
                            conda_env_file: str, file_name: str) -> None:
        """
        Copy notebook and conda environment files to job directory asynchronously.
        
        Args:
            job_dir: Target job directory
            notebook_path: Source notebook file path
            notebook_file: Notebook filename
            conda_env_file: Source conda environment file path
            file_name: Notebook name without extension
            
        Raises:
            ValueError: If notebook copy fails (conda env copy is non-critical)
        """
        loop = asyncio.get_event_loop()
        
        # Copy notebook file asynchronously
        try:
            notebook_dest = os.path.join(job_dir, notebook_file)
            await loop.run_in_executor(None, lambda: shutil.copy2(notebook_path, notebook_dest))
            logger.info("Copied notebook from {} to {}", notebook_path, notebook_dest)
        except Exception as e:
            logger.error("Failed to copy notebook: {}", e)
            raise ValueError(f"Cannot copy notebook to job directory: {e}")

        # Copy conda environment file asynchronously (non-critical)
        if os.path.exists(conda_env_file):
            try:
                conda_dest = os.path.join(job_dir, f"{file_name}-conda-env.txt")
                await loop.run_in_executor(None, lambda: shutil.copy2(conda_env_file, conda_dest))
                logger.info("Copied conda environment file from {} to {}", 
                           conda_env_file, conda_dest)
            except Exception as e:
                logger.warning("Failed to copy conda environment file: {}", e)
        else:
            logger.warning("Conda environment file was not generated, skipping copy")

    def _create_job_log_file(self, job_dir: str, nbqueue_job_name: str, 
                           notebook_file: str, owner: str, image: Optional[str], 
                           conda_env: Optional[str], cpu: str, ram: str, output_path: str) -> None:
        """
        Create initial log file with job metadata.
        
        Args:
            job_dir: Job directory path
            nbqueue_job_name: Job identifier
            notebook_file: Notebook filename
            owner: Job owner
            image: Container image (optional)
            conda_env: Conda environment (optional)
            cpu: CPU allocation
            ram: RAM allocation
            output_path: Output directory path
        """
        try:
            logs_file = os.path.join(job_dir, "logs.log")
            with open(logs_file, "w") as f:
                f.write(f"Job started at: {datetime.now().isoformat()}\n")
                f.write(f"Job ID: {nbqueue_job_name}\n")
                f.write(f"Notebook: {notebook_file}\n")
                f.write(f"Owner: {owner}\n")
                f.write(f"Output Path: {job_dir}\n")
                f.write(f"Image: {image if image else 'N/A'}\n")
                f.write(f"Conda Env: {conda_env if conda_env else 'N/A'}\n")
                f.write(f"CPU: {cpu}, RAM: {ram}\n")
                f.write("=" * 50 + "\n")
            logger.debug("Created logs file: {}", logs_file)
        except Exception as e:
            logger.warning("Failed to create logs file: {}", e)

    async def _cleanup_temporary_files(self, conda_env_file: str) -> None:
        """
        Clean up temporary files created during job preparation asynchronously.
        
        Args:
            conda_env_file: Path to temporary conda environment file
        """
        try:
            if os.path.exists(conda_env_file):
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, lambda: os.remove(conda_env_file))
                logger.debug("Cleaned up temporary conda file: {}", conda_env_file)
        except Exception as e:
            logger.warning("Failed to clean up temporary conda file: {}", e)

    def _submit_grpc_job(self, notebook_file: str, owner: str, project: str, 
                        nbqueue_job_name: str, image: str, conda_env: str, 
                        job_dir: str, cpu: str, ram: str, uid: str, gid: str):
        """
        Submit job to gRPC service (runs in thread pool).
        
        Args:
            notebook_file: Notebook filename
            owner: Job owner
            project: Project name
            nbqueue_job_name: Job identifier
            image: Container image
            conda_env: Conda environment
            job_dir: Job directory path
            cpu: CPU allocation
            ram: RAM allocation
            uid: User ID
            gid: Group ID
            
        Returns:
            gRPC response object
        """
        with grpc.insecure_channel(NBQUEUE_SERVER) as channel:
            stub = service_pb2_grpc.NBQueueServiceStub(channel)
            request = service_pb2.CreateJobRequest(
                notebook_file=notebook_file,
                owner=owner,
                project=project,
                nbqueue_job_name=nbqueue_job_name,
                image=image,
                conda_env=conda_env,
                output_path=job_dir,
                cpu=cpu,
                ram=ram,
                uid=uid,
                gid=gid,
            )
            logger.info(
                f"Sending gRPC job request: "
                f"notebook_file={notebook_file}, owner={owner}, project={project}, nbqueue_job_name={nbqueue_job_name}, "
                f"image={image}, conda_env={conda_env}, output_path={job_dir}, cpu={cpu}, ram={ram}, uid={uid}, gid={gid}"
            )
            response = stub.CreateJob(request)
            logger.debug("Received response from NBQUEUE_SERVER: {}", response)
            return response

    @tornado.web.authenticated
    async def post(self):
        """
        Handle POST requests for job submission.
        
        Validates request data, prepares job environment, and submits to gRPC service.
        Returns job status and metadata including directory structure information.
        """
        # Ensure proto modules are imported if they failed during initial import
        global service_pb2, service_pb2_grpc
        if service_pb2 is None or service_pb2_grpc is None:
            try:
                from .proto import service_pb2, service_pb2_grpc
            except ImportError as e:
                logger.error("Failed to import proto modules: {}", e)
                self.set_status(500)
                self.finish(json.dumps({"error": "gRPC service modules not available"}))
                return
        
        try:
            json_body = self.get_json_body()
            logger.info("Received request body: {}", json_body)

            if json_body is None:
                raise ValueError("Request body is missing.")

            # Validate and parse request using Pydantic
            try:
                job_data = JobRequestModel(**json_body)
            except ValidationError as ve:
                logger.error("Validation error: {}", ve)
                self.set_status(422)
                self.finish(json.dumps({"error": ve.errors()}))
                return

            # Extract and prepare job parameters
            notebook_file = job_data.notebook_file.name
            notebook_path = job_data.notebook_file.path
            file_name, file_extension = os.path.splitext(notebook_file)
            file_path, file_extension = os.path.splitext(notebook_path)

            # Extract username from URL
            full_url = self.request.full_url()
            # full_url = "http://localhost:8888/user/jovyan/jupyterlab-nbqueue/submit"
            logger.debug("Full URL: {}", full_url)
            match = re.search(r"/user/([^/]+)/", full_url)
            username = match.group(1) if match else "testuser"
            logger.debug("Extracted username: {}", username)

            # Extract validated values from request body
            image = job_data.image
            conda_env = job_data.conda_env
            output_path = job_data.output_path
            cpu = str(job_data.cpu)
            ram = str(job_data.ram)

            # Set optional fields with defaults
            owner = job_data.owner or username
            project = os.environ.get("OSSProject", "").strip()
            
            # Generate unique timestamp and job identifiers
            timestamp = datetime.now().strftime("%m%d%Y%H%M%S")
            job_folder_name = f"{file_name}-{timestamp}"
            nbqueue_job_name = job_data.nbqueue_job_name or f"{username}-{file_name}-{timestamp}"
            
            # Get system user IDs asynchronously
            uid, gid = await self._get_system_ids()

            # Generate conda environment file asynchronously
            conda_env_file = await self._generate_conda_environment_file(file_path)

            # Create job directory structure asynchronously
            job_dir = await self._create_job_directory_structure(
                output_path, owner, file_name, timestamp)

            # Copy files to job directory asynchronously
            await self._copy_job_files(job_dir, notebook_path, notebook_file, 
                                     conda_env_file, file_name)

            # Create initial log file
            self._create_job_log_file(job_dir, nbqueue_job_name, notebook_file, 
                                    owner, image, conda_env, cpu, ram, output_path)

            # Clean up temporary files asynchronously
            await self._cleanup_temporary_files(conda_env_file)

            # Submit job to gRPC service asynchronously
            logger.debug("Creating CreateJobRequest with extracted values")
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self._submit_grpc_job, 
                                                notebook_file, owner, project, nbqueue_job_name,
                                                image, conda_env, job_dir, cpu, ram, uid, gid)

            # Save request and response in the database
            session = self.SessionLocal()
            try:
                job_record = Job(
                    job_id=getattr(response, "job_id", None),
                    notebook_file=notebook_file,
                    owner=owner,
                    project=project,
                    nbqueue_job_name=nbqueue_job_name,
                    image=image,
                    conda_env=conda_env,
                    output_path=output_path,
                    cpu=cpu,
                    ram=ram,
                    uid=uid,
                    gid=gid,
                    request_json=json.dumps(json_body),
                    response_json=json.dumps({
                        "success": getattr(response, "success", None),
                        "job_id": getattr(response, "job_id", None),
                        "kubectl_output": getattr(response, "kubectl_output", None),
                        "error_message": getattr(response, "error_message", None)
                    }),
                    status="success" if getattr(response, "success", False) else "error",
                    error_message=getattr(response, "error_message", None)
                )
                session.add(job_record)
                session.commit()
            except Exception as db_exc:
                logger.error("Error saving job to database: {}", db_exc)
                session.rollback()
            finally:
                session.close()

            # Build response with job metadata
            response_data = {
                "success": getattr(response, "success", None),
                "job_id": getattr(response, "job_id", None),
                "kubectl_output": getattr(response, "kubectl_output", None),
                "job_directory": job_dir,
                "job_folder_name": job_folder_name
            }
            if getattr(response, "error_message", None):
                response_data["error_message"] = getattr(response, "error_message", None)

            self.write(response_data)
            
        except grpc.RpcError as e:
            logger.error("gRPC Error: {}", e)
            self.set_status(400)
            self.finish(json.dumps({"error": str(e)}))
        except (ValueError, KeyError) as e:
            logger.error("Error in the request body: {}", e)
            self.set_status(400)
            self.finish(json.dumps({"error": str(e)}))
        except Exception as e:
            logger.exception("Unhandled exception in JobHandler: {}", e)
            self.set_status(500)
            self.finish(json.dumps({"error": "Internal server error."}))
