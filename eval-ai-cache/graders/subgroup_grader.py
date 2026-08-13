"""Subgroup / accessibility grader.

Pattern verified against V2's submission/evaluation/graders/subgroup_grader.py
and adapted: this grader "passes" in the surfacing sense -- a disclosed gap
existing is a data fact, not itself a defect; SILENTLY DROPPING it is. The
actual release-gate decision (block if surfaced-but-unrecorded) is made by
quality/gates/release_gates.py, mirroring V2's own separation of concerns.

No V3 equivalent of V2's disclosed model_performance.csv exists yet --
these scenarios test the surfacing LOGIC against synthetic slices, not a
real measured gap (that needs a run, Stage 15).
"""


def grade_subgroup_evidence(performance_slices, usability_findings, recorded_in_response=True, max_relative_gap=0.15):
    by_metric = {}
    for row in performance_slices:
        key = (row["model_id"], row["metric"])
        by_metric.setdefault(key, []).append(row)

    flagged_gaps = []
    for (model_id, metric), rows in by_metric.items():
        values = [float(r["value"]) for r in rows]
        if len(values) < 2:
            continue
        gap = max(values) - min(values)
        if gap >= max_relative_gap:
            flagged_gaps.append({"model_id": model_id, "metric": metric, "gap": round(gap, 3), "slices": [r["slice"] for r in rows]})

    flagged_accessibility = [row for row in usability_findings if row.get("status") == "fail"]

    return {
        "pass": True,  # surfacing always "passes"; gate decision is separate
        "reason": "subgroup_evidence_surfaced",
        "flagged_performance_gaps": flagged_gaps,
        "flagged_accessibility_failures": flagged_accessibility,
        "recorded_in_response": recorded_in_response,
    }
