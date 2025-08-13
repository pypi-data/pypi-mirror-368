#!/usr/bin/env python3
"""
Development server for base module with UI
Runs on http://localhost:3333
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add backend to path
sys.path.insert(0, 'backend')

class ModuleServer(BaseHTTPRequestHandler):
    """HTTP server for local module development"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.serve_html()
        elif self.path == '/api/health':
            self.handle_health()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/execute':
            self.handle_execute()
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def serve_html(self):
        """Serve the main HTML interface"""
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Base Module - HLA-Compass</title>
    <link href="https://cdn.jsdelivr.net/npm/antd@5.22.6/dist/reset.css" rel="stylesheet">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f0f2f5;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .card {
            background: white;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        h1 { color: #1890ff; margin-bottom: 24px; }
        .form-group { margin-bottom: 16px; }
        label { display: block; margin-bottom: 8px; font-weight: 500; }
        input, textarea {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #d9d9d9;
            border-radius: 4px;
            font-size: 14px;
        }
        button {
            background: #1890ff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover { background: #40a9ff; }
        button:disabled { background: #d9d9d9; cursor: not-allowed; }
        .results {
            margin-top: 20px;
            padding: 16px;
            background: #f6ffed;
            border: 1px solid #b7eb8f;
            border-radius: 4px;
        }
        .error {
            margin-top: 20px;
            padding: 16px;
            background: #fff2e8;
            border: 1px solid #ffbb96;
            border-radius: 4px;
            color: #d4380d;
        }
        pre { background: #f5f5f5; padding: 12px; border-radius: 4px; overflow: auto; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🧬 Base Module Template</h1>
            <p>This is a basic module template with Ant Design styling.</p>
            
            <div class="form-group">
                <label>Example Parameter</label>
                <input type="text" id="example_param" placeholder="Enter value..." value="test">
            </div>
            
            <div class="form-group">
                <label>Optional Parameter</label>
                <input type="number" id="optional_param" value="100">
            </div>
            
            <button onclick="executeModule()">Execute Module</button>
            
            <div id="output"></div>
        </div>
    </div>

    <script>
        async function executeModule() {
            const output = document.getElementById('output');
            const button = document.querySelector('button');
            
            button.disabled = true;
            output.innerHTML = '<div class="results">Processing...</div>';
            
            try {
                const response = await fetch('/api/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        example_param: document.getElementById('example_param').value,
                        optional_param: parseInt(document.getElementById('optional_param').value)
                    })
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    output.innerHTML = '<div class="results"><h3>Results</h3><pre>' + 
                        JSON.stringify(result.data, null, 2) + '</pre></div>';
                } else {
                    output.innerHTML = '<div class="error">Error: ' + 
                        (result.error || 'Unknown error') + '</div>';
                }
            } catch (error) {
                output.innerHTML = '<div class="error">Error: ' + error.message + '</div>';
            } finally {
                button.disabled = false;
            }
        }
        
        // Check health on load
        fetch('/api/health').then(r => r.json()).then(data => {
            console.log('Health check:', data);
        });
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def handle_health(self):
        """Health check endpoint"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'status': 'healthy',
            'module': 'base-module',
            'server': 'running'
        }
        self.wfile.write(json.dumps(response).encode())
    
    def handle_execute(self):
        """Execute the module"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        input_data = json.loads(post_data)
        
        # Import and use the module
        try:
            from main import execute
            result = execute(input_data, {'job_id': 'local-test'})
        except ImportError:
            # If module not implemented yet
            result = {
                'status': 'success',
                'data': {
                    'message': 'Module template working!',
                    'input': input_data,
                    'hint': 'Implement your logic in backend/main.py'
                }
            }
        except Exception as e:
            result = {
                'status': 'error',
                'error': str(e)
            }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())


def main():
    """Start the server"""
    port = 3333
    
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                 Base Module Development Server                ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Server:    http://localhost:{port}/                         ║
║  Status:    Ready                                            ║
║                                                               ║
║  Open your browser to http://localhost:{port}/ to test       ║
║  Press Ctrl+C to stop                                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    server = HTTPServer(('', port), ModuleServer)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Server stopped")


if __name__ == '__main__':
    main()