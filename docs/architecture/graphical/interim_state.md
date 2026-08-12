# Interim State — Graphical View — Stage 08

**Source of truth:** `docs/product/state/interim/interim_state.md`
One workflow (Batch Review) end-to-end, proving seven assumptions before replication.

## Interim runtime — the minimum governed workflow

```mermaid
flowchart TB
    User(["EU Qualified Person<br/><i>named approver — EAB-3 closed</i>"])

    subgraph app["Web App"]
        UI["Batch Review view"]
    end

    subgraph orch["Orchestrator API — LangGraph"]
        direction TB
        BA["Batch-Review<br/>Agent node"]
        CV["Critic / Verifier<br/>node"]
        HITL["HITL interrupt<br/>handler"]
        BA --> CV --> HITL
    end

    subgraph tools["MCP Tool Servers — 2 only"]
        T1["Evidence Retrieval<br/><i>scoped, read-only</i>"]
        T2["Reconciliation<br/><i>read-only</i>"]
    end

    subgraph gov["Governance / Policy Engine"]
        PAG["Prohibited-Action Guard<br/><b>present from day one</b>"]
    end

    EP[("Evidence & Provenance<br/>status gate: untrusted +<br/>superseded NON-CITABLE")]
    AUD[("Audit / Evidence<br/>Log Store — minimal")]
    LS["LangSmith<br/>tracing"]
    SRC[/"Manufacturing · Lab · Quality<br/>READ-ONLY"/]

    User --> UI --> BA
    BA <--> T1
    BA <--> T2
    T1 --> EP
    EP --> SRC
    CV -.checks.-> PAG
    HITL --> User
    orch -.traces.-> LS
    orch --> AUD

    NOCACHE["Redis cache<br/>DELIBERATELY EXCLUDED"]
    orch -.-> NOCACHE

    classDef excluded fill:#f8d7da,stroke:#dc3545,stroke-dasharray: 5 5,color:#721c24
    classDef guard fill:#fff3cd,stroke:#ffc107,color:#856404
    class NOCACHE excluded
    class PAG,EP guard
```

**Why no cache:** introducing the stale-authority risk alongside agent-correctness risk
makes failures ambiguous. Cache lands only after the uncached path is proven correct.

**Why the guard is not staged:** ADR-004's argument is that prohibited-action enforcement
cannot be retrofitted safely — so it is present in the very first slice.

## The seven assumptions under test

```mermaid
flowchart LR
    subgraph must["MUST PASS — stop-the-line if they fail"]
        A1["1 · Prohibited action fails<br/>at SCHEMA layer"]
        A2["2 · untrusted/superseded<br/>never cited"]
    end
    subgraph should["MUST PASS — design corrections if they fail"]
        A3["3 · HITL routing +<br/>default-safe timeout"]
        A4["4 · Degraded mode safe"]
        A5["5 · Policy Engine<br/>fails CLOSED"]
        A7["7 · Hop count ≈ 7"]
    end
    subgraph measure["FIRST REAL MEASUREMENT"]
        A6["6 · Token / cost per run<br/><i>Unknown since Stage 01</i>"]
    end

    must --> FINAL{"Proceed to<br/>final state?"}
    should --> FINAL
    measure --> FINAL

    classDef critical fill:#f8d7da,stroke:#dc3545,color:#721c24
    classDef normal fill:#e7f1ff,stroke:#0d6efd,color:#084298
    classDef meas fill:#fff3cd,stroke:#ffc107,color:#856404
    class A1,A2 critical
    class A3,A4,A5,A7 normal
    class A6 meas
```

Assumption 6 carries disproportionate weight: it is the first point in the entire programme
where a real cost number exists. If it lands far off expectation, the final state's topology
changes **before** it is built three times over.
