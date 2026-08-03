"""
Machine-readable Knowledge Specification.
Defines invariants for the Knowledge Validator.
"""

KNOWLEDGE_SPEC = {
    "schema_version": "1.1",
    "required_entity_type": "DrugKnowledge",
    "identity": {
        "required": ["canonical_name", "aliases", "codes"],
        "codes_allowed": ["rxnorm", "atc"]
    },
    "clinical_knowledge": {
        "required": ["classifications", "clinical_characteristics", "pharmacodynamic_effects", "contraindications"]
    },
    "pharmacodynamic_effects": {
        "allowed_directions": ["INCREASE", "DECREASE"],
        "allowed_magnitudes": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    },
    "contraindications": {
        "allowed_severities": ["RELATIVE", "ABSOLUTE"]
    }
}
