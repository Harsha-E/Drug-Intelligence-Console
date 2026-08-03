import { eventBus } from '../core/EventBus.js';

class ApiClient {
    constructor(baseUrl = '/api/v1') {
        this.baseUrl = baseUrl;
    }

    async get(endpoint) {
        const start = performance.now();
        const reqId = `REQ-${Date.now()}`;
        eventBus.emit('API_REQUEST_START', { id: reqId, method: 'GET', endpoint });
        
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            
            const duration = Math.round(performance.now() - start);
            eventBus.emit('API_REQUEST_COMPLETE', { id: reqId, status: response.status, duration, data });
            return data;
        } catch (error) {
            const duration = Math.round(performance.now() - start);
            eventBus.emit('API_REQUEST_ERROR', { id: reqId, error: error.message, duration });
            throw error;
        }
    }

    async post(endpoint, payload) {
        const start = performance.now();
        const reqId = `REQ-${Date.now()}`;
        eventBus.emit('API_REQUEST_START', { id: reqId, method: 'POST', endpoint, payload });
        
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            
            const duration = Math.round(performance.now() - start);
            eventBus.emit('API_REQUEST_COMPLETE', { id: reqId, status: response.status, duration, data });
            return data;
        } catch (error) {
            const duration = Math.round(performance.now() - start);
            eventBus.emit('API_REQUEST_ERROR', { id: reqId, error: error.message, duration });
            throw error;
        }
    }
}

export const api = new ApiClient();
