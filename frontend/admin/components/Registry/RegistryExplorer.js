import { api } from '../../services/ApiClient.js';

export class RegistryExplorer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.render();
    }

    render() {
        if (!this.container) return;
        
        this.container.innerHTML = `
            <div class="registry-explorer">
                <h4>Registry Explorer</h4>
                <div class="registry-controls">
                    <select id="registry-select" class="input-glass">
                        <option value="drug_lookup">Drug Lookup</option>
                        <option value="alias_index">Alias Index</option>
                        <option value="rules">Rules</option>
                    </select>
                    <button id="registry-load-btn" class="btn-primary">Load</button>
                </div>
                <div class="registry-content">
                    <pre id="registry-json" class="json-viewer empty">Select a registry to view...</pre>
                </div>
            </div>
        `;
        
        const btn = this.container.querySelector('#registry-load-btn');
        btn.addEventListener('click', () => this.loadRegistry());
    }

    async loadRegistry() {
        const select = this.container.querySelector('#registry-select');
        const jsonView = this.container.querySelector('#registry-json');
        const res = select.value;
        
        jsonView.innerHTML = `Loading...`;
        
        try {
            const data = await api.get(`/registry/${res}`);
            // Show only first 50 keys to avoid browser crash on massive registries
            const keys = Object.keys(data).slice(0, 50);
            const preview = {};
            keys.forEach(k => preview[k] = data[k]);
            
            const count = Object.keys(data).length;
            
            jsonView.innerHTML = `// Showing 50 of ${count} records\n` + this.syntaxHighlight(JSON.stringify(preview, null, 2));
        } catch (error) {
            jsonView.innerHTML = `Error: ${error.message}`;
        }
    }
    
    syntaxHighlight(json) {
        if (!json) return "";
        json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
            let cls = 'number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'key';
                } else {
                    cls = 'string';
                }
            } else if (/true|false/.test(match)) {
                cls = 'boolean';
            } else if (/null/.test(match)) {
                cls = 'null';
            }
            return '<span class="' + cls + '">' + match + '</span>';
        });
    }
}
