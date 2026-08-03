import { eventBus } from '../core/EventBus.js';
import { api } from './ApiClient.js';

class RegistryStore {
    constructor() {
        this.manifest = null;
        this.stats = null;
        this.isLoading = false;
    }

    async loadStats() {
        if (this.isLoading) return;
        this.isLoading = true;
        try {
            // Future endpoint: /registry/stats
            this.stats = await api.get('/version'); 
            eventBus.emit('REGISTRY_STATS_UPDATED', this.stats);
        } catch (e) {
            console.error("Failed to load registry stats", e);
        } finally {
            this.isLoading = false;
        }
    }
}

export const registryStore = new RegistryStore();
