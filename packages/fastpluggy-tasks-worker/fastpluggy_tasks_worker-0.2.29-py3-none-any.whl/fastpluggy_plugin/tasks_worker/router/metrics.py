from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
import psutil
from typing import Optional, Dict, Annotated

from fastpluggy.core.database import get_db
from fastpluggy.core.dependency import get_view_builder

from ..models.report import TaskReportDB
from ..repository.schedule_monitoring import FilterCriteria

metrics_router = APIRouter()


def get_task_metrics(pid: int) -> Optional[Dict]:
    try:
        p = psutil.Process(pid)
        return {
            "pid": pid,
            "cpu_percent": p.cpu_percent(interval=0.1),  # small interval to get current usage
            "memory_info": {
                "rss": p.memory_info().rss,  # Resident Set Size
                "vms": p.memory_info().vms,  # Virtual Memory Size
            },
            "create_time": p.create_time(),
            "status": p.status(),
            "num_threads": p.num_threads(),
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None




@metrics_router.post("/api/task-reports")
async def get_task_reports(      request: Request,
        filter_criteria: Annotated[FilterCriteria, Query()],
        db: Session = Depends(get_db),
        view_builder=Depends(get_view_builder),):
    try:
        # Apply filters to your SQLAlchemy query
        query = db.query(TaskReportDB)

        if filter_criteria.task_name:
            query = query.filter(TaskReportDB.function.ilike(f"%{filter_criteria.task_name}%"))

        if filter_criteria.start_time:
            query = query.filter(TaskReportDB.start_time >= filter_criteria.start_time)

        if filter_criteria.end_time:
            query = query.filter(TaskReportDB.end_time <= filter_criteria.end_time)

        # Limit results per task
        # You might need custom logic here depending on your requirements

        results = query.all()

        # Return in expected format
        return [
            {
                "id": task.id,
                "function": task.function,
                "duration": task.duration,
                "status": task.status,
                "start_time": task.start_time.isoformat(),
                "end_time": task.end_time.isoformat() if task.end_time else None
            }
            for task in results
        ]

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@metrics_router.get("/tasks/{task_id}/metrics")
def get_task_resource_usage(task_id: str, db: Session = Depends(get_db)):
    task : TaskReportDB = db.query(TaskReportDB).filter(TaskReportDB.task_id == task_id).first()
    if not task or not task.thread_native_id:
        return {"error": "Task not found or PID missing"}

    metrics = get_task_metrics(int(task.thread_ident))
    return metrics or {"error": "Process not running or inaccessible"}
