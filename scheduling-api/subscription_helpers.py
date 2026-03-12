"""
subscription_helpers.py
Centralised tier-limit logic for ZainPM subscriptions.
"""
from db import subscriptions_col, projects_col, tasks_col

# ---------------------------------------------------------------------------
# Tier definitions
# ---------------------------------------------------------------------------
TIER_LIMITS = {
    "free": {
        "projects": 3,
        "tasks_per_project": 10,
        "members": 2,
        "label": "Free"
    },
    "pro": {
        "projects": None,          # unlimited
        "tasks_per_project": None,
        "members": 50,
        "label": "Pro"
    },
    "enterprise": {
        "projects": None,
        "tasks_per_project": None,
        "members": None,           # unlimited
        "label": "Enterprise"
    },
}


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------
class LimitExceededError(Exception):
    """Raised when a subscription tier limit has been reached."""
    def __init__(self, resource: str, limit: int, tier: str):
        self.resource = resource
        self.limit = limit
        self.tier = tier
        super().__init__(f"{tier} tier limit reached for {resource}: max {limit}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_subscription(company_name: str) -> dict:
    """Return the subscription document for a company, defaulting to Free."""
    doc = subscriptions_col.find_one({"company_name": company_name})
    if doc:
        return doc
    # Synthesise a free-tier default (company may pre-date subscription feature)
    return {
        "company_name": company_name,
        "tier": "free",
        "status": "active",
        "stripe_customer_id": None,
        "stripe_subscription_id": None,
        "current_period_end": None,
    }


def get_tier_limits(company_name: str) -> dict:
    """Return the limit dict for the company's current tier."""
    sub = get_subscription(company_name)
    tier = sub.get("tier", "free")
    return TIER_LIMITS.get(tier, TIER_LIMITS["free"])


def create_free_subscription(company_name: str):
    """Insert a free-tier subscription document for a newly registered company."""
    from datetime import datetime, timezone
    existing = subscriptions_col.find_one({"company_name": company_name})
    if existing:
        return existing
    doc = {
        "company_name": company_name,
        "tier": "free",
        "status": "active",
        "stripe_customer_id": None,
        "stripe_subscription_id": None,
        "current_period_end": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    subscriptions_col.insert_one(doc)
    return doc


# ---------------------------------------------------------------------------
# Limit checkers — raise LimitExceededError when quota is exceeded
# ---------------------------------------------------------------------------
def check_project_limit(company_name: str):
    """Raise LimitExceededError if the company has hit its project cap."""
    sub = get_subscription(company_name)
    tier = sub.get("tier", "free")
    limits = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
    max_projects = limits["projects"]
    if max_projects is None:
        return  # unlimited
    count = projects_col.count_documents({"company_name": company_name})
    if count >= max_projects:
        raise LimitExceededError("projects", max_projects, tier)


def check_task_limit(project_id: str):
    """Raise LimitExceededError if the project has hit its task cap."""
    proj = projects_col.find_one({"id": project_id})
    if not proj:
        return
    company_name = proj.get("company_name", "")
    sub = get_subscription(company_name)
    tier = sub.get("tier", "free")
    limits = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
    max_tasks = limits["tasks_per_project"]
    if max_tasks is None:
        return  # unlimited
    count = tasks_col.count_documents({"project_id": project_id})
    if count >= max_tasks:
        raise LimitExceededError("tasks_per_project", max_tasks, tier)


def check_member_limit(company_name: str):
    """Raise LimitExceededError if the company has hit its member cap."""
    sub = get_subscription(company_name)
    tier = sub.get("tier", "free")
    limits = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
    max_members = limits["members"]
    if max_members is None:
        return  # unlimited
    # Count unique members across all company projects
    pipeline = [
        {"$match": {"company_name": company_name}},
        {"$unwind": "$team"},
        {"$group": {"_id": "$team"}},
        {"$count": "total"}
    ]
    result = list(projects_col.aggregate(pipeline))
    count = result[0]["total"] if result else 0
    if count >= max_members:
        raise LimitExceededError("members", max_members, tier)
