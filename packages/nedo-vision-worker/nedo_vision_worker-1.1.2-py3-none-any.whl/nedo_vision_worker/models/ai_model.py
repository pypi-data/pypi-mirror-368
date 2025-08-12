import uuid
from sqlalchemy import Column, String, DateTime
from datetime import datetime
from ..database.DatabaseManager import Base

class AIModelEntity(Base):
    __tablename__ = "ai_model"
    __bind_key__ = "default"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    file = Column(String, nullable=False)
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    download_status = Column(String, nullable=True, default="completed")  # pending, downloading, completed, failed
    last_download_attempt = Column(DateTime, nullable=True)
    download_error = Column(String, nullable=True)

    def __repr__(self):
        return (
            f"<AIModelEntity(id={self.id}, name={self.name}, type={self.type}, "
            f"file={self.file}, version={self.version})>"
        )

    def __str__(self):
        return (
            f"AIModelEntity(id={self.id}, name={self.name}, type={self.type}, "
            f"file={self.file}, version={self.version}, status={self.download_status})"
        )