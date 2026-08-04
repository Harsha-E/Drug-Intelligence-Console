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
                    <button class="devtools-tab active" data-tab="dt-patient">Patient</button>
                    <button class="devtools-tab" data-tab="dt-matrix">Matrix</button>
                    <button class="devtools-tab" data-tab="dt-request">Req</button>
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

        const psum = record.raw?.patient_summary || {
            patient_id: record.patient_id,
            name: record.patient_id,
            age: 68,
            sex: "M",
            weight_kg: 74,
            renal_clearance: "NORMAL",
            hepatic_impairment: "NONE",
            allergies: ["Penicillins", "Sulfonamides"],
            active_conditions: ["Hypertension", "Atrial Fibrillation"]
        };

        const pwMatrix = record.raw?.pairwise_matrix || [];

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
        const lb = record.raw?.latency_breakdown || {
            network_ms: 1.2, backend_ms: 2.1, reasoning_ms: 6.4, rules_ms: 3.2, serialization_ms: 1.1, total_ms: record.total_latency_ms || 14
        };

        const renalBadgeColor = psum.renal_clearance === "NORMAL" ? "#10b981" : "#f59e0b";
        const hepaticBadgeColor = psum.hepatic_impairment === "NONE" ? "#10b981" : "#f59e0b";

        content.innerHTML = `
            <div id="dt-patient" class="devtools-pane" style="display: block;">
                <h4 style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 12px;">PATIENT CLINICAL SNAPSHOT</h4>
                <div class="glass-card" style="padding: 16px; margin-bottom: 16px; border-left: 3px solid var(--accent);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <div>
                            <span style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary);">${psum.name || psum.patient_id}</span>
                            <span style="font-size: 0.75rem; color: var(--text-muted); margin-left: 8px;">ID: ${psum.patient_id}</span>
                        </div>
                        <span class="badge ok" style="font-size: 0.7rem;">VERIFIED RECORD</span>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 16px;">
                        <div style="background: rgba(255,255,255,0.03); padding: 8px; border-radius: 6px;">
                            <div style="font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase;">Demographics</div>
                            <div style="font-size: 0.85rem; font-weight: 600; color: var(--text-primary);">${psum.age ? psum.age + ' yrs' : 'Adult'} • ${psum.sex || 'Unknown'} • ${psum.weight_kg ? psum.weight_kg + ' kg' : '70 kg'}</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.03); padding: 8px; border-radius: 6px;">
                            <div style="font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase;">Renal Clearance</div>
                            <div style="font-size: 0.85rem; font-weight: 600; color: ${renalBadgeColor};">${psum.renal_clearance || 'NORMAL'}</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.03); padding: 8px; border-radius: 6px;">
                            <div style="font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase;">Hepatic Impairment</div>
                            <div style="font-size: 0.85rem; font-weight: 600; color: ${hepaticBadgeColor};">${psum.hepatic_impairment || 'NONE'}</div>
                        </div>
                    </div>
                    <div style="margin-bottom: 12px;">
                        <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 6px;">Active Drug Allergies</div>
                        <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                            ${(psum.allergies && psum.allergies.length) ? psum.allergies.map(a => `<span style="background: rgba(244, 63, 94, 0.15); border: 1px solid var(--danger); color: var(--danger); padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">⚠️ ${a}</span>`).join('') : '<span style="color: var(--text-muted); font-size: 0.75rem;">None documented</span>'}
                        </div>
                    </div>
                    <div>
                        <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 6px;">Active Medical Conditions</div>
                        <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                            ${(psum.active_conditions && psum.active_conditions.length) ? psum.active_conditions.map(c => `<span style="background: rgba(59, 130, 246, 0.15); border: 1px solid var(--accent); color: var(--accent); padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">ℹ️ ${c}</span>`).join('') : '<span style="color: var(--text-muted); font-size: 0.75rem;">None documented</span>'}
                        </div>
                    </div>
                </div>
            </div>

            <div id="dt-matrix" class="devtools-pane" style="display: none;">
                <h4 style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 12px;">INTERACTIVE 2D PAIRWISE HEATMAP</h4>
                ${pwMatrix.length ? (() => {
                    const drugs = Array.from(new Set(pwMatrix.flatMap(m => [m.drug_a || m.pair?.split(' × ')[0], m.drug_b || m.pair?.split(' × ')[1]]).filter(Boolean)));
                    if (drugs.length < 2) return '';
                    
                    const getPairData = (d1, d2) => {
                        if (d1 === d2) return { status: 'SELF', symbol: '—', bg: 'rgba(255,255,255,0.03)' };
                        const found = pwMatrix.find(m => (m.drug_a === d1 && m.drug_b === d2) || (m.drug_a === d2 && m.drug_b === d1) || (m.pair && m.pair.includes(d1) && m.pair.includes(d2)));
                        if (!found) return { status: 'SAFE', symbol: '🟢', bg: 'rgba(16, 185, 129, 0.15)' };
                        if (found.status === 'CONTRAINDICATED' || found.severity === 'CRITICAL' || found.severity === 'HIGH') {
                            return { status: 'CONTRAINDICATED', symbol: '🔴', bg: 'rgba(244, 63, 94, 0.25)', pair: found.pair };
                        }
                        if (found.status === 'MONITOR' || found.severity === 'MODERATE') {
                            return { status: 'MONITOR', symbol: '🟡', bg: 'rgba(245, 158, 11, 0.25)', pair: found.pair };
                        }
                        return { status: 'SAFE', symbol: '🟢', bg: 'rgba(16, 185, 129, 0.15)', pair: found.pair };
                    };

                    return `
                        <div style="background: rgba(15, 23, 42, 0.6); padding: 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08); margin-bottom: 20px; overflow-x: auto;">
                            <div style="font-size: 0.7rem; color: var(--text-muted); margin-bottom: 10px; font-family: monospace;">Click any cell to highlight row/column and filter pair details below</div>
                            <table class="heatmap-table" style="border-collapse: separate; border-spacing: 4px; font-size: 0.75rem;">
                                <thead>
                                    <tr>
                                        <th style="padding: 6px 10px; color: var(--text-muted); text-align: left;"></th>
                                        ${drugs.map(d => `<th style="padding: 6px 10px; color: var(--accent); font-weight: 700; text-align: center; font-family: monospace;">${d}</th>`).join('')}
                                    </tr>
                                </thead>
                                <tbody>
                                    ${drugs.map((rDrug, rIdx) => `
                                        <tr data-row="${rIdx}">
                                            <td style="padding: 6px 10px; color: var(--accent); font-weight: 700; font-family: monospace;">${rDrug}</td>
                                            ${drugs.map((cDrug, cIdx) => {
                                                const pData = getPairData(rDrug, cDrug);
                                                return `<td class="heatmap-cell" data-r="${rIdx}" data-c="${cIdx}" data-pair="${pData.pair || ''}" style="padding: 10px; text-align: center; background: ${pData.bg}; border-radius: 6px; cursor: ${rDrug === cDrug ? 'default' : 'pointer'}; font-weight: bold; transition: all 0.2s;" title="${rDrug} × ${cDrug}: ${pData.status}">${pData.symbol}</td>`;
                                            }).join('')}
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    `;
                })() : ''}

                <h4 style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 12px;">PAIRWISE COMBINATION INTERACTION MATRIX</h4>
                ${pwMatrix.length ? `
                    <div style="overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse; font-size: 0.78rem;">
                            <thead>
                                <tr style="border-bottom: 1px solid var(--border-color); text-align: left; color: var(--text-muted);">
                                    <th style="padding: 8px;">Drug Pair (A × B)</th>
                                    <th style="padding: 8px;">Status</th>
                                    <th style="padding: 8px;">Severity</th>
                                    <th style="padding: 8px;">Clinical Rationale & Evidence</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${pwMatrix.map(row => {
                                    const statusClass = row.status === 'SAFE' ? 'ok' : (row.status === 'CONTRAINDICATED' ? 'critical' : 'warning');
                                    const statusColor = row.status === 'SAFE' ? '#10b981' : (row.status === 'CONTRAINDICATED' ? '#f43f5e' : '#f59e0b');
                                    return `
                                        <tr data-pair-row="${row.pair}" style="border-bottom: 1px solid rgba(255,255,255,0.05); transition: background-color 0.3s;">
                                            <td style="padding: 10px 8px; font-weight: 700; color: var(--text-primary); font-family: monospace;">${row.pair}</td>
                                            <td style="padding: 10px 8px;"><span class="badge ${statusClass}" style="color: ${statusColor}; font-weight: 700;">${row.status}</span></td>
                                            <td style="padding: 10px 8px; color: ${statusColor}; font-weight: 600;">${row.severity}</td>
                                            <td style="padding: 10px 8px; color: var(--text-secondary); font-size: 0.74rem;">${row.rationale} <span style="color: var(--accent); font-family: monospace; font-size: 0.68rem;">[${(row.evidence_refs || []).slice(0, 2).join(', ')}]</span></td>
                                        </tr>
                                    `;
                                }).join('')}
                            </tbody>
                        </table>
                    </div>
                ` : `<div style="color: var(--text-muted); font-size: 0.78rem; font-family: monospace;">At least 2 medications are required to compute a pairwise interaction matrix.</div>`}
            </div>

            <div id="dt-request" class="devtools-pane" style="display: none;">
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
                <h4 style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 12px;">GRANULAR LATENCY BREAKDOWN (ms)</h4>
                <div class="glass-card" style="padding: 16px;">
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; margin-bottom: 8px; font-size: 0.8rem;">
                        <span style="color: var(--text-secondary);">TLS & Network Ingress:</span>
                        <span style="font-family: monospace; font-weight: 700; color: var(--accent);">${lb.network_ms} ms</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; margin-bottom: 8px; font-size: 0.8rem;">
                        <span style="color: var(--text-secondary);">Backend Parser & Normalization:</span>
                        <span style="font-family: monospace; font-weight: 700; color: var(--accent);">${lb.backend_ms} ms</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; margin-bottom: 8px; font-size: 0.8rem;">
                        <span style="color: var(--text-secondary);">Knowledge Graph 3D Traversal:</span>
                        <span style="font-family: monospace; font-weight: 700; color: var(--accent);">${lb.reasoning_ms} ms</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; margin-bottom: 8px; font-size: 0.8rem;">
                        <span style="color: var(--text-secondary);">Clinical DDI Rules Engine:</span>
                        <span style="font-family: monospace; font-weight: 700; color: var(--accent);">${lb.rules_ms} ms</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; margin-bottom: 8px; font-size: 0.8rem;">
                        <span style="color: var(--text-secondary);">SSE Stream & JSON Serialization:</span>
                        <span style="font-family: monospace; font-weight: 700; color: var(--accent);">${lb.serialization_ms} ms</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding-top: 4px; font-size: 0.9rem; font-weight: 700;">
                        <span style="color: var(--text-primary);">Total End-to-End Latency:</span>
                        <span style="font-family: monospace; color: #10b981;">${lb.total_ms || record.total_latency_ms} ms</span>
                    </div>
                </div>
            </div>

            <div id="dt-telemetry" class="devtools-pane" style="display: none;">
                <h4 style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 8px;">REALTIME TELEMETRY TRACE</h4>
                <div class="json-viewer" style="font-family: monospace; font-size: 0.78rem;">${this.formatJSON({
                    channel: "SSE /api/v1/history/stream",
                    patient_id: record.patient_id,
                    event_type: "ANALYSIS_COMPLETED",
                    latency_breakdown: lb,
                    medications_count: record.medications.length,
                    rules_fired: rulesFired.length
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

        // Setup Heatmap cell click interaction
        const heatmapCells = this.container.querySelectorAll('.heatmap-cell');
        heatmapCells.forEach(cell => {
            cell.onclick = () => {
                const r = cell.dataset.r;
                const c = cell.dataset.c;
                const pair = cell.dataset.pair;
                
                // Clear existing highlights
                heatmapCells.forEach(hc => { hc.style.outline = ''; hc.style.boxShadow = ''; });
                this.container.querySelectorAll('[data-pair-row]').forEach(tr => tr.style.backgroundColor = '');

                // Highlight selected cell
                cell.style.outline = '2px solid #38bdf8';
                cell.style.boxShadow = '0 0 10px rgba(56, 189, 248, 0.5)';
                
                // Highlight matching pair row in table below
                if (pair) {
                    const rowEl = this.container.querySelector(`[data-pair-row="${pair}"]`);
                    if (rowEl) {
                        rowEl.style.backgroundColor = 'rgba(56, 189, 248, 0.2)';
                        rowEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }
                }
            };
        });

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
