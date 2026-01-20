export const adminHtml = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sentinel Overseer</title>
    <style>
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent: #3b82f6;
            --accent-hover: #2563eb;
            --success: #22c55e;
            --danger: #ef4444;
            --warning: #f59e0b;
            --border: #334155;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            margin: 0;
            padding: 0;
            line-height: 1.5;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 1rem;
        }

        h1 { margin: 0; font-size: 1.5rem; }
        h2 { margin-top: 0; font-size: 1.25rem; }

        .btn {
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            border: none;
            cursor: pointer;
            font-weight: 500;
            transition: opacity 0.2s;
        }
        .btn:hover { opacity: 0.9; }
        .btn-primary { background-color: var(--accent); color: white; }
        .btn-success { background-color: var(--success); color: white; }
        .btn-danger { background-color: var(--danger); color: white; }
        .btn-outline { background-color: transparent; border: 1px solid var(--border); color: var(--text-secondary); }

        .card {
            background-color: var(--bg-secondary);
            border-radius: 0.5rem;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid var(--border);
        }

        .request-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            border-bottom: 1px solid var(--border);
        }
        .request-item:last-child { border-bottom: none; }

        .badge {
            padding: 0.25rem 0.5rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .badge-pending { background-color: rgba(245, 158, 11, 0.2); color: var(--warning); }
        .badge-approved { background-color: rgba(34, 197, 94, 0.2); color: var(--success); }
        .badge-denied { background-color: rgba(239, 68, 68, 0.2); color: var(--danger); }

        .login-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background-color: var(--bg-primary);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }

        .hidden { display: none; }

        input {
            background-color: var(--bg-primary);
            border: 1px solid var(--border);
            color: var(--text-primary);
            padding: 0.5rem;
            border-radius: 0.375rem;
            width: 100%;
            margin-bottom: 1rem;
        }

        .tabs {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        .tab {
            padding: 0.5rem 1rem;
            cursor: pointer;
            border-bottom: 2px solid transparent;
        }
        .tab.active {
            border-bottom-color: var(--accent);
            color: var(--accent);
        }

        pre {
            background-color: rgba(0,0,0,0.3);
            padding: 0.5rem;
            border-radius: 0.25rem;
            overflow-x: auto;
            font-size: 0.875rem;
        }
    </style>
</head>
<body>

<div id="login" class="login-overlay">
    <div class="card" style="width: 400px;">
        <h2>Sentinel Authentication</h2>
        <p style="color: var(--text-secondary); margin-bottom: 1rem;">Enter your Sentinel API Key to access the Overseer dashboard.</p>
        <input type="password" id="apiKeyInput" placeholder="sentinel_sk_..." />
        <button onclick="login()" class="btn btn-primary" style="width: 100%">Connect</button>
    </div>
</div>

<div id="app" class="container hidden">
    <header>
        <div style="display: flex; align-items: center; gap: 1rem;">
            <h1>Sentinel Overseer</h1>
            <span class="badge badge-pending">Beta</span>
        </div>
        <button onclick="logout()" class="btn btn-outline">Logout</button>
    </header>

    <div class="tabs">
        <div class="tab active" onclick="switchTab('pending')">Pending Requests</div>
        <div class="tab" onclick="switchTab('history')">History</div>
        <div class="tab" onclick="switchTab('secrets')">Secrets</div>
    </div>

    <div id="pending-view">
        <div id="pending-list"></div>
    </div>

    <div id="history-view" class="hidden">
        <div id="history-list"></div>
    </div>

    <div id="secrets-view" class="hidden">
        <div id="secrets-list"></div>
    </div>
</div>

<script>
    let API_KEY = localStorage.getItem('sentinel_api_key');
    
    function init() {
        if (API_KEY) {
            document.getElementById('login').classList.add('hidden');
            document.getElementById('app').classList.remove('hidden');
            loadData();
        }
    }

    function login() {
        const key = document.getElementById('apiKeyInput').value.trim();
        if (key) {
            API_KEY = key;
            localStorage.setItem('sentinel_api_key', key);
            init();
        }
    }

    function logout() {
        localStorage.removeItem('sentinel_api_key');
        location.reload();
    }

    function switchTab(tab) {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        event.target.classList.add('active');
        
        document.getElementById('pending-view').classList.add('hidden');
        document.getElementById('history-view').classList.add('hidden');
        document.getElementById('secrets-view').classList.add('hidden');
        
        document.getElementById(tab + '-view').classList.remove('hidden');
    }

    async function api(path, method = 'GET', body = null) {
        const headers = {
            'Authorization': 'Bearer ' + API_KEY,
            'Content-Type': 'application/json'
        };
        const opts = { method, headers };
        if (body) opts.body = JSON.stringify(body);
        
        const res = await fetch('/v1' + path, opts);
        if (res.status === 401) {
            logout();
            return null;
        }
        return res.json();
    }

    async function loadData() {
        const requests = await api('/admin/requests');
        if (requests) {
            const pending = requests.filter(r => r.status === 'PENDING_APPROVAL');
            const history = requests.filter(r => r.status !== 'PENDING_APPROVAL');

            renderPending(pending);
            renderHistory(history);
        }

        const secrets = await api('/admin/secrets');
        if (secrets) {
            renderSecrets(secrets);
        }
    }

    function renderSecrets(items) {
        const container = document.getElementById('secrets-list');
        if (items.length === 0) {
            container.innerHTML = '<div class="card" style="text-align: center; color: var(--text-secondary)">No secrets found</div>';
            return;
        }

        // Group by resource_id
        const groups = {};
        items.forEach(s => {
            if (!groups[s.resource_id]) groups[s.resource_id] = [];
            groups[s.resource_id].push(s);
        });

        container.innerHTML = Object.entries(groups).map(([resourceId, versions]) => \`
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <div>
                        <strong style="color: var(--accent); font-size: 1.1rem;">\${resourceId}</strong>
                        <div style="color: var(--text-secondary); font-size: 0.875rem;">\${versions.length} versions</div>
                    </div>
                    <button onclick="rotateSecret('\${resourceId}')" class="btn btn-primary">Rotate Secret</button>
                </div>
                
                <div style="background: rgba(0,0,0,0.2); border-radius: 0.25rem; overflow: hidden;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 0.875rem;">
                        <thead>
                            <tr style="text-align: left; background: rgba(255,255,255,0.05);">
                                <th style="padding: 0.5rem; color: var(--text-secondary);">Ver</th>
                                <th style="padding: 0.5rem; color: var(--text-secondary);">Value</th>
                                <th style="padding: 0.5rem; color: var(--text-secondary);">Created</th>
                            </tr>
                        </thead>
                        <tbody>
                            \${versions.map((v, i) => \`
                                <tr style="border-top: 1px solid var(--border);">
                                    <td style="padding: 0.5rem;">v\${v.version} \${i===0 ? '<span class="badge badge-approved">Latest</span>' : ''}</td>
                                    <td style="padding: 0.5rem; font-family: monospace;">\${v.value.substring(0, 15)}...</td>
                                    <td style="padding: 0.5rem; color: var(--text-secondary);">\${new Date(v.created_at).toLocaleString()}</td>
                                </tr>
                            \`).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        \`).join('');
    }

    async function rotateSecret(resourceId) {
        if (!confirm(\`Are you sure you want to rotate the secret for \${resourceId}? This will generate a new version.\`)) return;
        await api(\`/admin/secrets/\${resourceId}/rotate\`, 'POST');
        loadData();
    }

    function renderPending(items) {
        const container = document.getElementById('pending-list');
        if (items.length === 0) {
            container.innerHTML = '<div class="card" style="text-align: center; color: var(--text-secondary)">No pending requests</div>';
            return;
        }

        container.innerHTML = items.map(req => \`
            <div class="card">
                <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                    <div>
                        <strong style="color: var(--accent)">\${req.agent_id}</strong>
                        <span style="color: var(--text-secondary)"> requested </span>
                        <strong>\${req.resource_id}</strong>
                    </div>
                    <span style="color: var(--text-secondary); font-size: 0.875rem;">\${new Date(req.created_at).toLocaleString()}</span>
                </div>
                
                <div style="background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 0.25rem; margin-bottom: 1rem;">
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.25rem;">INTENT</div>
                    <div style="font-weight: 500">\${req.intent.summary}</div>
                    <div style="color: var(--text-secondary); font-size: 0.875rem; margin-top: 0.25rem;">\${req.intent.description}</div>
                    <div style="margin-top: 0.5rem;"><span class="badge badge-pending">\${req.intent.task_id}</span></div>
                </div>

                <div style="display: flex; gap: 0.5rem; justify-content: flex-end;">
                    <button onclick="decide('\${req.id}', 'deny')" class="btn btn-danger">Deny</button>
                    <button onclick="decide('\${req.id}', 'approve')" class="btn btn-success">Approve</button>
                </div>
            </div>
        \`).join('');
    }

    function renderHistory(items) {
        const container = document.getElementById('history-list');
        if (items.length === 0) {
            container.innerHTML = '<div class="card" style="text-align: center; color: var(--text-secondary)">No history</div>';
            return;
        }

        container.innerHTML = items.map(req => \`
            <div class="request-item">
                <div>
                    <div style="margin-bottom: 0.25rem;">
                        <span class="badge badge-\${req.status.toLowerCase()}">\${req.status}</span>
                        <strong style="margin-left: 0.5rem;">\${req.agent_id}</strong>
                        <span style="color: var(--text-secondary)"> → \${req.resource_id}</span>
                    </div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">\${req.intent.summary}</div>
                </div>
                <div style="font-size: 0.875rem; color: var(--text-secondary);">
                    \${new Date(req.created_at).toLocaleTimeString()}
                </div>
            </div>
        \`).join('');
    }

    async function decide(id, decision) {
        if (!confirm(\`Are you sure you want to \${decision} this request?\`)) return;
        
        await api(\`/admin/requests/\${id}/\${decision}\`, 'POST');
        loadData();
    }

    // Auto-refresh every 5s
    setInterval(loadData, 5000);

    init();
</script>
</body>
</html>
`;
