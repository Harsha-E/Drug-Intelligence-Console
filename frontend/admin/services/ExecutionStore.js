import { eventBus } from '../core/EventBus.js';
import { api } from './ApiClient.js';

class ExecutionStore {
    constructor() {
        this.executions = new Map(); // id -> { stages: [], events: [], graph: {}, metrics: {} }
        this.activeExecutionId = null;
        
        eventBus.on('EXECUTION_UPDATED', (payload) => this._handleUpdate(payload));
    }

    _handleUpdate(payload) {
        const id = payload.execution_id;
        if (!this.executions.has(id)) {
            this.executions.set(id, {
                id,
                stages: new Map(), // stage_name -> latest payload
                events: [],
                nodes: new Map(),
                edges: []
            });
            eventBus.emit('NEW_EXECUTION_DETECTED', { execution_id: id });
        }

        const execution = this.executions.get(id);
        execution.events.push(payload);
        
        if (payload.stage) {
            execution.stages.set(payload.stage, payload);
        }

        if (payload.graph_changes) {
            if (payload.graph_changes.added_nodes) {
                payload.graph_changes.added_nodes.forEach(n => execution.nodes.set(n.id, n));
            }
            if (payload.graph_changes.added_edges) {
                payload.graph_changes.added_edges.forEach(e => execution.edges.push(e));
            }
        }
    }

    getExecution(id) {
        return this.executions.get(id);
    }
    
    getAllExecutions() {
        return Array.from(this.executions.values());
    }

    async fetchHistorical(id) {
        try {
            const data = await api.get(`/history/${id}`);
            // In a real scenario, we'd hydrate this.executions with historical data
            return data;
        } catch (e) {
            console.error("Failed to fetch history", e);
            return null;
        }
    }
}

export const executionStore = new ExecutionStore();
