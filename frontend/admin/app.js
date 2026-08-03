/**
 * app.js - DIC IDE Entry Point
 */
import { registry } from './components/PanelRegistry.js';
import { DockManager } from './components/DockManager.js';
import { LayoutHistory } from './components/LayoutHistory.js';
import { SidebarPanel } from './components/SidebarPanel.js';
import { WorkspacePanel } from './components/WorkspacePanel.js';
import { InspectorPanel } from './components/InspectorPanel.js';

const app = {
    init() {
        // 1. Register Panels
        registry.register({
            id: 'sidebar',
            title: 'Command Center',
            icon: '⌘',
            component: SidebarPanel
        });

        registry.register({
            id: 'workspace',
            title: 'Workspace',
            component: WorkspacePanel
        });

        registry.register({
            id: 'inspector',
            title: 'Inspector',
            component: InspectorPanel
        });

        // 2. Define Default IDE Layout Tree
        const defaultLayout = {
            type: 'split',
            direction: 'horizontal',
            children: [
                {
                    type: 'tabGroup',
                    size: 280,
                    collapsed: false,
                    panels: ['sidebar'],
                    active: 'sidebar'
                },
                {
                    type: 'split',
                    direction: 'horizontal',
                    children: [
                        {
                            type: 'tabGroup',
                            panels: ['workspace'],
                            active: 'workspace'
                        },
                        {
                            type: 'tabGroup',
                            size: 400,
                            collapsed: false,
                            panels: ['inspector'],
                            active: 'inspector'
                        }
                    ]
                }
            ]
        };

        // 3. Initialize Engine
        const rootElement = document.getElementById('dock-root');
        if (rootElement) {
            const dockManager = new DockManager(rootElement);
            dockManager.init(defaultLayout);
            
            // Initialize Undo History
            new LayoutHistory(dockManager);

            // Add Command Palette Trigger (Ctrl+Shift+P placeholder)
            window.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'p') {
                    e.preventDefault();
                    console.log('Command Palette triggered');
                    // Phase 3 Feature
                }
            });
        }
    }
};

document.addEventListener('DOMContentLoaded', () => app.init());
