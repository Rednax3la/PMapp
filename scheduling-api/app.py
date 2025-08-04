# scheduling-api/app.py
from datetime import datetime, timedelta
import pytz
import os
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
from validators import ProjectCreate, TaskCreate, BatchTaskCreate
from createandget import create_project, create_project_update, create_task, create_task_update, fetch_priority, get_latest_progress, get_member_tasks, get_project_by_company_and_name, get_project_tasks, create_tasks_batch, get_task_by_name, get_project_by_name, get_task_state, projects_db, tasks_db, updates_db
from helpers import format_duration, parse_duration, save_uploaded_file
from views import generate_timetable, generate_gantt_chart
from Projects.views import projects_bp
from flask_jwt_extended import (
    JWTManager, create_access_token, get_jwt, jwt_required,
    get_jwt_identity
)

app = Flask(__name__)
CORS(app, origins=['http://localhost:8080'], supports_credentials=True)
app.register_blueprint(projects_bp)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/projects', methods=['POST'])
@jwt_required()
def create_project_endpoint():
    print("=== PROJECT CREATION ENDPOINT ===")
    
    try:
        claims = get_jwt()
        print(f"JWT Claims: {claims}")
        
        data = request.json
        print(f"Request data: {data}")
        
        # Check company authorization
        if claims['company_name'] != data.get('company_name'):
            print(f"Unauthorized: JWT company '{claims['company_name']}' != request company '{data.get('company_name')}'")
            return jsonify({"error": "Unauthorized access"}), 403
        
        print("Company authorization passed")
        
        # Handle start_date conversion
        if data.get('start_date'):
            try:
                # Parse date string to datetime
                date_str = data['start_date']
                if isinstance(date_str, str):
                    # Parse date string (YYYY-MM-DD)
                    parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
                    # Make it timezone-aware using project timezone
                    timezone_str = data.get('timezone', 'UTC')
                    tz = pytz.timezone(timezone_str)
                    data['start_date'] = tz.localize(parsed_date)
                    print(f"Converted start_date: {data['start_date']}")
            except Exception as date_error:
                print(f"Date parsing error: {date_error}")
                return jsonify({"error": f"Invalid date format: {str(date_error)}"}), 400
        
        # Validate project data
        try:
            project_data = ProjectCreate(**data)
            print(f"ProjectCreate validation passed: {project_data}")
        except Exception as validation_error:
            print(f"ProjectCreate validation failed: {validation_error}")
            return jsonify({"error": f"Validation error: {str(validation_error)}"}), 400
        
        # Handle start_date
        if not project_data.start_date:
            project_data.start_date = datetime.now(pytz.UTC)
            print(f"Set default start_date: {project_data.start_date}")
        
        now = datetime.now(pytz.UTC)
        print(f"Current time: {now}")
        print(f"Project start_date: {project_data.start_date}")
        
        # Check scheduled project timing (convert both to UTC for comparison)
        if project_data.project_type == "scheduled":
            start_utc = project_data.start_date.astimezone(pytz.UTC) if project_data.start_date.tzinfo else pytz.UTC.localize(project_data.start_date)
            if start_utc < now:
                print(f"Scheduled project start date is in the past: {start_utc} < {now}")
                return jsonify({
                    "error": "Scheduled projects cannot start in the past – "
                             "either set start_date ≥ now or use project_type='documented'"
                }), 400

        print("About to call create_project function")
        project = create_project(
            name=project_data.project_name,
            start_date=project_data.start_date,
            company_name=project_data.company_name,
            objectives=project_data.objectives,
            timezone=project_data.timezone,
            project_type=project_data.project_type
        )
        
        if not project:
            print("create_project returned None - project name already exists")
            return jsonify({"error": "Project name already exists"}), 400
        
        print(f"Project created successfully: {project}")
        
        response_data = {
            "project_id": project['id'],
            "project_name": project['name'],
            "start_date": project['start_date'].isoformat(),
            "company_name": project['company_name'],
            "timezone": project['timezone'],
            "project_type": project['project_type'],
            "objectives": project['objectives'],
        }
        
        print(f"Returning response: {response_data}")
        return jsonify(response_data), 201
        
    except Exception as e:
        print(f"Unexpected error in create_project_endpoint: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/tasks', methods=['POST'])
def tasks_endpoint():
    data = request.json
    
    # Handle batch creation
    if isinstance(data, list):
        try:
            batch_data = BatchTaskCreate(tasks=data)
            task_dicts = []
            
            for task in batch_data.tasks:
                # Get project by name
                project = get_project_by_name(task.project_name)
                if not project:
                    return jsonify({"error": f"Project '{task.project_name}' not found"}), 400
                
                # Parse duration
                try:
                    duration_min = parse_duration(task.expected_duration)
                except Exception as e:
                    return jsonify({"error": f"Invalid duration: {str(e)}"}), 400
                
                # Resolve dependencies
                dependency_ids = []
                for dep_name in task.dependencies:
                    dep_task = get_task_by_name(project['id'], dep_name)
                    if not dep_task:
                        return jsonify({"error": f"Dependency task '{dep_name}' not found"}), 400
                    dependency_ids.append(dep_task['id'])
                
                task_dict = task.dict()
                task_dict['project_id'] = project['id']
                task_dict['expected_duration'] = duration_min
                task_dict['dependencies'] = dependency_ids
                task_dict['estimated_cost'] = task.estimated_cost
                task_dicts.append(task_dict)
            
            tasks = create_tasks_batch(task_dicts)
            # Auto-add all members from batch tasks to project team
            proj_record = projects_db.get(project['id'])
            if proj_record:
                team = set(proj_record.get('team', []))
                for t in batch_data.tasks:
                    team.update(t.members)
                proj_record['team'] = list(team)
            return jsonify({
             "message": f"{len(tasks)} tasks created successfully",
             "tasks": tasks
            }), 201
            
        except Exception as e:
            return jsonify({"error": f"Batch creation failed: {str(e)}"}), 400
    
    # Handle single task creation
    try:
        task_data = TaskCreate(**data)

        # 1) Lookup project
        project = get_project_by_name(task_data.project_name)
        if not project:
            return jsonify({"error": f"Project '{task_data.project_name}' not found"}), 404

        # 2) Determine start_time param for create_task:
        #    - If provided, ensure it's timezone‐aware
        #    - If not, pass None and let create_task pick defaults
        if task_data.start_time:
            if task_data.start_time.tzinfo is None:
                task_data.start_time = pytz.UTC.localize(task_data.start_time)
            start_time = task_data.start_time
        else:
            start_time = None

        # 3) Enforce “scheduled” projects can’t take a past explicit start_time
        if project.get('project_type') == 'scheduled' and start_time:
            if start_time < datetime.now(pytz.UTC):
                return jsonify({
                    "error": (
                        "A scheduled project cannot have an explicit start_time before now. "
                        "Either omit start_time to default to the project’s start_date, "
                        "or switch to project_type='documented'."
                    )
                }), 400

        # 4) Parse duration
        duration_min = parse_duration(task_data.expected_duration)

        # 5) Resolve dependencies
        dependency_ids = []
        for dep in task_data.dependencies or []:
            dep_task = get_task_by_name(project['id'], dep)
            if not dep_task:
                return jsonify({"error": f"Dependency task '{dep}' not found"}), 400
            dependency_ids.append(dep_task['id'])

        # 6) Create the task
        task = create_task(
            project_id=project['id'],
            name=task_data.task_name,
            start_time=start_time,
            expected_duration=duration_min,
            priority=task_data.priority,
            members=task_data.members,
            estimated_cost=task_data.estimated_cost,
            description=task_data.description,
            dependencies=dependency_ids
        )
        if not task:
            return jsonify({"error":"Task name already exists in this project"}), 400

        # 7) Auto‑add members to the project’s team
        proj_rec = projects_db[project['id']]
        team = set(proj_rec.get('team', []))
        team.update(task_data.members or [])
        proj_rec['team'] = list(team)

        # 8) Return
        return jsonify({
            "project_name": task_data.project_name,
            "task_name": task['name'],
            "start_time": task['start_time'].isoformat(),
            "expected_duration": format_duration(task['expected_duration']),
            "duration": format_duration(task['duration']),
            "priority": task['priority'],
            "members": task['members'],
            "dependencies": task_data.dependencies,
            "estimated_cost": task['estimated_cost'],
            "task_id": task['id']
        }), 201

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": f"Single task creation failed: {str(e)}"}), 400

@app.route('/tasks/updates', methods=['POST'])
def create_task_update_endpoint():
    try:
        # Get by names
        company_name = request.form.get('company_name')
        project_name = request.form.get('project_name')
        task_name = request.form.get('task_name')
        status_perc = int(request.form.get('status_percentage'))
        description = request.form.get('description', '')
        
        # Get project and task
        project = get_project_by_name(project_name)
        if not project:
            return jsonify({"error": "Project not found"}), 404
            
        task = get_task_by_name(project['id'], task_name)
        if not task:
            return jsonify({"error": "Task not found"}), 404

        # Process images
        images = request.files.getlist('images')
        update_count = len(task['updates']) + 1
        image_filenames = []
        
        for i, image in enumerate(images, start=1):
            if image.filename == '':
                continue
            filename = save_uploaded_file(
                image, 
                task_id=task['id'], 
                update_count=update_count, 
                image_count=i
            )
            if filename:
                image_filenames.append(filename)

        # Capture optional expenditure
        expenditure_val = request.form.get('expenditure')
        try:
            expenditure = float(expenditure_val) if expenditure_val is not None else None
        except ValueError:
            return jsonify({"error": "Invalid expenditure value"}), 400
        # Create update, storing expenditure
        update_id = create_task_update(
            task_id=task['id'],
            status_percentage=status_perc,
            description=description,
            image_filenames=image_filenames
        )
        # Persist expenditure in updates_db
        if expenditure is not None:
            updates_db[update_id]['expenditure'] = expenditure

        return jsonify ({
            "update_id": update_id,
            "company_name": company_name,
            "project_name": project_name,
            "task_name": task_name,
            "status_percentage": status_perc,
            "description": description,
            "images": image_filenames,
            "expenditure": expenditure if expenditure is not None else None,
            "timestamp": datetime.now().isoformat()
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/views/timetable', methods=['POST'])
def timetable_view():
    data = request.json
    if not data or 'company_name' not in data or 'project_name' not in data:
        return jsonify({"error": "company_name and project_name are required"}), 400
    
    project_name = data['project_name']
    project = get_project_by_name(project_name)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    tasks = get_project_tasks(project['id'])
    timetable = generate_timetable(project, tasks)
    return jsonify(timetable)

@app.route('/views/gantt', methods=['POST'])
def gantt_view():
    data = request.json
    if not data or 'company_name' not in data or 'project_name' not in data:
        return jsonify({"error": "company_name and project_name are required"}), 400
    
    project_name = data['project_name']
    project = get_project_by_name(project_name)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    tasks = get_project_tasks(project['id'])
    gantt = generate_gantt_chart(tasks)
    return jsonify(gantt)

# Update image endpoint to use names
# New endpoint to get all images for a task
@app.route('/views/images', methods=['POST'])
def get_task_images():
    data = request.json
    required_fields = ['project_name', 'task_name']
    if not data or 'company_name' not in data:
        return jsonify({"error": "company_name is required"}), 400
    if not data or any(field not in data for field in required_fields):
        return jsonify({"error": "project_name and task_name are required"}), 400

    try:
        project = get_project_by_name(data['project_name'])
        if not project:
            return jsonify({"error": "Project not found"}), 404
            
        task = get_task_by_name(project['id'], data['task_name'])
        if not task:
            return jsonify({"error": "Task not found"}), 404
            
        # Collect all images from all updates
        all_images = []
        upload_folder = app.config['UPLOAD_FOLDER']
        
        # List all files in upload directory
        for filename in os.listdir(upload_folder):
            if filename.startswith(f"task{task['id']}_update"):
                all_images.append({
                    "filename": filename,
                    "url": f"/uploads/{filename}"
                })
                
        return jsonify({
            "project": data['project_name'],
            "task": data['task_name'],
            "images": all_images
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/states', methods=['POST'])
def states_endpoint(): 
    data = request.json or {}
    now = datetime.now(pytz.UTC)
    if 'time' in data:
        t = datetime.fromisoformat(data['time'])
        now = pytz.UTC.localize(t) if t.tzinfo is None else t

    if data.get('type') == 'task':
        # require project_name + task_name
        proj = get_project_by_name(data.get('project_name'))
        task = get_task_by_name(proj['id'], data.get('task_name'))
        state = get_task_state(task['id'], now)
        return jsonify({"task": task['name'], "state": state}), 200

    elif data.get('type') == 'project':
        # require project_name
        proj = get_project_by_name(data.get('project_name'))
        # Evaluate dependencies first
        for dep in proj.get('dependencies', []):
            if projects_db[dep]['state'] != 'complete':
                return jsonify({"project": proj['name'], "state": "delayed"}), 200
        # Evaluate task states
        states = [get_task_state(t['id'], now) for t in get_project_tasks(proj['id'])]
        if not states or all(s == 'tentative' for s in states):
            st = 'tentative'
        elif all(s == 'complete' for s in states):
            st = 'complete'
        elif now > max(t['start_time'] + timedelta(minutes=t['expected_duration']) for t in get_project_tasks(proj['id'])):
            st = 'overdue'
        else:
            st = 'active'
        proj['state'] = st
        return jsonify({"project": proj['name'], "state": st}), 200

    else:
        return jsonify({"error": "type must be 'task' or 'project'"}), 400

# New endpoint to mark task status
@app.route('/tasks/mark-as', methods=['POST'])
def mark_as_endpoint():
    data = request.json

    if not data or 'company_name' not in data:
        return jsonify({"error": "company_name is required"}), 400

    if not data or 'project_name' not in data or 'task_name' not in data or 'state' not in data :
        return jsonify({"error": "project_name, task_name, and state are required"}), 400
    
    state = data['state'].lower()
    valid_states = ["started", "postponed", "complete"]
    
    if state not in valid_states:
        return jsonify({"error": f"Invalid state. Must be one of: {', '.join(valid_states)}"}), 400
    
    project = get_project_by_name(data['project_name'])
    if not project:
        return jsonify({"error": "Project not found"}), 404
        
    task = get_task_by_name(project['id'], data['task_name'])
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    if state == "started":
        if get_latest_progress(task['id']) == 0:
            update_id = create_task_update(
                task_id=task['id'],
                status_percentage=0,
                description="Task marked as started"
            )
        else:
            # idempotent: still log it
            update_id = create_task_update(
                task_id=task['id'],
                status_percentage=get_latest_progress(task['id']),
                description="Task re‑marked as started"
            )
        ts = updates_db[update_id]['timestamp'].isoformat()
        return jsonify({
            "message": f"Task marked as {state}",
            "task": task,
            "timestamp": ts
        }), 200

    
    elif state == "complete":
        update_id = create_task_update(
            task_id=task['id'],
            status_percentage=100,
            description="Task marked as complete"
        )
        ts = updates_db[update_id]['timestamp'].isoformat()
        return jsonify({
            "message": f"Task marked as {state}",
            "task": task,
            "timestamp": ts
        }), 200
    
    elif state == "postponed":
        update_id = create_task_update(
            task_id=task['id'],
            status_percentage=get_latest_progress(task['id']),
            description="Task marked as postponed"
        )
        ts = updates_db[update_id]['timestamp'].isoformat()
        return jsonify({
            "message": f"Task marked as {state}. Call /tasks/postpone-to to set new schedule",
            "task": task,
            "timestamp": ts
        }), 200

@app.route('/tasks/postpone-to', methods=['POST'])
def postpone_to_endpoint():
    data = request.json
    required = ['company_name', 'new_start_time']
    if not data or any(field not in data for field in required):
        return jsonify({"error": "company_name and new_start_time are required"}), 400
    
    try:
        company_name = data['company_name']
        project_name = data.get('project_name')
        task_name = data.get('task_name')
        new_start = datetime.fromisoformat(data['new_start_time'])
        
        if new_start.tzinfo is None:
            new_start = pytz.UTC.localize(new_start)
        
        # Postpone entire project
        if not project_name:
            projects = [p for p in projects_db.values() 
                       if p['company_name'].lower() == company_name.lower()]
            
            if not projects:
                return jsonify({"error": "No projects found for company"}), 404
            
            for project in projects:
                # Calculate time delta
                delta = new_start - project['start_date']
                project['start_date'] = new_start
                
                # Update all tasks in project
                for task_id in project['tasks']:
                    task = tasks_db.get(task_id)
                    if task:
                        task['start_time'] += delta
            
            # Log each project’s postponement
            for project in projects:
                create_project_update(
                    project_id=project['id'],
                    description=f"Project postponed to {new_start.isoformat()}"
                )
            return jsonify({
                "message": "All projects postponed",
                "new_start_time": new_start.isoformat(),
                "timestamp": datetime.now().isoformat()
            }), 200
        
        # Postpone specific project or task
        project = get_project_by_company_and_name(company_name, project_name)
        if not project:
            return jsonify({"error": "Project not found"}), 404
            
        # Postpone entire project
        if not task_name:
            delta = new_start - project['start_date']
            project['start_date'] = new_start
            
            for task_id in project['tasks']:
                task = tasks_db.get(task_id)
                if task:
                    task['start_time'] += delta
            
            create_project_update(
                project_id=project['id'],
                description=f"Project postponed to {new_start.isoformat()}"
            )
            return jsonify({
                "message": "Project postponed",
                "project": project,
                "new_start_time": new_start.isoformat(),
                "timestamp": datetime.now().isoformat()
            }), 200
        
        # Postpone specific task
        task = get_task_by_name(project['id'], task_name)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        new_duration = data.get('new_duration')
        if new_duration:
            try:
                new_duration_min = parse_duration(new_duration)
            except Exception as e:
                return jsonify({"error": f"Invalid duration: {str(e)}"}), 400
        else:
            new_duration_min = task['duration']
        
        task['start_time'] = new_start
        task['duration'] = new_duration_min
        task['postponed'] = False
        
        # Log as a task update
        update_id = create_task_update(
            task_id=task['id'],
            status_percentage=get_latest_progress(task['id']),
            description=f"Task postponed to {new_start.isoformat()}"
        )
        ts = updates_db[update_id]['timestamp'].isoformat()
        return jsonify({
            "message": "Task postponed",
            "task": task,
            "new_start_time": new_start.isoformat(),
            "timestamp": ts
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/tasks/priority', methods=['POST'])
def fetch_priority_endpoint():
    data = request.json
    project_name = data.get('project_name')
    priority = data.get('priority')
    
    if not project_name or not priority:
        return jsonify({"error": "project_name or priority is required"}), 400
    
    tasks = fetch_priority(project_name, priority)
    return jsonify([{
        "id": t['id'],
        "name": t['name'],
        "priority": t['priority']
    } for t in tasks])

@app.route('/tasks/member', methods=['POST'])
def get_member_tasks_endpoint():
    data = request.json
    project_name = data.get('project_name')
    member = data.get('member')
    
    if not data or 'company_name' not in data:
        return jsonify({"error": "company_name is required"}), 400

    if not project_name or not member:
        return jsonify({"error": "project_name or member is required"}), 400
    
    tasks = get_member_tasks(project_name, member)
    return jsonify([{
        "id": t['id'],
        "task_name": t['name'],
        "start_time": t['start_time'].isoformat()
    } for t in tasks])

@app.route('/tasks/members', methods=['POST'])
def get_task_members_endpoint():
    data = request.json
    project_name = data.get('project_name')
    task_name = data.get('task_name')
    
    if not data or 'company_name' not in data:
        return jsonify({"error": "company_name is required"}), 400

    if not project_name or not task_name:
        return jsonify({"error": "project_name and task_name are required"}), 400
    
    project = get_project_by_name(project_name)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    task = get_task_by_name(project['id'], task_name)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    return jsonify({
        "project": project_name,
        "task": task_name,
        "members": task['members']
    })

# Add this after app creation
app.config["JWT_SECRET_KEY"] = "your-secret-key"  # Change in production!
jwt = JWTManager(app)

# User storage (in production, use a database)
users_db = {}

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    required = ['company_name', 'username', 'password', 'role']
    if not data or any(field not in data for field in required):
        return jsonify({"error": "All fields are required"}), 400
    
    if data['username'] in users_db:
        return jsonify({"error": "Username already exists"}), 400
        
    users_db[data['username']] = {
        'company_name': data['company_name'],
        'password': data['password'],  # In production, hash passwords!
        'role': data['role'],
        'username': data['username']
    }
    
    return jsonify({
        "message": "User registered successfully",
        "username": data['username'],
        "company_name": data['company_name'],
        "role": data['role']
    }), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password required"}), 400
    
    user = users_db.get(data['username'])
    if not user or user['password'] != data['password']:
        return jsonify({"error": "Invalid credentials"}), 401
    
    print(f"Login successful for user: {user['username']}, company: {user['company_name']}")  # Debug log
    
    # Create JWT token
    access_token = create_access_token(
        identity=user['username'],
        additional_claims={
            'company_name': user['company_name'],
            'role': user['role']
        }
    )
    
    response_data = {
        "access_token": access_token,
        "username": user['username'],
        "company_name": user['company_name'],
        "role": user['role']
    }
    
    print(f"Sending login response: {response_data}")  # Debug log
    
    return jsonify(response_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)