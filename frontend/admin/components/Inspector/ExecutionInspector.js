import { eventBus } from '../../core/EventBus.js';
import { selectionManager } from '../../core/SelectionManager.js';

export class ExecutionInspector {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        
        eventBus.on('SELECTION_CHANGED', (sel) => this.render(sel));
        
        this.render(null);
    }

    render(selection) {
        if (!this.container) return;
        
        if (!selection || !selection.data) {
            this.container.innerHTML = `
                <div class="inspector-panel">
                    <div class="inspector-header">
                        <h3>Inspector</h3>
                    </div>
                    <div class="empty">Select a node, edge, or stage</div>
                </div>
            `;
            return;
        }
        
        const { type, data } = selection;
        
        this.container.innerHTML = `
            <div class="inspector-panel">
                <div class="inspector-header">
                    <h3>${type} Inspector</h3>
                </div>
                <div class="inspector-content">
                    <pre class="json-viewer">${this.syntaxHighlight(JSON.stringify(data, null, 2))}</pre>
                </div>
            </div>
        `;
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
