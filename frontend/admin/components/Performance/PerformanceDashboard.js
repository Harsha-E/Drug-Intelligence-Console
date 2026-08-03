import { api } from '../../services/ApiClient.js';

export class PerformanceDashboard {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.render();
        this.fetchData();
        
        setInterval(() => this.fetchData(), 15000); // 15s refresh
    }

    render() {
        if (!this.container) return;
        
        this.container.innerHTML = `
            <div class="performance-dashboard">
                <h4>Engine Performance</h4>
                <div id="perf-grid" class="metrics-grid">
                    <div class="empty">Loading...</div>
                </div>
            </div>
        `;
    }
    
    async fetchData() {
        if (!this.container) return;
        const grid = this.container.querySelector('#perf-grid');
        
        try {
            const metrics = await api.get('/metrics');
            
            const hitRate = (metrics.runtime_cache_hits + metrics.runtime_cache_misses) > 0 
                ? ((metrics.runtime_cache_hits / (metrics.runtime_cache_hits + metrics.runtime_cache_misses)) * 100).toFixed(1)
                : 0;

            grid.innerHTML = `
                <div class="metric-card">
                    <div class="metric-val">${metrics.average_analyze_latency_ms || 0}<span>ms</span></div>
                    <div class="metric-lbl">Avg Latency</div>
                </div>
                <div class="metric-card">
                    <div class="metric-val">${metrics.p95_analyze_latency_ms || 0}<span>ms</span></div>
                    <div class="metric-lbl">P95 Latency</div>
                </div>
                <div class="metric-card">
                    <div class="metric-val">${hitRate}<span>%</span></div>
                    <div class="metric-lbl">Cache Hit Rate</div>
                </div>
                <div class="metric-card">
                    <div class="metric-val">${metrics.uptime_seconds || 0}<span>s</span></div>
                    <div class="metric-lbl">Uptime</div>
                </div>
            `;
        } catch (error) {
            grid.innerHTML = `<div class="error">Failed to load performance metrics: ${error.message}</div>`;
        }
    }
}
