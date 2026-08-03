import { eventBus } from './EventBus.js';

class LayoutManager {
    constructor() {
        this.panels = new Map(); // e.g., { 'inspector': { visible: true, width: 300 } }
    }

    registerPanel(id, defaultState = { visible: true }) {
        this.panels.set(id, defaultState);
        this._updateDOM(id);
    }

    togglePanel(id) {
        const state = this.panels.get(id);
        if (state) {
            state.visible = !state.visible;
            this.panels.set(id, state);
            this._updateDOM(id);
            eventBus.emit('LAYOUT_CHANGED', { panel: id, state });
        }
    }
    
    setPanelVisibility(id, visible) {
        const state = this.panels.get(id);
        if (state && state.visible !== visible) {
            state.visible = visible;
            this.panels.set(id, state);
            this._updateDOM(id);
            eventBus.emit('LAYOUT_CHANGED', { panel: id, state });
        }
    }

    _updateDOM(id) {
        const el = document.getElementById(id);
        if (el) {
            const state = this.panels.get(id);
            el.style.display = state.visible ? '' : 'none';
        }
    }
}

export const layoutManager = new LayoutManager();
