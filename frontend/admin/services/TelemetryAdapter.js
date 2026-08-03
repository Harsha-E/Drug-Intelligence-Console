import { eventBus } from '../core/EventBus.js';

class TelemetryAdapter {
    constructor() {
        this.init();
    }

    init() {
        eventBus.on('RAW_SSE_EVENT', (data) => this.processEvent(data));
    }

    processEvent(payload) {
        // Assume payload follows the frozen contract:
        // { event_id, execution_id, stage, event (START|COMPLETE|ERROR), timestamp, duration_ms, inputs, outputs, graph_changes... }
        
        if (!payload || !payload.execution_id) {
            console.warn('[TelemetryAdapter] Ignored malformed payload', payload);
            return;
        }

        const { execution_id, stage, event, graph_changes } = payload;
        
        // Broadcast the specific execution event
        eventBus.emit('EXECUTION_UPDATED', payload);

        // Broadcast specific granular events to drive UI without tight coupling
        if (event === 'START') {
            eventBus.emit('STAGE_STARTED', payload);
        } else if (event === 'COMPLETE') {
            eventBus.emit('STAGE_COMPLETED', payload);
        } else if (event === 'ERROR') {
            eventBus.emit('STAGE_ERROR', payload);
        }

        // If graph changes exist, broadcast them for the Knowledge Universe team
        if (graph_changes) {
            if (graph_changes.added_nodes && graph_changes.added_nodes.length > 0) {
                eventBus.emit('GRAPH_NODES_ADDED', { execution_id, nodes: graph_changes.added_nodes });
            }
            if (graph_changes.added_edges && graph_changes.added_edges.length > 0) {
                eventBus.emit('GRAPH_EDGES_ADDED', { execution_id, edges: graph_changes.added_edges });
            }
        }
    }
}

export const telemetryAdapter = new TelemetryAdapter();
