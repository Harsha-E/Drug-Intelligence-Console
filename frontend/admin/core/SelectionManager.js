import { eventBus } from './EventBus.js';

class SelectionManager {
    constructor() {
        this.selectedItem = null; // { type: 'NODE' | 'STAGE' | 'EVENT', data: any }
    }

    select(type, data) {
        this.selectedItem = { type, data };
        eventBus.emit('ITEM_SELECTED', this.selectedItem);
    }

    clear() {
        this.selectedItem = null;
        eventBus.emit('SELECTION_CLEARED');
    }

    getSelection() {
        return this.selectedItem;
    }
}

export const selectionManager = new SelectionManager();
