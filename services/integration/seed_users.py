"""One-time (idempotent) seed of the ten synthetic demo accounts, one per ROLE_CATALOG
entry in user_store.py. Run directly: `python3 -m services.integration.seed_users`.

Passwords are synthetic and intentionally documented in
docs/governance/demo_login_credentials.md -- this is a capstone/demo environment with no
real PHI/PII and no real people behind these accounts, the same posture the project
already takes with every other fixture (see V1 CLAUDE.md's "Synthetic data only").
"""
from __future__ import annotations

from services.integration import user_store

# (user_id, display_name, role, password)
# Passwords use "_" rather than "-" so a double-click selects the whole string in one go
# (browsers treat "-" as a word boundary for double-click selection, "_" is not) --
# matching the user_id style, which already uses "_" for the same reason.
SEED_ACCOUNTS = [
    ("qp_eu_1", "Dinesh", "EU Qualified Person", "qp_eu_1_aegis"),
    ("safety_physician_1", "Dr. Payal", "Safety physician", "safety_phys_1_aegis"),
    ("supply_gov_1", "Mahesh", "Supply governance", "supply_gov_1_aegis"),
    ("research_head_1", "Dr. Kishore", "Head of Preclinical Research", "research_head_1_aegis"),
    ("clinical_monitor_1", "Dr. Kiran", "Clinical Trial Medical Monitor", "clinical_mon_1_aegis"),
    ("regulatory_head_1", "Anjali", "Head of Regulatory Affairs", "reg_head_1_aegis"),
    ("quality_reviewer_1", "Rajesh", "Quality reviewer", "quality_rev_1_aegis"),
    ("ciso_dpo_1", "Sunita", "CISO / DPO", "ciso_dpo_1_aegis"),
    ("auditor_1", "Arvind", "Auditor", "auditor_1_aegis"),
    ("unblinding_auth_1", "Dr. Nikhil", "Unblinding authority", "unblind_auth_1_aegis"),
]


def seed() -> None:
    conn = user_store.get_connection()
    try:
        for user_id, display_name, role, password in SEED_ACCOUNTS:
            user_store.create_user(conn, user_id, display_name, role, password)
    finally:
        conn.close()
    print(f"Seeded {len(SEED_ACCOUNTS)} accounts into {user_store.DEFAULT_DB_PATH}")


if __name__ == "__main__":
    seed()
