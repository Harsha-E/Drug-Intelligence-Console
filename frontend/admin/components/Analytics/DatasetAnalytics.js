import { api } from '../../services/ApiClient.js';

export class DatasetAnalytics {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.render();
        this.fetchData();
        
        // Auto refresh every 30s
        setInterval(() => this.fetchData(), 30000);
    }

    render() {
        if (!this.container) return;
        
        this.container.innerHTML = `
            <div class="dataset-analytics">
                <h4>Registry Analytics</h4>
                <div id="analytics-grid" class="metrics-grid">
                    <div class="empty">Loading...</div>
                </div>
            </div>
        `;
    }
    
    async fetchData() {
        if (!this.container) return;
        const grid = this.container.querySelector('#analytics-grid');
        
        try {
            const metrics = await api.get('/metrics');
            grid.innerHTML = `
                <div class="metric-card">
                    <div class="metric-val">${metrics.total_drugs || 0}</div>
                    <div class="metric-lbl">Total Drugs</div>
                </div>
                <div class="metric-card">
                    <div class="metric-val">${metrics.total_claims || 0}</div>
                    <div class="metric-lbl">Claims</div>
                </div>
                <div class="metric-card">
                    <div class="metric-val">${metrics.total_evidence || 0}</div>
                    <div class="metric-lbl">Evidence Links</div>
                </div>
                <div class="metric-card">
                    <div class="metric-val">${metrics.total_rules || 0}</div>
                    <div class="metric-lbl">Rules Generated</div>
                </div>
            `;
        } catch (error) {
            grid.innerHTML = `<div class="error">Failed to load analytics: ${error.message}</div>`;
        }
    }
}
