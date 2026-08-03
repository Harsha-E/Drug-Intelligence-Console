import { eventBus } from './core/EventBus.js';
import { router } from './core/Router.js';
import { sseClient } from './services/SSEClient.js';
import { telemetryAdapter } from './services/TelemetryAdapter.js';
import { layoutManager } from './core/LayoutManager.js';

import { mountDashboard } from './views/Dashboard.js';
import { mountAnalyze } from './views/Analyze.js';
import { mountAPI } from './views/API.js';
import { ExecutionInspector } from './components/Inspector/ExecutionInspector.js';

class Application {
    constructor() {
        this.init();
    }

    init() {
        console.log("Initializing Clinical Intelligence Observatory...");
        
        // 1. Setup Routing
        router.addRoute('/', () => mountDashboard('main-viewport'));
        router.addRoute('/analyze', () => mountAnalyze('main-viewport'));
        router.addRoute('/api', () => mountAPI('main-viewport'));
        
        // 2. Setup Layout
        layoutManager.registerPanel('devtools-panel', { visible: true, width: 400 });
        
        // 3. Mount Inspector globally
        new ExecutionInspector('devtools-panel');
        
        // 3. Bind Global Listeners
        eventBus.on('ITEM_SELECTED', () => {
            layoutManager.setPanelVisibility('devtools-panel', true);
        });
        
        // 4. Start Core Services
        router.init();
        sseClient.connect();
    }
}

// Bootstrap
window.addEventListener('DOMContentLoaded', () => {
    window.app = new Application();
});
