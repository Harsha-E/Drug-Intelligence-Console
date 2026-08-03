# Drug Intelligence Cloud: System Specification

This document defines **what** the Drug Intelligence Cloud (DIC) is building. It is the absolute reference for the platform's capabilities, independent of how they are implemented.

## 1. Core Purpose
The Drug Intelligence Cloud is a headless, API-first **Knowledge-Driven Clinical Reasoning Engine**. It evaluates complex patient states against a continuously updated biomedical knowledge graph to derive deterministic, evidence-based clinical insights. There are no black-box ML models in the reasoning path.

## 2. The Semantic Layer (Ontology)
The platform does not reason over raw strings (e.g., "Aspirin"). It reasons over a strict semantic ontology where every entity is mapped to its highest-order class and relationships.
*   **Example:** `Aspirin` → `NSAID` → `Platelet Inhibitor` → `COX-1 / COX-2 Inhibitor` → `Bleeding Risk`.
*   This Semantic Layer ensures that specialist agents do not need to reinvent mappings for every request.

## 3. The Clinical Constraint Language (CCL)
The defining innovation of the platform is the **Clinical Constraint Language**. Pharmacological safety is evaluated via formal constraint verification rather than monolithic Python scripts or black-box ML models.

### Example CCL Syntax:
```ccl
IF
  DrugA.inhibits(CYP3A4)
AND
  DrugB.metabolized_by(CYP3A4)
THEN
  Increase Exposure
  Severity = Moderate
  Confidence = High (Evidence Based)
  Evidence_Required = True
```
Benefits of CCL:
*   Clinicians can read, review, and audit the rules.
*   Rules are inherently versioned and portable.
*   Benchmarking is deterministic.

## 4. The Five Outputs
Every analysis request sent to the API must produce five distinct outputs. A generic "Result" is not acceptable.

1.  **Clinical Report:** The user-facing JSON payload containing the specific clinical recommendations and warnings.
2.  **Reasoning Trace:** The complete, step-by-step graph of how the conclusion was reached (e.g., *Identity Agent → PK Agent → Rule #18 → Report*).
3.  **Evidence Trace:** The specific literature, guidelines, or FDA labels that support the reasoning trace.
4.  **Audit Trace:** System-level metrics (latency, agent versions, knowledge base versions, missing data logs).
5.  **Analytics Event:** A decoupled event published to the Event Bus for population health tracking (e.g., *Interaction: Warfarin + Aspirin flagged*).

## 5. Supported Clinical Workflows
The platform orchestrates distinct, reusable workflows for different use cases:
*   **Clinical Workflow:** Point-of-care interaction and contraindication checking.
*   **Research Workflow:** Exploratory analysis of novel compounds or predicted interactions (isolated from production clinical data).
*   **Admin Workflow:** System diagnostics, knowledge ingestion triggers, and manual editorial overrides.
*   **Batch Workflow:** Running thousands of retrospective patient state vectors against a new rule to determine population impact.
*   **Validation Workflow:** Automated testing of the reasoning engine against a gold-standard benchmark dataset.

## 6. The Scope of Knowledge (Future Expansion)
While v1.0 focuses on Drug-Drug Interactions (DDI), the Specification explicitly requires the architecture to support:
*   Drug-Disease Interactions
*   Drug-Food/Nutritional Interactions
*   Pharmacogenomics (Drug-Gene)
*   Laboratory Interpretation (e.g., Renal/Hepatic dosage adjustments)
*   Wearable/Telemetry Physiological state changes
