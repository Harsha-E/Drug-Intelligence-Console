import { api } from '../../services/ApiClient.js';
import { executionStore } from '../../services/ExecutionStore.js';
import { eventBus } from '../../core/EventBus.js';

export class ExecutionReplay {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.render();
    }

    render() {
        if (!this.container) return;
        
        this.container.innerHTML = `
            <div class="execution-replay">
                <h4>Execution Replay</h4>
                <div class="replay-controls">
                    <input type="text" id="replay-id-input" placeholder="Enter Execution ID (ex_...)" class="input-glass" />
                    <button id="replay-load-btn" class="btn-primary">Load & Replay</button>
                </div>
                <div id="replay-status" class="replay-status"></div>
            </div>
        `;
        
        const btn = this.container.querySelector('#replay-load-btn');
        btn.addEventListener('click', () => this.loadExecution());
    }

    async loadExecution() {
        const input = this.container.querySelector('#replay-id-input');
        const status = this.container.querySelector('#replay-status');
        const id = input.value.trim();
        
        if (!id) return;
        
        status.innerHTML = `<span class="pending">Loading...</span>`;
        
        try {
            const data = await api.get(`/history/${id}`);
            // Synthesize execution record from trace_data
            const ex = {
                id: data.execution_id,
                events: data.reasoning_trace?.steps || [],
                clinical_decision: data.evidence || [],
                timestamp: data.timestamp
            };
            executionStore.executions.set(ex.id, ex);
            
            // Inform system
            eventBus.emit('NEW_EXECUTION_DETECTED', ex);
            
            // Emit graph if we have it
            if (data.knowledge_graph) {
                if (data.knowledge_graph.nodes) {
                    eventBus.emit('GRAPH_NODES_ADDED', { execution_id: ex.id, nodes: data.knowledge_graph.nodes });
                }
                if (data.knowledge_graph.edges) {
                    eventBus.emit('GRAPH_EDGES_ADDED', { execution_id: ex.id, edges: data.knowledge_graph.edges });
                }
            }
            
            status.innerHTML = `<span class="success">Loaded successfully</span>`;
        } catch (error) {
            status.innerHTML = `<span class="error">Failed: ${error.message}</span>`;
        }
    }
}
