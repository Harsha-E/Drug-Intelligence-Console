/**
 * DockManager.js
 * Generic IDE-style Docking Engine for UI layouts.
 */
import { registry } from './PanelRegistry.js';

export class DockManager {
    constructor(rootElement) {
        this.rootElement = rootElement;
        this.layoutTree = null;
        this.activeInstances = new Map();
        
        // Track dragging state globally
        this.dragState = {
            isDragging: false,
            node: null,
            childDom: null,
            direction: null
        };
        
        this.bindGlobalEvents();
    }

    init(defaultLayout) {
        const saved = localStorage.getItem('dic_layout');
        if (saved) {
            try {
                this.layoutTree = JSON.parse(saved);
            } catch (e) {
                console.warn('[DockManager] Failed to parse saved layout, using default.');
                this.layoutTree = defaultLayout;
            }
        } else {
            this.layoutTree = defaultLayout;
        }

        this.render();
    }

    render() {
        this.rootElement.innerHTML = '';
        const domNode = this.buildNode(this.layoutTree);
        this.rootElement.appendChild(domNode);
    }

    buildNode(node) {
        if (node.type === 'split') {
            return this.buildSplitNode(node);
        } else if (node.type === 'tabGroup') {
            return this.buildTabGroup(node);
        }
        return document.createElement('div');
    }

    buildSplitNode(node) {
        const container = document.createElement('div');
        container.className = `split-container ${node.direction}`;
        
        node.children.forEach((child, index) => {
            const childDom = this.buildNode(child);
            childDom.style.flex = child.size ? `0 0 ${child.size}px` : '1 1 0';
            
            // Collapsed handling
            if (child.collapsed) {
                childDom.style.display = 'none';
            }
            
            container.appendChild(childDom);

            // Add splitter
            if (index < node.children.length - 1) {
                const splitter = document.createElement('div');
                splitter.className = `layout-splitter ${node.direction}`;
                
                splitter.addEventListener('mousedown', (e) => {
                    this.dragState = {
                        isDragging: true,
                        childNode: child,
                        childDom: childDom,
                        direction: node.direction,
                        startX: e.clientX,
                        startY: e.clientY,
                        startSize: childDom.getBoundingClientRect()[node.direction === 'horizontal' ? 'width' : 'height']
                    };
                    document.body.style.cursor = node.direction === 'horizontal' ? 'col-resize' : 'row-resize';
                    e.preventDefault();
                });
                
                // Double click to reset/collapse toggle
                splitter.addEventListener('dblclick', () => {
                    child.collapsed = !child.collapsed;
                    this.saveLayout();
                    this.render();
                });

                container.appendChild(splitter);
            }
        });
        return container;
    }

    buildTabGroup(node) {
        const container = document.createElement('div');
        container.className = 'tab-group';

        const header = document.createElement('div');
        header.className = 'tab-header';

        const contentArea = document.createElement('div');
        contentArea.className = 'tab-content-area';

        // Set active tab if none
        if (node.panels.length > 0 && !node.active) {
            node.active = node.panels[0];
        }

        node.panels.forEach(panelId => {
            const config = registry.get(panelId);
            if (!config) return;

            const tabBtn = document.createElement('button');
            tabBtn.className = `tab-btn ${node.active === panelId ? 'active' : ''}`;
            tabBtn.innerHTML = `${config.icon || ''} ${config.title}`;
            
            tabBtn.onclick = () => {
                node.active = panelId;
                this.saveLayout();
                this.render();
            };

            header.appendChild(tabBtn);
        });

        // Fullscreen Toggle Button
        const fsBtn = document.createElement('button');
        fsBtn.className = 'tab-action-btn';
        fsBtn.innerHTML = '⛶';
        fsBtn.title = "Fullscreen";
        fsBtn.onclick = () => this.toggleFullscreen(container);
        header.appendChild(fsBtn);

        container.appendChild(header);

        // Render active panel component
        if (node.active) {
            const config = registry.get(node.active);
            if (config) {
                const wrapper = document.createElement('div');
                wrapper.className = 'panel-wrapper';
                
                // Instantiate component if not exists
                if (!this.activeInstances.has(node.active)) {
                    this.activeInstances.set(node.active, new config.component());
                }
                
                const instance = this.activeInstances.get(node.active);
                if (instance.render) {
                    const dom = instance.render();
                    if (dom instanceof HTMLElement) wrapper.appendChild(dom);
                    else wrapper.innerHTML = dom;
                }
                
                contentArea.appendChild(wrapper);
                
                // Post-mount update
                if (instance.update) {
                    setTimeout(() => instance.update(), 0);
                }
            }
        }

        container.appendChild(contentArea);
        return container;
    }

    bindGlobalEvents() {
        window.addEventListener('mousemove', (e) => {
            if (!this.dragState.isDragging) return;
            
            const state = this.dragState;
            let newSize;
            
            if (state.direction === 'horizontal') {
                const delta = e.clientX - state.startX;
                newSize = state.startSize + delta;
            } else {
                const delta = e.clientY - state.startY;
                newSize = state.startSize + delta;
            }
            
            // Constrain minimum
            newSize = Math.max(50, newSize);
            
            state.childNode.size = newSize;
            state.childDom.style.flex = `0 0 ${newSize}px`;
        });

        window.addEventListener('mouseup', () => {
            if (this.dragState.isDragging) {
                this.dragState.isDragging = false;
                document.body.style.cursor = '';
                this.saveLayout();
            }
        });

        // Keyboard Shortcuts
        window.addEventListener('keydown', (e) => {
            // F11: Fullscreen toggle inside DIC
            if (e.key === 'F11') {
                e.preventDefault();
                const activeTabGroup = document.querySelector('.tab-group:hover') || document.querySelector('.tab-group');
                if (activeTabGroup) this.toggleFullscreen(activeTabGroup);
            }
        });
    }

    toggleFullscreen(element) {
        if (element.classList.contains('dock-fullscreen')) {
            element.classList.remove('dock-fullscreen');
        } else {
            document.querySelectorAll('.dock-fullscreen').forEach(el => el.classList.remove('dock-fullscreen'));
            element.classList.add('dock-fullscreen');
        }
    }

    saveLayout() {
        localStorage.setItem('dic_layout', JSON.stringify(this.layoutTree));
    }
    
    // Allows completely replacing layout tree (for resets)
    loadLayout(newTree) {
        this.layoutTree = newTree;
        this.saveLayout();
        this.render();
    }
}
