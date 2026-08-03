export class InspectorPanel {
    render() {
        this.container = document.createElement('div');
        this.container.style.width = '100%';
        this.container.style.height = '100%';
        this.container.style.display = 'flex';
        this.container.style.flexDirection = 'column';
        
        this.container.innerHTML = `
            <div class="devtools-header" style="flex-shrink: 0;">
                <div class="devtools-tabs" style="display:flex; gap:4px; padding: 4px;">
                    <button class="devtools-tab active" data-tab="dt-request">Req</button>
                    <button class="devtools-tab" data-tab="dt-processing">Proc</button>
                    <button class="devtools-tab" data-tab="dt-response">Res</button>
                    <button class="devtools-tab" data-tab="dt-performance">Perf</button>
                </div>
            </div>
            <div class="devtools-content" id="devtools-content" style="flex: 1; overflow-y: auto; padding: 12px;">
                <div style="color: var(--text-muted); font-size: 0.8rem; text-align: center; margin-top: 24px;">Select an execution to inspect</div>
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

        // Listen for execution loaded events from WorkspacePanel
        if (!this.bound) {
            window.addEventListener('dic:analysis-loaded', (e) => this.onAnalysisLoaded(e.detail));
            this.bound = true;
        }
    }

    formatJSON(obj) {
        if (!obj) return 'null';
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
        
        content.innerHTML = `
            <div id="dt-request" class="devtools-pane" style="display: block;">
                <h4 style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 8px;">RAW INPUT PAYLOAD</h4>
                <div class="json-viewer">${this.formatJSON(record.raw_input || record.patient_summary)}</div>
            </div>
            <div id="dt-processing" class="devtools-pane" style="display: none;">
                <h4 style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 8px;">TIMELINE EVENTS</h4>
                <div class="json-viewer" id="dt-processing-json">${this.formatJSON(record.events)}</div>
            </div>
            <div id="dt-response" class="devtools-pane" style="display: none;">
                <h4 style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 8px;">RAW OUTPUT PAYLOAD</h4>
                <div class="json-viewer">${this.formatJSON(record.raw_output || record.report)}</div>
            </div>
            <div id="dt-performance" class="devtools-pane" style="display: none;">
                <h4 style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 8px;">EXECUTION METRICS</h4>
                <div class="json-viewer">${this.formatJSON({
                    execution_id: record.analysis_id,
                    total_latency_ms: record.total_latency_ms,
                    status: record.status,
                    versions: record.versions
                })}</div>
            </div>
        `;
    }
}
