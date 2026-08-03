from typing import List, Dict, Any, Optional

class Node:
    def __init__(self, node_id: str, node_type: str, properties: Dict[str, Any]):
        self.node_id = node_id
        self.node_type = node_type
        self.properties = properties
        
class Edge:
    def __init__(self, source_id: str, target_id: str, edge_type: str, evidence: List[Dict[str, Any]] = None):
        self.source_id = source_id
        self.target_id = target_id
        self.edge_type = edge_type
        self.evidence = evidence or [] # List of evidence property dicts ensuring provenance

class CompiledKnowledgeGraph:
    """
    In-memory knowledge graph representing the offline compiled clinical registry.
    This replaces flat JSON file lookups during reasoning.
    """
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        # edges are stored as source_id -> list of Edges
        self.edges: Dict[str, List[Edge]] = {}
        
    def add_node(self, node_id: str, node_type: str, properties: Dict[str, Any]):
        if node_id not in self.nodes:
            self.nodes[node_id] = Node(node_id, node_type, properties)
            
    def add_edge(self, source_id: str, target_id: str, edge_type: str, evidence: List[Dict[str, Any]] = None):
        edge = Edge(source_id, target_id, edge_type, evidence)
        if source_id not in self.edges:
            self.edges[source_id] = []
        self.edges[source_id].append(edge)
        
    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)
        
    def get_edges_from(self, source_id: str, edge_type: str = None) -> List[Edge]:
        edges = self.edges.get(source_id, [])
        if edge_type:
            return [e for e in edges if e.edge_type == edge_type]
        return edges

    def get_edges_to(self, target_id: str, edge_type: str = None) -> List[Edge]:
        # This is a bit slower since we iterate all edges, 
        # in a real DB it would be indexed. Good enough for in-memory graph.
        result = []
        for src, edges in self.edges.items():
            for e in edges:
                if e.target_id == target_id and (not edge_type or e.edge_type == edge_type):
                    result.append(e)
        return result
        
    @classmethod
    def build_from_registry(cls, registry_dir: str) -> 'CompiledKnowledgeGraph':
        import json, os
        
        graph = cls()
        
        # Load compiled registry
        drugs_file = os.path.join(registry_dir, "drug_lookup.json")
        claims_file = os.path.join(registry_dir, "claims.json")
        evidence_file = os.path.join(registry_dir, "evidence.json")
        
        if not os.path.exists(drugs_file) or not os.path.exists(claims_file):
            return graph
            
        with open(drugs_file, "r") as f:
            drugs = json.load(f)
        with open(claims_file, "r") as f:
            claims = json.load(f)
        with open(evidence_file, "r") as f:
            evidence_db = json.load(f)
            
        # 1. Build Drug & Ingredient Nodes
        for d_id, drug_data in drugs.items():
            graph.add_node(d_id, "Medication", drug_data.get("identity", {}))
            for ing in drug_data.get("ingredients", []):
                i_id = ing["ingredient_id"]
                graph.add_node(i_id, "Ingredient", {"name": ing.get("name")})
                graph.add_edge(d_id, i_id, "CONTAINS_INGREDIENT")
                
        # 2. Build Mechanism Nodes & Edges from Claims
        for c_id, claim in claims.items():
            subj = claim["subject"]
            pred = claim["predicate"]
            obj = claim["object"]
            obj_name = claim.get("object_name", obj)
            
            # Resolve evidence objects for this claim
            ev_list = []
            for ev_ref in claim.get("evidence_refs", []):
                ev = evidence_db.get(ev_ref)
                if ev:
                    ev_list.append(ev)
                    
            if pred == "HAS_EFFECT":
                graph.add_node(obj, "Effect", {"name": obj_name})
                graph.add_edge(subj, obj, pred, ev_list)
            elif pred in ["INHIBITS_ENZYME", "METABOLIZED_BY"]:
                graph.add_node(obj, "Enzyme", {"name": obj_name})
                graph.add_edge(subj, obj, pred, ev_list)
            elif pred in ["INHIBITS_TRANSPORTER", "TRANSPORTED_BY"]:
                graph.add_node(obj, "Transporter", {"name": obj_name})
                graph.add_edge(subj, obj, pred, ev_list)
            elif pred == "BINDS_TO_TARGET":
                graph.add_node(obj, "Target", {"name": obj_name})
                graph.add_edge(subj, obj, pred, ev_list)
            elif pred == "MODULATES_PATHWAY":
                graph.add_node(obj, "Pathway", {"name": obj_name})
                graph.add_edge(subj, obj, pred, ev_list)
            elif pred == "ALTERS_LAB":
                graph.add_node(obj, "Laboratory", {"name": obj_name})
                graph.add_edge(subj, obj, pred, ev_list)
            elif pred in ["CONTRAINDICATED_FOR", "REQUIRES_RENAL_ADJUSTMENT_IF", "REQUIRES_HEPATIC_ADJUSTMENT_IF"]:
                graph.add_node(obj, "Condition", {"name": obj_name})
                graph.add_edge(subj, obj, pred, ev_list)
            elif pred == "PREGNANCY_CATEGORY":
                graph.add_node(obj, "Category", {"name": obj_name})
                graph.add_edge(subj, obj, pred, ev_list)
            elif pred == "INCREASED_RISK_WITH":
                # Ensure the target ingredient node exists
                graph.add_node(obj, "Ingredient", {"name": obj})
                graph.add_edge(subj, obj, pred, ev_list)
                
        return graph
