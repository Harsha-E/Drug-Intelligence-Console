# Drug Intelligence Cloud: Architecture Reference

This document expands on the Constitution to define the structural wiring of the platform.

## 1. The Core Infrastructure
All shared logic resides in `core/` to prevent duplication.
*   `config/`: Environment variables and secrets management.
*   `schemas/`: Pydantic models defining the `ClinicalContext` and API contracts.
*   `logging/`: Structured JSON logging for Datadog/ELK integration.
*   `events/`: The Event Bus (Pub/Sub pattern) decoupling reasoning from auditing.

## 2. Multi-Agent Orchestration
The reasoning engine is split into isolated plugins.

### The Orchestrators (`agents/orchestrators/`)
*   **Clinical Orchestrator:** Manages real-time patient API requests.
*   **Batch Orchestrator:** Manages retrospective population analysis.

### The Specialists (`agents/specialists/`)
*   **Identity Agent:** Maps requested drugs to the Semantic Ontology (RxNorm).
*   **PK Agent:** Evaluates pharmacokinetic properties (CYP450 metabolism).
*   **Evidence Agent:** Retrieves supporting literature from the `evidence/` layer.

## 3. The Explicit Analysis Pipeline
The Clinical Orchestrator strictly enforces this sequence:
1.  **Validation:** API Gateway validates schema and JWT.
2.  **Normalization:** Identity Agent maps input strings to Semantic Concept IDs.
3.  **Context Building:** Instantiates the `ClinicalContext` state object.
4.  **Agent Dispatch:** Orchestrator queries the `CapabilityRegistry` and dispatches specialists concurrently.
5.  **Reasoning:** Agents apply the Clinical Constraint Language (CCL) rules against the Context.
6.  **Conflict Resolution:** Orchestrator resolves contradictory findings using evidence weighting.
7.  **Explanation Generation:** Every finding is paired with its causal trace.
8.  **Audit & Response:** The 5 outputs are generated, Events are published, and JSON is returned.

## 4. The Event Bus Pattern
Modules (like `audit/` and `analytics/`) **never** block the main clinical execution thread.
When an interaction is found, the Orchestrator publishes an event:
`{ type: "INTERACTION_FOUND", severity: "HIGH", context_id: "123" }`
Background workers consume these events to populate dashboards and logs.
