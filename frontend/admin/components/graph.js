export class GraphVisualizer {
    constructor(containerElement) {
        this.container = containerElement;
    }

    async render(graphData) {
        // Load Cytoscape dynamically if not already loaded
        if (!window.cytoscape) {
            await new Promise((resolve) => {
                const script = document.createElement('script');
                script.src = 'https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js';
                script.onload = resolve;
                document.head.appendChild(script);
            });
        }

        const elements = [
            ...graphData.nodes.map(n => ({
                data: { id: n.id, label: n.label || n.id, type: n.type }
            })),
            ...graphData.edges.map(e => ({
                data: { id: e.id, source: e.source, target: e.target, label: e.relation }
            }))
        ];

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
                        'font-family': 'Inter, sans-serif',
                        'font-size': '10px',
                        'background-color': '#27272a',
                        'border-width': 2,
                        'border-color': '#3f3f46',
                        'width': 'label',
                        'height': 'label',
                        'padding': '12px',
                        'shape': 'round-rectangle'
                    }
                },
                {
                    selector: 'node[type = "Patient"]',
                    style: { 'background-color': '#18181b', 'border-color': '#71717a' }
                },
                {
                    selector: 'node[type = "Drug"]',
                    style: { 'background-color': '#1e3a8a', 'border-color': '#3b82f6' }
                },
                {
                    selector: 'node[type = "Vocabulary"]',
                    style: { 'background-color': '#4c1d95', 'border-color': '#8b5cf6' }
                },
                {
                    selector: 'node[type = "Claim"]',
                    style: { 'background-color': '#064e3b', 'border-color': '#10b981' }
                },
                {
                    selector: 'node[type = "Evidence"]',
                    style: { 'background-color': '#78350f', 'border-color': '#f59e0b' }
                },
                {
                    selector: 'node[type = "Rule"]',
                    style: { 'background-color': '#831843', 'border-color': '#f43f5e' }
                },
                {
                    selector: 'node[type = "Recommendation"]',
                    style: { 'background-color': '#7f1d1d', 'border-color': '#ef4444' }
                },
                {
                    selector: 'node[type = "Decision"]',
                    style: { 'background-color': '#9d174d', 'border-color': '#f472b6' }
                },
                {
                    selector: 'node[type = "Ingredient"]',
                    style: { 'background-color': '#0f766e', 'border-color': '#2dd4bf' }
                },
                {
                    selector: 'node[type = "Mechanism"]',
                    style: { 'background-color': '#4338ca', 'border-color': '#818cf8' }
                },
                {
                    selector: 'node[type = "Target"]',
                    style: { 'background-color': '#b45309', 'border-color': '#fbbf24' }
                },
                {
                    selector: 'node[type = "Enzyme"]',
                    style: { 'background-color': '#15803d', 'border-color': '#4ade80' }
                },
                {
                    selector: 'node[type = "Transporter"]',
                    style: { 'background-color': '#0369a1', 'border-color': '#38bdf8' }
                },
                {
                    selector: 'node[type = "Pathway"]',
                    style: { 'background-color': '#a21caf', 'border-color': '#e879f9' }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': '#52525b',
                        'target-arrow-color': '#52525b',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'label': 'data(label)',
                        'font-size': '8px',
                        'color': '#a1a1aa',
                        'text-rotation': 'autorotate',
                        'text-margin-y': -8
                    }
                }
            ],
            layout: {
                name: 'breadthfirst',
                directed: true,
                padding: 30,
                spacingFactor: 1.5
            },
            userZoomingEnabled: true,
            userPanningEnabled: true,
            boxSelectionEnabled: false
        });

        this.cy.on('tap', 'node', function(evt){
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
