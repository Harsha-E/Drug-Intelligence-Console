import { KnowledgeGraph } from '../components/Knowledge/KnowledgeGraph.js';
import { PipelineVisualizer } from '../components/Pipeline/PipelineVisualizer.js';
import { TelemetryTimeline } from '../components/Timeline/TelemetryTimeline.js';
import { ExecutionReplay } from '../components/Replay/ExecutionReplay.js';

export function mountAnalyze(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = `
        <div class="view-analyze layout-split">
            <div class="panel" style="flex: 1; display: flex; flex-direction: column; gap: 16px;">
                <div id="replay-container"></div>
                <div id="pipeline-container"></div>
                <div id="timeline-container" style="flex: 1; overflow-y: auto;"></div>
            </div>
            <div id="graph-container" class="panel" style="flex: 2; position: relative;">
                <!-- TEAM C: Knowledge Universe mounts here -->
            </div>
        </div>
    `;
    
    new ExecutionReplay('replay-container');
    new PipelineVisualizer('pipeline-container');
    new TelemetryTimeline('timeline-container');
    
    const kg = new KnowledgeGraph('graph-container');
    setTimeout(() => kg.init(), 0); // Allow DOM to paint
}
