# scheduling-api/views.py
from datetime import timedelta
from createandget import get_latest_progress, get_task_state
import pytz
from helpers import format_duration


def generate_timetable(project, tasks):
    """
    FIXED: Generate timetable with proper date formatting including month/day names
    """
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
        
        # Use expected_duration if task not complete, otherwise use actual duration
        task_progress = get_latest_progress(task['id'])
        if task_progress == 100 and task.get('duration', 0) > 0:
            duration_to_use = task['duration']
        else:
            duration_to_use = task.get('expected_duration', 0)
            
        end = start + timedelta(minutes=duration_to_use)
        state = get_task_state(task['id'])

        # FIXED: Format dates with month and day names
        start_local = start.astimezone(timezone)
        end_local = end.astimezone(timezone)

        timetable.append({
            "task": task['name'],
            "start": start.isoformat(),
            "end": end.isoformat(),
            # FIXED: Add human-readable date formats
            "start_formatted": start_local.strftime("%A, %B %d, %Y at %I:%M %p"),
            "end_formatted": end_local.strftime("%A, %B %d, %Y at %I:%M %p"),
            "start_date": start_local.strftime("%Y-%m-%d"),
            "start_time": start_local.strftime("%I:%M %p"),
            "end_date": end_local.strftime("%Y-%m-%d"),
            "end_time": end_local.strftime("%I:%M %p"),
            "day_of_week": start_local.strftime("%A"),
            "month": start_local.strftime("%B"),
            "expected_duration": format_duration(task['expected_duration']),
            **({"actual_duration": format_duration(task['duration'])}
                if get_latest_progress(task['id']) == 100 else {}),
            "members": task.get('members', []),
            "progress": get_latest_progress(task['id']),
            "state": state,
            "priority": task.get('priority', 'medium'),
            "estimated_cost": task.get('estimated_cost', 0)
        })
        current_time = end

    return {
        "project_name": project['name'],
        "project_start": project_start.isoformat(),
        "project_start_formatted": project_start.astimezone(timezone).strftime("%A, %B %d, %Y at %I:%M %p"),
        "timezone": timezone_str,
        "tasks": timetable
    }

def generate_gantt_chart(tasks):
    """
    FIXED: Generate gantt chart with proper data from database (no dummy data)
    """
    chart = []
    
    if not tasks:
        return {
            "message": "No tasks found",
            "tasks": []
        }
    
    for task in tasks:
        # Make task start time timezone-aware if it isn't already
        task_start = task['start_time']
        if task_start.tzinfo is None:
            # Default to Africa/Addis_Ababa if no timezone info available
            timezone = pytz.timezone('Africa/Addis_Ababa')
            task_start = timezone.localize(task_start)
        
        # Use expected_duration if task not complete, otherwise use actual duration
        task_progress = get_latest_progress(task['id'])
        if task_progress == 100 and task.get('duration', 0) > 0:
            duration_to_use = task['duration']
            duration_label = "actual_duration"
        else:
            duration_to_use = task.get('expected_duration', 0)
            duration_label = "expected_duration"
            
        end_time = task_start + timedelta(minutes=duration_to_use)
        state = get_task_state(task['id'])
        
        # Format dates for display
        task_start_local = task_start.astimezone(pytz.timezone('Africa/Addis_Ababa'))
        end_time_local = end_time.astimezone(pytz.timezone('Africa/Addis_Ababa'))
        
        chart_item = {
            "id": task['id'],
            "task": task['name'],
            "start": task_start.isoformat(),
            "end": end_time.isoformat(),
            "start_formatted": task_start_local.strftime("%A, %B %d, %Y at %I:%M %p"),
            "end_formatted": end_time_local.strftime("%A, %B %d, %Y at %I:%M %p"),
            "expected_duration": format_duration(task.get('expected_duration', 0)),
            "priority": task.get('priority', 'medium'),
            "progress": task_progress,
            "members": task.get('members', []),
            "members_display": ", ".join(task.get('members', [])) if task.get('members') else "No members assigned",
            "state": state,
            "estimated_cost": task.get('estimated_cost', 0),
            "description": task.get('description', ''),
            "dependencies": task.get('dependencies', [])
        }
        
        # Add actual duration if task is complete
        if task_progress == 100 and task.get('duration', 0) > 0:
            chart_item["actual_duration"] = format_duration(task['duration'])
            chart_item["duration_variance"] = task['duration'] - task.get('expected_duration', 0)
            chart_item["duration_variance_formatted"] = format_duration(abs(chart_item["duration_variance"]))
            chart_item["is_overdue"] = chart_item["duration_variance"] > 0
        
        chart.append(chart_item)
    
    return {
        "total_tasks": len(chart),
        "completed_tasks": len([t for t in chart if t['progress'] == 100]),
        "in_progress_tasks": len([t for t in chart if 0 < t['progress'] < 100]),
        "not_started_tasks": len([t for t in chart if t['progress'] == 0]),
        "tasks": chart
    }