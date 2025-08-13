#!/usr/bin/env python3
"""
Local development server for peptide analyzer module
Runs on http://localhost:3333
"""

import json
import os
import sys
import psycopg2
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add backend to path
sys.path.insert(0, 'backend')

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'hla_compass',
    'user': 'postgres',
    'password': 'postgres'
}

class ModuleServer(BaseHTTPRequestHandler):
    """HTTP server for local module development"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            # Serve the main HTML page
            self.serve_html()
        elif parsed_path.path == '/api/health':
            self.handle_health()
        elif parsed_path.path == '/api/peptides':
            self.handle_peptides()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/analyze':
            self.handle_analyze()
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
    <title>Peptide Analyzer - HLA-Compass Module</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #444;
        }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            font-family: 'Courier New', monospace;
            resize: vertical;
            min-height: 60px;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background: #5a67d8;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .status {
            margin: 20px 0;
            padding: 15px;
            border-radius: 6px;
            display: none;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            display: block;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            display: block;
        }
        .status.info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
            display: block;
        }
        .results {
            margin-top: 30px;
            display: none;
        }
        .results.show {
            display: block;
        }
        .result-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        .result-section h3 {
            color: #495057;
            margin-bottom: 15px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        th {
            background: #667eea;
            color: white;
        }
        tr:hover {
            background: #f1f3f5;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge.strong { background: #28a745; color: white; }
        .badge.weak { background: #ffc107; color: #333; }
        .badge.non { background: #dc3545; color: white; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .stat {
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 6px;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        pre {
            background: #f4f4f4;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧬 Peptide Analyzer Module</h1>
        <p class="subtitle">Analyze peptide sequences and predict HLA binding affinity</p>
        
        <div class="form-group">
            <label for="sequence">Peptide Sequence *</label>
            <textarea id="sequence" placeholder="Enter peptide sequence (e.g., SIINFEKL)">SIINFEKL</textarea>
            <small style="color: #666;">7-15 amino acids using standard codes (ACDEFGHIKLMNPQRSTVWY)</small>
        </div>
        
        <div class="form-group">
            <label for="hla">HLA Allele</label>
            <select id="hla">
                <option value="HLA-A*02:01">HLA-A*02:01</option>
                <option value="HLA-A*01:01">HLA-A*01:01</option>
                <option value="HLA-A*03:01">HLA-A*03:01</option>
                <option value="HLA-A*24:02">HLA-A*24:02</option>
                <option value="HLA-B*07:02">HLA-B*07:02</option>
                <option value="HLA-B*08:01">HLA-B*08:01</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="limit">Max Similar Peptides</label>
            <input type="number" id="limit" value="10" min="1" max="100">
        </div>
        
        <button onclick="analyzePeptide()">
            Analyze Peptide
            <span id="loading" class="loading" style="display:none;"></span>
        </button>
        
        <div id="status" class="status"></div>
        
        <div id="results" class="results">
            <div class="result-section">
                <h3>Sequence Analysis</h3>
                <div id="analysis"></div>
            </div>
            
            <div class="result-section">
                <h3>HLA Binding Prediction</h3>
                <div id="prediction"></div>
            </div>
            
            <div class="result-section">
                <h3>Similar Peptides in Database</h3>
                <div id="similar"></div>
            </div>
        </div>
    </div>

    <script>
        async function analyzePeptide() {
            const sequence = document.getElementById('sequence').value.trim().toUpperCase();
            const hla = document.getElementById('hla').value;
            const limit = parseInt(document.getElementById('limit').value);
            
            // Validate
            if (!sequence) {
                showStatus('Please enter a peptide sequence', 'error');
                return;
            }
            
            if (!/^[ACDEFGHIKLMNPQRSTVWY]+$/.test(sequence)) {
                showStatus('Invalid sequence. Use only standard amino acids', 'error');
                return;
            }
            
            if (sequence.length < 7 || sequence.length > 15) {
                showStatus('Sequence must be 7-15 amino acids long', 'error');
                return;
            }
            
            // Show loading
            document.getElementById('loading').style.display = 'inline-block';
            document.querySelector('button').disabled = true;
            showStatus('Analyzing peptide...', 'info');
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        sequence: sequence,
                        hla_allele: hla,
                        limit: limit
                    })
                });
                
                const result = await response.json();
                
                if (result.status === 'success' && result.data) {
                    showStatus('Analysis complete!', 'success');
                    displayResults(result.data);
                } else {
                    showStatus(result.error || 'Analysis failed', 'error');
                }
            } catch (error) {
                showStatus('Error: ' + error.message, 'error');
            } finally {
                document.getElementById('loading').style.display = 'none';
                document.querySelector('button').disabled = false;
            }
        }
        
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.className = 'status ' + type;
            status.textContent = message;
        }
        
        function displayResults(data) {
            // Show results section
            document.getElementById('results').classList.add('show');
            
            // Display analysis
            const analysis = data.analysis;
            document.getElementById('analysis').innerHTML = `
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">${analysis.length}</div>
                        <div class="stat-label">Length (aa)</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">${analysis.molecular_weight.toFixed(1)}</div>
                        <div class="stat-label">MW (Da)</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">${analysis.hydrophobicity.toFixed(1)}%</div>
                        <div class="stat-label">Hydrophobicity</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">${analysis.charge_ratio.toFixed(1)}%</div>
                        <div class="stat-label">Charged</div>
                    </div>
                </div>
                <p style="margin-top:15px;"><strong>Sequence:</strong> <code style="font-size:18px;">${analysis.sequence}</code></p>
            `;
            
            // Display prediction
            const pred = data.predictions;
            const badgeClass = pred.binding_class === 'Strong Binder' ? 'strong' : 
                               pred.binding_class === 'Weak Binder' ? 'weak' : 'non';
            document.getElementById('prediction').innerHTML = `
                <p><strong>Allele:</strong> ${pred.hla_allele}</p>
                <p><strong>Score:</strong> ${pred.score.toFixed(1)} / 100</p>
                <p><strong>Classification:</strong> <span class="badge ${badgeClass}">${pred.binding_class}</span></p>
                <p><strong>Percentile Rank:</strong> ${pred.percentile_rank.toFixed(1)}%</p>
            `;
            
            // Display similar peptides
            if (data.similar_peptides && data.similar_peptides.length > 0) {
                let tableHtml = '<table><tr><th>Sequence</th><th>Length</th><th>MW</th><th>Source</th><th>Similarity</th></tr>';
                data.similar_peptides.forEach(p => {
                    tableHtml += `<tr>
                        <td><code>${p.sequence}</code></td>
                        <td>${p.length}</td>
                        <td>${p.molecular_weight?.toFixed(1) || 'N/A'}</td>
                        <td>${p.source}</td>
                        <td>${p.similarity.toFixed(1)}%</td>
                    </tr>`;
                });
                tableHtml += '</table>';
                document.getElementById('similar').innerHTML = tableHtml;
            } else {
                document.getElementById('similar').innerHTML = '<p>No similar peptides found in database</p>';
            }
        }
        
        // Test database on load
        window.onload = async function() {
            try {
                const response = await fetch('/api/health');
                const data = await response.json();
                if (data.status === 'healthy') {
                    console.log('✅ Database connected:', data);
                }
            } catch (error) {
                console.error('Database connection failed:', error);
            }
        };
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def handle_health(self):
        """Check database health"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM scientific.peptides")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            response = {
                'status': 'healthy',
                'database': 'connected',
                'peptide_count': count
            }
        except Exception as e:
            response = {
                'status': 'error',
                'message': str(e)
            }
        
        self.wfile.write(json.dumps(response).encode())
    
    def handle_peptides(self):
        """Get peptides from database"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sequence, length, molecular_weight, source 
                FROM scientific.peptides 
                LIMIT 10
            """)
            rows = cursor.fetchall()
            
            peptides = []
            for row in rows:
                peptides.append({
                    'sequence': row[0],
                    'length': row[1],
                    'molecular_weight': float(row[2]) if row[2] else 0,
                    'source': row[3]
                })
            
            cursor.close()
            conn.close()
            
            response = {'peptides': peptides}
        except Exception as e:
            response = {'error': str(e)}
        
        self.wfile.write(json.dumps(response).encode())
    
    def handle_analyze(self):
        """Analyze peptide using the module"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        input_data = json.loads(post_data)
        
        # Import and use the module
        try:
            from main import PeptideAnalyzer
            module = PeptideAnalyzer()
            
            # Mock the SDK database connection for local testing
            module.peptides = MockPeptideDB()
            
            result = module.execute(input_data, {'job_id': 'local-test'})
        except ImportError:
            # Fallback if module not found
            result = {
                'status': 'error',
                'error': 'Module not found. Make sure backend/main.py exists'
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
    
    def log_message(self, format, *args):
        """Override to reduce noise"""
        if '/api/' in self.path:
            print(f"[API] {self.path}")


class MockPeptide:
    """Mock peptide object for local testing"""
    def __init__(self, sequence, length, mw, source):
        self.sequence = sequence
        self.length = length
        self.molecular_weight = mw
        self.source = source


class MockPeptideDB:
    """Mock database for local testing"""
    def search(self, **kwargs):
        """Return mock peptides from database"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            # Build query based on parameters
            query = "SELECT sequence, length, molecular_weight, source FROM scientific.peptides WHERE 1=1"
            params = []
            
            if 'min_length' in kwargs:
                query += " AND length >= %s"
                params.append(kwargs['min_length'])
            
            if 'max_length' in kwargs:
                query += " AND length <= %s"
                params.append(kwargs['max_length'])
            
            limit = kwargs.get('limit', 10)
            query += " LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            peptides = []
            for row in rows:
                peptides.append(MockPeptide(row[0], row[1], float(row[2]) if row[2] else 0, row[3]))
            
            cursor.close()
            conn.close()
            
            return peptides
        except:
            # Return empty list if database not available
            return []


def main():
    """Start the server"""
    port = 3333
    
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║               Peptide Analyzer Module Server                 ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Server:    http://localhost:{port}/                         ║
║  Database:  PostgreSQL on localhost:5432                     ║
║  Status:    Ready for testing                                ║
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
    # Check if psycopg2 is installed
    try:
        import psycopg2
    except ImportError:
        print("Installing psycopg2-binary...")
        os.system("pip install psycopg2-binary")
        import psycopg2
    
    main()