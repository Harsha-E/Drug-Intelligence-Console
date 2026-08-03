import { eventBus } from '../../core/EventBus.js';
import { selectionManager } from '../../core/SelectionManager.js';

export class KnowledgeGraph {
    constructor(containerId) {
        this.containerId = containerId;
        this.cy = null;
        
        eventBus.on('GRAPH_NODES_ADDED', (payload) => this.addNodes(payload.nodes));
        eventBus.on('GRAPH_EDGES_ADDED', (payload) => this.addEdges(payload.edges));
        eventBus.on('NEW_EXECUTION_DETECTED', () => this.clear());
    }

    init() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        this.cy = cytoscape({
            container: container,
            elements: [],
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': '#0047FF',
                        'label': 'data(label)',
                        'color': '#ffffff',
                        'font-size': '10px',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'width': 60,
                        'height': 60
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': 'rgba(255, 255, 255, 0.1)',
                        'target-arrow-color': 'rgba(255, 255, 255, 0.3)',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'label': 'data(label)',
                        'font-size': '8px',
                        'color': '#888888',
                        'text-rotation': 'autorotate'
                    }
                }
            ],
            layout: { name: 'cose' }
        });

        this.cy.on('tap', 'node', (evt) => {
            selectionManager.select('NODE', evt.target.data());
        });
        this.cy.on('tap', 'edge', (evt) => {
            selectionManager.select('EDGE', evt.target.data());
        });
    }

    clear() {
        if (this.cy) this.cy.elements().remove();
    }

    addNodes(nodes) {
        if (!this.cy) return;
        const cyNodes = nodes.map(n => ({
            group: 'nodes',
            data: { id: n.id, label: n.label, type: n.type }
        }));
        this.cy.add(cyNodes);
        this.runLayout();
    }

    addEdges(edges) {
        if (!this.cy) return;
        const cyEdges = edges.map(e => ({
            group: 'edges',
            data: { id: `${e.source}-${e.target}-${e.type}`, source: e.source, target: e.target, label: e.type }
        }));
        this.cy.add(cyEdges);
        this.runLayout();
    }

    runLayout() {
        if (this.cy) {
            this.cy.layout({ name: 'cose', animate: true, animationDuration: 300 }).run();
        }
    }
}
