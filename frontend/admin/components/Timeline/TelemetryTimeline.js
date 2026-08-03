import { eventBus } from '../../core/EventBus.js';
import { executionStore } from '../../services/ExecutionStore.js';
import { selectionManager } from '../../core/SelectionManager.js';

export class TelemetryTimeline {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentExecution = null;
        
        eventBus.on('NEW_EXECUTION_DETECTED', (ex) => {
            this.currentExecution = executionStore.getExecution(ex.id);
            this.render();
        });
        
        eventBus.on('EXECUTION_UPDATED', (payload) => {
            if (this.currentExecution && this.currentExecution.id === payload.id) {
                this.render();
            }
        });
        
        eventBus.on('SELECTION_CHANGED', (sel) => {
            if (sel.type === 'EXECUTION') {
                this.currentExecution = sel.data;
                this.render();
            }
        });
    }

    render() {
        if (!this.container) return;
        
        if (!this.currentExecution || !this.currentExecution.events || this.currentExecution.events.length === 0) {
            this.container.innerHTML = `<div class="empty">No events for timeline</div>`;
            return;
        }
        
        const events = this.currentExecution.events;
        const startTime = events[0].timestamp;
        
        this.container.innerHTML = `
            <div class="telemetry-timeline">
                <h4>Telemetry Timeline</h4>
                <div class="timeline-track">
                    ${events.map((evt, i) => {
                        const relTime = (evt.timestamp - startTime).toFixed(2);
                        return `
                            <div class="timeline-event ${evt.event === 'ERROR' ? 'error' : ''}" data-index="${i}">
                                <div class="timeline-time">+${relTime}s</div>
                                <div class="timeline-marker"></div>
                                <div class="timeline-content">
                                    <span class="evt-stage">${evt.stage || 'CORE'}</span>
                                    <span class="evt-name">${evt.event}</span>
                                    <span class="evt-duration">${evt.duration_ms ? evt.duration_ms + 'ms' : ''}</span>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
        
        const evtNodes = this.container.querySelectorAll('.timeline-event');
        evtNodes.forEach(node => {
            node.addEventListener('click', () => {
                const idx = parseInt(node.dataset.index, 10);
                const eventData = events[idx];
                selectionManager.select('EVENT', eventData);
            });
        });
    }
}
