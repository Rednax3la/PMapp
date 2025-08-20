# scheduling-api/createandget.py
from datetime import datetime, timedelta
from collections import defaultdict
from helpers import format_duration
import pytz
import shortuuid
from db import projects_col, tasks_col, updates_col, project_updates_col, db

# Short UUID generator (keeps IDs short and string-based)
uuid = shortuuid.ShortUUID()

def generate_unique_id(length: int = 8) -> str:
    """Generate a short unique string id."""
    return uuid.random(length=length)

def _now():
    return datetime.now(pytz.UTC)

# ------------------------
# Project functions
# ------------------------
def create_project(name: str, start_date: datetime, company_name: str, timezone: str = "Africa/Addis_Ababa",
                   project_type: str = "scheduled", objectives: list = None):
    """
    Create a project document in projects_col. Returns the created project dict or None if duplicate.
    """
    # Ensure start_date is timezone-aware
    if start_date and start_date.tzinfo is None:
        start_date = pytz.UTC.localize(start_date)

    proj_id = generate_unique_id()
    doc = {
        "id": proj_id,
        "name": name,
        "start_date": start_date,
        "timezone": timezone,
        "project_type": project_type,
        "objectives": objectives or [],
        "expected_duration": None,
        "duration": 0,
        "total_estimated_cost": 0,
        "state": "tentative",
        "team": [],
        "company_name": company_name,
        "tasks": [],
        "created_at": _now(),
        "updated_at": _now()
    }
    try:
        projects_col.insert_one(doc)
        return doc
    except Exception as e:
        # Duplicate key or other insertion error
        return None

def get_project(project_id: str):
    """Return project dict or None."""
    return projects_col.find_one({"id": project_id})

def get_project_by_name(project_name: str):
    """Case-insensitive name match for a project."""
    return projects_col.find_one({"name": {"$regex": f"^{project_name}$", "$options": "i"}})

def get_project_by_company_and_name(company_name: str, project_name: str):
    return projects_col.find_one({
        "company_name": {"$regex": f"^{company_name}$", "$options": "i"},
        "name": {"$regex": f"^{project_name}$", "$options": "i"}
    })

# ------------------------
# Task functions
# ------------------------
def create_task(project_id: str, name: str, start_time: datetime = None, expected_duration: int = 0,
                priority: str = "medium", members: list = None, description: str = None,
                dependencies: list = None, estimated_cost: float = 0.0):
    """Create a task attached to a project. Returns the created task dict or None."""
    project = get_project(project_id)
    if not project:
        return None

    # Validate uniqueness of task name within project
    existing = tasks_col.find_one({"project_id": project_id, "name": {"$regex": f"^{name}$", "$options": "i"}})
    if existing:
        return None

    # Convert start_time to timezone-aware
    if start_time and start_time.tzinfo is None:
        start_time = pytz.UTC.localize(start_time)

    # Determine default start_time from dependencies or project start_date
    project_start = project.get("start_date") or _now()
    if project_start.tzinfo is None:
        project_start = pytz.UTC.localize(project_start)

    default_start = None
    valid_dependencies = []
    if dependencies:
        for dep in dependencies:
            dep_task = tasks_col.find_one({"id": dep})
            if dep_task:
                valid_dependencies.append(dep)
                dep_end = dep_task.get("start_time", project_start) + timedelta(minutes=dep_task.get("expected_duration", 0))
                default_start = max(default_start, dep_end) if default_start else dep_end

    if not start_time:
        start_time = max(default_start, project_start) if default_start else project_start
    else:
        if start_time < project_start:
            raise ValueError("Task start_time cannot be before project start_date")

    task_id = generate_unique_id()
    task_doc = {
        "id": task_id,
        "project_id": project_id,
        "name": name,
        "start_time": start_time,
        "expected_duration": expected_duration,
        "duration": 0,
        "priority": priority,
        "members": members or [],
        "description": description,
        "updates": [],            # list of update ids
        "estimated_cost": estimated_cost,
        "dependencies": valid_dependencies or [],
        "postponed": False,
        "latest_status": 0,
        "created_at": _now(),
        "updated_at": _now()
    }
    tasks_col.insert_one(task_doc)

    # Add reference to project.tasks
    projects_col.update_one({"id": project_id}, {"$push": {"tasks": task_id}, "$set": {"updated_at": _now()}})
    return task_doc

def get_task(task_id: str):
    return tasks_col.find_one({"id": task_id})

def get_task_by_name(project_id: str, task_name: str):
    return tasks_col.find_one({"project_id": project_id, "name": {"$regex": f"^{task_name}$", "$options": "i"}})

def get_project_tasks(project_id: str):
    """Return list of tasks belonging to a project, ordered by start_time ascending."""
    cursor = tasks_col.find({"project_id": project_id}).sort("start_time", 1)
    return list(cursor)

def get_latest_progress(task_id: str):
    """Return the most recent status_percentage for a task (0-100)."""
    upd = updates_col.find({"task_id": task_id}).sort("timestamp", -1).limit(1)
    up = list(upd)
    if not up:
        return 0
    return up[0].get("status_percentage", 0)

# ------------------------
# Update functions
# ------------------------
def create_task_update(task_id: str, status_percentage: int, description: str = None, image_filenames: list = None):
    """
    Create an update for a task. Maintains task.latest_status and task.duration if completed.
    Returns the new update id or None on error.
    """
    task = get_task(task_id)
    if not task:
        return None

    update_id = generate_unique_id()
    update_doc = {
        "id": update_id,
        "task_id": task_id,
        "status_percentage": int(status_percentage),
        "description": description,
        "image_filenames": image_filenames or [],
        "timestamp": _now()
    }
    updates_col.insert_one(update_doc)

    # Append update id to task.updates and set latest_status
    tasks_col.update_one({"id": task_id}, {"$push": {"updates": update_id}, "$set": {"latest_status": int(status_percentage), "updated_at": _now()}})

    if int(status_percentage) == 100:
        now = _now()
        task_doc = get_task(task_id)
        start_time = task_doc.get("start_time", now)
        actual_mins = int((now - start_time).total_seconds() // 60)
        tasks_col.update_one({"id": task_id}, {"$set": {"duration": actual_mins}})

        # If all project tasks are now complete, update project.duration
        project_id = task_doc.get("project_id")
        if project_id:
            # count incomplete tasks
            incomplete = tasks_col.count_documents({"project_id": project_id, "latest_status": {"$lt": 100}})
            if incomplete == 0:
                # sum durations
                pipeline = [
                    {"$match": {"project_id": project_id}},
                    {"$group": {"_id": None, "total": {"$sum": "$duration"}}}
                ]
                agg = list(tasks_col.aggregate(pipeline))
                total = agg[0]["total"] if agg else 0
                projects_col.update_one({"id": project_id}, {"$set": {"duration": total, "updated_at": _now()}})

    return update_id

def create_project_update(project_id: str, description: str):
    puid = generate_unique_id()
    doc = {
        "id": puid,
        "project_id": project_id,
        "description": description,
        "timestamp": _now()
    }
    project_updates_col.insert_one(doc)
    return puid

# ------------------------
# Batch task creation (improved error reporting)
# ------------------------
def create_tasks_batch(task_list: list, transactional: bool = False):
    """
    task_list: list of dicts with keys required by create_task
    Returns list of {success:bool, id:str|None, error:str|None} in same order.
    If transactional=True, performs operation inside a MongoDB session/transaction
    (requires a replica set / Atlas).
    """
    results = []
    if transactional:
        with db.client.start_session() as sess:
            with sess.start_transaction():
                for item in task_list:
                    try:
                        required = ('project_id', 'name', 'expected_duration')
                        for r in required:
                            if r not in item:
                                raise ValueError(f"Missing required field: {r}")
                        task = create_task(
                            project_id=item['project_id'],
                            name=item['name'],
                            start_time=item.get('start_time'),
                            expected_duration=item.get('expected_duration', 0),
                            priority=item.get('priority', 'medium'),
                            members=item.get('members', []),
                            description=item.get('description'),
                            dependencies=item.get('dependencies', []),
                            estimated_cost=item.get('estimated_cost', 0.0)
                        )
                        if task:
                            results.append({"success": True, "id": task["id"], "error": None})
                        else:
                            results.append({"success": False, "id": None, "error": "Duplicate or invalid data"})
                    except Exception as e:
                        results.append({"success": False, "id": None, "error": str(e)})
    else:
        for item in task_list:
            try:
                required = ('project_id', 'name', 'expected_duration')
                for r in required:
                    if r not in item:
                        raise ValueError(f"Missing required field: {r}")
                task = create_task(
                    project_id=item['project_id'],
                    name=item['name'],
                    start_time=item.get('start_time'),
                    expected_duration=item.get('expected_duration', 0),
                    priority=item.get('priority', 'medium'),
                    members=item.get('members', []),
                    description=item.get('description'),
                    dependencies=item.get('dependencies', []),
                    estimated_cost=item.get('estimated_cost', 0.0)
                )
                if task:
                    results.append({"success": True, "id": task["id"], "error": None})
                else:
                    results.append({"success": False, "id": None, "error": "Duplicate or invalid data"})
            except Exception as e:
                results.append({"success": False, "id": None, "error": str(e)})
    return results

# ------------------------
# Task & Project state helpers
# ------------------------
def get_task_state(task_id: str, at_time: datetime = None):
    """
    Determine state of a task: 'postponed','delayed','tentative','incipient','in progress','overdue','complete'
    Mirrors previous logic but queries DB.
    """
    if not at_time:
        at_time = _now()

    task = get_task(task_id)
    if not task:
        return None

    task_start = task.get("start_time") or _now()
    if task_start.tzinfo is None:
        task_start = pytz.UTC.localize(task_start)

    planned_end = task_start + timedelta(minutes=task.get("expected_duration", 0))

    if task.get("postponed", False):
        return "postponed"

    # Dependencies
    deps = task.get("dependencies", []) or []
    for dep_id in deps:
        dep_state = get_task_state(dep_id, at_time)
        if dep_state in ["delayed", "overdue"]:
            return "delayed"
        if dep_state != "complete":
            return "tentative"

    progress = get_latest_progress(task_id)
    if progress == 100:
        return "complete"

    if at_time < task_start:
        return "tentative"

    if at_time > planned_end:
        return "overdue"

    if progress == 0:
        if at_time > planned_end:
            return "overdue"
        return "incipient"

    return "in progress"

# ------------------------
# Convenience queries
# ------------------------
def fetch_priority(project_name: str, priority: str):
    project = get_project_by_name(project_name)
    if not project:
        return []
    return list(tasks_col.find({"project_id": project["id"], "priority": {"$regex": f"^{priority}$", "$options": "i"}}))

def get_member_tasks(project_name: str, member: str):
    project = get_project_by_name(project_name)
    if not project:
        return []
    return list(tasks_col.find({"project_id": project["id"], "members": member}))
