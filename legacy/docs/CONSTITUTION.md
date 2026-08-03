# Drug Intelligence Cloud Constitution

*This document defines the immutable architectural principles and laws governing the Drug Intelligence Cloud (DIC). It serves as the absolute blueprint for all development. No code will be written that violates these principles.*

---

## ⚖️ The 14 Immutable Laws

1. **No architectural rewrites.** The structural boundaries are permanent. We expand capabilities; we do not tear down walls.
2. **Agents communicate ONLY through the orchestrator.** Direct agent-to-agent communication is strictly forbidden to prevent tight coupling.
3. **All reasoning flows through a shared Clinical Context.** Agents read the context and append findings. They never mutate another agent's output.
4. **Every analysis is fully auditable and reproducible.** The system must trace exactly how a clinical decision was reached.
5. **Rules and Knowledge remain strictly deterministic.** Clinical rules must be evaluated against verified evidence; probabilistic ML predictions are strictly prohibited from the clinical path.
6. **Every module and analysis is versioned.** From API routes to knowledge graphs, versioning guarantees reproducibility across time.
7. **Research code never ships to production directly.** All experiments belong in the isolated `/research` workspace.
8. **Every capability must pass predefined Quality Gates.** A feature is only complete when tests, benchmarks, security, and audits pass.
9. **The platform is API-first.** MedCheck is merely one client. The DIC serves headless JSON logic.
10. **The platform is extensible through plugins.** Agents must conform to a strict interface (`ClinicalAgent`) so new specialists can be added without modifying the core orchestrator.
11. **Knowledge is a First-Class Citizen.** The platform never embeds clinical knowledge directly into agent code. If a guideline changes, the knowledge base is updated, not the reasoning engine.
12. **Explainability Before Intelligence.** No agent produces a conclusion without an accompanying explanation answering: *What, Why, Evidence, Rule, and Confidence (Quality).*
13. **Every Decision Produces a Reasoning Trace.** Every conclusion must be reconstructable via a complete reasoning graph (e.g., Drug → Identity → PK → Evidence → Rule → Report).
14. **Production Never Learns.** Production systems never modify knowledge automatically. The strict lifecycle is: Research → Validation → Benchmark → Approval → Production.

---

## 🏛️ Repository Organization Blueprint

```text
Drug-Intelligence-Cloud/
├── api/                  # REST API, Routing, Versioning
├── gateway/              # Rate limiting, Auth parsing, Request validation
├── core/                 # Shared Infrastructure (DO NOT DUPLICATE)
├── registry/             # Dynamic discovery of Agents, Rules, Knowledge, Plugins
├── governance/           # Constitution, Architecture, Clinical, Security, Quality policies
├── ingestion/            # Offline pipelines (RxNorm, DrugBank, Guidelines) -> Normalization
├── agents/               # Multi-Agent Orchestration (Plugins)
│    ├── orchestrators/   # Clinical, Research, Batch, Admin Orchestrators
│    └── specialists/     # Identity, PK, PD, Evidence, Recommendation, etc.
├── reasoning/            # Isolated Logic
│    └── rules/           # Deterministic (Clinical Constraint Language)
├── knowledge/            # What is known (Drug properties, Pathways, Targets)
├── evidence/             # How well we know it (Clinical trials, FDA labels, Guidelines)
├── audit/                # Lifecycle Auditing Pipeline
├── analytics/            # Dashboards and Metrics
├── research/             # Isolated experimentation space
├── testing/              # Capability Gates (Unit, E2E, Clinical)
└── infrastructure/       # Docker, CI/CD
```

---

## ⚙️ The Explicit Analysis Pipeline
Every request must traverse this exact lifecycle:

`API` → `Validation` → `Normalization` → `Context Building` → `Task Planning` → `Agent Dispatch` → `Knowledge Retrieval` → `Reasoning` → `Conflict Resolution` → `Confidence Scoring` → `Recommendation Generation` → `Explanation Generation` → `Audit` → `Analytics Events` → `Response`

---

## 🚀 Capability Progression

We progressively enrich capabilities without changing the underlying architecture.
*   **Platform Foundation** – Infrastructure, orchestration, auditing, plugin framework, API gateway.
*   **Knowledge Foundation** – Drug catalog, ontologies, evidence store, ingestion pipelines.
*   **Clinical Intelligence** – Deterministic reasoning and patient-context analysis.
*   **Operational Intelligence** – Analytics, dashboards, monitoring, governance.
