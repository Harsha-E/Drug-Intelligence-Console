import { eventBus } from '../../core/EventBus.js';
import { executionStore } from '../../services/ExecutionStore.js';
import { selectionManager } from '../../core/SelectionManager.js';

export class RuntimeObservatory {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        
        eventBus.on('NEW_EXECUTION_DETECTED', () => this.render());
        eventBus.on('EXECUTION_UPDATED', () => this.render());
        
        this.render();
    }

    render() {
        if (!this.container) return;
        
        const executions = executionStore.getAllExecutions().reverse();
        
        this.container.innerHTML = `
            <div class="runtime-observatory">
                <div class="executions-grid">
                    ${executions.map(ex => this.renderCard(ex)).join('')}
                    ${executions.length === 0 ? '<div class="empty">Waiting for requests...</div>' : ''}
                </div>
            </div>
        `;
        
        // Bind clicks
        const cards = this.container.querySelectorAll('.execution-card');
        cards.forEach(card => {
            card.addEventListener('click', () => {
                const id = card.dataset.id;
                selectionManager.select('EXECUTION', executionStore.getExecution(id));
                window.location.hash = `#/analyze?id=${id}`;
            });
        });
    }

    renderCard(ex) {
        // Find latest stage
        let latestStage = "INITIALIZING";
        let isComplete = false;
        let isError = false;
        
        const events = ex.events || [];
        if (events.length > 0) {
            const last = events[events.length - 1];
            latestStage = last.stage || latestStage;
            if (last.event === "ANALYSIS_COMPLETED") isComplete = true;
            if (last.event === "ERROR") isError = true;
        }
        
        return `
            <div class="glass-panel execution-card ${isComplete ? 'completed' : isError ? 'error' : 'running'}" data-id="${ex.id}">
                <div class="ex-header">
                    <span class="ex-id">${ex.id}</span>
                    <span class="ex-status">${isComplete ? 'COMPLETED' : isError ? 'FAILED' : 'RUNNING'}</span>
                </div>
                <div class="ex-stage">
                    ${latestStage}
                </div>
                <div class="ex-footer">
                    <span>${events.length} Events</span>
                </div>
            </div>
        `;
    }
}
