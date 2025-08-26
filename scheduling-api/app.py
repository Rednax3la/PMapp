# scheduling-api/app.py
from datetime import datetime, timedelta
from bson import ObjectId
import pytz
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from db import users_col, projects_col, tasks_col, updates_col, project_updates_col
from auth_helpers import is_valid_email, normalize_email, create_user, check_password
from validators import ProjectCreate, TaskCreate, BatchTaskCreate
from createandget import create_project, create_project_update, create_task, create_task_update, fetch_priority, get_latest_progress, get_member_tasks, get_project_by_company_and_name, get_project_tasks, create_tasks_batch, get_task_by_name, get_project_by_name, get_task_state
from helpers import format_duration, parse_duration, save_uploaded_file
from views import generate_timetable, generate_gantt_chart
from Projects.views import projects_bp
from flask_jwt_extended import (
    JWTManager, create_access_token, get_jwt, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies, verify_jwt_in_request
)
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app, origins=['http://localhost:8080'], supports_credentials=True)
app.register_blueprint(projects_bp)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load environment variables
load_dotenv()
jwt_secret = os.getenv("JWT_SECRET_KEY")
if not jwt_secret:
    raise RuntimeError("JWT_SECRET_KEY environment variable is required. Set a strong secret in your environment.")
app.config["JWT_SECRET_KEY"] = jwt_secret

# Configure JWT to use cookies for token storage
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]

# Cookie security flags - in production ensure SECURE=True and your site uses HTTPS.
app.config["JWT_COOKIE_SECURE"] = os.getenv("JWT_COOKIE_SECURE", "False").lower() in ("1", "true", "yes")
app.config["JWT_COOKIE_SAMESITE"] = os.getenv("JWT_COOKIE_SAMESITE", "Lax")  # Lax is a good default
app.config["JWT_COOKIE_CSRF_PROTECT"] = os.getenv("JWT_COOKIE_CSRF_PROTECT", "False").lower() in ("1", "true", "yes")

# FIXED: Shorter token expiration for better security and to fix session persistence issue
access_expires_min = int(os.getenv("JWT_ACCESS_EXPIRES_MIN", "30"))  # Reduced from 60 to 30 minutes
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=access_expires_min)

# Paths (optional) for cookies
app.config["JWT_ACCESS_COOKIE_PATH"] = os.getenv("JWT_ACCESS_COOKIE_PATH", "/")
app.config["JWT_REFRESH_COOKIE_PATH"] = os.getenv("JWT_REFRESH_COOKIE_PATH", "/token/refresh")

# Other useful config
app.config["PROPAGATE_EXCEPTIONS"] = True

# Initialize JWT extension
jwt = JWTManager(app)

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """Handle expired tokens - don't clear cookies immediately"""
    return jsonify({
        "error": "Token has expired",
        "requires_login": True
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    """Handle invalid tokens"""
    return jsonify({
        "error": "Invalid token", 
        "requires_login": True
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error_string):
    """Handle missing tokens"""
    return jsonify({
        "error": "Authorization required",
        "requires_login": True  
    }), 401

# FIXED: Add session validation endpoint
@app.route('/auth/validate', methods=['GET'])
def validate_session():
    """Validate current session without requiring JWT decorator"""
    try:
        # Manually verify JWT without requiring decorator
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        
        if not current_user_id:
            return jsonify({
                "valid": False,
                "requires_login": True
            }), 401
            
        return jsonify({
            "valid": True,
            "user": {
                "id": current_user_id,
                "company_name": claims.get("company_name"),
                "role": claims.get("role")
            }
        }), 200
        
    except Exception as e:
        # Token is invalid/expired/missing
        return jsonify({
            "valid": False, 
            "requires_login": True
        }), 401

@app.route("/logout", methods=["POST"])
def logout():
    """Clear the JWT cookies on logout."""
    resp = jsonify({"logout": True})
    unset_jwt_cookies(resp)
    return resp, 200

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    required = ['company_name', 'username', 'password']
    if any(field not in data or not data.get(field) for field in required):
        return jsonify({"error": "company_name, username and password are required"}), 400

    username = normalize_email(data['username'])
    if not is_valid_email(username):
        return jsonify({"error": "username must be a valid email address"}), 422

    try:
        user = create_user(username, data['password'], data['company_name'])
        serialized = {
            "id": str(user.get("id") or user.get("_id") or user.get("username")),
            "username": user.get("username"),
            "company_name": user.get("company_name")
        }
        return jsonify({
            "message": "User registered successfully",
            "user": serialized
        }), 201
    except ValueError as e:
        # Expected validation errors from create_user (e.g. duplicate email)
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Server error: " + str(e)}), 500

# Make sure your login endpoint sets cookies properly
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    if 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password required"}), 400

    username = normalize_email(data['username'])
    user_doc = users_col.find_one({"username": username})
    if not user_doc or not check_password(data['password'], user_doc.get('password', '')):
        return jsonify({"error": "Invalid credentials"}), 401

    # Create access token with longer expiration for testing
    access_token = create_access_token(
        identity=str(user_doc.get("id") or user_doc.get("_id") or user_doc.get("username")),
        additional_claims={
            "company_name": user_doc.get("company_name"),
            "role": user_doc.get("role")
        },
        expires_delta=timedelta(hours=24)  # Temporary: longer expiration for testing
    )

    resp = jsonify({
        "message": "Login successful",
        "username": user_doc.get("username"),
        "company_name": user_doc.get("company_name"),
        "role": user_doc.get("role")
    })
    
    # Set cookies with proper configuration
    set_access_cookies(resp, access_token)
    return resp, 200

# FIXED: Add user profile endpoint
@app.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        # Find user in database
        user_doc = users_col.find_one({"_id": ObjectId(user_id)}) if ObjectId.is_valid(user_id) else users_col.find_one({"username": user_id})
        
        if not user_doc:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify({
            "username": user_doc.get("username"),
            "company_name": user_doc.get("company_name"), 
            "role": user_doc.get("role"),
            "created_at": user_doc.get("created_at").isoformat() if user_doc.get("created_at") else None
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# FIXED: Add user profile update endpoint
@app.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    try:
        user_id = get_jwt_identity()
        data = request.json or {}
        
        # Find user in database
        user_doc = users_col.find_one({"_id": ObjectId(user_id)}) if ObjectId.is_valid(user_id) else users_col.find_one({"username": user_id})
        
        if not user_doc:
            return jsonify({"error": "User not found"}), 404
            
        # Update allowed fields
        update_data = {}
        if 'company_name' in data:
            update_data['company_name'] = data['company_name']
        if 'role' in data:
            update_data['role'] = data['role']
            
        if update_data:
            users_col.update_one(
                {"_id": user_doc["_id"]},
                {"$set": update_data}
            )
            
        return jsonify({"message": "Profile updated successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# FIXED: Add user deletion endpoint
@app.route('/users/<username>', methods=['DELETE'])
@jwt_required()
def delete_user(username):
    """Delete user account with options for data handling"""
    try:
        claims = get_jwt()
        current_user_id = get_jwt_identity()
        data = request.json or {}
        
        # Normalize the username to delete
        target_username = normalize_email(username)
        
        # Find the target user
        target_user = users_col.find_one({"username": target_username})
        if not target_user:
            return jsonify({"error": "User not found"}), 404
            
        company_name = target_user.get("company_name")
        
        # Check authorization - only allow deletion if:
        # 1. Deleting own account, OR
        # 2. User is admin in same company
        current_user = users_col.find_one({"_id": ObjectId(current_user_id)}) if ObjectId.is_valid(current_user_id) else users_col.find_one({"username": current_user_id})
        
        is_self_delete = current_user.get("username") == target_username
        is_admin_same_company = (current_user.get("role") == "admin" and 
                                current_user.get("company_name") == company_name)
        
        if not (is_self_delete or is_admin_same_company):
            return jsonify({"error": "Unauthorized to delete this user"}), 403
            
        # Handle data based on delete_option
        delete_option = data.get('delete_option', 'transfer_to_admin')  # 'transfer_to_admin' or 'delete_all'
        
        if delete_option == 'delete_all':
            # Delete all company data
            projects = list(projects_col.find({"company_name": company_name}))
            project_ids = [p.get('id') for p in projects]
            
            # Delete all tasks, updates, and project updates for this company
            if project_ids:
                tasks_col.delete_many({"project_id": {"$in": project_ids}})
                updates_col.delete_many({"task_id": {"$in": [t.get('id') for t in tasks_col.find({"project_id": {"$in": project_ids}})]}})
                project_updates_col.delete_many({"project_id": {"$in": project_ids}})
                
            # Delete all projects
            projects_col.delete_many({"company_name": company_name})
            
            # Delete all users in the company
            users_col.delete_many({"company_name": company_name})
            
            message = f"User '{target_username}' and all company '{company_name}' data deleted successfully"
            
        else:  # transfer_to_admin
            # Find an admin in the same company to transfer ownership
            admin_user = users_col.find_one({
                "company_name": company_name,
                "role": "admin",
                "username": {"$ne": target_username}
            })
            
            if not admin_user:
                return jsonify({
                    "error": "No admin found to transfer data to. Use delete_option='delete_all' to delete all company data."
                }), 400
                
            admin_email = admin_user.get("username")
            
            # Transfer project ownership and team memberships
            projects_col.update_many(
                {"company_name": company_name},
                {"$set": {"team.$[elem]": admin_email}},
                array_filters=[{"elem": target_username}]
            )
            
            # Transfer task memberships
            tasks_col.update_many(
                {"members": target_username},
                {"$set": {"members.$[elem]": admin_email}},
                array_filters=[{"elem": target_username}]
            )
            
            # Delete the user
            users_col.delete_one({"username": target_username})
            
            message = f"User '{target_username}' deleted successfully. Data transferred to admin '{admin_email}'"
        
        # If deleting own account, logout
        resp = jsonify({"message": message})
        if is_self_delete:
            unset_jwt_cookies(resp)
            
        return resp, 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/projects', methods=['POST'])
@jwt_required()
def create_project_endpoint():
    print("=== PROJECT CREATION ENDPOINT ===")
    
    try:
        claims = get_jwt() or {}
        print(f"JWT Claims: {claims}")

        data = request.json or {}
        print(f"Request data: {data}")

        # Resolve company_name: prefer request body, fall back to JWT claim
        jwt_company = claims.get('company_name')
        req_company = data.get('company_name')

        if req_company:
            # If client supplied a company, ensure it matches the authenticated user's company
            if jwt_company and jwt_company != req_company:
                print(f"Unauthorized: JWT company '{jwt_company}' != request company '{req_company}'")
                return jsonify({"error": "Unauthorized access: company mismatch"}), 403
            company = req_company
            print(f"Using company from request body: {company}")
        else:
            # No company in body, try to use company from JWT
            if not jwt_company:
                print("Missing company_name in both request body and JWT claims")
                return jsonify({
                    "error": "company_name missing in request body and JWT claims. Please log in or include company_name in payload."
                }), 400
            company = jwt_company
            print(f"Using company from JWT claims: {company}")

        # Attach effective company_name into data variable so downstream code can use it
        data['company_name'] = company

        # FIXED: Handle start_date conversion properly
        if data.get('start_date'):
            try:
                # Parse date string to datetime
                date_str = data['start_date']
                if isinstance(date_str, str):
                    # Parse ISO format date string
                    if 'T' in date_str:
                        parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:
                        # Parse date string (YYYY-MM-DD)
                        parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
                        # Make it timezone-aware using project timezone
                        timezone_str = data.get('timezone', 'Africa/Addis_Ababa')
                        tz = pytz.timezone(timezone_str)
                        parsed_date = tz.localize(parsed_date)
                    
                    # Ensure it's in the correct timezone
                    if parsed_date.tzinfo is None:
                        timezone_str = data.get('timezone', 'Africa/Addis_Ababa')
                        tz = pytz.timezone(timezone_str)
                        parsed_date = tz.localize(parsed_date)
                        
                    data['start_date'] = parsed_date
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
            timezone_str = project_data.timezone or 'Africa/Addis_Ababa'
            tz = pytz.timezone(timezone_str)
            project_data.start_date = datetime.now(tz)
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
            "team": project.get('team', []),  # FIXED: Include team in response
            "expected_duration": project.get('expected_duration')  # FIXED: Include expected_duration
        }
        
        print(f"Returning response: {response_data}")
        return jsonify(response_data), 201
        
    except Exception as e:
        print(f"Unexpected error in create_project_endpoint: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# FIXED: Add project deletion endpoint
@app.route('/projects/<project_name>', methods=['DELETE'])
@jwt_required()
def delete_project(project_name):
    """Delete a project and all associated data"""
    try:
        claims = get_jwt()
        company_name = claims['company_name']
        
        # Find the project
        project = get_project_by_company_and_name(company_name, project_name)
        if not project:
            return jsonify({"error": "Project not found"}), 404
            
        project_id = project['id']
        
        # Delete all tasks and their updates
        tasks = get_project_tasks(project_id)
        task_ids = [task['id'] for task in tasks]
        
        if task_ids:
            # Delete task updates
            updates_col.delete_many({"task_id": {"$in": task_ids}})
            # Delete tasks
            tasks_col.delete_many({"project_id": project_id})
            
        # Delete project updates
        project_updates_col.delete_many({"project_id": project_id})
        
        # Delete the project
        projects_col.delete_one({"id": project_id})
        
        return jsonify({"message": f"Project '{project_name}' deleted successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tasks', methods=['POST'])
@jwt_required()  # FIXED: Add JWT protection
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
                
                # FIXED: Parse duration with better error handling
                try:
                    if not task.expected_duration or task.expected_duration.strip() == "":
                        return jsonify({"error": "expected_duration cannot be empty"}), 400
                    duration_min = parse_duration(task.expected_duration)
                    if duration_min <= 0:
                        return jsonify({"error": "expected_duration must be positive"}), 400
                except Exception as e:
                    return jsonify({"error": f"Invalid duration '{task.expected_duration}': {str(e)}"}), 400
                
                # Resolve dependencies
                dependency_ids = []
                for dep_name in task.dependencies:
                    dep_task = get_task_by_name(project['id'], dep_name)
                    if not dep_task:
                        return jsonify({"error": f"Dependency task '{dep_name}' not found"}), 400
                    dependency_ids.append(dep_task['id'])
                
                members_list = []
                for m in (task.members or []):
                    m_norm = normalize_email(m)
                    if not is_valid_email(m_norm):
                        return jsonify({"error": f"Invalid member email in batch: {m}"}), 422
                    members_list.append(m_norm)

                task_dict = task.dict()
                task_dict['members'] = members_list
                task_dict['project_id'] = project['id']
                task_dict['expected_duration'] = duration_min
                task_dict['dependencies'] = dependency_ids
                task_dict['estimated_cost'] = task.estimated_cost
                task_dicts.append(task_dict)
            
            tasks = create_tasks_batch(task_dicts)
            # Auto-add all members from batch tasks to project team
            proj_record = projects_col.find_one({"id": project['id']})
            if proj_record:
                team = set(proj_record.get('team', []))
                for t in batch_data.tasks:
                    team.update(t.members or [])
                projects_col.update_one({"id": project['id']}, {"$set": {"team": list(team)}})
            return jsonify({
             "message": f"{len(tasks)} tasks created successfully",
             "tasks": tasks
            }), 201
            
        except Exception as e:
            return jsonify({"error": f"Batch creation failed: {str(e)}"}), 400
    
    # Handle single task creation
    try:
        # Log the incoming data for debugging
        print(f"Incoming task data: {data}")
    
        # FIXED: Better validation for expected_duration
        if 'expected_duration' not in data or not data['expected_duration']:
            return jsonify({"error": "expected_duration is required and cannot be empty"}), 400
        
        if isinstance(data['expected_duration'], str) and data['expected_duration'].strip() == "":
            return jsonify({"error": "expected_duration cannot be empty"}), 400
    
        task_data = TaskCreate(**data)
        print(f"TaskCreate validation passed: {task_data}")

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

        # 3) Enforce "scheduled" projects can't take a past explicit start_time
        if project.get('project_type') == 'scheduled' and start_time:
            if start_time < datetime.now(pytz.UTC):
                return jsonify({
                    "error": (
                        "A scheduled project cannot have an explicit start_time before now. "
                        "Either omit start_time to default to the project's start_date, "
                        "or switch to project_type='documented'."
                    )
                }), 400

        # 4) FIXED: Parse duration with better error handling
        try:
            if not task_data.expected_duration or task_data.expected_duration.strip() == "":
                return jsonify({"error": "expected_duration cannot be empty"}), 400
            duration_min = parse_duration(task_data.expected_duration)
            if duration_min <= 0:
                return jsonify({"error": "expected_duration must be positive"}), 400
        except Exception as e:
            return jsonify({"error": f"Invalid duration '{task_data.expected_duration}': {str(e)}"}), 400

        # 5) Resolve dependencies
        dependency_ids = []
        for dep in task_data.dependencies or []:
            dep_task = get_task_by_name(project['id'], dep)
            if not dep_task:
                return jsonify({"error": f"Dependency task '{dep}' not found"}), 400
            dependency_ids.append(dep_task['id'])

        # 6) Create the task
        # validate members are emails and normalized
        if not isinstance(task_data.members, list):
            return jsonify({"error":"members must be a list of emails"}), 422
        invalid = [m for m in (task_data.members or []) if not is_valid_email(normalize_email(m))]
        if invalid:
            return jsonify({"error":"Invalid member emails", "invalid": invalid}), 422

        members_clean = [normalize_email(m) for m in (task_data.members or [])]

        task = create_task(
            project_id=project['id'],
            name=task_data.task_name,
            start_time=start_time,
            expected_duration=duration_min,
            priority=task_data.priority,
            members=members_clean,
            estimated_cost=task_data.estimated_cost,
            description=task_data.description,
            dependencies=dependency_ids
        )
        if not task:
            return jsonify({"error":"Task name already exists in this project"}), 400

        # 7) Auto‑add members to the project's team
        proj_rec = projects_col.find_one({"id": project['id']})
        team = set(proj_rec.get('team', []))
        team.update(members_clean or [])
        projects_col.update_one({"id": project['id']}, {"$set": {"team": list(team)}})

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

    except Exception as validation_error:
        print(f"TaskCreate validation failed: {validation_error}")
        return jsonify({"error": f"Validation error: {str(validation_error)}"}), 400

# FIXED: Add task deletion endpoint
@app.route('/tasks/<project_name>/<task_name>', methods=['DELETE'])
@jwt_required()
def delete_task(project_name, task_name):
    """Delete a task and all associated updates"""
    try:
        claims = get_jwt()
        company_name = claims['company_name']
        
        # Find the project
        project = get_project_by_company_and_name(company_name, project_name)
        if not project:
            return jsonify({"error": "Project not found"}), 404
            
        # Find the task
        task = get_task_by_name(project['id'], task_name)
        if not task:
            return jsonify({"error": "Task not found"}), 404
            
        task_id = task['id']
        
        # Delete task updates
        updates_col.delete_many({"task_id": task_id})
        
        # Remove task from project's task list
        projects_col.update_one(
            {"id": project['id']},
            {"$pull": {"tasks": task_id}}
        )
        
        # Delete the task
        tasks_col.delete_one({"id": task_id})
        
        return jsonify({"message": f"Task '{task_name}' deleted successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tasks/updates', methods=['POST'])
@jwt_required()  # FIXED: Add JWT protection
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

        if get_task_state(task['id']) == 'complete':
            return jsonify({"error": "Task is complete. Restore the task before creating updates."}), 400

        # Create update, storing expenditure
        update_id = create_task_update(
            task_id=task['id'],
            status_percentage=status_perc,
            description=description,
            image_filenames=image_filenames
        )
        if not update_id:
            # Defensive: should not happen if task exists, but return a clear error
            return jsonify({"error": "Failed to create update (internal)"}), 500
        # Persist expenditure in updates_db
        if expenditure is not None:
            updates_col.update_one({"id": update_id}, {"$set": {"expenditure": expenditure}})

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

# FIXED: Add task update deletion endpoint
@app.route('/tasks/updates/<update_id>', methods=['DELETE'])
@jwt_required()
def delete_task_update(update_id):
    """Delete a task update"""
    try:
        # Find the update
        update = updates_col.find_one({"id": update_id})
        if not update:
            return jsonify({"error": "Update not found"}), 404
            
        # Find the associated task
        task = tasks_col.find_one({"id": update['task_id']})
        if not task:
            return jsonify({"error": "Associated task not found"}), 404
            
        # Remove update from task's updates list
        tasks_col.update_one(
            {"id": task['id']},
            {"$pull": {"updates": update_id}}
        )
        
        # Update task's latest_status to previous update or 0
        remaining_updates = [uid for uid in task['updates'] if uid != update_id]
        if remaining_updates:
            # Get the most recent remaining update
            latest_update = updates_col.find_one(
                {"id": {"$in": remaining_updates}},
                sort=[("timestamp", -1)]
            )
            latest_status = latest_update['status_percentage'] if latest_update else 0
        else:
            latest_status = 0
            
        tasks_col.update_one(
            {"id": task['id']},
            {"$set": {"latest_status": latest_status}}
        )
        
        # Delete the update
        updates_col.delete_one({"id": update_id})
        
        return jsonify({"message": "Task update deleted successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/views/timetable', methods=['POST'])
@jwt_required()  # FIXED: Add JWT protection
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
@jwt_required()  # FIXED: Add JWT protection  
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
@jwt_required()  # FIXED: Add JWT protection
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
@jwt_required()  # FIXED: Add JWT protection
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
            dep_proj = projects_col.find_one({"id": dep})
            if dep_proj and dep_proj.get('state') != 'complete':
                return jsonify({"project": proj['name'], "state": "delayed"}), 200
        # Evaluate task states
        tasks = get_project_tasks(proj['id'])
        states = [get_task_state(t['id'], now) for t in tasks]
        if not states or all(s == 'tentative' for s in states):
            st = 'tentative'
        elif all(s == 'complete' for s in states):
            st = 'complete'
        elif now > max(t['start_time'] + timedelta(minutes=t.get('expected_duration', 0)) for t in tasks):
            st = 'overdue'
        else:
            st = 'active'
        projects_col.update_one({"id": proj['id']}, {"$set": {"state": st}})
        return jsonify({"project": proj['name'], "state": st}), 200

    else:
        return jsonify({"error": "type must be 'task' or 'project'"}), 400

# New endpoint to mark task status
@app.route('/tasks/mark-as', methods=['POST'])
@jwt_required()  # FIXED: Add JWT protection
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
        update_doc = updates_col.find_one({"id": update_id})
        ts = update_doc['timestamp'].isoformat()
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
        update_doc = updates_col.find_one({"id": update_id})
        ts = update_doc['timestamp'].isoformat()
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
        update_doc = updates_col.find_one({"id": update_id})
        ts = update_doc['timestamp'].isoformat()
        return jsonify({
            "message": f"Task marked as {state}. Call /tasks/postpone-to to set new schedule",
            "task": task,
            "timestamp": ts
        }), 200

@app.route('/tasks/postpone-to', methods=['POST'])
@jwt_required()  # FIXED: Add JWT protection
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
            projects = list(projects_col.find({"company_name": {"$regex": f"^{company_name}$", "$options": "i"}}))
            
            if not projects:
                return jsonify({"error": "No projects found for company"}), 404
            
            for project in projects:
                # Calculate time delta
                delta = new_start - project['start_date']
                projects_col.update_one({"id": project['id']}, {"$set": {"start_date": new_start}})
                
                # Update all tasks in project
                tasks_col.update_many(
                    {"project_id": project['id']},
                    {"$inc": {"start_time": delta.total_seconds() * 1000}}  # MongoDB date math
                )
            
            # Log each project's postponement
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
            projects_col.update_one({"id": project['id']}, {"$set": {"start_date": new_start}})
            
            # Update all tasks in project
            for task_id in project['tasks']:
                task = tasks_col.find_one({"id": task_id})
                if task:
                    new_task_start = task['start_time'] + delta
                    tasks_col.update_one({"id": task_id}, {"$set": {"start_time": new_task_start}})
            
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
        
        tasks_col.update_one(
            {"id": task['id']},
            {"$set": {
                "start_time": new_start,
                "duration": new_duration_min,
                "postponed": False
            }}
        )
        
        # Log as a task update
        update_id = create_task_update(
            task_id=task['id'],
            status_percentage=get_latest_progress(task['id']),
            description=f"Task postponed to {new_start.isoformat()}"
        )
        update_doc = updates_col.find_one({"id": update_id})
        ts = update_doc['timestamp'].isoformat()
        return jsonify({
            "message": "Task postponed",
            "task": task,
            "new_start_time": new_start.isoformat(),
            "timestamp": ts
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/tasks/priority', methods=['POST'])
@jwt_required()  # FIXED: Add JWT protection
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
@jwt_required()  # FIXED: Add JWT protection
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
@jwt_required()  # FIXED: Add JWT protection
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)