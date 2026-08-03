import { eventBus } from '../../core/EventBus.js';

export class ApiInspector {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.requests = new Map();
        
        eventBus.on('API_REQUEST_START', (req) => this.onStart(req));
        eventBus.on('API_REQUEST_COMPLETE', (res) => this.onComplete(res));
        eventBus.on('API_REQUEST_ERROR', (err) => this.onError(err));
        
        this.render();
    }

    onStart(req) {
        this.requests.set(req.id, { ...req, status: 'PENDING' });
        this.render();
    }

    onComplete(res) {
        const req = this.requests.get(res.id);
        if (req) {
            this.requests.set(res.id, { ...req, ...res });
            this.render();
        }
    }

    onError(err) {
        const req = this.requests.get(err.id);
        if (req) {
            this.requests.set(err.id, { ...req, ...err, status: 'ERROR' });
            this.render();
        }
    }

    render() {
        if (!this.container) return;
        
        const reqs = Array.from(this.requests.values()).reverse();
        
        this.container.innerHTML = `
            <div class="api-inspector">
                <h4>Network Logs</h4>
                <div class="api-list">
                    ${reqs.length === 0 ? '<div class="empty">No requests recorded</div>' : ''}
                    ${reqs.map(r => `
                        <div class="api-row ${r.status === 'ERROR' ? 'error' : ''} ${r.status === 'PENDING' ? 'pending' : ''}">
                            <span class="method">${r.method}</span>
                            <span class="endpoint">${r.endpoint}</span>
                            <span class="status">${r.status === 'PENDING' ? '⏳' : r.status}</span>
                            <span class="latency">${r.duration ? r.duration + 'ms' : '-'}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
}
