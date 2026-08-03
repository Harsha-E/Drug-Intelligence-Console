import { eventBus } from './EventBus.js';

class State {
    constructor() {
        this.data = {
            connectionStatus: 'DISCONNECTED',
            activeExecutionId: null,
            theme: 'dark'
        };
    }

    get(key) {
        return this.data[key];
    }

    set(key, value) {
        if (this.data[key] !== value) {
            this.data[key] = value;
            eventBus.emit('STATE_CHANGED', { key, value });
        }
    }
}

export const state = new State();
