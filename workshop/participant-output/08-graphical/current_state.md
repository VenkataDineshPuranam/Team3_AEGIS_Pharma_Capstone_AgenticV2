# Current State — Graphical View — Stage 08

**Source of truth:** `docs/product/state/current/current_state_assessment.md` (measured
2026-08-12: 249 tracked files, 4 of 21 stages complete, zero implementation).

## What exists today

```mermaid
flowchart TB
    subgraph done["COMPLETE — design artefacts (docs/)"]
        S1["Stage 01<br/>Discovery + SCQA<br/><i>stable</i>"]
        S2["Stage 02<br/>DDD<br/><i>stable</i>"]
        S3["Stage 03<br/>C4<br/><i>stable</i>"]
        S4["Stage 04<br/>ADR — all 8 accepted<br/>review: <i>pass</i>"]
        S5["Stage 05<br/>Current state<br/><i>this measurement</i>"]
        S1 --> S2 --> S3 --> S4 --> S5
    end

    subgraph pending["NOT STARTED — scaffold only"]
        P1["Stages 06–09<br/>interim / final / graphical / DMAIC"]
        P2["Stages 10–13<br/>agentic arch · MCP · skills+hooks · ontology"]
        P3["Stages 14–19<br/>eval-cache · perf · governance · observability · security · compliance"]
        P4["Stage 20–21<br/>implementation · documentation"]
    end

    subgraph resolved["BLOCKERS — both now CLOSED"]
        B1["EAB-2 — air-gap? <b>CLOSED</b><br/>cloud-connected confirmed"]
        B2["EAB-3 — HITL approvers? <b>CLOSED</b><br/>named from V1 stakeholder pack"]
    end

    done --> pending
    B1 -.unblocked.-> P4
    B2 -.unblocked.-> P3

    classDef complete fill:#d4edda,stroke:#28a745,color:#155724
    classDef todo fill:#f8f9fa,stroke:#adb5bd,color:#495057
    classDef blocker fill:#d4edda,stroke:#28a745,color:#155724
    class S1,S2,S3,S4,S5 complete
    class P1,P2,P3,P4 todo
    class B1,B2 blocker
```

## Repository content: real vs. scaffold

```mermaid
flowchart LR
    subgraph real["Real content"]
        R1["docs/ — 59 files<br/>adr, architecture, product"]
        R2["prompts/ — 25 files<br/>13 adapted + 10 new"]
        R3["workshop/ — 47 files<br/>mirrors of stages 01–04"]
        R4["eval-ai-cache/ — 29 files<br/><b>UNCONSUMED</b>"]
    end

    subgraph stub["Scaffold only (README stubs)"]
        T1["apps/ services/ packages/<br/>tests/ — 0 implementation"]
        T2["security/ ops/ infra/<br/>quality/ deploy/"]
        T3["evidence/ — 0 records<br/>(correct: nothing has run)"]
        T4["templates/ — 10 blank"]
    end

    classDef realcls fill:#d4edda,stroke:#28a745,color:#155724
    classDef stubcls fill:#f8f9fa,stroke:#adb5bd,color:#495057
    classDef warn fill:#fff3cd,stroke:#ffc107,color:#856404
    class R1,R2,R3 realcls
    class R4 warn
    class T1,T2,T3,T4 stubcls
```

**The amber box is the notable one:** `eval-ai-cache/` holds 29 files of directly-applicable
reference material (24-file brownfield-evals runbook, Redis caching runbook, OpenTelemetry
runbook) that no stage has drawn on yet. Stages 14/15/17 should consume it rather than
derive equivalents (NAB-4).

## Honest reading of this view

There is **no system** yet — only design artefacts and their mirrors. That is correct and
intentional (Stage 20 is deliberately last), but it means every architectural claim made so
far is unvalidated by execution. The interim state exists precisely to change that.
