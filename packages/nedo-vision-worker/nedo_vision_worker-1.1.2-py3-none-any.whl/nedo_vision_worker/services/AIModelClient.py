import os
import logging
import threading
import time
from pathlib import Path
from enum import Enum
from typing import Dict, Optional

from ..models.ai_model import AIModelEntity
from ..repositories.AIModelRepository import AIModelRepository
from .GrpcClientBase import GrpcClientBase
from ..protos.AIModelService_pb2_grpc import AIModelGRPCServiceStub
from ..protos.AIModelService_pb2 import (
    GetAIModelListRequest, 
    DownloadAIModelRequest
)
from ..database.DatabaseManager import _get_storage_paths


class DownloadState(Enum):
    """Enum for tracking download states."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DownloadInfo:
    """Class to track download information."""
    def __init__(self, model_id: str, model_name: str, version: str):
        self.model_id = model_id
        self.model_name = model_name
        self.version = version
        self.state = DownloadState.PENDING
        self.start_time = None
        self.end_time = None
        self.error_message = None
        self.thread = None
        self.stop_event = threading.Event()


class AIModelClient(GrpcClientBase):
    """Client for interacting with AI models via gRPC with improved download tracking."""
    
    def __init__(self, token, server_host: str, server_port: int = 50051):
        super().__init__(server_host, server_port)
        storage_paths = _get_storage_paths()
        self.models_path = storage_paths["models"]
        self.models_path.mkdir(parents=True, exist_ok=True)
        self.repository = AIModelRepository()
        self.token = token
        
        # Download tracking
        self.download_tracker: Dict[str, DownloadInfo] = {}
        self.download_lock = threading.Lock()
        
        try:
            self.connect(AIModelGRPCServiceStub)
        except Exception as e:
            logging.error(f"Failed to connect to gRPC server: {e}")
            self.stub = None

    def _get_model_path(self, file: str) -> Path:
        """Get the path to a local AI model file."""
        return self.models_path / os.path.basename(file)

    def _is_model_file_exists(self, file_path: str) -> bool:
        """Check if the model file actually exists on disk."""
        if not file_path:
            return False
        model_path = self._get_model_path(file_path)
        return model_path.exists() and model_path.stat().st_size > 0

    def _get_download_info(self, model_id: str) -> Optional[DownloadInfo]:
        """Get download info for a model."""
        with self.download_lock:
            return self.download_tracker.get(model_id)

    def _set_download_info(self, model_id: str, download_info: DownloadInfo):
        """Set download info for a model."""
        with self.download_lock:
            self.download_tracker[model_id] = download_info

    def _remove_download_info(self, model_id: str):
        """Remove download info for a model."""
        with self.download_lock:
            self.download_tracker.pop(model_id, None)

    def _is_downloading(self, model_id: str) -> bool:
        """Check if a model is currently being downloaded."""
        download_info = self._get_download_info(model_id)
        if not download_info:
            return False
        return download_info.state in [DownloadState.PENDING, DownloadState.DOWNLOADING]

    def _cancel_download(self, model_id: str):
        """Cancel an ongoing download."""
        download_info = self._get_download_info(model_id)
        if download_info and download_info.state in [DownloadState.PENDING, DownloadState.DOWNLOADING]:
            download_info.state = DownloadState.CANCELLED
            download_info.stop_event.set()
            if download_info.thread and download_info.thread.is_alive():
                download_info.thread.join(timeout=5)
            self._update_model_download_status(model_id, "cancelled", "Download cancelled")
            logging.info(f"🛑 Cancelled download for model {download_info.model_name}")

    def _update_model_download_status(self, model_id: str, status: str, error_message: str = None):
        """Update the download status in the database."""
        try:
            from datetime import datetime
            model = self.repository.get_model_by_id(model_id)
            if model:
                model.download_status = status
                model.last_download_attempt = datetime.utcnow()
                if error_message:
                    model.download_error = error_message
                self.repository.session.commit()
        except Exception as e:
            logging.error(f"❌ Error updating model download status: {e}")
            self.repository.session.rollback()

    def sync_ai_models(self, worker_id: str) -> dict:
        """Fetch and sync AI model list from gRPC service using token authentication."""
        if not self.stub:
            return {"success": False, "message": "gRPC connection is not established."}
        
        try:
            # Get model list from server
            response = self._fetch_model_list(worker_id)
            if not response or not response.success:
                return {"success": False, "message": response.message if response else "Unknown error"}
            
            # Process models
            self._process_server_models(response.data)
            
            return {"success": True, "message": response.message, "data": response.data}
        
        except Exception as e:
            logging.error(f"Error fetching AI model list: {e}")
            return {"success": False, "message": f"Error occurred: {e}"}

    def _fetch_model_list(self, worker_id: str):
        """Fetch model list from server using token authentication."""
        request = GetAIModelListRequest(worker_id=worker_id, token=self.token)
        return self.handle_rpc(self.stub.GetAIModelList, request)

    def _process_server_models(self, server_models):
        """Process server models, handling additions, updates, and deletions."""
        local_models = {model.id: model for model in self.repository.get_models()}
        server_model_ids = set()
        
        new_models = []
        updated_models = []
        
        # Process each model from the server
        for model in server_models:
            server_model_ids.add(model.id)
            existing_model = local_models.get(model.id)

            if existing_model:
                self._handle_existing_model(model, existing_model, updated_models)
            else:
                self._handle_new_model(model, new_models)
        
        # Handle models that no longer exist on the server
        models_to_delete = [
            model for model_id, model in local_models.items()
            if model_id not in server_model_ids
        ]
        
        self._save_changes(new_models, updated_models, models_to_delete)

    def _handle_existing_model(self, server_model, local_model, updated_models):
        """Handle model that exists locally but might need updates."""
        # Check if model file actually exists
        if not self._is_model_file_exists(local_model.file):
            logging.warning(f"⚠️ Model file missing for {local_model.name}. Re-downloading...")
            self._schedule_model_download(server_model)
            return

        # Check if version or type changed
        if server_model.version == local_model.version and server_model.ai_model_type_code == local_model.type:
            return

        logging.info(f"🔄 Model update detected: {server_model.name} "
                    f"(Version {local_model.version} -> {server_model.version}). Updating...")
        
        # Cancel any ongoing download for this model
        self._cancel_download(server_model.id)
        
        # Delete old model file
        self.delete_local_model(local_model.file)
        
        # Schedule new download
        self._schedule_model_download(server_model)

        # Update properties regardless
        local_model.name = server_model.name
        local_model.type = server_model.ai_model_type_code
        local_model.version = server_model.version
        updated_models.append(local_model)

    def _handle_new_model(self, server_model, new_models):
        """Handle model that doesn't exist locally."""
        # Check if already downloading this model
        if self._is_downloading(server_model.id):
            logging.info(f"⏳ Model {server_model.name} is already being downloaded. Skipping...")
            return

        new_model = AIModelEntity(
            id=server_model.id, 
            name=server_model.name, 
            type=server_model.ai_model_type_code,
            file=os.path.basename(server_model.file_path), 
            version=server_model.version
        )
        new_models.append(new_model)
        
        logging.info(f"⬇️ New model detected: {server_model.name}. Scheduling download...")
        self._schedule_model_download(server_model)

    def _schedule_model_download(self, model):
        """Schedule a model download in background thread."""
        # Cancel any existing download for this model
        self._cancel_download(model.id)
        
        # Create new download info
        download_info = DownloadInfo(
            model_id=model.id,
            model_name=model.name,
            version=model.version
        )
        download_info.state = DownloadState.PENDING
        download_info.start_time = time.time()
        
        # Update database status
        self._update_model_download_status(model.id, "pending", None)
        
        # Start download in background thread
        download_info.thread = threading.Thread(
            target=self._download_model_worker,
            args=(model, download_info),
            daemon=True,
            name=f"ModelDownload-{model.id}"
        )
        download_info.thread.start()
        
        self._set_download_info(model.id, download_info)

    def _download_model_worker(self, model, download_info):
        """Background worker for downloading a model."""
        try:
            download_info.state = DownloadState.DOWNLOADING
            self._update_model_download_status(model.id, "downloading", None)
            logging.info(f"📥 Starting download for AI model '{model.name}'...")
            
            if self.download_model(model, download_info):
                download_info.state = DownloadState.COMPLETED
                download_info.end_time = time.time()
                duration = download_info.end_time - download_info.start_time
                self._update_model_download_status(model.id, "completed", None)
                logging.info(f"✅ AI Model '{model.name}' downloaded successfully in {duration:.2f}s")
            else:
                download_info.state = DownloadState.FAILED
                download_info.error_message = "Download failed"
                self._update_model_download_status(model.id, "failed", "Download failed")
                logging.error(f"❌ Failed to download AI Model '{model.name}'")
                
        except Exception as e:
            download_info.state = DownloadState.FAILED
            download_info.error_message = str(e)
            self._update_model_download_status(model.id, "failed", str(e))
            logging.error(f"❌ Error downloading AI Model '{model.name}': {e}")
        finally:
            # Clean up download info after a delay to allow status checking
            threading.Timer(300, lambda: self._remove_download_info(model.id)).start()

    def _save_changes(self, new_models, updated_models, models_to_delete):
        """Save all changes to database in a single transaction."""
        try:
            if new_models:
                self.repository.session.bulk_save_objects(new_models)

            if updated_models:
                self.repository.session.bulk_save_objects(updated_models)
                
            for model in models_to_delete:
                logging.info(f"🗑️ Model removed from server: {model.name}. Deleting local copy...")
                # Cancel any ongoing download
                self._cancel_download(model.id)
                self.repository.session.delete(model)
                self.delete_local_model(model.file)
                
            self.repository.session.commit()
        except Exception as e:
            self.repository.session.rollback()
            logging.error(f"Error saving model changes: {e}")
            raise

    def download_model(self, model, download_info=None) -> bool:
        """Download the AI model and save it to the models directory."""
        if not self.stub:
            logging.error("gRPC connection is not established.")
            return False
        
        try:
            request = DownloadAIModelRequest(ai_model_id=model.id, token=self.token)
            file_path = self._get_model_path(model.file_path)
            
            # Check if download was cancelled
            if download_info and download_info.stop_event.is_set():
                logging.info(f"🛑 Download cancelled for model '{model.name}'")
                return False
            
            with open(file_path, "wb") as f:
                for chunk in self.stub.DownloadAIModel(request):
                    # Check if download was cancelled during streaming
                    if download_info and download_info.stop_event.is_set():
                        logging.info(f"🛑 Download cancelled during streaming for model '{model.name}'")
                        return False
                    f.write(chunk.file_chunk)
            
            return True
        
        except Exception as e:
            logging.error(f"❌ Error downloading AI Model '{model.name}': {e}")
            return False
    
    def delete_local_model(self, file: str) -> None:
        """Delete a local AI model file."""
        file_path = self._get_model_path(file)
        try:
            if file_path.exists():
                file_path.unlink()
                logging.info(f"🗑️ Model file deleted: {file}")
        except Exception as e:
            logging.error(f"❌ Error deleting model file: {e}")

    def get_download_status(self, model_id: str) -> Optional[Dict]:
        """Get the download status for a specific model."""
        download_info = self._get_download_info(model_id)
        if not download_info:
            return None
            
        return {
            "model_id": download_info.model_id,
            "model_name": download_info.model_name,
            "version": download_info.version,
            "state": download_info.state.value,
            "start_time": download_info.start_time,
            "end_time": download_info.end_time,
            "error_message": download_info.error_message
        }

    def get_all_download_status(self) -> Dict[str, Dict]:
        """Get download status for all models."""
        with self.download_lock:
            return {
                model_id: self.get_download_status(model_id)
                for model_id in self.download_tracker.keys()
            }