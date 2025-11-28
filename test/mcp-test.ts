// test/mcp-test.ts
import { spawn } from 'child_process';
import { join } from 'path';

/**
 * Simple test script to verify the MCP server is working
 * This simulates an MCP client by sending JSON-RPC requests via stdio
 */

const serverPath = join(process.cwd(), 'src', 'index.ts');

async function testMCP() {
  console.log('Testing FairMind MCP Server...\n');

  const server = spawn('bun', [serverPath], {
    stdio: ['pipe', 'pipe', 'pipe'],
    cwd: process.cwd(),
  });

  let outputBuffer = '';

  server.stdout?.on('data', (data: Buffer) => {
    outputBuffer += data.toString();
    // MCP uses JSON-RPC, look for complete JSON responses
    try {
      const lines = outputBuffer.split('\n').filter(l => l.trim());
      outputBuffer = '';
      
      for (const line of lines) {
        if (line.trim().startsWith('{')) {
          const response = JSON.parse(line);
          console.log('Response:', JSON.stringify(response, null, 2));
        }
      }
    } catch (e) {
      // Buffer incomplete messages
    }
  });

  server.stderr?.on('data', (data: Buffer) => {
    const msg = data.toString();
    if (!msg.includes('FairMind MCP server running')) {
      console.error('Server stderr:', msg);
    }
  });

  // Wait for server to initialize
  await new Promise(resolve => setTimeout(resolve, 1000));

  // Test 1: List tools
  console.log('\nTest 1: Testing List Tools');
  const listToolsRequest = {
    jsonrpc: '2.0',
    id: 1,
    method: 'tools/list',
    params: {},
  };
  
  server.stdin?.write(JSON.stringify(listToolsRequest) + '\n');
  await new Promise(resolve => setTimeout(resolve, 500));

  // Test 2: Call evaluate_bias tool
  console.log('\nTest 2: Testing evaluate_bias tool');
  const evaluateRequest = {
    jsonrpc: '2.0',
    id: 2,
    method: 'tools/call',
    params: {
      name: 'evaluate_bias',
      arguments: {
        content: 'Nurses are gentle women who care for patients',
        protected_attribute: 'gender',
        task_type: 'generative',
      },
    },
  };
  
  server.stdin?.write(JSON.stringify(evaluateRequest) + '\n');
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Test 3: Call generate_counterfactuals tool
  console.log('\nTest 3: Testing generate_counterfactuals tool');
  const counterfactualRequest = {
    jsonrpc: '2.0',
    id: 3,
    method: 'tools/call',
    params: {
      name: 'generate_counterfactuals',
      arguments: {
        content: 'The nurse was gentle',
        sensitive_group: 'gender',
      },
    },
  };
  
  server.stdin?.write(JSON.stringify(counterfactualRequest) + '\n');
  await new Promise(resolve => setTimeout(resolve, 2000));

  console.log('\nTests completed!');
  console.log('Note: MCP servers communicate via JSON-RPC over stdio.');
  console.log('   For full integration testing, use an MCP client like Claude Desktop.\n');

  server.kill();
  process.exit(0);
}

testMCP().catch(console.error);

