from typing import List, Dict, Any, Set, Optional
from .knowledge_graph import CompiledKnowledgeGraph
from backend.core.telemetry import emit_event, add_graph_node, add_graph_edge
from backend.core.execution import ExecutionRecord
import time

class ReasoningEngine:
    def check_interactions(self, execution: ExecutionRecord, medications: List[Any], patient: Optional[Any], graph: CompiledKnowledgeGraph):
        # We need the drug ids for extraction
        if isinstance(medications, list) and len(medications) > 0 and hasattr(medications[0], "id"):
            drug_ids = [m.id for m in medications]
        else:
            # Fallback if given a list of strings
            drug_ids = [m for m in medications if isinstance(m, str)]
            
        emit_event(execution, "STAGE_START", "KNOWLEDGE_LOADING", {"drug_ids": drug_ids})
        
        if not graph or not graph.nodes:
            emit_event(execution, "ERROR", "KNOWLEDGE_LOADING", {"message": "Knowledge Graph not provided or empty"})
            return
            
        interactions = []
        patient_alerts = []
        
        # 1. Resolve drugs to canonical ingredients
        emit_event(execution, "STAGE_START", "IDENTITY_RESOLUTION", {})
        ingredient_to_drugs = {}
        for d_id in drug_ids:
            drug_node = graph.get_node(d_id)
            if drug_node:
                add_graph_node(execution, d_id, "Medication", drug_node.properties.get("canonical_name", d_id), drug_node.properties)
                
                # Find ingredients
                ing_edges = graph.get_edges_from(d_id, "CONTAINS_INGREDIENT")
                for edge in ing_edges:
                    ing_id = edge.target_id
                    ingredient_to_drugs.setdefault(ing_id, []).append(d_id)
                    ing_node = graph.get_node(ing_id)
                    ing_name = ing_node.properties.get("name", ing_id) if ing_node else ing_id
                    
                    add_graph_node(execution, ing_id, "Ingredient", ing_name, ing_node.properties if ing_node else {})
                    add_graph_edge(execution, d_id, ing_id, "CONTAINS")
                    
        ingredients_present = list(ingredient_to_drugs.keys())
        emit_event(execution, "STAGE_COMPLETE", "IDENTITY_RESOLUTION", {"ingredients_extracted": ingredients_present})
        
        # 2. Extract properties for all ingredients
        emit_event(execution, "STAGE_START", "CLAIMS_RESOLUTION", {})
        
        # Dictionaries to store extracted properties
        def new_set(): return {ing: set() for ing in ingredients_present}
        ing_effects = new_set()
        ing_inhibits = new_set()
        ing_metabolized_by = new_set()
        ing_targets = new_set()
        ing_pathways = new_set()
        ing_transporter_inhibits = new_set()
        ing_transported_by = new_set()
        
        # Patient specific checks
        ing_contra = new_set()
        ing_renal = new_set()
        ing_hepatic = new_set()
        ing_preg = new_set()
        
        def extract_edges(edge_type, storage_dict, node_type_lbl):
            for ing in ingredients_present:
                edges = graph.get_edges_from(ing, edge_type)
                for d_id in ingredient_to_drugs[ing]:
                    edges.extend(graph.get_edges_from(d_id, edge_type))
                
                for e in edges:
                    storage_dict[ing].add((e.target_id, tuple(ev.get("evidence_id") for ev in e.evidence)))
                    
                for e in edges:
                    add_graph_edge(execution, e.source_id, e.target_id, edge_type)
                    if graph.get_node(e.target_id):
                        add_graph_node(execution, e.target_id, node_type_lbl, graph.get_node(e.target_id).properties.get("name", e.target_id), graph.get_node(e.target_id).properties)
                        for ev in e.evidence:
                            ev_id = ev.get("evidence_id")
                            add_graph_node(execution, ev_id, "Evidence", ev.get("publication", ev_id), ev)
                            add_graph_edge(execution, e.source_id, ev_id, "BACKED_BY")

        extract_edges("HAS_EFFECT", ing_effects, "Effect")
        extract_edges("INHIBITS_ENZYME", ing_inhibits, "Enzyme")
        extract_edges("METABOLIZED_BY", ing_metabolized_by, "Enzyme")
        extract_edges("BINDS_TO_TARGET", ing_targets, "Target")
        extract_edges("MODULATES_PATHWAY", ing_pathways, "Pathway")
        extract_edges("INHIBITS_TRANSPORTER", ing_transporter_inhibits, "Transporter")
        extract_edges("TRANSPORTED_BY", ing_transported_by, "Transporter")
        extract_edges("CONTRAINDICATED_FOR", ing_contra, "Condition")
        extract_edges("REQUIRES_RENAL_ADJUSTMENT_IF", ing_renal, "Condition")
        extract_edges("REQUIRES_HEPATIC_ADJUSTMENT_IF", ing_hepatic, "Condition")
        extract_edges("PREGNANCY_CATEGORY", ing_preg, "Category")
        
        emit_event(execution, "STAGE_COMPLETE", "CLAIMS_RESOLUTION", {})
        
        # 3. Analyze Patient Context
        emit_event(execution, "STAGE_START", "PATIENT_CONTEXT_EVALUATION", {})
        if patient:
            for ing in ingredients_present:
                involved_drugs = ingredient_to_drugs[ing]
                
                # Pregnancy
                if getattr(patient, "is_pregnant", False):
                    for preg_id, ev_ids in ing_preg[ing]:
                        node = graph.get_node(preg_id)
                        preg_name = node.properties.get("name", preg_id).upper() if node else preg_id
                        if "CATEGORY_X" in preg_name or "CATEGORY_D" in preg_name:
                            patient_alerts.append({
                                "type": "PATIENT_CONTRAINDICATION",
                                "drugs": involved_drugs,
                                "ingredients": [ing],
                                "reason": f"Teratogenic in pregnancy ({preg_name})",
                                "severity": "SEVERE",
                                "evidence": list(ev_ids)
                            })
                            
                # Contraindications against active conditions
                active_conds = [c.upper() for c in getattr(patient, "active_conditions", [])]
                for cond_id, ev_ids in ing_contra[ing]:
                    node = graph.get_node(cond_id)
                    cond_name = node.properties.get("name", cond_id).upper() if node else cond_id
                    for ac in active_conds:
                        if ac in cond_name:
                            patient_alerts.append({
                                "type": "PATIENT_CONTRAINDICATION",
                                "drugs": involved_drugs,
                                "ingredients": [ing],
                                "reason": f"Contraindicated for {cond_name}",
                                "severity": "HIGH",
                                "evidence": list(ev_ids)
                            })
                            
                # Renal Adjustment
                renal_clear = getattr(patient, "renal_clearance", "NORMAL").upper()
                if renal_clear != "NORMAL":
                    for cond_id, ev_ids in ing_renal[ing]:
                        node = graph.get_node(cond_id)
                        cond_name = node.properties.get("name", cond_id).upper() if node else cond_id
                        if renal_clear in cond_name or "IMPAIRMENT" in cond_name:
                            patient_alerts.append({
                                "type": "DOSAGE_ADJUSTMENT",
                                "drugs": involved_drugs,
                                "ingredients": [ing],
                                "reason": f"Requires dose adjustment in {renal_clear} renal impairment",
                                "severity": "MODERATE",
                                "evidence": list(ev_ids)
                            })
                            
                # Hepatic Adjustment
                hepatic_clear = getattr(patient, "hepatic_impairment", "NONE").upper()
                if hepatic_clear != "NONE":
                    for cond_id, ev_ids in ing_hepatic[ing]:
                        node = graph.get_node(cond_id)
                        cond_name = node.properties.get("name", cond_id).upper() if node else cond_id
                        if hepatic_clear in cond_name or "IMPAIRMENT" in cond_name:
                            patient_alerts.append({
                                "type": "DOSAGE_ADJUSTMENT",
                                "drugs": involved_drugs,
                                "ingredients": [ing],
                                "reason": f"Requires dose adjustment in {hepatic_clear} hepatic impairment",
                                "severity": "MODERATE",
                                "evidence": list(ev_ids)
                            })

        emit_event(execution, "STAGE_COMPLETE", "PATIENT_CONTEXT_EVALUATION", {})
        
        # 4. Analyze Pairwise and Multi-Drug Interactions
        emit_event(execution, "STAGE_START", "RULES_ENGINE", {})
        
        def check_pk_inhibition(ingA, ingB, inh_dict, metab_dict, type_name):
            inhibitsA = {x for x, _ in inh_dict[ingA]}
            metabB = {x for x, _ in metab_dict[ingB]}
            overlap = inhibitsA.intersection(metabB)
            for x in overlap:
                ev_inv = []
                for e, ev_ids in inh_dict[ingA]:
                    if e == x: ev_inv.extend(ev_ids)
                for e, ev_ids in metab_dict[ingB]:
                    if e == x: ev_inv.extend(ev_ids)
                interactions.append({
                    "type": type_name,
                    "drugs": list(set(ingredient_to_drugs[ingA] + ingredient_to_drugs[ingB])),
                    "ingredients": [ingA, ingB],
                    "mechanism": x,
                    "effect": f"Increased toxicity of {ingB}",
                    "strength": "HIGH",
                    "evidence": list(set(ev_inv))
                })
        
        def check_overlap(ingA, ingB, dict_a, type_name, effect_desc):
            setA = {x for x, _ in dict_a[ingA]}
            setB = {x for x, _ in dict_a[ingB]}
            overlap = setA.intersection(setB)
            for x in overlap:
                ev_inv = []
                for e, ev_ids in dict_a[ingA]:
                    if e == x: ev_inv.extend(ev_ids)
                for e, ev_ids in dict_a[ingB]:
                    if e == x: ev_inv.extend(ev_ids)
                interactions.append({
                    "type": type_name,
                    "drugs": list(set(ingredient_to_drugs[ingA] + ingredient_to_drugs[ingB])),
                    "ingredients": [ingA, ingB],
                    "mechanism": x,
                    "effect": effect_desc,
                    "strength": "MODERATE",
                    "evidence": list(set(ev_inv))
                })

        for i in range(len(ingredients_present)):
            for j in range(i + 1, len(ingredients_present)):
                ing1 = ingredients_present[i]
                ing2 = ingredients_present[j]
                
                involved_drugs = list(set(ingredient_to_drugs[ing1] + ingredient_to_drugs[ing2]))
                
                # A. Direct Interactions
                for e in graph.get_edges_from(ing1, "INCREASED_RISK_WITH"):
                    if e.target_id == ing2:
                        interactions.append({
                            "type": "DIRECT_INTERACTION",
                            "drugs": involved_drugs,
                            "ingredients": [ing1, ing2],
                            "effect": "Increased Risk",
                            "strength": "UNKNOWN",
                            "evidence": [ev.get("evidence_id") for ev in e.evidence]
                        })
                for e in graph.get_edges_from(ing2, "INCREASED_RISK_WITH"):
                    if e.target_id == ing1:
                        interactions.append({
                            "type": "DIRECT_INTERACTION",
                            "drugs": involved_drugs,
                            "ingredients": [ing2, ing1],
                            "effect": "Increased Risk",
                            "strength": "UNKNOWN",
                            "evidence": [ev.get("evidence_id") for ev in e.evidence]
                        })
                        
                # B. Overlapping PD Effects
                check_overlap(ing1, ing2, ing_effects, "OVERLAPPING_EFFECT", "Synergistic Pharmacodynamic Effect")
                
                # C. Overlapping Targets (Synergistic PD)
                check_overlap(ing1, ing2, ing_targets, "OVERLAPPING_TARGET", "Synergistic Target Modulation")
                
                # D. Overlapping Pathways (Synergistic Pathway Modulation)
                check_overlap(ing1, ing2, ing_pathways, "OVERLAPPING_PATHWAY", "Synergistic Pathway Modulation")
                
                # E. PK Enzyme Inhibition
                check_pk_inhibition(ing1, ing2, ing_inhibits, ing_metabolized_by, "PK_ENZYME_INHIBITION")
                check_pk_inhibition(ing2, ing1, ing_inhibits, ing_metabolized_by, "PK_ENZYME_INHIBITION")
                
                # F. PK Transporter Inhibition
                check_pk_inhibition(ing1, ing2, ing_transporter_inhibits, ing_transported_by, "PK_TRANSPORTER_INHIBITION")
                check_pk_inhibition(ing2, ing1, ing_transporter_inhibits, ing_transported_by, "PK_TRANSPORTER_INHIBITION")

        # 5. Multi-Drug Patterns (e.g. 3+ drugs with same effect)
        all_effects = {}
        for ing, eff_set in ing_effects.items():
            for eff, ev_ids in eff_set:
                if eff not in all_effects:
                    all_effects[eff] = []
                all_effects[eff].append((ing, ev_ids))
                
        for eff, items in all_effects.items():
            if len(items) >= 3:
                involved_drugs = []
                evidence_involved = []
                ings = []
                
                for ing, ev_ids in items:
                    ings.append(ing)
                    involved_drugs.extend(ingredient_to_drugs[ing])
                    evidence_involved.extend(ev_ids)
                
                interactions.append({
                    "type": "CUMULATIVE_TOXICITY",
                    "drugs": list(set(involved_drugs)),
                    "ingredients": ings,
                    "effect": eff,
                    "strength": "SEVERE",
                    "evidence": list(set(evidence_involved))
                })
                
        emit_event(execution, "STAGE_COMPLETE", "RULES_ENGINE", {})
        
        # Format results
        execution.clinical_decision = patient_alerts + interactions
