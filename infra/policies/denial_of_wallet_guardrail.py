"""Denial-of-wallet guardrail -- a hard ceiling (per user, per workflow, per
day) enforced before a run is admitted, not just documented.

Executes prompts/19_performance_tuning.md SS4 / exit criterion: "implemented
as an enforced hook, not a documented policy only."

Ceiling derivation (all structural, none measured -- U1/U2 are still Unknown;
see docs/quality/performance/token_economics.md SS0 for why this is the
honest thing to do before 20a runs):

  DAILY_RUN_CEILING = 20
    Same number as C4 (failure_and_loop_guards.md SS3: "Runs per requester
    per hour" = 20), reinterpreted as a deliberately conservative PER-DAY
    cap. A single requester issuing more than 20 total governed-workflow
    runs across a full day would already have tripped the hourly circuit
    breaker (C4) multiple times over -- using the same number for the daily
    backstop is a defensible worst-case bound, not a new guess.

  MAX_TOKENS_PER_RUN = 150,000
    = C1, failure_and_loop_guards.md SS3. Worst case, not typical.

  MAX_DAILY_SPEND_USD = DAILY_RUN_CEILING * (MAX_TOKENS_PER_RUN / 1e6) *
                         SONNET_5_OUTPUT_PRICE
    Priced at the Sonnet 5 output rate ($15/MTok, the more expensive side of
    Sonnet 5's $3 in / $15 out, and the model token_economics.md SS2
    recommends for 20a) as a conservative all-output-tokens assumption.
    = 20 * 0.15 * 15 = $45.00 per (user, workflow) per day.

This is a CEILING (catches a run that has gone insane), not a BUDGET (a
tuned target from measured typical cost) -- same distinction
failure_and_loop_guards.md SS1 draws for the per-run guards. Replaced by a
measured budget at the Stage 15 measured pass, per BC-13/14.
"""
from collections import defaultdict
from datetime import date

DAILY_RUN_CEILING = 20
MAX_TOKENS_PER_RUN = 150_000
_SONNET_5_OUTPUT_PRICE_PER_MTOK = 15.00
MAX_DAILY_SPEND_USD = round(
    DAILY_RUN_CEILING * (MAX_TOKENS_PER_RUN / 1_000_000) * _SONNET_5_OUTPUT_PRICE_PER_MTOK, 2
)  # 45.00


class DenialOfWalletGuard:
    """In-process ceiling tracker, one instance per deployment process.

    A real deployment backs this with a shared store (Redis or the audit
    store, per ADR-006) so the ceiling holds across process restarts and
    horizontally-scaled instances -- the in-memory dict here is sufficient
    for this stage's self-test, exactly as V1's own tool_gateway.py used an
    in-process dict for its idempotency cache "since the tests exercise a
    single process" (verified pattern, Stage 14).
    """

    def __init__(self):
        self._run_count: dict[tuple[str, str, date], int] = defaultdict(int)
        self._spend_usd: dict[tuple[str, str, date], float] = defaultdict(float)

    def _key(self, user_id: str, workflow: str, as_of: date) -> tuple[str, str, date]:
        return (user_id, workflow, as_of)

    def check_and_admit(self, user_id: str, workflow: str, as_of: date,
                         estimated_tokens: int = MAX_TOKENS_PER_RUN,
                         estimated_output_price_per_mtok: float = _SONNET_5_OUTPUT_PRICE_PER_MTOK):
        """Call before admitting a new run. Returns {"admit": bool, "reason": str, ...}.

        Uses the WORST-CASE estimate (MAX_TOKENS_PER_RUN, i.e. C1) unless the
        caller supplies a real pre-run estimate -- admitting on worst case is
        deliberately conservative: it can reject a run that would have cost
        less than estimated, never the reverse. Same fail-safe direction as
        every other guard in this programme (ADR-005 fails closed)."""
        key = self._key(user_id, workflow, as_of)
        runs_so_far = self._run_count[key]
        spend_so_far = self._spend_usd[key]

        if runs_so_far >= DAILY_RUN_CEILING:
            return {
                "admit": False,
                "reason": f"daily_run_ceiling_exceeded: {runs_so_far} runs already recorded for "
                          f"({user_id}, {workflow}) on {as_of}, ceiling is {DAILY_RUN_CEILING}",
            }

        projected_spend = spend_so_far + (estimated_tokens / 1_000_000) * estimated_output_price_per_mtok
        if projected_spend > MAX_DAILY_SPEND_USD:
            return {
                "admit": False,
                "reason": f"daily_spend_ceiling_exceeded: projected ${projected_spend:.2f} > "
                          f"ceiling ${MAX_DAILY_SPEND_USD:.2f} for ({user_id}, {workflow}) on {as_of}",
            }

        return {"admit": True, "reason": "within_ceiling", "runs_so_far": runs_so_far, "spend_so_far": round(spend_so_far, 2)}

    def record_run(self, user_id: str, workflow: str, as_of: date,
                    actual_tokens: int, actual_output_price_per_mtok: float = _SONNET_5_OUTPUT_PRICE_PER_MTOK):
        """Call after a run completes, with its REAL token usage -- not the
        pre-run estimate. This is what makes the ceiling self-correcting:
        a run that actually used far fewer tokens than the worst-case
        estimate leaves more daily headroom for the next one."""
        key = self._key(user_id, workflow, as_of)
        self._run_count[key] += 1
        self._spend_usd[key] += (actual_tokens / 1_000_000) * actual_output_price_per_mtok
