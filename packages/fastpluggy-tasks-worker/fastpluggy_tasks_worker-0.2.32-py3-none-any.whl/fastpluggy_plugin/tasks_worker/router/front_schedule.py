import json
import logging
from typing import Annotated

from fastapi import Request, Depends, APIRouter, Query
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from fastpluggy.core.database import get_db
from fastpluggy.core.dependency import get_view_builder
from fastpluggy.core.flash import FlashMessage
from fastpluggy.core.menu.decorator import menu_entry
from fastpluggy.core.tools.fastapi import redirect_to_previous
from fastpluggy.core.widgets.render_field_tools import RenderFieldTools
from fastpluggy.core.view_builer.components.table_model import TableModelView
from fastpluggy.core.widgets import AutoLinkWidget, CustomTemplateWidget
from fastpluggy.core.widgets.categories.input.button_list import ButtonListWidget
from fastpluggy_plugin.crud_tools.crud_link_helper import CrudLinkHelper
from fastpluggy_plugin.crud_tools.schema import CrudAction
from ..config import TasksRunnerSettings
from ..models.scheduled import ScheduledTaskDB
from ..repository.schedule_monitoring import MonitorData, _build_filter_info, \
    _fetch_reports_by_task, _fetch_scheduled_tasks, FilterCriteria
from ..schema.request_input import CreateScheduledTaskRequest
from ..widgets.task_form import TaskFormView

front_schedule_task_router = APIRouter(
    prefix='/scheduled_task',
    tags=["task_router"],
)


@front_schedule_task_router.get("/", name="list_scheduled_tasks")
def list_scheduled_tasks(request: Request,
                         view_builder=Depends(get_view_builder)):
    buttons = []
    settings = TasksRunnerSettings()
    if settings.allow_create_schedule_task:
        buttons.append(AutoLinkWidget(label="Create a Scheduled Task", route_name='create_scheduled_task', ))
        buttons.append(AutoLinkWidget(label='Scheduled Task Monitoring', route_name='scheduled_task_monitoring', ))
    items = [
        ButtonListWidget(
            buttons=buttons
        ),
        TableModelView(
            model=ScheduledTaskDB,
            title="Task scheduled",
            fields=[
                ScheduledTaskDB.name, ScheduledTaskDB.cron, ScheduledTaskDB.interval,
                #  ScheduledTaskDB.last_status,
                ScheduledTaskDB.is_late, ScheduledTaskDB.next_run, ScheduledTaskDB.last_attempt,
                ScheduledTaskDB.last_task_id, ScheduledTaskDB.enabled],
            links=[
                AutoLinkWidget(
                    label="View Last Task",
                    route_name="task_details",  # from your existing router
                    param_inputs={"task_id": '<last_task_id>'},
                    condition=lambda row: row['last_task_id'] is not None
                ),
                # TODO : add a retry button
                CrudLinkHelper.get_crud_link(model=ScheduledTaskDB, action=CrudAction.EDIT),
            ],
            field_callbacks={
                ScheduledTaskDB.enabled: RenderFieldTools.render_boolean,
                ScheduledTaskDB.last_attempt: RenderFieldTools.render_datetime,
                ScheduledTaskDB.next_run: RenderFieldTools.render_datetime,
                ScheduledTaskDB.last_task_id: lambda
                    v: f'<a href="{request.url_for("task_details", task_id=v)}">{v}</a>',
                ScheduledTaskDB.is_late: lambda
                    v: '<span class="badge bg-red">Yes</span>' if v else '<span class="badge bg-green">No</span>',

            },
            exclude_fields=[
                ScheduledTaskDB.created_at,
                ScheduledTaskDB.updated_at,
                ScheduledTaskDB.kwargs,
                ScheduledTaskDB.notify_on,
                ScheduledTaskDB.function,
            ]
        )
    ]

    return view_builder.generate(
        request,
        title="List of scheduled tasks",
        items=items
    )

@menu_entry(label="Schedule Monitoring", icon='ti ti-activity')
@front_schedule_task_router.get("/monitoring", name="scheduled_task_monitoring")
def scheduled_task_monitoring(
        request: Request,
        filter_criteria: Annotated[FilterCriteria, Query()],
        db: Session = Depends(get_db),
        view_builder=Depends(get_view_builder),
):
    """
    Renders the "Cron Task Status Monitor" page with time-based filtering and pagination.

    Query Parameters:
        task_name: Partial task name search (case-insensitive)
        start_time: "2025-06-01T00:00:00Z" or "1h" (1 hour ago) or "7d" (7 days ago)
        end_time: "2025-06-06T23:59:59Z" or "now"
        max_reports_per_task: 1-200 (default: 10)
        page: Current page number (default: 1)
        page_size: Number of tasks per page (default: 10)

    Examples:
        /monitoring?task_name=backup&start_time=7d&end_time=now
        /monitoring?start_time=2025-06-01T00:00:00Z
        /monitoring?task_name=email&start_time=1d&page=2
    """
    try:
        # Validate and limit parameters from FilterCriteria
        # Apply additional validation constraints beyond Pydantic validation
        filter_criteria.max_reports_per_task = min(max(1, filter_criteria.max_reports_per_task), 50)
        filter_criteria.page = max(1, filter_criteria.page)
        filter_criteria.page_size = min(max(1, filter_criteria.page_size), 20)

        # 1) Fetch all scheduled tasks based on criteria (for counting)
        all_scheduled_tasks = _fetch_scheduled_tasks(db, filter_criteria)

        # Calculate pagination
        total_tasks = len(all_scheduled_tasks)
        total_pages = (total_tasks + filter_criteria.page_size - 1) // filter_criteria.page_size

        # Apply pagination to tasks
        start_idx = (filter_criteria.page - 1) * filter_criteria.page_size
        end_idx = start_idx + filter_criteria.page_size
        paginated_tasks = all_scheduled_tasks[start_idx:end_idx]

        if not paginated_tasks:
            # Handle empty state gracefully
            monitor_data = MonitorData.create(scheduled_tasks=[], reports_by_task={}, filter_criteria=filter_criteria)
        else:
            # 2) Fetch reports with time filtering only for paginated tasks
            reports_by_task = _fetch_reports_by_task(
                db, paginated_tasks, filter_criteria.max_reports_per_task, filter_criteria
            )

            # 4) Create monitor data using simplified constructor
            monitor_data = MonitorData.create(
                scheduled_tasks=paginated_tasks,
                reports_by_task=reports_by_task,
                filter_criteria=filter_criteria
            )

        # Prepare template context with filter info
        filter_info = _build_filter_info(filter_criteria, total_tasks)

        # Add pagination info
        pagination_info = {
            "current_page": filter_criteria.page,
            "total_pages": total_pages,
            "page_size": filter_criteria.page_size,
            "total_items": total_tasks,
            "has_previous": filter_criteria.page > 1,
            "has_next": filter_criteria.page < total_pages,
            "previous_page": filter_criteria.page - 1 if filter_criteria.page > 1 else None,
            "next_page": filter_criteria.page + 1 if filter_criteria.page < total_pages else None,
        }

        return view_builder.generate(
            request,
            widgets=[CustomTemplateWidget(
                template_name="tasks_worker/scheduled_monitor.html.j2",
                context={
                    "request": request,
                    "monitor_data": monitor_data,
                    "filter_info": filter_info,
                    "pagination": pagination_info,
                    "url_retry_task": str(request.url_for("retry_task", task_id="TASK_ID_REPLACE")),
                    "url_task_details": str(request.url_for("task_details", task_id="TASK_ID_REPLACE")),
                    "current_params": filter_criteria,
                },
            )],
            title=f'Scheduled Task Monitoring{" - Filtered" if filter_criteria.has_active_filters() else ""}',
        )

    except Exception as e:
        # Log the error and return a graceful error page
        logging.error(f"Error in scheduled_task_monitoring: {e}", exc_info=True)

        # Use existing filter_criteria or create a default one if it doesn't exist
        if 'filter_criteria' not in locals():
            filter_criteria = FilterCriteria()

        # Return minimal error state
        empty_monitor_data = MonitorData.create(scheduled_tasks=[], reports_by_task={}, filter_criteria=filter_criteria)

        return view_builder.generate(
            request,
            widgets=[CustomTemplateWidget(
                template_name="tasks_worker/scheduled_monitor.html.j2",
                context={
                    "request": request,
                    "monitor_data": empty_monitor_data,
                    "error_message": f"Unable to load monitoring data: {str(e)}",
                    "pagination": {
                        "current_page": 1,
                        "total_pages": 1,
                        "page_size": filter_criteria.page_size,
                        "total_items": 0,
                        "has_previous": False,
                        "has_next": False,
                        "previous_page": None,
                        "next_page": None,
                    },
                },
            )],
            title='Scheduled Task Monitoring - Error',
        )


@front_schedule_task_router.get("/create", name="create_scheduled_task")
def create_scheduled_task(
        request: Request,
        view_builder=Depends(get_view_builder)
):
    view = TaskFormView(
        title="New Scheduled Task",
        submit_url=str(request.url_for("create_scheduled_task_post")),
        url_after_submit=str(request.url_for("list_scheduled_tasks")),
        mode="schedule_task",
    )
    return view_builder.generate(request, widgets=[view])


@front_schedule_task_router.post("/create", name="create_scheduled_task_post")
def create_scheduled_task_post(
        request: Request,
        payload: CreateScheduledTaskRequest,
        method: str = 'web',
        db: Session = Depends(get_db)
):
    task = ScheduledTaskDB(
        name=payload.name,
        function=payload.function,
        cron=payload.cron,
        interval=payload.interval,
        kwargs=json.dumps(payload.kwargs),
        notify_on=json.dumps(payload.notify_on),
        enabled=True,
    )
    db.add(task)
    db.commit()
    mesg = FlashMessage.add(request=request, message=f"Scheduled Task {payload.name} created !")

    if method == "web":
        return redirect_to_previous(request)
    else:
        return JSONResponse(content=mesg.to_dict())
