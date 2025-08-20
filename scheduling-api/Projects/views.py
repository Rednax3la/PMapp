# scheduling-api/Projects/views.py
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import re
import pytz
from createandget import create_project, create_project_update, create_task, get_project_by_company_and_name
from createandget import get_project_tasks, get_task_state, get_task_by_name
from helpers import format_duration
from db import projects_col, tasks_col, updates_col, project_updates_col

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')

@projects_bp.route('/view', methods=['POST'])
def view_projects():
    data = request.json or {}
    company = data.get('company_name')
    if not company:
        return jsonify({"error": "company_name is required"}), 400

    company_filter = {"company_name": {"$regex": f"^{re.escape(company)}$", "$options": "i"}}

    results = []
    for proj in projects_col.find(company_filter):
        # Prefer explicit 'id' if you set it; else fall back to Mongo _id
        proj_id = proj.get('id') or (str(proj.get('_id')) if proj.get('_id') is not None else None)

        # Fetch tasks via helper (Mongo-backed), then compute aggregates locally
        tasks = get_project_tasks(proj_id) or []

        # Map task id -> name for dependency name resolution
        id_to_name = {t.get('id'): t.get('name') for t in tasks if t}

        total_cost = sum((t or {}).get('estimated_cost', 0) for t in tasks)

        # Safe datetime -> ISO8601
        start_date_val = proj.get('start_date')
        if isinstance(start_date_val, datetime):
            start_date_iso = start_date_val.isoformat()
        else:
            start_date_iso = start_date_val if start_date_val is None else str(start_date_val)

        proj_info = {
            "id": proj_id,
            "name": proj.get('name'),
            "start_date": start_date_iso,
            "project_type": proj.get('project_type', 'scheduled'),
            "objectives": proj.get('objectives', []),
            "expected_duration": proj.get('expected_duration'),
            **({"duration": format_duration(proj['duration'])} if proj.get('duration') else {}),
            "total_estimated_cost": total_cost,
            "state": proj.get('state'),
            "team": proj.get('team', []),
            "tasks": []
        }

        for t in tasks:
            if not t:
                continue
            # Safe datetime -> ISO8601
            st_val = t.get('start_time')
            if isinstance(st_val, datetime):
                st_iso = st_val.isoformat()
            else:
                st_iso = st_val if st_val is None else str(st_val)

            # Convert dependency ids -> names when possible
            dep_names = [id_to_name.get(dep, dep) for dep in (t.get('dependencies', []) or [])]

            task_entry = {
                "id": t.get('id'),
                "name": t.get('name'),
                "start_time": st_iso,
                # Keep previous key; tolerate either precomputed string or minutes value
                "expected_duration": t.get('duration_str', t.get('expected_duration')),
                # Previously duration was included only when a 100% update existed; here we include it if present
                **({"duration": format_duration(t['duration'])} if t.get('duration') else {}),
                "estimated_cost": t.get('estimated_cost', 0),
                "members": t.get('members', []),
                "dependencies": dep_names,
                "state": t.get('state')
            }
            proj_info['tasks'].append(task_entry)

        results.append(proj_info)

    return jsonify({"projects": results}), 200

@projects_bp.route('/latest_updates', methods=['POST'])
def latest_updates():
    data = request.json or {}
    company = data.get('company_name')
    if not company:
        return jsonify({"error": "company_name is required"}), 400

    # Filter projects
    proj_name = data.get('project_name')
    matching = [
        p for p in projects_col.find()
        if p.get('company_name', '').lower() == company.lower()
           and (not proj_name or p['name'].lower() == proj_name.lower())
    ]
    if proj_name and not matching:
        return jsonify({"error": "Project not found"}), 404

    proj_ids = {p['id'] for p in matching}

    # Collect latest update *per task*
    latest_by_task = {}
    for upd in updates_col.values():
        tid = upd['task_id']
        if tid in proj_ids:
            existing = latest_by_task.get(tid)
            if not existing or upd['timestamp'] > existing['timestamp']:
                latest_by_task[tid] = upd

    # Build the response list
    entries = []
    for upd in latest_by_task.values():
        task = tasks_col[upd['task_id']]
        proj = next(p for p in matching if p['id'] == task['project_id'])
        entries.append({
            "type": "task_update",
            "project_name": proj['name'],
            "task_name": task['name'],
            "description": upd['description'],
            "status_percentage": upd['status_percentage'],
            "timestamp": upd['timestamp'].isoformat()
        })

    # Include any project-level updates, too
    for pud in project_updates_col.values():
        if pud['project_id'] in proj_ids:
            proj = next(p for p in matching if p['id'] == pud['project_id'])
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
def split_project():
    data = request.json or {}
    company = data.get('company_name')
    original = data.get('project_name')
    splits = data.get('splits', [])  # list of {'name':..., 'tasks':[...]}
    if not company or not original or len(splits) != 2:
        return jsonify({'error':'company_name, project_name and two splits required'}),400
    proj = get_project_by_company_and_name(company, original)
    if not proj:
        return jsonify({'error':'Project not found'}),404
    new_ids = []
    for i, part in enumerate(splits, start=1):
        name = part.get('name') or f"{original}({i})"
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
            for t in get_project_tasks(proj['id']):
                if t['name']==tname:
                    t['project_id']=new['id']
                    new['tasks'].append(t['id'])
                    break
        create_project_update(new['id'], f"Project split from {original}")
    return jsonify({'new_projects':new_ids}),200

@projects_bp.route('/merge', methods=['POST'])
def merge_projects():
    data = request.json or {}
    company = data.get('company_name')
    names = data.get('project_names', [])  # list
    new_name = data.get('new_name') or f"{names[0]}-{names[1]}"
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
        for tid in p['tasks']:
            t=tasks_col[tid]
            t['project_id']=merged['id']
            merged['tasks'].append(tid)
    create_project_update(merged['id'], f"Merged {names}")
    return jsonify({'merged_project':{'id':merged['id'],'name':merged['name']}}),200

@projects_bp.route('/clone', methods=['POST'])
def clone_project():
    data = request.json or {}
    company = data.get('company_name')
    original = data.get('project_name')
    new_name = data.get('new_name') or f"{original}(copy)"
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
    for t in get_project_tasks(proj['id']):
        newt=create_task(
            project_id=cloned['id'],
            name=t['name'],
            start_time=t['start_time'],
            duration=t['duration'],
            priority=t['priority'],
            members=t['members'],
            description=t.get('description'),
            dependencies=[]
        )
        old_to_new[t['id']]=newt['id']
    # fix dependencies
    for old, new in old_to_new.items():
        for dep in tasks_col[new]['dependencies']:
            tasks_col[new]['dependencies']=[old_to_new.get(d) for d in dep]
    create_project_update(cloned['id'], f"Cloned from {original}")
    return jsonify({'cloned_project':{'id':cloned['id'],'name':cloned['name']}}),200

@projects_bp.route('/states', methods=['POST'])
def project_states():
    data = request.json or {}
    company = data.get('company_name')
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
    for proj in projects_col.values():
        if proj.get('company_name', '').lower() != company.lower():
            continue

        # Handle project-level dependencies
        deps = proj.get('dependencies', [])  # list of project IDs
        if deps:
            for dep_id in deps:
                dep_proj = projects_col.get(dep_id)
                if dep_proj:
                    # if dependent project not complete
                    if dep_proj.get('state') != 'complete':
                        results.append({
                            'project_id': proj['id'],
                            'project_name': proj['name'],
                            'state': 'delayed'
                        })
                        break
            else:
                delayed = False
        else:
            delayed = False

        # Skip further checks if delayed
        if deps and any(
            projects_col.get(d, {}).get('state') != 'complete'
            for d in deps
        ): continue

        # Compute task states
        tasks = get_project_tasks(proj['id'])
        states = [get_task_state(t['id'], now) for t in tasks]
        # Determine project state
        if all(s == 'tentative' for s in states):
            state = 'tentative'
        elif all(s == 'complete' for s in states) and states:
            state = 'complete'
        elif now > max(
            (t['start_time'] + timedelta(minutes=t.get('expected_duration', 0)))
            for t in tasks
        ):
            state = 'overdue'
        else:
            state = 'active'

        # Save and append
        proj['state'] = state
        results.append({
            'project_id': proj['id'],
            'project_name': proj['name'],
            'state': state
        })

    return jsonify({'projects': results}), 200

@projects_bp.route('/restore', methods=['POST'])
def restore():
    data = request.json or {}
    company = data.get('company_name')
    proj_name = data.get('project_name')
    task_name = data.get('task_name')
    if not company or not proj_name:
        return jsonify({"error": "company_name and project_name required"}), 400

    proj = get_project_by_company_and_name(company, proj_name)
    if not proj:
        return jsonify({"error": "Project not found"}), 404

    # Restore project
    if not task_name:
        prev_state = proj.get('state')
        proj['state'] = 'active'
        # restore all tasks to in progress if they were complete
        for tid in proj.get('tasks', []):
            task = tasks_col.get(tid)
            if task and get_task_state(tid) == 'complete':
                # create a zero-percent update to shift state
                uid = create_project_update(proj['id'], f"Restore project, task {task['name']} to in progress")
                task_state = get_task_state(tid)
                task_updates = task.get('updates', [])
                # no change to actual progress but re-open
                # no direct db change; UI can interpret new project state
        create_project_update(proj['id'], f"Project '{proj_name}' restored from {prev_state}")
        return jsonify({
            "message": f"Project '{proj_name}' restored",
            "project": {
                "id": proj['id'],
                "name": proj['name'],
                "state": proj['state']
            }
        }), 200

    # Restore specific task
    task = get_task_by_name(proj['id'], task_name)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    # only restore if complete
    if get_task_state(task['id']) != 'complete':
        return jsonify({"error": "Task is not complete and cannot be restored"}), 400

    # Create a project_update log
    create_project_update(proj['id'], f"Restore task '{task_name}' to in progress")
    # Remove final completion update so state reverts
    last_upd = task.get('updates', [])[-1]
    if updates_col.get(last_upd, {}).get('status_percentage') == 100:
        # mark it as in progress by adding a new update with same percent
        uid = create_project_update(proj['id'], f"Task '{task_name}' restored to in progress")
    task['postponed'] = False
    return jsonify({
        "message": f"Task '{task_name}' in project '{proj_name}' restored",
        "task": {
            "id": task['id'],
            "name": task['name'],
            "state": 'in progress'
        }
    }), 200

@projects_bp.route('/add_objective', methods=['POST'])
def add_objective():    
    data = request.json or {}
    company = data.get('company_name')
    proj_name = data.get('project_name')
    objective = data.get('objective')
    if not company or not proj_name or not objective:
        return jsonify({"error": "company_name, project_name and objective required"}), 400

    proj = get_project_by_company_and_name(company, proj_name)
    if not proj:
        return jsonify({"error": "Project not found"}), 404

    # Ensure objectives list exists
    if 'objectives' not in proj:
        proj['objectives'] = []
    
    proj['objectives'].append(objective)
    create_project_update(proj['id'], f"Objective added: {objective}")
    return jsonify({"message": "Objective added", "project": proj}), 200

@projects_bp.route('/add_users', methods=['POST'])
def add_users():
    data = request.json or {}
    company = data.get('company_name')
    proj_name = data.get('project_name')
    users = data.get('users', [])
    if not company or not proj_name or not isinstance(users, list):
        return jsonify({"error": "company_name, project_name, and users list required"}), 400
    proj = get_project_by_company_and_name(company, proj_name)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    team = set(proj.get('team', []))
    team.update(users)
    proj['team'] = list(team)
    return jsonify({
        "message": f"Users added to project '{proj_name}'",
        "team": proj['team']
    }), 200

@projects_bp.route('/allocate_roles', methods=['POST'])
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

@projects_bp.route('/remove_allocation', methods=['POST'])
def remove_allocation():
    data = request.json or {}
    company = data.get('company_name')
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
    ra = proj.get('role_allocations', {})
    allocs = ra.get(task['id'], [])
    new_allocs = [a for a in allocs if a['member'] != member]
    ra[task['id']] = new_allocs
    return jsonify({"message": f"Allocation removed for {member}", "allocations": new_allocs}), 200

@projects_bp.route('/change_allocation', methods=['POST'])
def change_allocation():
    data = request.json or {}
    company = data.get('company_name')
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
    ra = proj.get('role_allocations', {})
    allocs = ra.get(task['id'], [])
    for a in allocs:
        if a['member'] == member:
            a['duty'] = duty
            break
    else:
        return jsonify({"error": "Allocation not found for member"}), 404
    return jsonify({"message": f"Allocation updated for {member}", "allocations": allocs}), 200

@projects_bp.route('/allocate_funds', methods=['POST'])
def allocate_funds():
    data = request.json or {}
    company = data.get('company_name')
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
    fa = proj.setdefault('fund_allocations', [])
    entry = {"amount": amount, "member": member, "task_name": task_name}
    fa.append(entry)
    return jsonify({"message": "Funds allocated", "fund_allocations": fa}), 200


@projects_bp.route('/create_team', methods=['POST'])
def create_team():
    data = request.json or {}
    company = data.get('company_name')
    proj_name = data.get('project_name')

    members = data.get('team', data.get('members', []))
    if not company or not proj_name or not isinstance(members, list):
        return jsonify({"error": "company_name, project_name, and team list required"}), 400
    proj = get_project_by_company_and_name(company, proj_name)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    # validate and normalize emails
    cleaned = []
    invalid = []
    from auth_helpers import is_valid_email, normalize_email
    for m in members:
        norm = normalize_email(m)
        if not is_valid_email(norm):
            invalid.append(m)
        else:
            cleaned.append(norm)
    if invalid:
        return jsonify({"error": "Invalid member emails", "invalid": invalid}), 422
    proj['team'] = list(dict.fromkeys(cleaned))  # unique, preserve order
    return jsonify({
        "message": f"Team set for project '{proj_name}'",
        "team": proj['team']
    }), 200