const http = require('http');

const PORT = 1000;

const server = http.createServer((req, res) => {
    // Basic CORS headers for MedCheck PWA
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    // API Routes for Drug Intelligence Cloud (Runtime Registry API)
    if (req.url === '/api/v1/health' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'ok', engine: 'Drug Intelligence Cloud', version: '1.0' }));
        return;
    }

    if (req.url.startsWith('/api/v1/analyze') && req.method === 'POST') {
        // Placeholder for clinical logic evaluation against the registry
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            status: "success",
            recommendation: "Clinical analysis pending implementation of Registry API.",
            triggered_rules: [],
            highest_severity: "NONE"
        }));
        return;
    }

    // 404 Not Found
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Endpoint not found in DIC' }));
});

server.listen(PORT, () => {
    console.log(`Drug Intelligence Cloud API Server running on port ${PORT}`);
    console.log(`Healthcheck: http://localhost:${PORT}/api/v1/health`);
});
