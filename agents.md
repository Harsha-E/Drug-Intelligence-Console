---
name: Drug Intelligence Console
description: Drug Intelligence Console API providing MedCheck functionality for medication interactions, allergy checking, and clinical timeline reasoning.
---

# Drug Intelligence Console API

This Space hosts the Drug Intelligence Console backend and the Admin Frontend. It is designed to act as a headless intelligence engine for clinical tools.

## Base URL
The API is available at the root URL of this Space.

## Available Endpoints

### 1. POST /api/v1/analyze
**Purpose**: Analyzes a list of medications against a patient's context for drug-drug interactions, contraindications, and dosage adjustments.
**Payload Schema**:
`json
{
  "medications": [
    {
      "id": "string (canonical ID, e.g. DIC_DRUG_ATORVASTATIN)",
      "name": "string"
    }
  ],
  "patient": {
    "age": "int (optional)",
    "weight_kg": "float (optional)",
    "renal_clearance": "NORMAL | MILD_IMPAIRMENT | MODERATE_IMPAIRMENT | SEVERE_IMPAIRMENT",
    "hepatic_impairment": "NONE | MILD | MODERATE | SEVERE"
  }
}
`
**Response**: Returns an execution trace containing the clinical_report and evidence.

### 2. POST /api/v1/interactions
**Purpose**: Quick check for interactions between a list of canonical medication IDs.
**Payload Schema**:
`json
{
  "medication_ids": ["DIC_DRUG_1", "DIC_DRUG_2"]
}
`
**Response**: Returns { "interactions": [...] }.

### 3. GET /api/v1/drugs/search?q={query}
**Purpose**: Search the in-memory registry for medications by name or canonical ID.

### 4. Health and Metrics
- GET /health
- GET /ready
- GET /metrics
- GET /version

## Frontend
The Admin Console is served at the root GET / and can be used to visually debug requests and view the clinical ledger.
