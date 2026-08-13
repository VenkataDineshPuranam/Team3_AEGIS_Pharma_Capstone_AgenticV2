"""Loop-guard grader -- the 8 structural caps (G1-G8) and cycle detection.

Rule source: docs/architecture/agentic/failure_and_loop_guards.md SS2, SS4.
Numeric values copied verbatim.
"""

CAPS = {
    "G1_max_llm_calls": 6,
    "G2_max_agent_critic_loops": 2,
    "G3_max_retrieval_broadenings": 1,
    "G4_max_tool_calls": 8,
    "G5_max_graph_steps": 40,
    "G6_max_wall_clock_s": 300,
}


def grade_loop_guards(llm_calls, agent_critic_loops, retrieval_broadenings, tool_calls, graph_steps, wall_clock_s):
    checks = [
        ("G1", llm_calls, CAPS["G1_max_llm_calls"]),
        ("G2", agent_critic_loops, CAPS["G2_max_agent_critic_loops"]),
        ("G3", retrieval_broadenings, CAPS["G3_max_retrieval_broadenings"]),
        ("G4", tool_calls, CAPS["G4_max_tool_calls"]),
        ("G5", graph_steps, CAPS["G5_max_graph_steps"]),
        ("G6", wall_clock_s, CAPS["G6_max_wall_clock_s"]),
    ]
    for name, value, cap in checks:
        if value > cap:
            return {"pass": False, "reason": f"{name}_exceeded: {value} > {cap}"}
    return {"pass": True, "reason": "within_all_structural_caps"}


def grade_cycle_detection(fingerprints):
    """failure_and_loop_guards.md SS4: an identical (evidence_ids,
    draft_output_hash, critic_reason_code) fingerprint on consecutive
    iterations means the retry changed nothing -- terminate as no_progress
    regardless of remaining budget."""
    for i in range(1, len(fingerprints)):
        if fingerprints[i] == fingerprints[i - 1]:
            return {"pass": False, "reason": f"no_progress: identical fingerprint on consecutive iterations ({fingerprints[i]!r})"}
    return {"pass": True, "reason": "no_cycle_detected"}
