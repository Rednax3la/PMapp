# scheduling-api/Projects/views.py
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import re
import pytz
from createandget import _now, create_project, create_project_update, create_task, generate_unique_id, get_project_by_company_and_name
from createandget import get_project_tasks, get_task_state, get_task_by_name
from helpers import format_duration
from db import projects_col, tasks_col, updates_col, project_updates_col, teams_col
from flask_jwt_extended import jwt_required, get_jwt

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')

@projects_bp.route('/view', methods=['POST'])
@jwt_required()  # FIXED: Add JWT protection
def view_projects():
    data = request.json or {}
    claims = get_jwt()
    company = claims.get('company_name')  # FIXED: Get company from JWT claims
    
    if not company:
        return jsonify({"error": "company_name is required"}), 400

    company_filter = {"company_name": {"$regex": f"^{re.escape(company)}$", "$options": "i"}}

    results = []
    projects_cursor = projects_col.find(company_filter)
    
    for proj in projects_cursor:
        # Prefer explicit 'id' if you set it; else fall back to Mongo _id
        proj_id = proj.get('id') or (str(proj.get('_id')) if proj.get('_id') is not None else None)

        # Fetch tasks via helper (Mongo-backed), then compute aggregates locally
        tasks = get_project_tasks(proj_id) or []

        # Map task id -> name for dependency name resolution
        id_to_name = {t.get('id'): t.get('name') for t in tasks if t}

        total_cost = sum((t or {}).get('estimated_cost', 0) for t in tasks)

        # FIXED: Safe datetime -> ISO8601 conversion
        start_date_val = proj.get('start_date')
        if isinstance(start_date_val, datetime):
            # Ensure timezone awareness
            if start_date_val.tzinfo is None:
                timezone_str = proj.get('timezone', 'Africa/Nairobi')
                tz = pytz.timezone(timezone_str)
                start_date_val = tz.localize(start_date_val)
            start_date_iso = start_date_val.isoformat()
        else:
            start_date_iso = start_date_val if start_date_val is None else str(start_date_val)

        # FIXED: Calculate project state based on task states
        task_states = [get_task_state(t['id']) for t in tasks if t.get('id')]
        if not task_states:
            project_state = 'tentative'
        elif all(state == 'complete' for state in task_states):
            project_state = 'complete'
        elif any(state in ['active', 'in progress'] for state in task_states):
            project_state = 'active'
        elif any(state == 'overdue' for state in task_states):
            project_state = 'overdue'
        else:
            project_state = 'tentative'

        proj_info = {
            "id": proj_id,
            "name": proj.get('name'),
            "start_date": start_date_iso,
            "project_type": proj.get('project_type', 'scheduled'),
            "objectives": proj.get('objectives', []),
            "expected_duration": proj.get('expected_duration'),
            **({"duration": format_duration(proj['duration'])} if proj.get('duration') else {}),
            "total_estimated_cost": total_cost,
            "state": project_state,  # FIXED: Use calculated state
            "team": proj.get('team', []),
            "timezone": proj.get('timezone', 'Africa/Nairobi'),  # FIXED: Include timezone
            "task_count": len(tasks),  # FIXED: Add task count
            "completed_tasks": len([t for t in tasks if get_task_state(t['id']) == 'complete']),  # FIXED: Add completed task count
            "tasks": []
        }

        for t in tasks:
            if not t:
                continue
                
            # FIXED: Safe datetime -> ISO8601 conversion for tasks
            st_val = t.get('start_time')
            if isinstance(st_val, datetime):
                if st_val.tzinfo is None:
                    timezone_str = proj.get('timezone', 'Africa/Nairobi')
                    tz = pytz.timezone(timezone_str)
                    st_val = tz.localize(st_val)
                st_iso = st_val.isoformat()
            else:
                st_iso = st_val if st_val is None else str(st_val)

            # Convert dependency ids -> names when possible
            dep_names = [id_to_name.get(dep, dep) for dep in (t.get('dependencies', []) or [])]

            task_entry = {
                "id": t.get('id'),
                "name": t.get('name'),
                "start_time": st_iso,
                "expected_duration": format_duration(t.get('expected_duration', 0)),  # Keep formatted string for display
                "expected_duration_minutes": t.get('expected_duration', 0),  # NEW: Raw minutes for calculations
                **({"actual_duration": format_duration(t['duration'])} if t.get('duration', 0) > 0 else {}),
                **({"actual_duration_minutes": t.get('duration', 0)} if t.get('duration', 0) > 0 else {}),  # NEW: If actual exists
                "estimated_cost": t.get('estimated_cost', 0),
                "members": t.get('members', []),
                "dependencies": dep_names,
                "status": get_task_state(t['id']),  # CHANGED: Rename from "state" to "status" for frontend consistency
                "priority": t.get('priority', 'medium'),
                "progress": t.get('latest_status', 0)  # Already good
            }
            proj_info['tasks'].append(task_entry)

        results.append(proj_info)

    return jsonify({"projects": results}), 200

@projects_bp.route('/latest_updates', methods=['POST'])
@jwt_required()  # FIXED: Add JWT protection
def latest_updates():
    data = request.json or {}
    claims = get_jwt()
    company = claims.get('company_name')  # FIXED: Get company from JWT claims
    
    if not company:
        return jsonify({"error": "company_name is required"}), 400

    # Filter projects
    proj_name = data.get('project_name')
    matching = list(projects_col.find({
        "company_name": {"$regex": f"^{re.escape(company)}$", "$options": "i"},
        **({"name": {"$regex": f"^{re.escape(proj_name)}$", "$options": "i"}} if proj_name else {})
    }))
    
    if proj_name and not matching:
        return jsonify({"error": "Project not found"}), 404

    proj_ids = [p['id'] for p in matching]

    # Collect latest update *per task*
    latest_by_task = {}
    updates_cursor = updates_col.find({"task_id": {"$in": proj_ids}}).sort("timestamp", -1)
    
    for upd in updates_cursor:
        tid = upd['task_id']
        if tid not in latest_by_task:  # Only keep the latest (first due to sort)
            latest_by_task[tid] = upd

    # Build the response list
    entries = []
    for upd in latest_by_task.values():
        task = tasks_col.find_one({"id": upd['task_id']})
        if not task:
            continue
            
        proj = next((p for p in matching if p['id'] == task['project_id']), None)
        if not proj:
            continue
            
        entries.append({
            "type": "task_update",
            "project_name": proj['name'],
            "task_name": task['name'],
            "description": upd['description'],
            "status_percentage": upd['status_percentage'],
            "timestamp": upd['timestamp'].isoformat()
        })

    # Include any project-level updates, too
    project_updates_cursor = project_updates_col.find({"project_id": {"$in": proj_ids}})
    for pud in project_updates_cursor:
        proj = next((p for p in matching if p['id'] == pud['project_id']), None)
        if proj:
            entries.append({
                "type": "project_update",
                "project_name": proj['name'],
                "description": pud['description'],
                "timestamp": pud['timestamp'].isoformat()
            })

    # Newest first
    entries.sort(key=lambda e: e['timestamp'], reverse=True)
    return jsonify({"updates": entries}), 200

@projects_bp.route('/split', methods=['POST'])
@jwt_required()  # FIXED: Add JWT protection
def split_project():
    data = request.json or {}
    claims = get_jwt()
    company = claims.get('company_name')
    original = data.get('project_name')
    splits = data.get('splits', [])  # list of {'name':..., 'tasks':[...]}
    split_team = bool(data.get('split_team', False))
    delete_original = bool(data.get('delete_original', True))
    if not company or not original or not splits:
        return jsonify({'error':'company_name, project_name and splits required'}),400
    proj = get_project_by_company_and_name(company, original)
    if not proj:
        return jsonify({'error':'Project not found'}),404
    new_ids = []
    for i, part in enumerate(splits, start=1):
        name = part.get('name') or f"{original}_{i}"
        new = create_project(
            name=name,
            start_date=proj['start_date'],
            company_name=company,
            timezone=proj.get('timezone'),
            project_type=proj.get('project_type'),
        )
        new_ids.append({'id':new['id'],'name':new['name']})
        # move tasks
        for tname in part.get('tasks',[]):
            task = get_task_by_name(proj['id'], tname)
            if task:
                tasks_col.update_one({"id": task['id']}, {"$set": {"project_id": new['id']}})
                projects_col.update_one({"id": new['id']}, {"$push": {"tasks": task['id']}})
                projects_col.update_one({"id": proj['id']}, {"$pull": {"tasks": task['id']}})
        create_project_update(new['id'], f"Project split from {original}")
        if split_team:
            try:
                teams_col.insert_one({
                    "company_name": company,
                    "project_name": new['name'],
                    "members": [], 
                    "created_at": _now()
                })
            except Exception:
                pass
    if delete_original:
        projects_col.delete_one({"id": proj['id']})
        try:
            teams_col.delete_one({"project_name": original, "company_name": company})
        except Exception:
            pass
    return jsonify({'new_projects':new_ids}),200

@projects_bp.route('/merge', methods=['POST'])
@jwt_required()  # FIXED: Add JWT protection  
def merge_projects():
    data = request.json or {}
    claims = get_jwt()
    company = claims.get('company_name')
    names = data.get('project_names', [])  # list
    new_name = data.get('new_name') or f"{names[0]}-{names[1]}"
    delete_sources = bool(data.get('delete_sources', True))
    merge_teams = bool(data.get('merge_teams', True))
    if not company or len(names)<2:
        return jsonify({'error':'company_name and at least two project_names required'}),400
    projs=[get_project_by_company_and_name(company,n) for n in names]
    if not all(projs):
        return jsonify({'error':'One or more projects not found'}),404
    # choose earliest start and compounded type
    start=min(p['start_date'] for p in projs)
    ptype='documented' if any(p.get('project_type')=='documented' for p in projs) else 'scheduled'
    merged=create_project(new_name, start, company, projs[0].get('timezone'), ptype)
    for p in projs:
        for tid in p.get('tasks', []):
            tasks_col.update_one({"id": tid}, {"$set": {"project_id": merged['id']}})
            projects_col.update_one({"id": merged['id']}, {"$push": {"tasks": tid}})
        if merge_teams:
            # Merge team arrays into merged project (unique)
            source_team = p.get('team', [])
            if source_team:
                projects_col.update_one(
                    {"id": merged['id']},
                    {"$addToSet": {"team": {"$each": source_team}}}
                )
        if delete_sources:
            projects_col.delete_one({"id": p['id']})
            try:
                teams_col.delete_one({"project_name": p['name'], "company_name": company})
            except Exception:
                pass
    create_project_update(merged['id'], f"Merged {names}")
    return jsonify({'merged_project':{'id':merged['id'],'name':merged['name']}}),200

@projects_bp.route('/clone', methods=['POST'])
@jwt_required()  # FIXED: Add JWT protection
def clone_project():
    data = request.json or {}
    claims = get_jwt()
    company = claims.get('company_name')
    original = data.get('project_name') or data.get('proj_name') or data.get('original')
    raw_new = data.get('new_name')
    if raw_new:
        new_name = raw_new
    else:
        base = re.sub(r"[()]", "", original or "")
        base = base.strip()
        base = base if base else f"clone_{generate_unique_id()}"
        new_name = f"{base}.c"
    if not company or not original:
        return jsonify({'error':'company_name and project_name required'}),400
    proj=get_project_by_company_and_name(company,original)
    if not proj:
        return jsonify({'error':'Project not found'}),404
    cloned=create_project(
        name=new_name,
        start_date=proj['start_date'],
        company_name=company,
        timezone=proj.get('timezone'),
        project_type=proj.get('project_type')
    )
    old_to_new={}
    # clone tasks
    tasks = get_project_tasks(proj['id'])
    for t in tasks:
        newt=create_task(
            project_id=cloned['id'],
            name=t['name'],
            start_time=t['start_time'],
            expected_duration=t.get('expected_duration', 0),
            priority=t.get('priority', 'medium'),
            members=t.get('members', []),
            description=t.get('description'),
            dependencies=[]
        )
        old_to_new[t['id']]=newt['id']
    # fix dependencies
    for old_id, new_id in old_to_new.items():
        old_task = tasks_col.find_one({"id": old_id})
        new_deps = [old_to_new.get(d, d) for d in old_task.get('dependencies', [])]
        tasks_col.update_one({"id": new_id}, {"$set": {"dependencies": new_deps}})
    create_project_update(cloned['id'], f"Cloned from {original}")
    return jsonify({'cloned_project':{'id':cloned['id'],'name':cloned['name']}}),200

@projects_bp.route('/states', methods=['POST'])
@jwt_required()  # FIXED: Add JWT protection
def project_states():
    data = request.json or {}
    claims = get_jwt()
    company = claims.get('company_name')
    
    if not company:
        return jsonify({"error": "company_name is required"}), 400

    time_str = data.get('time')
    now = datetime.now(pytz.UTC)
    if time_str:
        try:
            now = datetime.fromisoformat(time_str)
            if now.tzinfo is None:
                now = pytz.UTC.localize(now)
        except ValueError:
            return jsonify({"error": "Invalid time format, use ISO8601"}), 400

    results = []
    projects_cursor = projects_col.find({"company_name": {"$regex": f"^{re.escape(company)}$", "$options": "i"}})
    
    for proj in projects_cursor:
        # Handle project-level dependencies
        deps = proj.get('dependencies', [])  # list of project IDs
        delayed = False
        
        if deps:
            for dep_id in deps:
                dep_proj = projects_col.find_one({"id": dep_id})
                if dep_proj and dep_proj.get('state') != 'complete':
                    delayed = True
                    break

        if delayed:
            state = 'delayed'
        else:
            # Compute task states
            tasks = get_project_tasks(proj['id'])
            if not tasks:
                state = 'tentative'
            else:
                states = [get_task_state(t['id'], now) for t in tasks]
                # Determine project state
                if all(s == 'tentative' for s in states):
                    state = 'tentative'
                elif all(s == 'complete' for s in states):
                    state = 'complete'
                elif now > max(
                    (t['start_time'] + timedelta(minutes=t.get('expected_duration', 0)))
                    for t in tasks
                ):
                    state = 'overdue'
                else:
                    state = 'active'

        # Save and append
        projects_col.update_one({"id": proj['id']}, {"$set": {"state": state}})
        results.append({
            'project_id': proj['id'],
            'project_name': proj['name'],
            'state': state
        })

    return jsonify({'projects': results}), 200

@projects_bp.route('/restore', methods=['POST'])
@jwt_required()  # FIXED: Add JWT protection
def restore():
    data = request.json or {}
    claims = get_jwt()
    company = claims.get('company_name')
    proj_name = data.get('project_name')
    task_name = data.get('task_name')
    if not company or not proj_name:
        return jsonify({"error": "company_name and project_name required"}), 400

    proj = get_project_by_company_and_name(company, proj_name)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    task = get_task_by_name(proj['id'], task_name)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    if not task_name:
        prev_state = proj.get('state')
        projects_col.update_one({"id": proj['id']}, {"$set": {"state": "active"}})
        
        # restore all tasks to in progress if they were complete
        for tid in proj.get('tasks', []):
            task = tasks_col.find_one({"id": tid})
            if task and get_task_state(tid) == 'complete':
                # Reset task status by updating latest_status
                tasks_col.update_one({"id": tid}, {"$set": {"latest_status": 90, "postponed": False}})
                
        create_project_update(proj['id'], f"Project '{proj_name}' restored from {prev_state}")
        return jsonify({
            "message": f"Project '{proj_name}' restored",
            "project": {
                "id": proj['id'],
                "name": proj['name'],
                "state": "active"
            }
        }), 200

    # Restore specific task
    task = get_task_by_name(proj['id'], task_name)
    if not task:
        return jsonify({"error": "Task not found"}), 404
        
    # only restore if complete
    if get_task_state(task['id']) != 'complete':
        return jsonify({"error": "Task is not complete and cannot be restored"}), 400

    # Create a project_update log and reset task
    create_project_update(proj['id'], f"Restore task '{task_name}' to in progress")
    tasks_col.update_one({"id": task['id']}, {"$set": {"latest_status": 90, "postponed": False}})
    
    return jsonify({
        "message": f"Task '{task_name}' in project '{proj_name}' restored",
        "task": {
            "id": task['id'],
            "name": task['name'],
            "state": 'in progress'
        }
    }), 200

@projects_bp.route('/remove_allocation', methods=['POST'])
@jwt_required()  # FIXED: Add JWT protection
def remove_allocation():
    data = request.json or {}
    claims = get_jwt()
    company = claims.get('company_name')
    proj_name = data.get('project_name')
    task_name = data.get('task_name')
    member = data.get('member')
    if not all([company, proj_name, task_name, member]):
        return jsonify({"error": "company_name, project_name, task_name, and member are required"}), 400
    proj = get_project_by_company_and_name(company, proj_name)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    task = get_task_by_name(proj['id'], task_name)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    role_allocations = proj.get('role_allocations', {})
    allocations = role_allocations.get(task['id'], [])
    new_allocations = [a for a in allocations if a['member'] != member]
    role_allocations[task['id']] = new_allocations
    projects_col.update_one({"id": proj['id']}, {"$set": {"role_allocations": role_allocations}})
    return jsonify({"message": f"Allocation removed for {member}", "allocations": new_allocations}), 200

@projects_bp.route('/change_allocation', methods=['POST'])
@jwt_required()  # FIXED: Add JWT protection
def change_allocation():
    data = request.json or {}
    claims = get_jwt()
    company = claims.get('company_name')
    proj_name = data.get('project_name')
    task_name = data.get('task_name')
    member = data.get('member')
    duty = data.get('duty')
    if not all([company, proj_name, task_name, member, duty is not None]):
        return jsonify({"error": "company_name, project_name, task_name, member, and duty are required"}), 400
    proj = get_project_by_company_and_name(company, proj_name)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    task = get_task_by_name(proj['id'], task_name)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    allocation_type = data.get('allocation_type', 'role')
    if allocation_type == 'role':
        role_allocations = proj.get('role_allocations', {})
        allocations = role_allocations.get(task['id'], [])
        for a in allocations:
            if a['member'] == member:
                a['duty'] = duty
                break
        else:
            # not found -> create a new allocation for this member
            allocations.append({"member": member, "duty": duty})
        role_allocations[task['id']] = allocations
        projects_col.update_one({"id": proj['id']}, {"$set": {"role_allocations": role_allocations}})
        return jsonify({"message": f"Role allocation updated for {member}", "allocations": allocations}), 200
    elif allocation_type == 'funds':
        amount = data.get('amount')
        if amount is None:
            return jsonify({"error": "amount is required for funds allocation"}), 400
        fund_allocations = proj.get('fund_allocations', [])
        fund_allocations.append({"member": member, "amount": amount, "task_name": task_name})
        projects_col.update_one({"id": proj['id']}, {"$set": {"fund_allocations": fund_allocations}})
        return jsonify({"message": f"Funds allocation updated for {member}", "fund_allocations": fund_allocations}), 200
    else:
        return jsonify({"error":"Unknown allocation_type; use 'role' or 'funds'"}), 400

@projects_bp.route('/allocate_funds', methods=['POST'])
@jwt_required()  # FIXED: Add JWT protection
def allocate_funds():
    data = request.json or {}
    claims = get_jwt()
    company = claims.get('company_name')
    proj_name = data.get('project_name')
    amount = data.get('amount')
    member = data.get('member')
    task_name = data.get('task_name')
    if not all([company, proj_name, amount is not None]) or (not member and not task_name):
        return jsonify({"error": "company_name, project_name, amount, and either member or task_name are required"}), 400
    proj = get_project_by_company_and_name(company, proj_name)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    # Initialize fund_allocations
    fund_allocations = proj.get('fund_allocations', [])
    entry = {"amount": amount, "member": member, "task_name": task_name}
    fund_allocations.append(entry)
    projects_col.update_one({"id": proj['id']}, {"$set": {"fund_allocations": fund_allocations}})
    return jsonify({"message": "Funds allocated", "fund_allocations": fund_allocations}), 200

@projects_bp.route('/create_team', methods=['POST'])
@jwt_required()  # FIXED: Add JWT protection
def create_team():
    data = request.json or {}
    claims = get_jwt()
    company = claims.get('company_name')
    # Accept both keys to match frontend/Postman payloads
    proj_name = data.get('proj_name') or data.get('project_name')

    # Members can be: ["a@x.com","b@y.com"] OR [{"email":"a@x.com","role":"lead"}, ...]
    member_inputs = data.get('team') or data.get('members') or []
    roles_input = data.get('roles')  # optional: {"a@x.com":"lead"} OR [{"email":"a@x.com","role":"lead"}]

    if not company or not proj_name or not isinstance(member_inputs, list):
        return jsonify({"error": "company_name, project_name/proj_name, and team list are required"}), 400

    proj = get_project_by_company_and_name(company, proj_name)
    if not proj:
        return jsonify({"error": "Project not found"}), 404

    from auth_helpers import is_valid_email, normalize_email

    # Normalize roles_input into a dict: email -> role
    roles_map = {}
    if isinstance(roles_input, dict):
        for k, v in roles_input.items():
            email = normalize_email(k)
            roles_map[email] = (v or "member")
    elif isinstance(roles_input, list):
        for item in roles_input:
            if isinstance(item, dict):
                email = normalize_email(item.get("email", ""))
                role = (item.get("role") or "member")
                if email:
                    roles_map[email] = role

    cleaned_emails = []
    invalid = []
    members_doc = []  # [{email, role}]

    for m in member_inputs:
        # Support string or {email, role}
        if isinstance(m, dict):
            raw_email = m.get("email", "")
            role = (m.get("role") or "member")
        else:
            raw_email = str(m)
            role = "member"

        email = normalize_email(raw_email)
        # role override from roles_map, if provided
        role = roles_map.get(email, role)

        if not is_valid_email(email):
            invalid.append(raw_email)
            continue

        cleaned_emails.append(email)
        members_doc.append({"email": email, "role": role or "member"})

    if invalid:
        return jsonify({"error": "Invalid member emails", "invalid": invalid}), 422

    # Deduplicate while preserving last role assignment
    dedup = {}
    for entry in members_doc:
        dedup[entry["email"]] = entry["role"] or "member"
    members_doc = [{"email": e, "role": r} for e, r in dedup.items()]
    unique_emails = list(dedup.keys())

    # Update project's plain email team list
    proj_team = set(proj.get('team', []))
    proj_team.update(unique_emails)
    projects_col.update_one({"id": proj['id']}, {"$set": {"team": list(proj_team)}})

    # Upsert full team document (with roles) in teams_col
    now_utc = datetime.utcnow()
    teams_col.update_one(
        {"company_name": company, "project_id": proj['id']},
        {
            "$set": {
                "company_name": company,
                "project_id": proj['id'],
                "project_name": proj_name,
                "members": members_doc,
                "updated_at": now_utc
            },
            "$setOnInsert": {"created_at": now_utc}
        },
        upsert=True
    )

    return jsonify({
        "message": f"Team set for project '{proj_name}'",
        "team": list(proj_team),
        "members_with_roles": members_doc
    }), 200

# FIXED: Add project deletion endpoint
@projects_bp.route('/<project_name>', methods=['DELETE'])
@jwt_required()
def delete_project(project_name):
    """Delete a project and all associated data"""
    try:
        claims = get_jwt()
        company = claims.get('company_name')
        
        # Find the project
        project = get_project_by_company_and_name(company, project_name)
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

# FIXED: Add team management endpoints
@projects_bp.route('/team/<project_name>', methods=['GET'])
@jwt_required()
def get_team_members(project_name):
    """Get all team members for a project"""
    try:
        claims = get_jwt()
        company = claims.get('company_name')
        
        project = get_project_by_company_and_name(company, project_name)
        if not project:
            return jsonify({"error": "Project not found"}), 404
            
        team_members = project.get('team', [])
        
        # Get member details and their roles from tasks
        member_details = []
        for member in team_members:
            # Count tasks assigned to this member
            member_tasks = list(tasks_col.find({
                "project_id": project['id'],
                "members": member
            }))
            
            member_info = {
                "email": member,
                "name": member.split('@')[0],  # Use email prefix as name
                "role": "Member",  # Default role
                "task_count": len(member_tasks),
                "completed_tasks": len([t for t in member_tasks if t.get('latest_status', 0) == 100])
            }
            member_details.append(member_info)
            
        return jsonify({
            "project_name": project_name,
            "team_members": member_details,
            "total_members": len(member_details)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@projects_bp.route('/team/<project_name>/add', methods=['POST'])
@jwt_required()
def add_team_member(project_name):
    """Add a new team member to a project"""
    try:
        claims = get_jwt()
        company = claims.get('company_name')
        data = request.json or {}
        
        email = data.get('email', '').strip().lower()
        role = data.get('role', 'Member')
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
            
        # Basic email validation
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({"error": "Invalid email format"}), 400
            
        project = get_project_by_company_and_name(company, project_name)
        if not project:
            return jsonify({"error": "Project not found"}), 404
            
        # Check if member already exists
        current_team = project.get('team', [])
        if email in current_team:
            return jsonify({"error": "Member already exists in team"}), 400
            
        # Add member to team
        current_team.append(email)
        projects_col.update_one(
            {"id": project['id']},
            {"$set": {"team": current_team}}
        )
        
        create_project_update(project['id'], f"Added team member: {email}")
        
        return jsonify({
            "message": f"Member {email} added successfully",
            "member": {
                "email": email,
                "name": email.split('@')[0],
                "role": role,
                "task_count": 0,
                "completed_tasks": 0
            }
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@projects_bp.route('/team/<project_name>/remove/<member_email>', methods=['DELETE'])
@jwt_required()
def remove_team_member(project_name, member_email):
    """Remove a team member from a project"""
    try:
        claims = get_jwt()
        company = claims.get('company_name')
        
        member_email = member_email.lower().strip()
        
        project = get_project_by_company_and_name(company, project_name)
        if not project:
            return jsonify({"error": "Project not found"}), 404
            
        # Check if member exists
        current_team = project.get('team', [])
        if member_email not in current_team:
            return jsonify({"error": "Member not found in team"}), 404
            
        # Remove member from team
        current_team.remove(member_email)
        projects_col.update_one(
            {"id": project['id']},
            {"$set": {"team": current_team}}
        )
        
        # Remove member from all tasks in this project
        tasks_col.update_many(
            {"project_id": project['id']},
            {"$pull": {"members": member_email}}
        )
        
        create_project_update(project['id'], f"Removed team member: {member_email}")
        
        return jsonify({"message": f"Member {member_email} removed successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Keep existing endpoints with JWT protection added...
@projects_bp.route('/add_objective', methods=['POST'])
@jwt_required()  # FIXED: Add JWT protection
def add_objective():    
    data = request.json or {}
    claims = get_jwt()
    company = claims.get('company_name')
    proj_name = data.get('project_name')
    objective = data.get('objective')
    if not company or not proj_name or not objective:
        return jsonify({"error": "company_name, project_name and objective required"}), 400

    proj = get_project_by_company_and_name(company, proj_name)
    if not proj:
        return jsonify({"error": "Project not found"}), 404

    # Ensure objectives list exists
    objectives = proj.get('objectives', [])
    objectives.append(objective)
    
    projects_col.update_one({"id": proj['id']}, {"$set": {"objectives": objectives}})
    create_project_update(proj['id'], f"Objective added: {objective}")
    return jsonify({"message": "Objective added", "objectives": objectives}), 200

@projects_bp.route('/add_users', methods=['POST'])
@jwt_required()  # FIXED: Add JWT protection
def add_users():
    data = request.json or {}
    claims = get_jwt()
    company = claims.get('company_name')
    proj_name = data.get('project_name')
    users = data.get('users', [])
    if not company or not proj_name or not isinstance(users, list):
        return jsonify({"error": "company_name, project_name, and users list required"}), 400
    proj = get_project_by_company_and_name(company, proj_name)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    team = set(proj.get('team', []))
    team.update(users)
    projects_col.update_one({"id": proj['id']}, {"$set": {"team": list(team)}})
    return jsonify({
        "message": f"Users added to project '{proj_name}'",
        "team": list(team)
    }), 200

@projects_bp.route('/allocate_roles', methods=['POST'])
@jwt_required()  # FIXED: Add JWT protection
def allocate_roles():
    data = request.json or {}
    company = data.get('company_name')
    proj_name = data.get('project_name')
    task_name = data.get('task_name')
    member = data.get('member')
    duty = data.get('duty', '')
    if not all([company, proj_name, task_name, member]):
        return jsonify({"error": "company_name, project_name, task_name, and member are required"}), 400
    proj = get_project_by_company_and_name(company, proj_name)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    task = get_task_by_name(proj['id'], task_name)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    # Initialize role_allocations structure
    ra = proj.setdefault('role_allocations', {})
    allocations = ra.setdefault(task['id'], [])
    allocations.append({"member": member, "duty": duty})
    return jsonify({"message": f"Role allocated to {member} on {task_name}", "allocations": allocations}), 200
