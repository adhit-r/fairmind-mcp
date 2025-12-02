// test/real-world-testing.ts
/**
 * Real-world testing script for FairMind MCP
 * Tests all tools through the MCP server to validate end-to-end functionality
 */
import { PythonBridge } from '../src/python_bridge.js';
import { handleEvaluateBias } from '../src/tools/evaluate_bias.js';
import { handleEvaluateBiasAdvanced } from '../src/tools/evaluate_bias_advanced.js';
import { handleGenerateCounterfactuals } from '../src/tools/generate_counterfactuals.js';
import { handleCompareCodeBias } from '../src/tools/compare_code_bias.js';
import { handleEvaluateModelOutputs } from '../src/tools/evaluate_model_outputs.js';
import { handleEvaluateModelResponse } from '../src/tools/evaluate_model_response.js';
import { handleAnalyzeRepositoryBias } from '../src/tools/analyze_repository_bias.js';

interface TestResult {
  tool: string;
  status: 'PASS' | 'FAIL' | 'SKIP';
  duration: number;
  error?: string;
  result?: any;
}

async function testTool(
  bridge: PythonBridge,
  toolName: string,
  handler: (bridge: PythonBridge, args: any) => Promise<any>,
  args: any,
  timeout: number = 30000
): Promise<TestResult> {
  const startTime = performance.now();
  
  try {
    console.log(`\n🧪 Testing: ${toolName}`);
    console.log(`   Args: ${JSON.stringify(args, null, 2).substring(0, 100)}...`);
    
    const result = await Promise.race([
      handler(bridge, args),
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Timeout')), timeout)
      ),
    ]);
    
    const duration = performance.now() - startTime;
    
    console.log(`   ✅ PASS (${duration.toFixed(0)}ms)`);
    
    return {
      tool: toolName,
      status: 'PASS',
      duration,
      result,
    };
  } catch (error: any) {
    const duration = performance.now() - startTime;
    const errorMsg = error.message || String(error);
    
    console.log(`   ❌ FAIL (${duration.toFixed(0)}ms): ${errorMsg}`);
    
    return {
      tool: toolName,
      status: 'FAIL',
      duration,
      error: errorMsg,
    };
  }
}

async function runRealWorldTests() {
  console.log('='.repeat(70));
  console.log('FairMind MCP - Real-World Testing');
  console.log('='.repeat(70));
  
  const bridge = new PythonBridge();
  const results: TestResult[] = [];
  
  // Wait for Python process to initialize
  console.log('\n⏳ Initializing Python bridge...');
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  try {
    // Test 1: evaluate_bias (basic text)
    results.push(await testTool(bridge, 'evaluate_bias', handleEvaluateBias, {
      content: 'Nurses are gentle women who care for patients.',
      protected_attribute: 'gender',
      task_type: 'generative',
      content_type: 'text',
    }));
    
    // Test 2: evaluate_bias (code)
    results.push(await testTool(bridge, 'evaluate_bias', handleEvaluateBias, {
      content: 'function getAdminUser() { return "admin"; }',
      protected_attribute: 'gender',
      task_type: 'generative',
      content_type: 'code',
    }));
    
    // Test 3: evaluate_bias_advanced
    results.push(await testTool(bridge, 'evaluate_bias_advanced', handleEvaluateBiasAdvanced, {
      content: 'The CEO is a strong leader who makes tough decisions.',
      protected_attributes: ['gender', 'age'],
      task_type: 'generative',
      content_type: 'text',
    }));
    
    // Test 4: generate_counterfactuals
    results.push(await testTool(bridge, 'generate_counterfactuals', handleGenerateCounterfactuals, {
      content: 'The nurse helped the patient.',
      sensitive_group: 'gender',
    }));
    
    // Test 5: compare_code_bias
    results.push(await testTool(bridge, 'compare_code_bias', handleCompareCodeBias, {
      code_a: 'function getUser() { return "admin"; }',
      code_b: 'function fetchUser() { return "user"; }',
      persona_a: 'Persona A',
      persona_b: 'Persona B',
    }));
    
    // Test 6: evaluate_model_outputs
    results.push(await testTool(bridge, 'evaluate_model_outputs', handleEvaluateModelOutputs, {
      outputs: [
        'The doctor examined the patient.',
        'The nurse helped the patient.',
      ],
      protected_attributes: ['gender'],
      task_type: 'generative',
      content_type: 'text',
    }));
    
    // Test 7: evaluate_model_response
    results.push(await testTool(bridge, 'evaluate_model_response', handleEvaluateModelResponse, {
      prompt: 'Describe a typical software engineer.',
      response: 'A software engineer is typically a young man who codes all day.',
      protected_attributes: ['gender', 'age'],
      task_type: 'generative',
      content_type: 'text',
    }));
    
    // Test 8: analyze_repository_bias (small test)
    const repoPath = process.cwd();
    results.push(await testTool(bridge, 'analyze_repository_bias', handleAnalyzeRepositoryBias, {
      repository_path: repoPath,
      protected_attributes: ['gender'],
      max_commits: 5,  // Small test
      min_commits_per_author: 1,
      anonymize_authors: false,
    }, 60000));  // 60s timeout for repo analysis
    
    // Print summary
    console.log('\n' + '='.repeat(70));
    console.log('TEST SUMMARY');
    console.log('='.repeat(70));
    
    const passed = results.filter(r => r.status === 'PASS').length;
    const failed = results.filter(r => r.status === 'FAIL').length;
    const skipped = results.filter(r => r.status === 'SKIP').length;
    
    console.log(`\n✅ Passed: ${passed}/${results.length}`);
    console.log(`❌ Failed: ${failed}/${results.length}`);
    console.log(`⏭️  Skipped: ${skipped}/${results.length}`);
    
    const totalDuration = results.reduce((sum, r) => sum + r.duration, 0);
    console.log(`\n⏱️  Total Duration: ${(totalDuration / 1000).toFixed(2)}s`);
    
    if (failed > 0) {
      console.log('\n❌ FAILED TESTS:');
      results
        .filter(r => r.status === 'FAIL')
        .forEach(r => {
          console.log(`\n   ${r.tool}:`);
          console.log(`   Error: ${r.error}`);
        });
    }
    
    console.log('\n' + '='.repeat(70));
    
    if (failed === 0) {
      console.log('✅ All tests passed!');
    } else {
      console.log(`⚠️  ${failed} test(s) failed. Review errors above.`);
      process.exit(1);
    }
    
  } catch (error: any) {
    console.error('\n❌ Test suite failed:', error);
    process.exit(1);
  } finally {
    bridge.destroy();
  }
}

runRealWorldTests().catch(console.error);

