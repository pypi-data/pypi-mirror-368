from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(128), index=True)
    notebook_file = Column(String(256))
    owner = Column(String(128))
    project = Column(String(128))
    nbqueue_job_name = Column(String(128))
    image = Column(String(256))
    conda_env = Column(String(256))
    output_path = Column(String(256))
    cpu = Column(String(32))
    ram = Column(String(32))
    uid = Column(String(32))
    gid = Column(String(32))
    request_json = Column(Text)
    response_json = Column(Text)
    status = Column(String(32))
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
