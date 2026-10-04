"""Fail-closed checks shared by approval and deployment. No external services."""
import json


def require_reviewable_configuration(conn, config_id, require_approved=False):
    row = conn.execute("""
        SELECT c.parameters_json, c.status, a.cross_eval_json,
               a.recommended_eza_config_json
        FROM eza_configurations c LEFT JOIN analysis_jobs a ON a.id = c.analysis_job_id
        WHERE c.id = ?
    """, (config_id,)).fetchone()
    if row is None:
        raise ValueError("Configuration not found")
    try:
        audit = json.loads(row["cross_eval_json"] or "{}")
        parameters = json.loads(row["parameters_json"] or "{}")
        recommended = json.loads(row["recommended_eza_config_json"] or "{}")
    except (ValueError, TypeError):
        raise ValueError("Invalid analysis audit") from None
    if not isinstance(audit, dict) or audit.get("status") != "READY_FOR_REVIEW" or audit.get("blocking_reasons") != []:
        raise ValueError("Analysis requires resolution and a new review before approval or deployment")
    if not parameters or parameters != recommended:
        raise ValueError("Configuration does not match the reviewed analysis")
    if require_approved and row["status"] != "APPROVED":
        raise ValueError("Configuration requires explicit approval before deployment")
    return parameters
