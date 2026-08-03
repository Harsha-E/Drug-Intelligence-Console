from typing import List, Dict, Any
from .base import SourceProvider

class OpenFDAProvider(SourceProvider):
    def get_provider_name(self) -> str:
        return "OpenFDA"
        
    def fetch_all(self) -> List[Dict[str, Any]]:
        # Offline authoritative data source for OpenFDA
        # Generates canonical drug definitions with comprehensive mechanisms
        return [
            {
                "canonical_name": "warfarin",
                "codes": {"openfda": "WAR_01"},
                "ingredients": [{"name": "warfarin", "role": "active"}],
                "classifications": ["Anticoagulant", "Vitamin K Antagonist"],
                "claims": [
                    {"subject_name": "warfarin", "predicate": "INHIBITS_ENZYME", "object_name": "VKORC1", "evidence": {"confidence": "HIGH"}},
                    {"subject_name": "warfarin", "predicate": "METABOLIZED_BY", "object_name": "CYP2C9", "evidence": {"confidence": "HIGH"}},
                    {"subject_name": "warfarin", "predicate": "HAS_EFFECT", "object_name": "PD_EFFECT_BLEEDING", "strength": "HIGH", "evidence": {"confidence": "HIGH"}},
                    {"subject_name": "warfarin", "predicate": "CONTRAINDICATED_FOR", "object_name": "PREGNANCY", "evidence": {"confidence": "HIGH"}}
                ]
            },
            {
                "canonical_name": "atorvastatin",
                "codes": {"openfda": "ATO_01"},
                "ingredients": [{"name": "atorvastatin", "role": "active"}],
                "classifications": ["Statin", "HMG-CoA Reductase Inhibitor"],
                "claims": [
                    {"subject_name": "atorvastatin", "predicate": "BINDS_TO_TARGET", "object_name": "HMGCR", "evidence": {"confidence": "HIGH"}},
                    {"subject_name": "atorvastatin", "predicate": "TRANSPORTED_BY", "object_name": "OATP1B1", "evidence": {"confidence": "HIGH"}},
                    {"subject_name": "atorvastatin", "predicate": "METABOLIZED_BY", "object_name": "CYP3A4", "evidence": {"confidence": "HIGH"}},
                    {"subject_name": "atorvastatin", "predicate": "ALTERS_LAB", "object_name": "LAB_ALT_AST_ELEVATION", "evidence": {"confidence": "HIGH"}},
                    {"subject_name": "atorvastatin", "predicate": "HAS_EFFECT", "object_name": "PD_EFFECT_MYOPATHY", "strength": "MODERATE", "evidence": {"confidence": "HIGH"}}
                ]
            },
            {
                "canonical_name": "cyclosporine",
                "codes": {"openfda": "CYC_01"},
                "ingredients": [{"name": "cyclosporine", "role": "active"}],
                "classifications": ["Immunosuppressant", "Calcineurin Inhibitor"],
                "claims": [
                    {"subject_name": "cyclosporine", "predicate": "INHIBITS_ENZYME", "object_name": "CYP3A4", "evidence": {"confidence": "HIGH"}},
                    {"subject_name": "cyclosporine", "predicate": "INHIBITS_TRANSPORTER", "object_name": "OATP1B1", "evidence": {"confidence": "HIGH"}},
                    {"subject_name": "cyclosporine", "predicate": "INHIBITS_TRANSPORTER", "object_name": "P-gp", "evidence": {"confidence": "HIGH"}}
                ]
            },
            {
                "canonical_name": "methotrexate",
                "codes": {"openfda": "MTX_01"},
                "ingredients": [{"name": "methotrexate", "role": "active"}],
                "classifications": ["Antimetabolite", "DMARD"],
                "claims": [
                    {"subject_name": "methotrexate", "predicate": "PREGNANCY_CATEGORY", "object_name": "CATEGORY_X", "evidence": {"confidence": "HIGH"}},
                    {"subject_name": "methotrexate", "predicate": "HAS_EFFECT", "object_name": "PD_EFFECT_HEPATOTOXICITY", "strength": "SEVERE", "evidence": {"confidence": "HIGH"}},
                    {"subject_name": "methotrexate", "predicate": "REQUIRES_HEPATIC_ADJUSTMENT_IF", "object_name": "SEVERE_IMPAIRMENT", "evidence": {"confidence": "HIGH"}}
                ]
            },
            {
                "canonical_name": "lisinopril",
                "codes": {"openfda": "LIS_01"},
                "ingredients": [{"name": "lisinopril", "role": "active"}],
                "classifications": ["ACE Inhibitor"],
                "claims": [
                    {"subject_name": "lisinopril", "predicate": "BINDS_TO_TARGET", "object_name": "ACE", "evidence": {"confidence": "HIGH"}},
                    {"subject_name": "lisinopril", "predicate": "REQUIRES_RENAL_ADJUSTMENT_IF", "object_name": "SEVERE_IMPAIRMENT", "evidence": {"confidence": "HIGH"}},
                    {"subject_name": "lisinopril", "predicate": "CONTRAINDICATED_FOR", "object_name": "PREGNANCY", "evidence": {"confidence": "HIGH"}}
                ]
            },
            {
                "canonical_name": "augmentin",
                "codes": {"openfda": "AUG_01"},
                "ingredients": [
                    {"name": "amoxicillin", "role": "active"},
                    {"name": "clavulanate", "role": "active"}
                ],
                "classifications": ["Penicillin Antibiotic", "Beta-Lactamase Inhibitor"],
                "claims": [
                    {"subject_name": "amoxicillin", "predicate": "HAS_EFFECT", "object_name": "PD_EFFECT_BACTERICIDAL", "evidence": {"confidence": "HIGH"}},
                    {"subject_name": "clavulanate", "predicate": "INHIBITS_ENZYME", "object_name": "BETA_LACTAMASE", "evidence": {"confidence": "HIGH"}}
                ]
            }
        ]
