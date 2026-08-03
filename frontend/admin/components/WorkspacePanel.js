import { GraphVisualizer } from './components/graph.js';

export class WorkspacePanel {
    render() {
        this.container = document.createElement('div');
        this.container.style.width = '100%';
        this.container.style.height = '100%';
        this.container.style.display = 'flex';
        this.container.style.flexDirection = 'column';
        
        this.container.innerHTML = `
            <header class="topbar" style="flex-shrink: 0;">
                <div class="breadcrumbs" id="breadcrumbs">Live Requests</div>
                <div class="topbar-actions">
                    <div class="status-indicator" id="connection-status">
                        <span class="pulse green"></span> System Online
                    </div>
                </div>
            </header>
            <div class="content" id="app-content" style="flex: 1; overflow-y: auto;">
                <!-- Content injected here by router -->
            </div>
        `;
        return this.container;
    }

    update() {
        this.content = this.container.querySelector('#app-content');
        this.breadcrumbs = this.container.querySelector('#breadcrumbs');
        this.currentEventSource = null;
        
        if (!this.bound) {
            window.addEventListener('hashchange', () => this.route());
            if (!window.location.hash) window.location.hash = '#/live-analyses';
            this.bound = true;
        }
        this.route();
    }

    async route() {
        if (!this.content) return;
        const hash = window.location.hash.slice(1) || '/live-analyses';
        const path = hash.split('?')[0];
        
        this.breadcrumbs.textContent = path.replace('/', '').toUpperCase();
        this.content.innerHTML = '<div style="color: #a1a1aa; font-family: monospace; animation: pulse 1.5s infinite;">LOADING...</div>';

        try {
            if (path === '/live-analyses') await this.renderLiveAnalyses();
            else if (path === '/event-log') await this.renderEventLog();
            else if (path.startsWith('/analysis/')) await this.renderExecutionExplorer(path.split('/')[2]);
            else if (path === '/api-keys') await this.renderApiKeys();
            else if (path === '/metrics') await this.renderMetrics();
            else if (path === '/runtime') await this.renderRuntime();
            else if (path === '/deployment') await this.renderDeployment();
            else if (path === '/diagnostics') await this.renderDiagnostics();
            else if (['/knowledge', '/claims', '/evidence', '/rules', '/vocabulary', '/mappings', '/registry'].includes(path)) {
                await this.renderRegistry(path.slice(1) === 'registry' ? 'manifest' : path.slice(1));
            }
            else this.content.innerHTML = '<div class="glass-card"><h2 class="card-value">View Active</h2><p>Monitoring operational telemetry.</p></div>';
        } catch (e) {
            this.content.innerHTML = `<div class="glass-card" style="border-color: var(--danger);"><h2 class="card-value" style="color: var(--danger);">Error</h2><p>${e.message}</p></div>`;
        }
    }

    connectSSE() {
        if (this.currentEventSource) return;

        let reconnectTimeout = 1000;
        const statusEl = this.container.querySelector('#connection-status');
        
        const connect = () => {
            this.currentEventSource = new EventSource('/api/v1/history/stream');
            
            this.currentEventSource.onopen = () => {
                reconnectTimeout = 1000;
                if (statusEl) {
                    statusEl.innerHTML = '<span class="pulse green"></span> System Online';
                    statusEl.style.color = '';
                    statusEl.style.borderColor = '';
                }
            };
            
            this.currentEventSource.onmessage = (event) => {
                const h = JSON.parse(event.data);
                const tbody = this.container.querySelector('#live-analyses-tbody');
                if (tbody) {
                    const noData = this.container.querySelector('#no-data');
                    if (noData) noData.remove();
                    
                    const tr = document.createElement('tr');
                    tr.onclick = () => window.location.hash = '#/analysis/' + h.analysis_id;
                    tr.innerHTML = `
                        <td style="font-family: monospace; color: var(--accent);">${h.analysis_id}</td>
                        <td style="font-size: 0.8rem; color: var(--text-muted);">${new Date(h.request_timestamp).toLocaleString()}</td>
                        <td>${h.patient_summary?.patient_id || 'Unknown'}</td>
                        <td style="font-family: monospace;">${h.total_latency_ms}ms</td>
                        <td><span class="badge ${h.status}">${h.status}</span></td>
                    `;
                    tr.style.backgroundColor = 'var(--accent)';
                    tr.style.transition = 'background-color 1s ease';
                    tbody.insertBefore(tr, tbody.firstChild);
                    setTimeout(() => tr.style.backgroundColor = '', 50);
                }
            };
            
            this.currentEventSource.onerror = () => {
                this.currentEventSource.close();
                if (statusEl) {
                    statusEl.innerHTML = '<span class="pulse" style="background:var(--danger); box-shadow: 0 0 8px rgba(244,63,94,0.6)"></span> Unavailable';
                    statusEl.style.color = 'var(--danger)';
                    statusEl.style.borderColor = 'rgba(244,63,94,0.3)';
                }
                setTimeout(connect, reconnectTimeout);
                reconnectTimeout = Math.min(reconnectTimeout * 2, 30000);
            };
        };
        
        connect();
    }

    async renderLiveAnalyses() {
        this.connectSSE();
        const history = await fetch('/api/v1/history').then(res => res.json()).catch(() => []);
        
        this.content.innerHTML = `
            <div class="glass-card" style="padding: 0;">
                <table class="data-table">
                    <thead><tr><th>Analysis ID</th><th>Timestamp</th><th>Patient</th><th>Latency</th><th>Status</th></tr></thead>
                    <tbody id="live-analyses-tbody">
                        ${history.map(h => `
                            <tr onclick="window.location.hash='#/analysis/${h.analysis_id}'">
                                <td style="font-family: monospace; color: var(--accent);">${h.analysis_id}</td>
                                <td style="font-size: 0.8rem; color: var(--text-muted);">${new Date(h.request_timestamp).toLocaleString()}</td>
                                <td>${h.patient_summary?.patient_id || 'Unknown'}</td>
                                <td style="font-family: monospace;">${h.total_latency_ms}ms</td>
                                <td><span class="badge ${h.status}">${h.status}</span></td>
                            </tr>
                        `).join('')}
                        ${history.length === 0 ? '<tr id="no-data"><td colspan="5" style="text-align: center; padding: 32px;">No executions logged yet.</td></tr>' : ''}
                    </tbody>
                </table>
            </div>
        `;
    }

    async renderEventLog() {
        this.content.innerHTML = '<div class="glass-card"><h2 class="card-value">Event Log</h2><p>Global event stream not yet implemented.</p></div>';
    }

    async renderApiKeys() {
        this.content.innerHTML = '<div class="glass-card"><h2 class="card-value">API Keys</h2><p>Management interface here.</p></div>';
    }

    async renderExecutionExplorer(id) {
        const record = await fetch(`/api/v1/history/${id}`).then(res => res.json());
        this.breadcrumbs.innerHTML = `<span style="color:var(--text-muted); cursor:pointer;" onclick="window.history.back()">Live Requests</span> <span style="margin: 0 8px;">/</span> ${id}`;
        
        // Dispatch event so InspectorPanel can pick it up
        window.dispatchEvent(new CustomEvent('dic:analysis-loaded', { detail: record }));

        const downloadJsonUrl = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(record, null, 2));

        this.content.innerHTML = `
            <div class="execution-header">
                <div>
                    <h1 class="execution-title">${record.analysis_id}</h1>
                    <div class="execution-meta">
                        <span>Time: ${new Date(record.request_timestamp).toLocaleString()}</span>
                    </div>
                </div>
                <div style="display: flex; gap: 12px; align-items: center;">
                    <a href="${downloadJsonUrl}" download="${record.analysis_id}.json" style="background: rgba(255,255,255,0.05); border: 1px solid var(--border-color); color: var(--text-primary); padding: 8px 16px; border-radius: 4px; cursor: pointer; font-family: monospace; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; text-decoration: none;">Download JSON</a>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 350px 1fr; gap: 24px; margin-bottom: 24px;">
                <div class="glass-card" style="padding: 24px; overflow-y: auto; max-height: 500px;">
                    <h3 style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 24px;">Execution Pipeline</h3>
                    <div id="pipeline-container"></div>
                </div>
                <div class="glass-card" style="padding: 0; display: flex; flex-direction: column;">
                    <div style="padding: 16px 24px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between;">
                        <h3 style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted);">Knowledge Graph Viewer</h3>
                        <span style="font-size: 0.75rem; color: var(--text-secondary);">Click nodes for metadata</span>
                    </div>
                    <div id="kg-container" style="flex-grow: 1; min-height: 400px; position: relative;"></div>
                </div>
            </div>
        `;

        const renderPipelineHTML = (executedNodes) => {
            const hasNodesOfType = (type) => executedNodes.some(n => n.type === type);
            const stages = [
                { id: 'input', label: 'Input Received', executed: true, details: `Patient ID: ${record.patient_summary?.patient_id}` },
                { id: 'ocr', label: 'OCR', executed: hasNodesOfType('OCR'), details: 'No OCR nodes found.' },
                { id: 'decision', label: 'Clinical Decision', executed: hasNodesOfType('Recommendation'), details: `Generated ${record.report?.alerts?.length || 0} alerts.` },
                { id: 'latency', label: 'Total Latency', executed: true, details: `${record.total_latency_ms}ms` }
            ];

            return stages.map(stage => `
                <div style="border-left: 2px solid ${stage.executed ? 'var(--accent)' : 'var(--border-color)'}; padding-left: 16px; margin-bottom: 24px; position: relative;">
                    <div style="position: absolute; left: -7px; top: 0; width: 12px; height: 12px; border-radius: 50%; background: ${stage.executed ? 'var(--accent)' : 'var(--bg-dark)'}; border: 2px solid ${stage.executed ? 'var(--accent)' : 'var(--border-color)'};"></div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="font-size: 0.9rem; color: ${stage.executed ? 'var(--text-primary)' : 'var(--text-muted)'}; margin-bottom: 4px;">${stage.label}</h3>
                    </div>
                    ${stage.executed ? `<p style="font-size: 0.75rem; color: var(--text-secondary);">${stage.details}</p>` : ''}
                </div>
            `).join('');
        };

        const allNodes = record.graph?.nodes || [];
        const allEdges = record.graph?.edges || [];
        
        const pc = this.container.querySelector('#pipeline-container');
        if (pc) pc.innerHTML = renderPipelineHTML(allNodes);

        const kgContainer = this.container.querySelector('#kg-container');
        const visualizer = new GraphVisualizer(kgContainer);
        visualizer.render({nodes: allNodes, edges: allEdges});
    }

    async renderRegistry(endpoint) {
        const data = await fetch(`/api/v1/registry/${endpoint}`).then(res => res.json()).catch(() => ({}));
        const keys = Object.keys(data);
        
        this.content.innerHTML = `
            <div class="glass-card" style="margin-bottom: 24px;">
                <div class="card-title">${endpoint.toUpperCase()} REGISTRY</div>
                <div class="card-value">${keys.length} Items Indexed</div>
            </div>
        `;
    }

    async renderMetrics() {
        this.content.innerHTML = '<div class="glass-card"><h2 class="card-value">Metrics</h2></div>';
    }

    async renderRuntime() {
        this.content.innerHTML = '<div class="glass-card"><h2 class="card-value">Runtime</h2></div>';
    }

    async renderDeployment() {
        this.content.innerHTML = '<div class="glass-card"><h2 class="card-value">Deployment</h2></div>';
    }

    async renderDiagnostics() {
        this.content.innerHTML = '<div class="glass-card"><h2 class="card-value">Diagnostics</h2></div>';
    }
}
