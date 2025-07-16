from datetime import timedelta
from createandget import get_latest_progress, get_task_state
import pytz
from helpers import format_duration


def generate_timetable(project, tasks):
    # Get project timezone (default to Africa/Addis_Ababa if not specified)
    timezone_str = project.get('timezone', 'Africa/Addis_Ababa')
    timezone = pytz.timezone(timezone_str)
    
    # Make project start date timezone-aware if it isn't already
    project_start = project['start_date']
    if project_start.tzinfo is None:
        project_start = timezone.localize(project_start)
    
    # Ensure all task start_times are timezone-aware BEFORE sorting
    for t in tasks:
        if t['start_time'].tzinfo is None:
            t['start_time'] = timezone.localize(t['start_time'])

    sorted_tasks = sorted(tasks, key=lambda t: t['start_time'])
    timetable = []
    current_time = project_start

    for task in sorted_tasks:
        # task['start_time'] is now guaranteed to be timezone-aware
        task_start = task['start_time']
        start = max(task_start, current_time)
        end = start + timedelta(minutes=task['duration'])
        state = get_task_state(task['id'])

        timetable.append({
            "task": task['name'],
            "start": start.isoformat(),
            "end": end.isoformat(),
            "expected_duration": format_duration(task['expected_duration']),
            **({"duration": format_duration(task['duration'])}
                if get_latest_progress(task['id']) == 100 else {}),
            "members": task.get('members', []),
            "progress": get_latest_progress(task['id']),
            "state": state  # Add state
        })
        current_time = end

    return timetable

def generate_gantt_chart(tasks):
    chart = []
    for task in tasks:
        # Make task start time timezone-aware if it isn't already
        task_start = task['start_time']
        if task_start.tzinfo is None:
            # Default to Africa/Addis_Ababa if no timezone info available
            timezone = pytz.timezone('Africa/Addis_Ababa')
            task_start = timezone.localize(task_start)
        
        end_time = task_start + timedelta(minutes=task['duration'])
        state = get_task_state(task['id'])
        
        chart.append({
            "task": task['name'],
            "start": task_start.isoformat(),
            "end": end_time.isoformat(),
            "expected_duration": format_duration(task['expected_duration']),
            **({"duration": format_duration(task['duration'])}
                if get_latest_progress(task['id']) == 100 else {}),
            "priority": task['priority'],
            "progress": get_latest_progress(task['id']),
            "members": ", ".join(task.get('members', [])),
            "state": state  # Add state
        })
    return chart