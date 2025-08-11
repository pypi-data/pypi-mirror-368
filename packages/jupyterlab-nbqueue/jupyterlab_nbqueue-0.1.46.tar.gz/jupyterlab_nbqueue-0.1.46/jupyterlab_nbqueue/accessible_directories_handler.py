"""
Accessible Directories Handler for JupyterLab NBQueue Extension.

This module provides HTTP request handling for listing accessible subdirectories
within a shared directory path. It filters directories based on user permissions
to improve user experience by showing only accessible paths.

Main components:
- Pydantic models for request validation
- Asynchronous directory access checking
- User permission validation
- Error handling and logging
"""

import json
import os
import re
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

import tornado.web
from jupyter_server.base.handlers import APIHandler
from loguru import logger
from pydantic import BaseModel, ValidationError, field_validator, constr
from typing_extensions import Annotated

# Import config in a try-catch to avoid circular imports
try:
    from .config import settings
    
    # Load configuration settings
    LOG_LEVEL = settings.LOG_LEVEL
    NBQUEUE_LOG_FILE_PATH = settings.NBQUEUE_LOG_FILE_PATH
    IS_DEV = LOG_LEVEL == "DEBUG"
except ImportError as e:
    # Fallback values if imports fail during initialization
    LOG_LEVEL = "DEBUG"
    NBQUEUE_LOG_FILE_PATH = "logs/accessible_directories.log"
    IS_DEV = True
    print(f"Warning: Could not import config modules: {e}")

# Configure logger for this handler
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
class DirectoryAccessRequest(BaseModel):
    """
    Model for validating directory access requests.
    
    Validates the root directory path from which to list accessible subdirectories.
    """
    root_path: Annotated[str, constr(strip_whitespace=True, min_length=1)]
    
    @field_validator('root_path')
    @classmethod
    def validate_root_path(cls, v):
        """Ensure root path is not empty and is a valid path format."""
        if not v or v.strip() == "":
            raise ValueError("Root path cannot be empty.")
        
        # Expand '~' to absolute path
        v = os.path.expanduser(v)
        
        # Basic path validation (no traversal attacks)
        if ".." in v:
            raise ValueError("Invalid path: path traversal not allowed.")
        
        return v.strip()

    class Config:
        extra = 'forbid'  # Don't allow extra fields


class DirectoryInfo(BaseModel):
    """Model for directory information response."""
    name: str
    path: str
    is_accessible: bool
    error_message: Optional[str] = None
    last_modified: Optional[str] = None
    size_bytes: Optional[int] = None


class AccessibleDirectoriesHandler(APIHandler):
    """
    Handler for listing accessible subdirectories within a shared directory.
    
    Processes directory access requests by:
    1. Validating the root directory path
    2. Listing all subdirectories in the root path
    3. Testing access permissions for each subdirectory
    4. Returning only accessible directories with metadata
    """

    async def _check_directory_access(self, directory_path: str) -> Dict[str, Any]:
        """
        Check if a directory is accessible to the user asynchronously.
        
        Args:
            directory_path: Path to the directory to check
            
        Returns:
            Dict containing access information and metadata
        """
        directory_info = {
            "name": os.path.basename(directory_path),
            "path": directory_path,
            "is_accessible": False,
            "error_message": None,
            "last_modified": None,
            "size_bytes": None
        }
        
        try:
            # Check if directory exists
            if not os.path.exists(directory_path):
                directory_info["error_message"] = "Directory does not exist"
                return directory_info
            
            if not os.path.isdir(directory_path):
                directory_info["error_message"] = "Path is not a directory"
                return directory_info
            
            # Use asyncio executor for I/O operations to avoid blocking
            loop = asyncio.get_event_loop()
            
            # Test read access by trying to list directory contents
            try:
                contents = await loop.run_in_executor(None, lambda: os.listdir(directory_path))
                directory_info["is_accessible"] = True
                
                # Get additional metadata if accessible
                stat_info = await loop.run_in_executor(None, lambda: os.stat(directory_path))
                directory_info["last_modified"] = datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                directory_info["size_bytes"] = stat_info.st_size
                
            except PermissionError:
                directory_info["is_accessible"] = False
                directory_info["error_message"] = "Permission denied"
                
            except Exception as e:
                directory_info["is_accessible"] = False
                directory_info["error_message"] = f"Access check failed: {str(e)}"
                logger.warning("Access check failed for directory {}: {}", directory_path, e)
                
        except Exception as e:
            directory_info["error_message"] = f"Unexpected error: {str(e)}"
            logger.error("Unexpected error checking directory access for {}: {}", directory_path, e)
        
        return directory_info

    async def _get_accessible_subdirectories(self, root_path: str) -> List[Dict[str, Any]]:
        """
        Get list of accessible subdirectories within the root path using 'find' for accurate filtering.
        Only first-level subdirectories that are readable and executable are returned.
        """
        logger.info("Getting accessible subdirectories for root path: {}", root_path)
        import subprocess
        accessible_dirs = []
        try:
            if not os.path.exists(root_path):
                logger.error("Root directory does not exist: {}", root_path)
                return []
            if not os.path.isdir(root_path):
                logger.error("Root path is not a directory: {}", root_path)
                return []
            # Run the find command to get first-level readable and executable directories
            find_cmd = [
                "find", root_path,
                "-maxdepth", "1",
                "-mindepth", "1",
                "-type", "d",
                "-readable",
                "-exec", "test", "-x", "{}", ";",
                "-print"
            ]
            proc = await asyncio.create_subprocess_exec(
                *find_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                logger.error("find command failed: {}", stderr.decode())
                return []
            dir_paths = [line.strip() for line in stdout.decode().splitlines() if line.strip()]
            # Check access for each directory
            access_tasks = [self._check_directory_access(d) for d in dir_paths]
            directory_results = await asyncio.gather(*access_tasks, return_exceptions=True)
            for result in directory_results:
                if isinstance(result, dict):
                    accessible_dirs.append(result)
                    if result["is_accessible"]:
                        logger.debug("Accessible: {}", result["path"])
                else:
                    logger.warning("Error in directory access check: {}", result)
            accessible_dirs.sort(key=lambda x: x["name"].lower())
        except Exception as e:
            logger.exception("Unexpected error getting accessible subdirectories: {}", e)
        return accessible_dirs

    @tornado.web.authenticated
    async def post(self):
        """
        Handle POST requests for listing accessible directories.
        
        Validates request data, extracts username, and returns list of accessible
        subdirectories with their metadata and access status.
        """
        try:
            json_body = self.get_json_body()
            logger.info("Received accessible directories request: {}", json_body)

            if json_body is None:
                raise ValueError("Request body is missing.")

            # Validate and parse request using Pydantic
            try:
                request_data = DirectoryAccessRequest(**json_body)
            except ValidationError as ve:
                logger.error("Validation error: {}", ve)
                self.set_status(422)
                self.finish(json.dumps({
                    "error": "Validation failed",
                    "details": [
                        {
                            "type": err["type"],
                            "loc": err["loc"],
                            "msg": err["msg"],
                            "input": err.get("input")
                        } for err in ve.errors()
                    ]
                }))
                return

            # Extract parameters
            root_path = request_data.root_path
            
            logger.info("Processing directory access request for path: {}", 
                       root_path)

            # Get accessible subdirectories
            accessible_directories = await self._get_accessible_subdirectories(root_path)
            
            # Build response
            response_data = {
                "success": True,
                "root_path": root_path,
                "total_directories": len(accessible_directories),
                "accessible_directories": accessible_directories,
                "accessible_count": sum(1 for d in accessible_directories if d["is_accessible"]),
                "timestamp": datetime.now().isoformat()
            }
            
            self.set_header("Content-Type", "application/json")
            self.write(response_data)
            
        except ValueError as e:
            logger.error("Validation error in request: {}", e)
            self.set_status(400)
            self.finish(json.dumps({
                "success": False,
                "error": "Invalid request",
                "message": str(e)
            }))
        except Exception as e:
            logger.exception("Unhandled exception in AccessibleDirectoriesHandler: {}", e)
            self.set_status(500)
            self.finish(json.dumps({
                "success": False,
                "error": "Internal server error",
                "message": "An unexpected error occurred while processing the request."
            }))
