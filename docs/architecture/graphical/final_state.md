# Final State — Graphical View — Stage 08

**Source of truth:** `docs/product/state/final/final_state.md`, `docs/architecture/c4/`

## Target system — three graphs, one deployment

```mermaid
flowchart TB
    QA(["QA Reviewer"])
    PV(["PV Safety Physician"])
    SC(["Supply Chain Lead"])

    subgraph apps["Apps"]
        WEB["Web App"]
        ADM["Admin — run inspector,<br/>eval dashboards"]
    end

    subgraph orch["Orchestrator API — one deployment, three graphs (ADR-008)"]
        direction LR
        subgraph g1["Graph A · Batch Review"]
            A1["Batch-Review Agent"] --> C1["Critic"]
        end
        subgraph g2["Graph B · PV Intake"]
            A2["PV-Intake Agent"] --> C2["Critic"]
        end
        subgraph g3["Graph C · Supply Planning"]
            A3["Supply-Planning Agent"] --> C3["Critic"]
        end
    end

    subgraph tools["MCP Tool Servers — all read-only"]
        T1["Evidence Retrieval<br/><i>shared, context-scoped</i>"]
        T2["Reconciliation"]
        T3["Duplicate-Check"]
        T4["Option-Generation<br/><i>no allocate method</i>"]
    end

    GOV["Governance / Policy Engine<br/>fails CLOSED (ADR-005)"]
    EP[("Evidence & Provenance<br/>+ semantic layer / KG")]
    CACHE[("Redis — tiered TTL,<br/>status-aware keys")]
    AUD[("Audit Store — owned<br/>(ADR-006)")]
    LS["LangSmith — traces,<br/>evals, dashboards"]
    SRC[/"Brownfield systems<br/><b>READ-ONLY, zero writes</b>"/]

    QA --> WEB
    PV --> WEB
    SC --> WEB
    WEB --> orch
    ADM --> LS

    A1 <--> T1
    A1 <--> T2
    A2 <--> T1
    A2 <--> T3
    A3 <--> T1
    A3 <--> T4

    T1 --> EP
    EP --> SRC
    orch <--> CACHE
    orch -.every output.-> GOV
    orch --> AUD
    orch -.traces.-> LS

    C1 --> QA
    C2 --> PV
    C3 --> SC

    classDef readonly fill:#e2e3e5,stroke:#6c757d,color:#41464b
    classDef guard fill:#fff3cd,stroke:#ffc107,color:#856404
    class SRC readonly
    class GOV,EP guard
```

**Note the absent arrows.** There is no edge between Graph A, B, and C — ADR-008 forbids
cross-graph agent calls permanently. There is no arrow *into* the brownfield systems — zero
write integrations, permanently. Both absences are the design, not an omission.

## Interim → final delta

```mermaid
flowchart LR
    subgraph I["INTERIM"]
        I1["1 workflow"]
        I2["2 MCP tools"]
        I3["no cache"]
        I4["placeholder approver"]
        I5["tracing only"]
        I6["no compliance evidence"]
    end
    subgraph F["FINAL"]
        F1["3 workflows"]
        F2["4 MCP tools"]
        F3["Redis + correctness evals"]
        F4["named accountable people"]
        F5["dashboards · alerts · SLOs"]
        F6["EU AI Act + ISO 42001 evidence"]
    end
    I1 --> F1
    I2 --> F2
    I3 --> F3
    I4 --> F4
    I5 --> F5
    I6 --> F6

    classDef gated fill:#f8d7da,stroke:#dc3545,color:#721c24
    class F4 gated
```

The red box is gated on **EAB-3**, which is still open. A governed system with an unnamed
approver is not governed — so this delta cannot close on engineering effort alone.

## Completion gates

```mermaid
flowchart TB
    G1["1 · All 7 interim<br/>assumptions passed"]
    G2["2 · EAB-3 closed —<br/>named approvers"]
    G3["3 · EAB-2 resolved —<br/>air-gap decision"]
    G4["4 · DDD + C4 → stable"]
    G5["5 · ADRs 005–008 ratified"]
    G6["6 · Zero prohibited-action<br/>findings"]
    G7["7 · Compliance evidence<br/>from real runs"]
    DONE{{"FINAL STATE<br/>COMPLETE"}}

    G1 --> DONE
    G2 --> G4
    G3 --> G4
    G4 --> G5 --> DONE
    G6 --> DONE
    G7 --> DONE

    classDef human fill:#f8d7da,stroke:#dc3545,color:#721c24
    class G2,G3 human
```

Gates 2 and 3 (red) require **human answers, not engineering work**. Until they are
answered, the final state cannot be declared complete no matter how much gets built.
