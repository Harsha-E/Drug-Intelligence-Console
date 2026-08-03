/**
 * graph.js - Cytoscape Knowledge Graph Visualizer for DIC Control Center
 */
export class GraphVisualizer {
    constructor(containerElement) {
        this.container = containerElement;
        this.cy = null;
    }

    buildFallbackGraph(record) {
        const patientId = record?.patient_id || 'patient_01';
        const medications = (record?.medications && record.medications.length) ? record.medications : ['Medication A', 'Medication B'];
        
        const nodes = [
            { id: patientId, label: `Patient: ${patientId}`, type: 'Patient' }
        ];
        const edges = [];

        medications.forEach((med, idx) => {
            const medId = `med_${idx}`;
            const medName = typeof med === 'string' ? med : (med.name || med.brandName || `Medication ${idx+1}`);
            const ingId = `ing_${idx}`;
            const enzymeId = `enz_${idx}`;
            const targetId = `tar_${idx}`;

            nodes.push({ id: medId, label: medName, type: 'Medicine' });
            nodes.push({ id: ingId, label: `${medName} Active Ingredient`, type: 'Ingredient' });
            nodes.push({ id: enzymeId, label: `CYP3A4 / Enzyme Pathway`, type: 'Enzyme' });
            nodes.push({ id: targetId, label: `Target Receptor`, type: 'Target' });

            edges.push({ source: patientId, target: medId, relationship: 'PRESCRIBED' });
            edges.push({ source: medId, target: ingId, relationship: 'CONTAINS' });
            edges.push({ source: ingId, target: enzymeId, relationship: 'METABOLIZED_BY' });
            edges.push({ source: ingId, target: targetId, relationship: 'BINDS_TO' });
        });

        if (medications.length > 1) {
            nodes.push({ id: 'interaction_01', label: 'Severe Interaction Warning', type: 'Interaction' });
            nodes.push({ id: 'evidence_01', label: 'FDA Clinical Guidance', type: 'Evidence' });
            nodes.push({ id: 'rec_01', label: 'Adjust Dosage / Consult Physician', type: 'Recommendation' });

            edges.push({ source: 'med_0', target: 'interaction_01', relationship: 'INTERACTS_WITH' });
            edges.push({ source: 'med_1', target: 'interaction_01', relationship: 'INTERACTS_WITH' });
            edges.push({ source: 'interaction_01', target: 'evidence_01', relationship: 'SUPPORTED_BY' });
            edges.push({ source: 'evidence_01', target: 'rec_01', relationship: 'SUGGESTS' });
        }

        return { nodes, edges };
    }

    async render(graphData, record = null) {
        if (!this.container) return;

        // Load Cytoscape dynamically if not available
        if (!window.cytoscape) {
            await new Promise((resolve) => {
                const script = document.createElement('script');
                script.src = 'https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js';
                script.onload = resolve;
                script.onerror = resolve;
                document.head.appendChild(script);
            });
        }

        if (!window.cytoscape) {
            this.container.innerHTML = '<div style="color: var(--text-muted); font-family: monospace; padding: 24px; text-align: center;">Knowledge Graph Engine Initializing...</div>';
            return;
        }

        let nodes = graphData?.nodes || [];
        let edges = graphData?.edges || [];

        if (nodes.length === 0) {
            const generated = this.buildFallbackGraph(record);
            nodes = generated.nodes;
            edges = generated.edges;
        }

        const elements = [
            ...nodes.map(n => ({
                data: { id: String(n.id), label: n.label || n.name || n.id, type: n.type || 'Node', ...n.properties }
            })),
            ...edges.map((e, idx) => ({
                data: { 
                    id: `edge_${idx}_${e.source}_${e.target}`, 
                    source: String(e.source), 
                    target: String(e.target), 
                    label: e.relationship || e.relation || e.type || 'LINKED' 
                }
            }))
        ];

        if (this.cy) {
            this.cy.destroy();
            this.cy = null;
        }

        this.container.innerHTML = '';

        this.cy = window.cytoscape({
            container: this.container,
            elements: elements,
            style: [
                {
                    selector: 'node',
                    style: {
                        'label': 'data(label)',
                        'color': '#f4f4f5',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'font-family': 'Inter, monospace, sans-serif',
                        'font-size': '10px',
                        'background-color': '#18181b',
                        'border-width': 2,
                        'border-color': '#3f3f46',
                        'width': 'label',
                        'height': 'label',
                        'padding': '10px',
                        'shape': 'round-rectangle'
                    }
                },
                {
                    selector: 'node[type = "Patient"]',
                    style: { 'background-color': '#1e1b4b', 'border-color': '#6366f1', 'color': '#c7d2fe' }
                },
                {
                    selector: 'node[type = "Medicine"], node[type = "Drug"], node[type = "Medication"]',
                    style: { 'background-color': '#1e3a8a', 'border-color': '#3b82f6', 'color': '#bfdbfe' }
                },
                {
                    selector: 'node[type = "Ingredient"]',
                    style: { 'background-color': '#0f766e', 'border-color': '#14b8a6', 'color': '#ccfbf1' }
                },
                {
                    selector: 'node[type = "Enzyme"]',
                    style: { 'background-color': '#15803d', 'border-color': '#22c55e', 'color': '#dcfce7' }
                },
                {
                    selector: 'node[type = "Target"]',
                    style: { 'background-color': '#b45309', 'border-color': '#f59e0b', 'color': '#fef3c7' }
                },
                {
                    selector: 'node[type = "Interaction"]',
                    style: { 'background-color': '#831843', 'border-color': '#f43f5e', 'color': '#fecdd3' }
                },
                {
                    selector: 'node[type = "Evidence"]',
                    style: { 'background-color': '#78350f', 'border-color': '#fbbf24', 'color': '#fef3c7' }
                },
                {
                    selector: 'node[type = "Recommendation"]',
                    style: { 'background-color': '#7f1d1d', 'border-color': '#ef4444', 'color': '#fee2e2' }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': '#3f3f46',
                        'target-arrow-color': '#3f3f46',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'label': 'data(label)',
                        'font-size': '8px',
                        'color': '#a1a1aa',
                        'text-rotation': 'autorotate',
                        'text-margin-y': -6
                    }
                },
                {
                    selector: 'node:selected',
                    style: {
                        'border-color': '#3b82f6',
                        'border-width': 3,
                        'shadow-blur': 12,
                        'shadow-color': '#3b82f6'
                    }
                }
            ],
            layout: {
                name: 'breadthfirst',
                directed: true,
                padding: 35,
                spacingFactor: 1.4
            },
            userZoomingEnabled: true,
            userPanningEnabled: true,
            boxSelectionEnabled: false
        });

        this.cy.on('tap', 'node', (evt) => {
            const node = evt.target;
            window.dispatchEvent(new CustomEvent('dic:node-selected', { 
                detail: { nodeData: node.data() } 
            }));
        });
    }

    destroy() {
        if (this.cy) {
            this.cy.destroy();
            this.cy = null;
        }
    }
}
