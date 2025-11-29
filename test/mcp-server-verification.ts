// test/mcp-server-verification.ts
/**
 * Verifies MCP server is working correctly
 * Can be used to test before trying with Claude Desktop/Cursor
 */
import { PythonBridge } from '../src/python_bridge.js';

async function verifyMCPServer() {
  console.log('='.repeat(60));
  console.log('MCP Server Verification');
  console.log('='.repeat(60));
  
  const bridge = new PythonBridge();
  
  try {
    // Wait for Python process to initialize
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const tests = [
      {
        name: 'evaluate_bias (text)',
        test: async () => {
          const result = await bridge.evaluateBias(
            'Nurses are gentle women who care for patients.',
            'gender',
            'generative',
            'text'
          );
          return result.result?.status !== undefined;
        }
      },
      {
        name: 'evaluate_bias (code)',
        test: async () => {
          const result = await bridge.evaluateBias(
            '// Nurses are gentle women\nfunction assignRole(user) { if (user.gender === "female") return "nurse"; }',
            'gender',
            'generative',
            'code'
          );
          return result.result?.status !== undefined;
        }
      },
      {
        name: 'generate_counterfactuals',
        test: async () => {
          const result = await bridge.generateCounterfactuals(
            'The nurse was gentle',
            'gender'
          );
          return result.counterfactuals !== undefined;
        }
      },
      {
        name: 'analyze_repository_bias',
        test: async () => {
          const result = await bridge.analyzeRepositoryBias(
            process.cwd(),
            ['gender'],
            5, // Just 5 commits for quick test
            1,
            [],
            []
          );
          return result.result?.analysis_summary !== undefined;
        }
      }
    ];
    
    console.log('\nRunning verification tests...\n');
    
    let passed = 0;
    let failed = 0;
    
    for (const test of tests) {
      try {
        const startTime = performance.now();
        const result = await test.test();
        const duration = ((performance.now() - startTime) / 1000).toFixed(2);
        
        if (result) {
          console.log(`✅ ${test.name} - PASSED (${duration}s)`);
          passed++;
        } else {
          console.log(`❌ ${test.name} - FAILED (unexpected result)`);
          failed++;
        }
      } catch (error) {
        console.log(`❌ ${test.name} - FAILED (${error instanceof Error ? error.message : String(error)})`);
        failed++;
      }
    }
    
    console.log('\n' + '='.repeat(60));
    console.log(`Results: ${passed} passed, ${failed} failed`);
    console.log('='.repeat(60));
    
    if (failed === 0) {
      console.log('\n✅ All tests passed! MCP server is ready for use.');
      console.log('\nNext steps:');
      console.log('1. Restart Claude Desktop or Cursor');
      console.log('2. Test tools in a conversation');
      console.log('3. See docs/REAL_WORLD_TESTING_QUICK_START.md for test prompts');
    } else {
      console.log('\n⚠️  Some tests failed. Check the errors above.');
      console.log('The MCP server may not work correctly with clients.');
    }
    
  } catch (error) {
    console.error('\n❌ Verification failed:', error);
  } finally {
    bridge.destroy();
  }
}

verifyMCPServer().catch(console.error);

