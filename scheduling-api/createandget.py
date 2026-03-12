# scheduling-api/createandget.py
from datetime import datetime, timedelta
import re
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
def create_project(name: str, start_date: datetime, company_name: str, timezone: str = "Africa/Nairobi",
                   project_type: str = "scheduled", objectives: list = None):
    """
    FIXED: Create a project document in projects_col with proper field handling.
    Returns the created project dict or None if duplicate.
    """
    # Check for duplicate project names within the company
    existing = projects_col.find_one({
        "company_name": {"$regex": f"^{company_name}$", "$options": "i"},
        "name": {"$regex": f"^{name}$", "$options": "i"}
    })
    
    if existing:
        return None  # Project name already exists
    
    # Ensure start_date is timezone-aware
    if start_date and start_date.tzinfo is None:
        tz = pytz.timezone(timezone)
        start_date = tz.localize(start_date)
    elif start_date:
        # Convert to project timezone if needed
        tz = pytz.timezone(timezone)
        start_date = start_date.astimezone(tz)

    proj_id = generate_unique_id()
    doc = {
        "id": proj_id,
        "name": name,
        "start_date": start_date,
        "timezone": timezone,
        "project_type": project_type,
        "objectives": objectives or [],
        "expected_duration": None,  # Will be calculated from tasks
        "duration": 0,  # Actual duration when complete
        "total_estimated_cost": 0,  # Will be calculated from tasks
        "state": "tentative",
        "team": [],  # FIXED: Initialize as empty list
        "company_name": company_name,
        "tasks": [],  # List of task IDs
        "role_allocations": {},  # Task ID -> list of role allocations
        "fund_allocations": [],  # List of fund allocations
        "dependencies": [],  # List of project IDs this project depends on
        "created_at": _now(),
        "updated_at": _now()
    }
    
    try:
        result = projects_col.insert_one(doc)
        # Return the document with the generated ID
        return doc
    except Exception as e:
        print(f"Error creating project: {e}")
        return None

def get_project(project_id: str):
    """Return project dict or None."""
    return projects_col.find_one({"id": project_id})

def get_project_by_name(project_name: str):
    if not project_name:
        return None
    safe = re.escape(project_name)
    return projects_col.find_one({"name": {"$regex": f"^{safe}$", "$options": "i"}})

def get_project_by_company_and_name(company_name: str, project_name: str):
    if not company_name or not project_name:
        return None
    safe_company = re.escape(company_name)
    safe_proj = re.escape(project_name)
    return projects_col.find_one({
        "company_name": {"$regex": f"^{safe_company}$", "$options": "i"},
        "name": {"$regex": f"^{safe_proj}$", "$options": "i"}
    })

def create_task(project_id: str, name: str, start_time: datetime = None, expected_duration: int = 0,
                priority: str = "medium", members: list = None, description: str = None,
                dependencies: list = None, estimated_cost: float = 0.0):
    """
    FIXED: Create a task attached to a project with proper validation and field handling.
    Returns the created task dict or None.
    """
    project = get_project(project_id)
    if not project:
        print(f"Project {project_id} not found")
        return None

    # Validate uniqueness of task name within project
    existing = tasks_col.find_one({
        "project_id": project_id, 
        "name": {"$regex": f"^{name}$", "$options": "i"}
    })
    if existing:
        print(f"Task {name} already exists in project {project_id}")
        return None

    # FIXED: Ensure expected_duration is positive
    if expected_duration <= 0:
        raise ValueError("expected_duration must be positive")

    # Convert start_time to timezone-aware
    project_timezone = project.get('timezone', 'Africa/Nairobi')
    tz = pytz.timezone(project_timezone)
    
    if start_time and start_time.tzinfo is None:
        start_time = tz.localize(start_time)
    elif start_time:
        start_time = start_time.astimezone(tz)

    # Determine default start_time from dependencies or project start_date
    project_start = project.get("start_date") or _now()
    if project_start.tzinfo is None:
        project_start = tz.localize(project_start)

    default_start = None
    valid_dependencies = []
    if dependencies:
        for dep in dependencies:
            dep_task = tasks_col.find_one({"id": dep})
            if dep_task:
                valid_dependencies.append(dep)
                dep_start = dep_task.get("start_time", project_start)
                if dep_start.tzinfo is None:
                    dep_start = tz.localize(dep_start)
                dep_end = dep_start + timedelta(minutes=dep_task.get("expected_duration", 0))
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
        "expected_duration": expected_duration,  # FIXED: Ensure this is set
        "duration": 0,  # Actual duration when complete
        "priority": priority,
        "members": members or [],
        "description": description,
        "updates": [],  # list of update ids
        "estimated_cost": estimated_cost,
        "dependencies": valid_dependencies or [],
        "postponed": False,
        "latest_status": 0,  # 0-100 progress percentage
        "created_at": _now(),
        "updated_at": _now()
    }
    
    try:
        result = tasks_col.insert_one(task_doc)
        
        # Add reference to project.tasks and update project totals
        projects_col.update_one(
            {"id": project_id}, 
            {
                "$push": {"tasks": task_id}, 
                "$set": {"updated_at": _now()},
                "$inc": {"total_estimated_cost": estimated_cost}
            }
        )
        
        # Update project expected_duration (sum of all task expected durations)
        _update_project_expected_duration(project_id)
        
        return task_doc
    except Exception as e:
        print(f"Error creating task: {e}")
        return None

def _update_project_expected_duration(project_id: str):
    """Helper function to update project's expected_duration based on task durations"""
    try:
        # Calculate total expected duration from all tasks
        pipeline = [
            {"$match": {"project_id": project_id}},
            {"$group": {"_id": None, "total_duration": {"$sum": "$expected_duration"}}}
        ]
        result = list(tasks_col.aggregate(pipeline))
        total_duration = result[0]["total_duration"] if result else 0
        
        projects_col.update_one(
            {"id": project_id},
            {"$set": {"expected_duration": total_duration, "updated_at": _now()}}
        )
    except Exception as e:
        print(f"Error updating project expected duration: {e}")

def get_task(task_id: str):
    return tasks_col.find_one({"id": task_id})

def get_task_by_name(project_id: str, task_name: str):
    return tasks_col.find_one({
        "project_id": project_id, 
        "name": {"$regex": f"^{task_name}$", "$options": "i"}
    })

def get_project_tasks(project_id: str):
    """Return list of tasks belonging to a project, ordered by start_time ascending."""
    cursor = tasks_col.find({"project_id": project_id}).sort("start_time", 1)
    return list(cursor)

def get_latest_progress(task_id: str):
    """Return the most recent status_percentage for a task (0-100)."""
    task = get_task(task_id)
    if not task:
        return 0
    return task.get("latest_status", 0)

# ------------------------
# Update functions
# ------------------------
def create_task_update(task_id: str, status_percentage: int, description: str = None, image_filenames: list = None):
    """
    FIXED: Create an update for a task. Maintains task.latest_status and task.duration if completed.
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
    
    try:
        result = updates_col.insert_one(update_doc)
        
        # Update task with new status and add update reference
        update_data = {
            "latest_status": int(status_percentage),
            "updated_at": _now()
        }
        
        tasks_col.update_one(
            {"id": task_id}, 
            {
                "$push": {"updates": update_id},
                "$set": update_data
            }
        )

        # If task is completed, calculate actual duration
        if int(status_percentage) == 100:
            now = _now()
            task_doc = get_task(task_id)
            start_time = task_doc.get("start_time", now)
            actual_mins = int((now - start_time).total_seconds() // 60)
            
            tasks_col.update_one(
                {"id": task_id}, 
                {"$set": {"duration": actual_mins}}
            )

            # If all project tasks are now complete, update project.duration
            project_id = task_doc.get("project_id")
            if project_id:
                # Count incomplete tasks
                incomplete_count = tasks_col.count_documents({
                    "project_id": project_id, 
                    "latest_status": {"$lt": 100}
                })
                
                if incomplete_count == 0:
                    # Sum actual durations
                    pipeline = [
                        {"$match": {"project_id": project_id}},
                        {"$group": {"_id": None, "total": {"$sum": "$duration"}}}
                    ]
                    agg_result = list(tasks_col.aggregate(pipeline))
                    total_duration = agg_result[0]["total"] if agg_result else 0
                    
                    projects_col.update_one(
                        {"id": project_id}, 
                        {"$set": {"duration": total_duration, "state": "complete", "updated_at": _now()}}
                    )

        return update_id
    except Exception as e:
        print(f"Error creating task update: {e}")
        return None

def create_project_update(project_id: str, description: str):
    """Create a project-level update/log entry"""
    puid = generate_unique_id()
    doc = {
        "id": puid,
        "project_id": project_id,
        "description": description,
        "timestamp": _now()
    }
    try:
        result = project_updates_col.insert_one(doc)
        return puid
    except Exception as e:
        print(f"Error creating project update: {e}")
        return None

# ------------------------
# Batch task creation (improved error reporting)
# ------------------------
def create_tasks_batch(task_list: list, transactional: bool = False):
    """
    FIXED: Batch task creation with better error handling and validation.
    task_list: list of dicts with keys required by create_task
    Returns list of created tasks or raises exception on failure.
    """
    if not task_list:
        return []
        
    created_tasks = []
    
    # Validate all tasks first
    for i, item in enumerate(task_list):
        required = ('project_id', 'name', 'expected_duration')
        for r in required:
            if r not in item:
                raise ValueError(f"Task {i}: Missing required field: {r}")
                
        if item['expected_duration'] <= 0:
            raise ValueError(f"Task {i}: expected_duration must be positive")
    
    if transactional and hasattr(db, 'client'):
        # Use transaction if available
        try:
            with db.client.start_session() as session:
                with session.start_transaction():
                    for item in task_list:
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
                        if not task:
                            raise ValueError(f"Failed to create task: {item['name']}")
                        created_tasks.append(task)
        except Exception as e:
            raise ValueError(f"Batch creation failed: {str(e)}")
    else:
        # Non-transactional batch creation
        for item in task_list:
            try:
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
                if not task:
                    raise ValueError(f"Failed to create task: {item['name']}")
                created_tasks.append(task)
            except Exception as e:
                # Rollback created tasks on failure
                for created_task in created_tasks:
                    try:
                        tasks_col.delete_one({"id": created_task['id']})
                        projects_col.update_one(
                            {"id": created_task['project_id']},
                            {"$pull": {"tasks": created_task['id']}}
                        )
                    except:
                        pass  # Best effort cleanup
                raise ValueError(f"Batch creation failed at task '{item['name']}': {str(e)}")
    
    return created_tasks

# ------------------------
# Task & Project state helpers
# ------------------------
def get_task_state(task_id: str, at_time: datetime = None):
    """
    FIXED: Determine state of a task with better logic.
    Returns: 'postponed','delayed','tentative','incipient','in progress','overdue','complete'
    """
    if not at_time:
        at_time = _now()

    task = get_task(task_id)
    if not task:
        return None

    task_start = task.get("start_time") or _now()
    if task_start.tzinfo is None:
        task_start = pytz.UTC.localize(task_start)

    expected_duration = task.get("expected_duration", 0)
    planned_end = task_start + timedelta(minutes=expected_duration)
    
    # Convert at_time to same timezone as task_start
    if at_time.tzinfo is None:
        at_time = pytz.UTC.localize(at_time)

    if task.get("postponed", False):
        return "postponed"

    # Check dependencies
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
        return "incipient"

    return "in progress"

# ------------------------
# Convenience queries
# ------------------------
def fetch_priority(project_name: str, priority: str):
    project = get_project_by_name(project_name)
    if not project:
        return []
    return list(tasks_col.find({
        "project_id": project["id"], 
        "priority": {"$regex": f"^{priority}$", "$options": "i"}
    }))

def get_member_tasks(project_name: str, member: str):
    project = get_project_by_name(project_name)
    if not project:
        return []
    return list(tasks_col.find({
        "project_id": project["id"], 
        "members": member
    }))