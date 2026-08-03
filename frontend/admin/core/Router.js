import { eventBus } from './EventBus.js';

class Router {
    constructor() {
        this.routes = new Map();
        this.currentRoute = null;
        
        window.addEventListener('hashchange', () => this.handleHashChange());
    }

    addRoute(path, viewHandler) {
        this.routes.set(path, viewHandler);
    }

    init() {
        if (!window.location.hash) {
            window.location.hash = '#/';
        }
        this.handleHashChange();
    }

    handleHashChange() {
        const path = window.location.hash.slice(1) || '/';
        const handler = this.routes.get(path);
        
        if (handler) {
            this.currentRoute = path;
            eventBus.emit('ROUTE_CHANGED', { path });
            handler();
        } else {
            console.warn(`Route not found: ${path}`);
            if (this.routes.has('/')) {
                window.location.hash = '#/';
            }
        }
    }
    
    navigate(path) {
        window.location.hash = `#${path}`;
    }
}

export const router = new Router();
