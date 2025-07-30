# scheduling-api/createandget.py
from datetime import datetime, timedelta
from collections import defaultdict
from helpers import format_duration
import pytz
import shortuuid

# Data storage 
projects_db = {}
tasks_db = {}
updates_db = {}
companies_db = {}
project_updates_db = {}

# State tracking variables
task_states = {}
task_dependencies = defaultdict(list)

# Auto-increment counters
update_counter = 1
company_counter = 1
project_update_counter = 1

def generate_unique_id():
    return shortuuid.ShortUUID().random(length=10)

def create_project(name: str, start_date: datetime, company_name: str, timezone: str = "Africa/Addis_Ababa", project_type: str = "scheduled",objectives: list = None):
    # Check name uniqueness
    for project in projects_db.values():
        if project['name'].lower() == name.lower():
            return None
    
    # Check uniqueness within company
    for project in projects_db.values():
        if project['company_name'].lower() == company_name.lower() and \
           project['name'].lower() == name.lower():
            return None
    
    # Create company if not exists (and ensure unique company names)
    company_id = None
    for cid, cdata in companies_db.items():
        if cdata['name'].lower() == company_name.lower():
            company_id = cid
            break
            
    if not company_id:
        global company_counter
        company_id = company_counter
        companies_db[company_id] = {
            'id': company_id,
            'name': company_name
        }
        company_counter += 1
    
    project_id = generate_unique_id()
    while project_id in projects_db:
        project_id = generate_unique_id()

    # Create project
    projects_db[project_id] = {
        'id': project_id,
        'name': name,
        'start_date': start_date,
        'timezone': timezone,
        'project_type': project_type,
        'objectives': objectives or [],
        'expected_duration': None,
        'duration': 0,
        'total_estimated_cost': 0,
        'state': 'tentative',  # Initial state
        'team': [],
        'company_id': company_id,  # Link to company
        "company_name": company_name,
        'tasks': []
    }
    project = projects_db[project_id]
    return project  # Return full project object

def create_task(project_id: int, name: str, start_time: datetime, expected_duration: int, 
               priority: str = "medium", members: list = None, description: str = None,
               dependencies: list = None, estimated_cost: float = 0.0):
    # Retrieve and validate project
    project = projects_db.get(project_id)
    if not project:
        return None

    # Ensure project start_date is available
    project_start = project['start_date']
    if not project_start:
        project_start = datetime.now(pytz.UTC)

    # Check name uniqueness in project
    for task_id in project['tasks']:
        task = tasks_db.get(task_id)
        if task and task['name'].lower() == name.lower():
            return None

    # Validate dependencies
    valid_dependencies = []
    if dependencies:
        for dep_id in dependencies:
            if dep_id in tasks_db and tasks_db[dep_id]['project_id'] == project_id:
                valid_dependencies.append(dep_id)

    # Calculate the latest-dependency end, if any
    default_start = None
    if valid_dependencies:
        for dep_id in valid_dependencies:
            dep_task = tasks_db.get(dep_id)
            if dep_task:
                dep_end = dep_task['start_time'] + timedelta(minutes=dep_task['expected_duration'])
                default_start = max(default_start, dep_end) if default_start else dep_end

    # Determine actual task start
    if not start_time:
        # No explicit start: use dependency end if later than project start, else project start
        start_time = max(default_start, project_start) if default_start else project_start
    else:
        # Explicit start: ensure not before project start
        if start_time.tzinfo is None:
            start_time = pytz.UTC.localize(start_time)
        if start_time < project_start:
            raise ValueError(
                f"Task start_time ({start_time.isoformat()}) cannot be before project start_date ({project_start.isoformat()})"
            )

    # Create unique task_id
    task_id = generate_unique_id()
    while task_id in tasks_db:
        task_id = generate_unique_id()

    # Store task
    tasks_db[task_id] = {
        'id': task_id,
        'project_id': project_id,
        'name': name,
        'start_time': start_time,
        'expected_duration': expected_duration,
        'duration': 0,
        'priority': priority,
        'members': members or [],
        'description': description,
        'updates': [],
        'estimated_cost': estimated_cost,
        'dependencies': valid_dependencies,
        'rescheduled': False
    }

    # Initialize state and dependency pointers
    task_states[task_id] = "tentative"
    for dep_id in valid_dependencies:
        task_dependencies[dep_id].append(task_id)
    # Add formatted duration
    tasks_db[task_id]['duration_str'] = format_duration(tasks_db[task_id].get('duration', 0))    
    if 'tasks' not in project:
        project['tasks'] = []
    project['tasks'].append(task_id)

    return tasks_db[task_id]
def create_tasks_batch(task_list: list):
    created_ids = []
    for task_data in task_list:
        try:
            # Ensure all required fields are present
            required_fields = ['project_id', 'name', 'start_time', 'duration']
            if not all(field in task_data for field in required_fields):
                print(f"Missing required fields in task data: {task_data}")
                created_ids.append(None)
                continue
                
            task_id = create_task(
                project_id=task_data['project_id'],
                name=task_data['name'],
                start_time=task_data['start_time'],
                expected_duration=task_data['expected_duration'],
                priority=task_data.get('priority', "medium"),
                members=task_data.get('members', []),
                description=task_data.get('description'),
                estimated_cost=task_data.get('estimated_cost', 0.0)
            )
            created_ids.append(task_id)
        except Exception as e:
            print(f"Error creating task: {e}")
            created_ids.append(None)
    
    # Return only successfully created task IDs
    successful_ids = [tid for tid in created_ids if tid is not None]
    return successful_ids

def create_task_update(task_id: int, status_percentage: int, description: str = None, 
                     image_filename: str = None, image_filenames: list = None):
    global update_counter
    
    if task_id not in tasks_db:
        return None
    
    update_id = update_counter
    updates_db[update_id] = {
        'id': update_id,
        'task_id': task_id,
        'status_percentage': status_percentage,
        'description': description,
        'image_filename': image_filename,  # Backward compatible
        'image_filenames': image_filenames or [],  # New multi-image support
        'timestamp': datetime.now()
     }

    # If this update marks task complete, record actual duration
    task = tasks_db.get(task_id)
    if status_percentage == 100 and task:
        now = datetime.now(pytz.UTC)
        actual_mins = int((now - task['start_time']).total_seconds() // 60)
        task['duration'] = actual_mins

        task['updates'].append(update_id)
        updates_db[update_id]['task_id'] = task_id  # Ensure update links back

        # If all tasks in project are now complete, finalize project duration
        proj = projects_db.get(task['project_id'])
        if proj:
            all_done = all(
                updates_db[uid]['status_percentage'] == 100
                for tid in proj['tasks']
                for uid in tasks_db[tid]['updates']
            )
            if all_done:
                proj['duration'] = sum(tasks_db[tid]['duration'] for tid in proj['tasks'])
    return update_id

def create_project_update(project_id: str, description: str):
    global project_update_counter
    puid = project_update_counter
    project_updates_db[puid] = {
        'id': puid,
        'project_id': project_id,
        'description': description,
        'timestamp': datetime.now()
    }
    project_update_counter += 1
    return puid

def get_project(project_id: int):
    return projects_db.get(project_id)

def get_task(task_id: int):
    return tasks_db.get(task_id)

def get_project_tasks(project_id: int):
    project = get_project(project_id)
    if not project:
        return []
    return [tasks_db[task_id] for task_id in project['tasks']]

def get_latest_progress(task_id: int):
    task = get_task(task_id)
    if not task or not task['updates']:
        return 0
    last_update_id = task['updates'][-1]
    return updates_db[last_update_id]['status_percentage']

def get_project_by_name(project_name: str):
    for project in projects_db.values():
        if project['name'].lower() == project_name.lower():
            return project
    return None

def get_task_by_name(project_id: int, task_name: str):
    project = get_project(project_id)
    if not project:
        return None
        
    for task_id in project['tasks']:
        task = tasks_db.get(task_id)
        if task and task['name'].lower() == task_name.lower():
            return task
    return None

def get_task_state(task_id: str, at_time: datetime = None):
    if not at_time:
        at_time = datetime.now(pytz.UTC)
    
    task = get_task(task_id)
    if not task:
        return None
    
    # Handle timezones
    task_start = task['start_time']
    if task_start.tzinfo is None:
        task_start = pytz.UTC.localize(task_start)
    
    planned_end = task_start + timedelta(minutes=task['expected_duration'])
    
    # Check if task is postponed
    if task.get('postponed', False):
        return "postponed"
    
    # Check dependencies
    if task['dependencies']:
        for dep_id in task['dependencies']:
            dep_state = get_task_state(dep_id, at_time)
            if dep_state in ["delayed", "overdue"]:
                return "delayed"
            if dep_state != "complete":
                return "tentative"
    
    # Get progress
    progress = get_latest_progress(task_id)
    
    # State determination - FIXED LOGIC
    if progress == 100:
        return "complete"
    
    if at_time < task_start:
        return "tentative"
    
    # Handle overdue state for incipient tasks
    if at_time > planned_end:
        return "overdue"
    
    if progress == 0:
        if at_time > planned_end:
            return "overdue"
        return "incipient"
    
    return "in progress"

def get_project_by_company_and_name(company_name: str, project_name: str):
    for project in projects_db.values():
        if project['company_name'].lower() == company_name.lower() and \
           project['name'].lower() == project_name.lower():
            return project
    return None

def fetch_priority(project_name, priority):
    project = get_project_by_name(project_name)
    if not project:
        return []
    tasks = get_project_tasks(project['id'])
    return [t for t in tasks if t['priority'].lower() == priority.lower()]

def get_member_tasks(project_name: str, member: str):
    project = get_project_by_name(project_name)
    if not project:
        return []
    tasks = get_project_tasks(project['id'])
    return [task for task in tasks if member in task['members']]