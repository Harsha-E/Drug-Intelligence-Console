/**
 * LayoutHistory.js
 * Handles Ctrl+Z for layout modifications.
 */
export class LayoutHistory {
    constructor(dockManager) {
        this.dockManager = dockManager;
        this.history = [];
        this.currentIndex = -1;
        this.maxSize = 50;

        // Save initial state
        setTimeout(() => this.pushState(), 500);

        window.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'z' && !e.shiftKey) {
                e.preventDefault();
                this.undo();
            }
            if (e.ctrlKey && e.key === 'y' || (e.ctrlKey && e.shiftKey && e.key === 'Z')) {
                e.preventDefault();
                this.redo();
            }
        });
    }

    pushState() {
        const currentState = JSON.stringify(this.dockManager.layoutTree);
        
        // Don't push duplicates
        if (this.currentIndex >= 0 && this.history[this.currentIndex] === currentState) {
            return;
        }

        // Drop redo history if we make a new action
        this.history = this.history.slice(0, this.currentIndex + 1);
        this.history.push(currentState);
        
        if (this.history.length > this.maxSize) {
            this.history.shift();
        } else {
            this.currentIndex++;
        }
    }

    undo() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            const stateStr = this.history[this.currentIndex];
            this.dockManager.loadLayout(JSON.parse(stateStr));
        }
    }

    redo() {
        if (this.currentIndex < this.history.length - 1) {
            this.currentIndex++;
            const stateStr = this.history[this.currentIndex];
            this.dockManager.loadLayout(JSON.parse(stateStr));
        }
    }
}
