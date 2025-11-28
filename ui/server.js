// ui/server.js
// Simple Bun server to serve the UI and provide API endpoints for testing MCP tools

import { spawn } from 'child_process';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { readFileSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = join(__dirname, '..');
const PORT = 3000;

const server = Bun.serve({
  port: PORT,
  async fetch(req) {
    const url = new URL(req.url);
    
    // Serve UI
    if (url.pathname === '/' || url.pathname === '/ui' || url.pathname === '/ui/') {
      const html = readFileSync(join(__dirname, 'index.html'), 'utf-8');
      return new Response(html, {
        headers: { 'Content-Type': 'text/html' },
      });
    }
    
    // API endpoint to test MCP tools
    if (url.pathname === '/api/test-tool' && req.method === 'POST') {
      try {
        const { tool, params } = await req.json();
        
        // Get project root
        const pythonPath = join(projectRoot, 'py_engine', '.venv', 'bin', 'python');
        const scriptPath = join(projectRoot, 'py_engine', 'main.py');
        
        // Prepare command
        let command;
        if (tool === 'evaluate_bias') {
          command = {
            command: 'evaluate_bias',
            content: params.content,
            protected_attribute: params.protected_attribute,
            task_type: params.task_type
          };
        } else if (tool === 'generate_counterfactuals') {
          command = {
            command: 'generate_counterfactuals',
            content: params.content,
            sensitive_group: params.sensitive_group
          };
        } else {
          return new Response(JSON.stringify({ error: 'Unknown tool' }), {
            status: 400,
            headers: { 'Content-Type': 'application/json' },
          });
        }
        
        // Call Python process
        const python = spawn(pythonPath, [scriptPath], {
          cwd: join(projectRoot, 'py_engine'),
          stdio: ['pipe', 'pipe', 'pipe']
        });
        
        let output = '';
        let errorOutput = '';
        
        python.stdout.on('data', (data) => {
          output += data.toString();
        });
        
        python.stderr.on('data', (data) => {
          errorOutput += data.toString();
        });
        
        python.stdin.write(JSON.stringify(command) + '\n');
        python.stdin.end();
        
        return new Promise((resolve) => {
          python.on('close', (code) => {
            if (code !== 0) {
              resolve(new Response(JSON.stringify({ 
                error: 'Python process failed',
                details: errorOutput 
              }), {
                status: 500,
                headers: { 'Content-Type': 'application/json' },
              }));
              return;
            }
            
            try {
              const result = JSON.parse(output.trim());
              resolve(new Response(JSON.stringify(result), {
                headers: { 'Content-Type': 'application/json' },
              }));
            } catch (e) {
              resolve(new Response(JSON.stringify({ 
                error: 'Failed to parse result',
                output: output,
                errorOutput: errorOutput
              }), {
                status: 500,
                headers: { 'Content-Type': 'application/json' },
              }));
            }
          });
        });
        
      } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { 'Content-Type': 'application/json' },
        });
      }
    }
    
    // 404
    return new Response('Not Found', { status: 404 });
  },
});

console.log(`FairMind MCP UI running at http://localhost:${PORT}`);
console.log(`📖 Open http://localhost:${PORT} in your browser`);

