import { eventBus } from '../../core/EventBus.js';
import { executionStore } from '../../services/ExecutionStore.js';
import { selectionManager } from '../../core/SelectionManager.js';

export class PipelineVisualizer {
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
        
        // Listen to selection (e.g. from Runtime queue)
        eventBus.on('SELECTION_CHANGED', (sel) => {
            if (sel.type === 'EXECUTION') {
                this.currentExecution = sel.data;
                this.render();
            }
        });
    }

    render() {
        if (!this.container) return;
        
        if (!this.currentExecution) {
            this.container.innerHTML = `<div class="empty">Select or wait for an execution</div>`;
            return;
        }
        
        // Extract unique stages
        const stagesMap = new Map();
        
        (this.currentExecution.events || []).forEach(evt => {
            if (!evt.stage) return;
            if (!stagesMap.has(evt.stage)) {
                stagesMap.set(evt.stage, { 
                    name: evt.stage, 
                    status: 'PENDING', 
                    events: [] 
                });
            }
            const stg = stagesMap.get(evt.stage);
            stg.events.push(evt);
            
            if (evt.event === 'STAGE_START') stg.status = 'RUNNING';
            if (evt.event === 'STAGE_COMPLETE' || evt.event === 'ANALYSIS_COMPLETED') stg.status = 'COMPLETED';
            if (evt.event === 'ERROR') stg.status = 'ERROR';
        });
        
        const stages = Array.from(stagesMap.values());
        
        this.container.innerHTML = `
            <div class="pipeline-visualizer">
                <div class="pipeline-header">
                    <h4>Execution: ${this.currentExecution.id}</h4>
                </div>
                <div class="pipeline-track">
                    ${stages.map((stg, i) => `
                        <div class="pipeline-node ${stg.status.toLowerCase()}" data-stage="${stg.name}">
                            <div class="node-icon"></div>
                            <div class="node-label">${stg.name.replace(/_/g, ' ')}</div>
                            ${i < stages.length - 1 ? '<div class="node-connector"></div>' : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        const nodes = this.container.querySelectorAll('.pipeline-node');
        nodes.forEach(node => {
            node.addEventListener('click', () => {
                const stageName = node.dataset.stage;
                const stageData = stagesMap.get(stageName);
                selectionManager.select('STAGE', stageData);
            });
        });
    }
}
