#!/usr/bin/env python3
"""
Local development server skeleton
TODO: Implement your server logic
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add backend to path
sys.path.insert(0, 'backend')

# TODO: Configure your database if needed
# DB_CONFIG = {
#     'host': 'localhost',
#     'port': 5432,
#     'database': 'hla_compass',
#     'user': 'postgres',
#     'password': 'postgres'
# }

class ModuleServer(BaseHTTPRequestHandler):
    """HTTP server for local module development"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            
            html = '''<!DOCTYPE html>
<html>
<head>
    <title>Module Server</title>
</head>
<body>
    <h1>Module Server Running</h1>
    <p>TODO: Implement your UI here</p>
    <p>Server running on http://localhost:3333</p>
</body>
</html>'''
            self.wfile.write(html.encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/execute':
            # TODO: Implement your API endpoint
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            input_data = json.loads(post_data)
            
            # Import and use your module
            try:
                from main import MyModule
                module = MyModule()
                result = module.execute(input_data, {'job_id': 'local-test'})
            except Exception as e:
                result = {'status': 'error', 'error': str(e)}
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


def main():
    """Start the server"""
    port = 3333
    
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                    Module Development Server                 ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Server:    http://localhost:{port}/                         ║
║  Status:    Ready                                            ║
║                                                               ║
║  TODO: Implement your module logic                           ║
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