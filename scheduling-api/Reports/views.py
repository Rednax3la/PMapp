"""
Reports Blueprint — summary stats, per-project analytics, and CSV export.
"""
import csv
import io
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt

from db import projects_col, tasks_col, updates_col
from createandget import get_project_tasks, get_task_state

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


def _get_company() -> str:
    return get_jwt().get("company_name", "")


# ---------------------------------------------------------------------------
# Summary endpoint
# ---------------------------------------------------------------------------
@reports_bp.route('/summary', methods=['GET'])
@jwt_required()
def summary():
    """Return company-wide aggregated stats."""
    company = _get_company()
    if not company:
        return jsonify({"error": "company_name missing from token"}), 400

    projects = list(projects_col.find({"company_name": company}))
    total_projects = len(projects)

    total_tasks = 0
    completed_tasks = 0
    overdue_tasks = 0
    in_progress_tasks = 0
    member_set = set()

    for proj in projects:
        proj_id = proj.get("id") or str(proj.get("_id"))
        tasks = get_project_tasks(proj_id) or []
        total_tasks += len(tasks)

        for t in tasks:
            if not t:
                continue
            state = get_task_state(t.get("id") or "")
            if state == "complete":
                completed_tasks += 1
            elif state == "overdue":
                overdue_tasks += 1
            elif state in ("in progress", "incipient"):
                in_progress_tasks += 1

        for email in proj.get("team", []):
            member_set.add(email)

    active_projects = sum(
        1 for p in projects
        if any(get_task_state(t.get("id", "")) in ("in progress", "incipient")
               for t in (get_project_tasks(p.get("id") or str(p.get("_id"))) or []) if t)
    )
    completed_projects = sum(
        1 for p in projects
        if all(get_task_state(t.get("id", "")) == "complete"
               for t in (get_project_tasks(p.get("id") or str(p.get("_id"))) or []) if t)
        and (get_project_tasks(p.get("id") or str(p.get("_id"))) or [])
    )

    completion_rate = round((completed_tasks / total_tasks * 100) if total_tasks else 0, 1)

    return jsonify({
        "total_projects": total_projects,
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": overdue_tasks,
        "in_progress_tasks": in_progress_tasks,
        "completion_rate": completion_rate,
        "team_members": len(member_set),
    }), 200


# ---------------------------------------------------------------------------
# Per-project stats
# ---------------------------------------------------------------------------
@reports_bp.route('/project/<project_name>', methods=['GET'])
@jwt_required()
def project_report(project_name):
    """Return detailed stats for a single project."""
    company = _get_company()
    import re
    proj = projects_col.find_one({
        "company_name": {"$regex": f"^{re.escape(company)}$", "$options": "i"},
        "name": {"$regex": f"^{re.escape(project_name)}$", "$options": "i"},
    })
    if not proj:
        return jsonify({"error": "Project not found"}), 404

    proj_id = proj.get("id") or str(proj.get("_id"))
    tasks = get_project_tasks(proj_id) or []

    task_breakdown = {"complete": 0, "in_progress": 0, "overdue": 0, "tentative": 0, "other": 0}
    total_estimated = 0
    total_actual = 0
    member_contribution = {}

    for t in tasks:
        if not t:
            continue
        state = get_task_state(t.get("id", ""))
        if state == "complete":
            task_breakdown["complete"] += 1
        elif state in ("in progress", "incipient"):
            task_breakdown["in_progress"] += 1
        elif state == "overdue":
            task_breakdown["overdue"] += 1
        elif state == "tentative":
            task_breakdown["tentative"] += 1
        else:
            task_breakdown["other"] += 1

        total_estimated += t.get("estimated_cost", 0) or 0
        total_actual += t.get("duration", 0) or 0

        for m in t.get("members", []):
            if m not in member_contribution:
                member_contribution[m] = {"assigned": 0, "completed": 0}
            member_contribution[m]["assigned"] += 1
            if state == "complete":
                member_contribution[m]["completed"] += 1

    total_tasks = len(tasks)
    completed_tasks = task_breakdown["complete"]
    completion_rate = round((completed_tasks / total_tasks * 100) if total_tasks else 0, 1)

    return jsonify({
        "project": project_name,
        "total_tasks": total_tasks,
        "task_breakdown": task_breakdown,
        "completion_rate": completion_rate,
        "total_estimated_cost": total_estimated,
        "member_contribution": member_contribution,
    }), 200


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------
@reports_bp.route('/export', methods=['GET'])
@jwt_required()
def export_csv():
    """Stream a CSV of all tasks (optionally filtered by project)."""
    company = _get_company()
    project_filter = request.args.get("project", "")

    import re
    query = {"company_name": {"$regex": f"^{re.escape(company)}$", "$options": "i"}}
    if project_filter:
        query["name"] = {"$regex": f"^{re.escape(project_filter)}$", "$options": "i"}

    projects = list(projects_col.find(query))

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Project", "Task", "Status", "Priority",
        "Progress %", "Assigned Members", "Estimated Cost",
        "Expected Duration (min)", "Actual Duration (min)"
    ])

    for proj in projects:
        proj_id = proj.get("id") or str(proj.get("_id"))
        tasks = get_project_tasks(proj_id) or []
        for t in tasks:
            if not t:
                continue
            state = get_task_state(t.get("id", ""))
            writer.writerow([
                proj.get("name", ""),
                t.get("name", ""),
                state,
                t.get("priority", ""),
                t.get("latest_status", 0),
                ", ".join(t.get("members", [])),
                t.get("estimated_cost", 0),
                t.get("expected_duration", 0),
                t.get("duration", 0),
            ])

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=zainpm_report.csv"}
    )
