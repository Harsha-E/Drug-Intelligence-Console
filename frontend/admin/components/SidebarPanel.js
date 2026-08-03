export class SidebarPanel {
    render() {
        const container = document.createElement('div');
        container.style.width = '100%';
        container.style.height = '100%';
        container.style.display = 'flex';
        container.style.flexDirection = 'column';
        
        container.innerHTML = `
            <div class="sidebar-header" style="flex-shrink: 0;">
                <div class="logo">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="glow-icon">
                        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                    </svg>
                    <span>Command Center</span>
                </div>
            </div>
            
            <nav class="sidebar-nav" style="flex: 1; overflow-y: auto;">
                <a href="#/live-analyses" class="nav-item">
                    Live Requests 
                    <span class="live-pulse" id="live-indicator"></span>
                </a>
                <a href="#/event-log" class="nav-item">Event Log</a>
                <a href="#/runtime" class="nav-item">Runtime</a>
                
                <div class="nav-section">KNOWLEDGE BASE</div>
                <a href="#/registry" class="nav-item">Registry</a>
                <a href="#/knowledge" class="nav-item">Knowledge</a>
                <a href="#/claims" class="nav-item">Claims</a>
                <a href="#/evidence" class="nav-item">Evidence</a>
                <a href="#/rules" class="nav-item">Rules</a>
                
                <div class="nav-section">INFRASTRUCTURE</div>
                <a href="#/metrics" class="nav-item">Metrics</a>
                <a href="#/api-keys" class="nav-item">API Keys</a>
                <a href="#/deployment" class="nav-item">Deployment</a>
                <a href="#/diagnostics" class="nav-item">Diagnostics</a>
            </nav>
        `;
        
        return container;
    }

    update() {
        const hash = window.location.hash.slice(1) || '/live-analyses';
        const path = hash.split('?')[0];
        
        document.querySelectorAll('.sidebar-nav .nav-item').forEach(el => {
            el.classList.remove('active');
            if (el.getAttribute('href') === '#' + path) {
                el.classList.add('active');
            }
        });
        
        // Listen to hash changes independently
        if (!this.bound) {
            window.addEventListener('hashchange', () => this.update());
            this.bound = true;
        }
    }
}
