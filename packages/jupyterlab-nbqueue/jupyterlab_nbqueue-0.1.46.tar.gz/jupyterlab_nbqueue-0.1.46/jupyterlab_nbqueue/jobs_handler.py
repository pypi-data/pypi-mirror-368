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
            # Import proto modules (evita error de import circular)
            try:
                from .proto import service_pb2, service_pb2_grpc
            except ImportError:
                service_pb2 = None
                service_pb2_grpc = None
            import grpc
            for job in jobs:
                # Consulta el estatus actual usando gRPC
                status = job.status
                error_message = job.error_message
                start_time = job.created_at.isoformat() if job.created_at else None
                completion_time = None
                if service_pb2 and service_pb2_grpc:
                    try:
                        with grpc.insecure_channel(os.environ.get("NBQUEUE_SERVER", "localhost:50051")) as channel:
                            stub = service_pb2_grpc.NBQueueServiceStub(channel)
                            namespace = "default"  # Si tienes el campo en la base de datos, úsalo aquí
                            request = service_pb2.JobStatusRequest(job_id=job.job_id, namespace=namespace)
                            response = stub.JobStatus(request)
                            status = getattr(response, "status", status)
                            error_message = getattr(response, "error_message", error_message)
                            start_time = getattr(response, "start_time", start_time)
                            completion_time = getattr(response, "completion_time", None)
                    except Exception as exc:
                        error_message = f"gRPC error: {exc}"
                job_list.append({
                    "job_id": job.job_id,
                    "status": status,
                    "start_time": start_time,
                    "completion_time": completion_time,
                    "error_message": error_message
                })
            self.write(json.dumps(job_list))
        except Exception as exc:
            self.set_status(500)
            self.finish(json.dumps({"error": str(exc)}))
        finally:
            session.close()
