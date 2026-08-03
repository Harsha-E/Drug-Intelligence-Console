import { RuntimeObservatory } from '../components/Runtime/RuntimeObservatory.js';
import { RegistryExplorer } from '../components/Registry/RegistryExplorer.js';
import { DatasetAnalytics } from '../components/Analytics/DatasetAnalytics.js';
import { PerformanceDashboard } from '../components/Performance/PerformanceDashboard.js';

export function mountDashboard(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = `
        <div class="view-dashboard layout-split">
            <div class="dashboard-main panel" style="flex: 2;">
                <h2>Command Center</h2>
                <div id="perf-container"></div>
                <div id="analytics-container"></div>
                <div id="runtime-container" style="margin-top: 24px;"></div>
            </div>
            <div class="dashboard-side panel" style="flex: 1;">
                <div id="registry-container"></div>
            </div>
        </div>
    `;
    
    new RuntimeObservatory('runtime-container');
    new PerformanceDashboard('perf-container');
    new DatasetAnalytics('analytics-container');
    new RegistryExplorer('registry-container');
}
