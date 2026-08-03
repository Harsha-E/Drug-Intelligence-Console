import { eventBus } from '../core/EventBus.js';

class SSEClient {
    constructor(endpoint = '/api/v1/history/stream') {
        this.endpoint = endpoint;
        this.eventSource = null;
        this.reconnectAttempts = 0;
        this.maxReconnects = 10;
        this.baseBackoff = 1000;
    }

    connect() {
        if (this.eventSource) return;

        console.log(`[SSE] Connecting to ${this.endpoint}...`);
        this.eventSource = new EventSource(this.endpoint);

        this.eventSource.onopen = () => {
            console.log('[SSE] Connected');
            this.reconnectAttempts = 0;
            eventBus.emit('CONNECTION_STATUS', 'CONNECTED');
        };

        this.eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                eventBus.emit('RAW_SSE_EVENT', data);
            } catch (e) {
                console.error('[SSE] Failed to parse event data:', e);
            }
        };

        this.eventSource.onerror = (error) => {
            console.error('[SSE] Connection error', error);
            eventBus.emit('CONNECTION_STATUS', 'DISCONNECTED');
            this.eventSource.close();
            this.eventSource = null;
            this.scheduleReconnect();
        };
    }

    scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnects) {
            console.error('[SSE] Max reconnection attempts reached.');
            return;
        }
        
        const delay = this.baseBackoff * Math.pow(2, this.reconnectAttempts);
        this.reconnectAttempts++;
        console.log(`[SSE] Reconnecting in ${delay}ms (Attempt ${this.reconnectAttempts})`);
        
        setTimeout(() => this.connect(), delay);
    }

    disconnect() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
            eventBus.emit('CONNECTION_STATUS', 'DISCONNECTED');
        }
    }
}

export const sseClient = new SSEClient();
