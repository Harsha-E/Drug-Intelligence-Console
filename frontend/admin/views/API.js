import { ApiInspector } from '../components/API/ApiInspector.js';

export function mountAPI(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = `
        <div class="view-api">
            <h2>API Observatory</h2>
            <div id="api-inspector-container" class="panel">
                <!-- TEAM E: API Inspector mounts here -->
            </div>
        </div>
    `;
    
    new ApiInspector('api-inspector-container');
}
