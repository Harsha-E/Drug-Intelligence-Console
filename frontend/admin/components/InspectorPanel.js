/**
 * InspectorPanel.js - IDE-style Multi-Tab Inspector for DIC Control Center
 */
export class InspectorPanel {
    render() {
        this.container = document.createElement('div');
        this.container.style.width = '100%';
        this.container.style.height = '100%';
        this.container.style.display = 'flex';
        this.container.style.flexDirection = 'column';
        
        this.container.innerHTML = `
            <div class="devtools-header" style="flex-shrink: 0; border-bottom: 1px solid var(--border-color); background: rgba(0,0,0,0.2);">
                <div class="devtools-tabs" style="display: flex; gap: 2px; padding: 4px; overflow-x: auto;">
                    <button class="devtools-tab active" data-tab="dt-request">Req</button>
                    <button class="devtools-tab" data-tab="dt-processing">Proc</button>
                    <button class="devtools-tab" data-tab="dt-response">Res</button>
                    <button class="devtools-tab" data-tab="dt-performance">Perf</button>
                    <button class="devtools-tab" data-tab="dt-telemetry">Telem</button>
                    <button class="devtools-tab" data-tab="dt-rules">Rules</button>
                    <button class="devtools-tab" data-tab="dt-evidence">Evid</button>
                    <button class="devtools-tab" data-tab="dt-graph">Graph</button>
                    <button class="devtools-tab" data-tab="dt-json">JSON</button>
                </div>
            </div>
            <div class="devtools-content" id="devtools-content" style="flex: 1; overflow-y: auto; padding: 14px;">
                <div style="color: var(--text-muted); font-size: 0.8rem; text-align: center; margin-top: 32px; font-family: monospace;">Select an execution from Live Requests to inspect telemetry.</div>
            </div>
        `;
        
        return this.container;
    }

    update() {
        const tabs = this.container.querySelectorAll('.devtools-tab');
        tabs.forEach(tab => {
            tab.onclick = () => {
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                this.container.querySelectorAll('.devtools-pane').forEach(p => p.style.display = 'none');
                const pane = this.container.querySelector('#' + tab.dataset.tab);
                if (pane) pane.style.display = 'block';
            };
        });

        if (!this.bound) {
            window.addEventListener('dic:analysis-loaded', (e) => this.onAnalysisLoaded(e.detail));
            window.addEventListener('dic:node-selected', (e) => this.onNodeSelected(e.detail));
            this.bound = true;
        }
    }

    formatJSON(obj) {
        if (obj === undefined) return '<span class="json-null">undefined</span>';
        if (obj === null) return '<span class="json-null">null</span>';
        
        const str = JSON.stringify(obj, null, 2);
        return str.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
            let cls = 'json-number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) cls = 'json-key';
                else cls = 'json-string';
            } else if (/true|false/.test(match)) {
                cls = 'json-boolean';
            } else if (/null/.test(match)) {
                cls = 'json-null';
            }
            return '<span class="' + cls + '">' + match + '</span>';
        });
    }

    onAnalysisLoaded(record) {
        const content = this.container.querySelector('#devtools-content');
        if (!content) return;

        const rawInput = record.raw?.raw_input || record.raw?.patient_summary || {
            patient_id: record.patient_id,
            medications: record.medications,
            request_timestamp: record.formattedDate
        };

        const rawOutput = record.raw?.raw_output || record.raw?.report || {
            status: record.status,
            total_latency_ms: record.total_latency_ms,
            clinical_decision: record.clinical_decision
        };

        const rulesFired = record.clinical_decision.filter(c => c.type || c.rule_id) || [];
        const evidenceUsed = record.clinical_decision.filter(c => c.evidence || c.claims) || [];

        content.innerHTML = `
            <div id="dt-request" class="devtools-pane" style="display: block;">
                <h4 style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 8px;">RAW INPUT PAYLOAD</h4>
                <div class="json-viewer" style="font-family: monospace; font-size: 0.78rem;">${this.formatJSON(rawInput)}</div>
            </div>

            <div id="dt-processing" class="devtools-pane" style="display: none;">
                <h4 style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 8px;">EXECUTION TIMELINE EVENTS</h4>
                <div class="json-viewer" style="font-family: monospace; font-size: 0.78rem;">${this.formatJSON(record.events.length ? record.events : {
                    stage_1: "Input Received",
                    stage_2: "RxNorm Terminology Normalization",
                    stage_3: "Graph Traversal",
                    stage_4: "Rules Evaluation",
                    stage_5: "Completed"
                })}</div>
            </div>

            <div id="dt-response" class="devtools-pane" style="display: none;">
                <h4 style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 8px;">RAW OUTPUT PAYLOAD</h4>
                <div class="json-viewer" style="font-family: monospace; font-size: 0.78rem;">${this.formatJSON(rawOutput)}</div>
            </div>

            <div id="dt-performance" class="devtools-pane" style="display: none;">
                <h4 style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 8px;">EXECUTION METRICS</h4>
                <div class="json-viewer" style="font-family: monospace; font-size: 0.78rem;">${this.formatJSON({
                    execution_id: record.analysis_id,
                    total_latency_ms: record.total_latency_ms,
                    status: record.status,
                    medications_analyzed: record.medications.length,
                    timestamp: record.formattedDate
                })}</div>
            </div>

            <div id="dt-telemetry" class="devtools-pane" style="display: none;">
                <h4 style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 8px;">REALTIME TELEMETRY TRACE</h4>
                <div class="json-viewer" style="font-family: monospace; font-size: 0.78rem;">${this.formatJSON({
                    channel: "SSE /api/v1/history/stream",
                    patient_id: record.patient_id,
                    event_type: "ANALYSIS_COMPLETED",
                    latency_ms: record.total_latency_ms
                })}</div>
            </div>

            <div id="dt-rules" class="devtools-pane" style="display: none;">
                <h4 style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 8px;">CLINICAL RULES FIRED (${rulesFired.length})</h4>
                <div class="json-viewer" style="font-family: monospace; font-size: 0.78rem;">${this.formatJSON(rulesFired.length ? rulesFired : { rules_matched: 0, status: "No severe contraindications triggered" })}</div>
            </div>

            <div id="dt-evidence" class="devtools-pane" style="display: none;">
                <h4 style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 8px;">EVIDENCE STATEMENTS USED (${evidenceUsed.length})</h4>
                <div class="json-viewer" style="font-family: monospace; font-size: 0.78rem;">${this.formatJSON(evidenceUsed.length ? evidenceUsed : { evidence_sources: ["FDA Label Database", "RxNorm DDI Matrix"] })}</div>
            </div>

            <div id="dt-graph" class="devtools-pane" style="display: none;">
                <h4 style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 8px;">GRAPH NODES & EDGES</h4>
                <div class="json-viewer" style="font-family: monospace; font-size: 0.78rem;">${this.formatJSON(record.graph)}</div>
            </div>

            <div id="dt-json" class="devtools-pane" style="display: none;">
                <h4 style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 8px;">COMPLETE JSON RECORD</h4>
                <div class="json-viewer" style="font-family: monospace; font-size: 0.78rem;">${this.formatJSON(record.raw)}</div>
            </div>
        `;

        this.update();
    }

    onNodeSelected(detail) {
        const content = this.container.querySelector('#devtools-content');
        if (!content) return;

        const nodeData = detail.nodeData || {};
        
        let graphTab = this.container.querySelector('#dt-graph');
        if (!graphTab) {
            graphTab = document.createElement('div');
            graphTab.id = 'dt-graph';
            graphTab.className = 'devtools-pane';
            content.appendChild(graphTab);
        }

        // Activate Graph tab
        const tabs = this.container.querySelectorAll('.devtools-tab');
        tabs.forEach(t => t.classList.remove('active'));
        const gTab = this.container.querySelector('[data-tab="dt-graph"]');
        if (gTab) gTab.classList.add('active');

        this.container.querySelectorAll('.devtools-pane').forEach(p => p.style.display = 'none');
        graphTab.style.display = 'block';

        graphTab.innerHTML = `
            <h4 style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--accent); margin-bottom: 8px;">SELECTED NODE METADATA</h4>
            <div class="json-viewer" style="font-family: monospace; font-size: 0.78rem;">${this.formatJSON(nodeData)}</div>
        `;
    }
}
