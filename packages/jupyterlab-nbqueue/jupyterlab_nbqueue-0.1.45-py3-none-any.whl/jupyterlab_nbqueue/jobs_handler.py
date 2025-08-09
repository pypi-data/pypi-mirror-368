import json
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jupyter_server.base.handlers import APIHandler
from jupyterlab_nbqueue.models import Job, Base
import tornado


class JobsHandler(APIHandler):
    engine = create_engine(f"sqlite:///.nbqueue_jobs.db", echo=False, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    @tornado.web.authenticated
    def delete(self):
        session = self.SessionLocal()
        try:
            num_deleted = session.query(Job).delete()
            session.commit()
            self.write(json.dumps({"success": True, "deleted": num_deleted}))
        except Exception as exc:
            session.rollback()
            self.set_status(500)
            self.finish(json.dumps({"error": str(exc)}))
        finally:
            session.close()

    @tornado.web.authenticated
    def get(self):
        session = self.SessionLocal()
        try:
            # Consulta todos los jobs ordenados por fecha de creación descendente
            jobs = session.query(Job).order_by(Job.created_at.desc()).all()
            job_list = []
            for job in jobs:
                job_list.append({
                    "job_id": job.job_id,
                    "status": job.status,
                    "start_time": job.created_at.isoformat() if job.created_at else None,
                    "completion_time": None,  # Si tienes este dato en la respuesta, puedes extraerlo
                    "error_message": job.error_message
                })
            self.write(json.dumps(job_list))
        except Exception as exc:
            self.set_status(500)
            self.finish(json.dumps({"error": str(exc)}))
        finally:
            session.close()
