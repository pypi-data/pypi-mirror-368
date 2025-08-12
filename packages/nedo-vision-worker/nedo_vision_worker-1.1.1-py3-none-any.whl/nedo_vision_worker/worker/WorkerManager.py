import logging
from ..services.WorkerStatusClient import WorkerStatusClient
from ..services.GrpcClientManager import GrpcClientManager
from ..services.GrpcClientBase import GrpcClientBase
from .PipelineActionWorker import PipelineActionWorker
from .DataSyncWorker import DataSyncWorker
from .DataSenderWorker import DataSenderWorker
from .PipelineImageWorker import PipelineImageWorker
from .VideoStreamWorker import VideoStreamWorker
from .CoreActionWorker import CoreActionWorker
from .DatasetFrameWorker import DatasetFrameWorker

logger = logging.getLogger(__name__)

class WorkerManager:
    def __init__(self, config):
        """Initialize all worker threads with the given config."""
        self.config = config
        self.worker_id = self.config.get("worker_id")
        self.server_host = self.config.get("server_host")
        self.token = self.config.get("token")

        if not self.worker_id:
            raise ValueError("⚠️ [APP] Configuration is missing 'worker_id'.")
        if not self.server_host:
            raise ValueError("⚠️ [APP] Configuration is missing 'server_host'.")
        if not self.token:
            raise ValueError("⚠️ [APP] Configuration is missing 'token'.")

        # Configure the centralized gRPC client manager
        self.client_manager = GrpcClientManager.get_instance()
        self.client_manager.configure(self.server_host)
        
        # Get shared client instance
        self.status_client = self.client_manager.get_client(WorkerStatusClient)

        self.data_sync_worker = DataSyncWorker(config, sync_interval=10)
        self.data_sender_worker = DataSenderWorker(config, send_interval=10)
        self.video_stream_worker = VideoStreamWorker(config)
        self.pipeline_image_worker = PipelineImageWorker(config)
        self.pipeline_action_worker = PipelineActionWorker(config)
        self.core_action_worker = CoreActionWorker(config, self._start_workers, self._stop_workers)
        self.dataset_frame_worker = DatasetFrameWorker(config)

    def _start_workers(self):
        """Start processing workers while keeping monitoring workers running."""
        try:
            self.video_stream_worker.start()
            logger.info("🚀 [APP] Video Stream Worker started.")

            self.pipeline_image_worker.start()
            logger.info("🚀 [APP] Pipeline Image Worker started.")

            self.data_sender_worker.start_updating()
            logger.info("🚀 [APP] Data Sender Worker started updating.")
            
            self.dataset_frame_worker.start()
            logger.info("🚀 [APP] Dataset Frame Worker started.")
            
            self._update_status("run")

        except Exception as e:
            logger.error("🚨 [APP] Failed to start processing workers.", exc_info=True)

    def _stop_workers(self):
        """Stop processing workers while keeping monitoring workers running."""
        try:
            self.video_stream_worker.stop()
            logger.info("🛑 [APP] Video Stream Worker stopped.")

            self.pipeline_image_worker.stop()
            logger.info("🛑 [APP] Pipeline Image Worker stopped.")

            self.data_sender_worker.stop_updating()
            logger.info("🛑 [APP] Data Sender Worker stopped updating.")

            self.dataset_frame_worker.stop()
            logger.info("🛑 [APP] Dataset Frame Worker stopped.")

            self._update_status("stop")

        except Exception as e:
            logger.error("🚨 [APP] Failed to stop processing workers.", exc_info=True)

    def start_all(self):
        """Start all workers including monitoring workers."""
        try:
            # Start monitoring workers first
            self.core_action_worker.start()
            logging.info("🚀 [APP] Core Action Worker started and listening for commands.")

            self.data_sync_worker.start()
            logger.info("🚀 [APP] Data Sync Worker started.")

            self.data_sender_worker.start()
            logger.info("🚀 [APP] Data Sender Worker started.")

            self.pipeline_action_worker.start()
            logger.info("🚀 [APP] Pipeline Action Worker started.")

            self._start_workers()

            logger.info("✅ [APP] All workers started successfully.")

        except Exception as e:
            logger.error("🚨 [APP] Failed to start all workers.", exc_info=True)

    def stop_all(self):
        """Stop all workers including monitoring workers."""
        try:
            self.core_action_worker.stop()
            logger.info("🛑 [APP] Core Action Worker stopped.")

            self.data_sync_worker.stop()
            logger.info("🛑 [APP] Data Sync Worker stopped.")

            self.data_sender_worker.stop()
            logger.info("🛑 [APP] Data Sender Worker stopped.")

            self.pipeline_action_worker.stop()
            logger.info("🛑 [APP] Pipeline Action Worker stopped.")

            self._stop_workers()

            logger.info("✅ [APP] All workers stopped successfully.")

        except Exception as e:
            logger.error("🚨 [APP] Failed to stop all workers.", exc_info=True)
        finally:
            # Cleanup: close gRPC clients when workers are stopped
            try:
                logger.info("🔌 [APP] Closing gRPC client connections...")
                self.client_manager.close_all_clients()
            except Exception as e:
                logger.warning(f"⚠️ [APP] Error closing gRPC clients: {e}")
    
    def _update_status(self, status_code):
        """
        Update the worker status via gRPC.
        
        Args:
            status_code (str): Status code to report to the server
        """
        try:
            logger.info(f"📡 [APP] Updating worker status to {status_code}")
            result = self.status_client.update_worker_status(self.worker_id, status_code, self.token)
            
            if result["success"]:
                logger.info(f"✅ [APP] Status update successful: {result['message']}")
            else:
                error_message = GrpcClientBase.get_error_message(result)
                logger.warning(f"⚠️ [APP] Status update failed: {error_message}")
                
        except Exception as e:
            logger.error(f"🚨 [APP] Error updating worker status: {str(e)}")
