/**
 * PanelRegistry.js
 * Central registry for all IDE panels.
 */

class PanelRegistry {
    constructor() {
        this.panels = new Map();
    }

    /**
     * Registers a panel type into the system.
     * @param {Object} config - { id, title, icon, component, minWidth, dockable, defaultLayout }
     */
    register(config) {
        if (!config.id) throw new Error("Panel requires an ID");
        if (!config.component) throw new Error(`Panel ${config.id} requires a component class`);
        this.panels.set(config.id, config);
        console.log(`[PanelRegistry] Registered panel: ${config.id}`);
    }

    get(id) {
        return this.panels.get(id);
    }

    getAll() {
        return Array.from(this.panels.values());
    }
}

export const registry = new PanelRegistry();
