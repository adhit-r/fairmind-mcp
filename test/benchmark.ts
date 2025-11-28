// test/benchmark.ts
/**
 * Performance Benchmarking Suite for FairMind MCP
 * 
 * Measures:
 * - TOON vs JSON token savings
 * - Latency for different content sizes
 * - Response times per tool
 * - Throughput (requests/second)
 * - Memory usage patterns
 */
import { PythonBridge } from '../src/python_bridge.js';
import { encode } from '@toon-format/toon';

interface BenchmarkResult {
  name: string;
  jsonSize: number;
  toonSize: number;
  tokenSavings: number;
  tokenSavingsPercent: number;
  latency: number;
  success: boolean;
  error?: string;
}

interface ToolBenchmark {
  tool: string;
  results: BenchmarkResult[];
  avgLatency: number;
  avgTokenSavings: number;
  successRate: number;
}

// Test content samples of different sizes
const TEST_CONTENT = {
  small: 'Nurses are gentle women who care for patients.',
  medium: `We are looking for a software engineer to join our team. The ideal candidate should have strong programming skills and be able to work independently. Experience with Python, JavaScript, and cloud technologies is preferred. The role requires excellent communication skills and the ability to collaborate with cross-functional teams.`,
  large: `The technology industry has long been criticized for its lack of diversity and inclusion. Despite numerous initiatives and programs aimed at increasing representation of women and underrepresented minorities, progress has been slow. Studies have shown that diverse teams perform better, yet many companies continue to struggle with creating truly inclusive environments. This bias extends beyond hiring practices into product development, where algorithms and AI systems can perpetuate and amplify existing inequalities. Fairness in AI is not just a technical challenge but a fundamental requirement for building systems that serve all members of society equitably.`,
  code: `function processUser(user) {
    if (user.gender === 'female') {
      return applyDiscount(user, 0.1);
    } else if (user.gender === 'male') {
      return applyFullPrice(user);
    }
    return user;
  }`,
};

// Sample responses for token counting
const SAMPLE_RESPONSES = {
  evaluate_bias: {
    status: 'FAIL',
    metrics: [
      {
        name: 'Gender_Stereotype_Disparity',
        value: 0.89,
        threshold: 0.5,
        result: 'FAIL',
      },
    ],
    details: 'Detected 5 female-associated and 2 male-associated stereotype terms.',
  },
  generate_counterfactuals: {
    counterfactuals: [
      'The medical professional was gentle',
      'The healthcare worker was gentle',
      'The clinician was gentle',
    ],
  },
};

async function measureTokenSavings(data: any): Promise<{ json: number; toon: number; savings: number; savingsPercent: number }> {
  const jsonStr = JSON.stringify(data);
  const jsonSize = jsonStr.length;
  
  const toonStr = encode(data);
  const toonSize = toonStr.length;
  
  // Approximate token count (rough estimate: 1 token ≈ 4 characters)
  const jsonTokens = Math.ceil(jsonSize / 4);
  const toonTokens = Math.ceil(toonSize / 4);
  
  const savings = jsonTokens - toonTokens;
  const savingsPercent = ((savings / jsonTokens) * 100);
  
  return {
    json: jsonTokens,
    toon: toonTokens,
    savings,
    savingsPercent,
  };
}

async function benchmarkTool(
  bridge: PythonBridge,
  toolName: string,
  args: any,
  iterations: number = 5
): Promise<ToolBenchmark> {
  const results: BenchmarkResult[] = [];
  
  console.log(`\nBenchmarking ${toolName}...`);
  
  for (let i = 0; i < iterations; i++) {
    const startTime = performance.now();
    
    try {
      let result;
      
      switch (toolName) {
        case 'evaluate_bias':
          result = await bridge.evaluateBias(
            args.content,
            args.protected_attribute || 'gender',
            args.task_type || 'generative',
            args.content_type || 'text'
          );
          break;
        case 'generate_counterfactuals':
          result = await bridge.generateCounterfactuals(
            args.content,
            args.sensitive_group || 'gender'
          );
          break;
        case 'evaluate_bias_advanced':
          result = await bridge.evaluateBiasAdvanced(
            args.content,
            args.protected_attributes || ['gender'],
            args.task_type || 'generative',
            true,
            false,
            undefined,
            args.content_type || 'text'
          );
          break;
        default:
          throw new Error(`Unknown tool: ${toolName}`);
      }
      
      const endTime = performance.now();
      const latency = endTime - startTime;
      
      // Measure token savings
      const tokenMetrics = await measureTokenSavings(result);
      
      results.push({
        name: `${toolName} (iteration ${i + 1})`,
        jsonSize: tokenMetrics.jsonBytes,
        toonSize: tokenMetrics.toonBytes,
        tokenSavings: tokenMetrics.savings,
        tokenSavingsPercent: tokenMetrics.savingsPercent,
        latency,
        success: true,
      });
      
      console.log(`  Iteration ${i + 1}: ${latency.toFixed(2)}ms, ${tokenMetrics.savingsPercent.toFixed(1)}% token savings`);
    } catch (error) {
      const endTime = performance.now();
      results.push({
        name: `${toolName} (iteration ${i + 1})`,
        jsonSize: 0,
        toonSize: 0,
        tokenSavings: 0,
        tokenSavingsPercent: 0,
        latency: endTime - startTime,
        success: false,
        error: error instanceof Error ? error.message : String(error),
      });
    }
  }
  
  const successful = results.filter(r => r.success);
  const avgLatency = successful.length > 0
    ? successful.reduce((sum, r) => sum + r.latency, 0) / successful.length
    : 0;
  const avgTokenSavings = successful.length > 0
    ? successful.reduce((sum, r) => sum + r.tokenSavingsPercent, 0) / successful.length
    : 0;
  const successRate = (successful.length / results.length) * 100;
  
  return {
    tool: toolName,
    results,
    avgLatency,
    avgTokenSavings,
    successRate,
  };
}

async function benchmarkThroughput(
  bridge: PythonBridge,
  toolName: string,
  args: any,
  concurrentRequests: number = 10
): Promise<{ requestsPerSecond: number; avgLatency: number; errors: number; minLatency: number; maxLatency: number }> {
  console.log(`\nThroughput test: ${concurrentRequests} concurrent requests...`);
  
  const latencies: number[] = [];
  const startTime = performance.now();
  
  const promises = Array(concurrentRequests).fill(null).map(async () => {
    const reqStart = performance.now();
    try {
      let result;
      switch (toolName) {
        case 'evaluate_bias':
          result = await bridge.evaluateBias(
            args.content,
            args.protected_attribute || 'gender',
            args.task_type || 'generative',
            args.content_type || 'text'
          );
          break;
        default:
          return null;
      }
      const reqEnd = performance.now();
      latencies.push(reqEnd - reqStart);
      return result;
    } catch {
      const reqEnd = performance.now();
      latencies.push(reqEnd - reqStart);
      return null;
    }
  });
  
  const results = await Promise.all(promises);
  const endTime = performance.now();
  const totalTime = (endTime - startTime) / 1000; // seconds
  
  const successful = results.filter(r => r !== null);
  const requestsPerSecond = successful.length / totalTime;
  const avgLatency = latencies.length > 0 
    ? latencies.reduce((a, b) => a + b, 0) / latencies.length 
    : 0;
  const minLatency = latencies.length > 0 ? Math.min(...latencies) : 0;
  const maxLatency = latencies.length > 0 ? Math.max(...latencies) : 0;
  const errors = concurrentRequests - successful.length;
  
  return {
    requestsPerSecond,
    avgLatency,
    errors,
    minLatency,
    maxLatency,
  };
}

async function runBenchmarks() {
  console.log('='.repeat(60));
  console.log('FairMind MCP Performance Benchmark Suite');
  console.log('='.repeat(60));
  
  const bridge = new PythonBridge();
  
  try {
    // Wait for Python process to initialize
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const benchmarks: ToolBenchmark[] = [];
    
    // 1. Benchmark evaluate_bias with different content sizes
    console.log('\n[1/4] Content Size Impact on evaluate_bias');
    console.log('-'.repeat(60));
    
    for (const [size, content] of Object.entries(TEST_CONTENT)) {
      const result = await benchmarkTool(
        bridge,
        'evaluate_bias',
        {
          content,
          protected_attribute: 'gender',
          task_type: 'generative',
          content_type: size === 'code' ? 'code' : 'text',
        },
        3
      );
      benchmarks.push(result);
    }
    
    // 2. Benchmark different tools
    console.log('\n[2/4] Tool Performance Comparison');
    console.log('-'.repeat(60));
    
    const toolBenchmarks = [
      {
        name: 'evaluate_bias',
        args: {
          content: TEST_CONTENT.medium,
          protected_attribute: 'gender',
          task_type: 'generative',
        },
      },
      {
        name: 'generate_counterfactuals',
        args: {
          content: 'The nurse was gentle',
          sensitive_group: 'gender',
        },
      },
      {
        name: 'evaluate_bias_advanced',
        args: {
          content: TEST_CONTENT.medium,
          protected_attributes: ['gender', 'race'],
          task_type: 'generative',
        },
      },
    ];
    
    for (const { name, args } of toolBenchmarks) {
      const result = await benchmarkTool(bridge, name, args, 3);
      benchmarks.push(result);
    }
    
    // 3. Token savings analysis
    console.log('\n[3/4] TOON vs JSON Token Savings Analysis');
    console.log('-'.repeat(60));
    
    const tokenAnalysis = await measureTokenSavings(SAMPLE_RESPONSES.evaluate_bias);
    console.log(`Sample evaluate_bias response:`);
    console.log(`  JSON: ${tokenAnalysis.jsonBytes} bytes (${tokenAnalysis.json} tokens)`);
    console.log(`  TOON: ${tokenAnalysis.toonBytes} bytes (${tokenAnalysis.toon} tokens)`);
    console.log(`  Savings: ${tokenAnalysis.savings} tokens (${tokenAnalysis.savingsPercent.toFixed(1)}%)`);
    console.log(`  Size reduction: ${((tokenAnalysis.jsonBytes - tokenAnalysis.toonBytes) / tokenAnalysis.jsonBytes * 100).toFixed(1)}%`);
    
    const counterfactualAnalysis = await measureTokenSavings(SAMPLE_RESPONSES.generate_counterfactuals);
    console.log(`\nSample generate_counterfactuals response:`);
    console.log(`  JSON: ${counterfactualAnalysis.jsonBytes} bytes (${counterfactualAnalysis.json} tokens)`);
    console.log(`  TOON: ${counterfactualAnalysis.toonBytes} bytes (${counterfactualAnalysis.toon} tokens)`);
    console.log(`  Savings: ${counterfactualAnalysis.savings} tokens (${counterfactualAnalysis.savingsPercent.toFixed(1)}%)`);
    if (counterfactualAnalysis.jsonBytes > 0) {
      console.log(`  Size reduction: ${((counterfactualAnalysis.jsonBytes - counterfactualAnalysis.toonBytes) / counterfactualAnalysis.jsonBytes * 100).toFixed(1)}%`);
    }
    
    // 4. Throughput test
    console.log('\n[4/4] Throughput Test');
    console.log('-'.repeat(60));
    
    const throughput = await benchmarkThroughput(
      bridge,
      'evaluate_bias',
      {
        content: TEST_CONTENT.small,
        protected_attribute: 'gender',
        task_type: 'generative',
      },
      10
    );
    
    console.log(`  Requests/second: ${throughput.requestsPerSecond.toFixed(2)}`);
    console.log(`  Average latency: ${throughput.avgLatency.toFixed(2)}ms`);
    console.log(`  Min latency: ${throughput.minLatency.toFixed(2)}ms`);
    console.log(`  Max latency: ${throughput.maxLatency.toFixed(2)}ms`);
    console.log(`  Errors: ${throughput.errors}`);
    
    // Summary Report
    console.log('\n' + '='.repeat(60));
    console.log('BENCHMARK SUMMARY');
    console.log('='.repeat(60));
    
    console.log('\nTool Performance:');
    benchmarks.forEach(b => {
      if (b.results.length > 0 && b.successRate > 0) {
        console.log(`  ${b.tool}:`);
        console.log(`    Avg Latency: ${b.avgLatency.toFixed(2)}ms`);
        console.log(`    Avg Token Savings: ${b.avgTokenSavings.toFixed(1)}%`);
        console.log(`    Success Rate: ${b.successRate.toFixed(1)}%`);
      }
    });
    
    console.log('\nOverall Metrics:');
    const allLatencies = benchmarks.flatMap(b => b.results.filter(r => r.success).map(r => r.latency));
    const allSavings = benchmarks.flatMap(b => b.results.filter(r => r.success).map(r => r.tokenSavingsPercent));
    const allJsonSizes = benchmarks.flatMap(b => b.results.filter(r => r.success).map(r => r.jsonSize));
    const allToonSizes = benchmarks.flatMap(b => b.results.filter(r => r.success).map(r => r.toonSize));
    
    if (allLatencies.length > 0) {
      const avgLatency = allLatencies.reduce((a, b) => a + b, 0) / allLatencies.length;
      const p95Latency = allLatencies.sort((a, b) => a - b)[Math.floor(allLatencies.length * 0.95)];
      const p99Latency = allLatencies.sort((a, b) => a - b)[Math.floor(allLatencies.length * 0.99)];
      const avgSavings = allSavings.reduce((a, b) => a + b, 0) / allSavings.length;
      const totalJsonBytes = allJsonSizes.length > 0 ? allJsonSizes.reduce((a, b) => a + b, 0) : 0;
      const totalToonBytes = allToonSizes.length > 0 ? allToonSizes.reduce((a, b) => a + b, 0) : 0;
      const overallSizeReduction = totalJsonBytes > 0 
        ? ((totalJsonBytes - totalToonBytes) / totalJsonBytes * 100) 
        : 0;
      
      console.log(`  Average Latency: ${avgLatency.toFixed(2)}ms`);
      console.log(`  P95 Latency: ${p95Latency.toFixed(2)}ms`);
      console.log(`  P99 Latency: ${p99Latency.toFixed(2)}ms`);
      console.log(`  Average Token Savings: ${avgSavings.toFixed(1)}%`);
      console.log(`  Overall Size Reduction: ${overallSizeReduction.toFixed(1)}%`);
      console.log(`  Throughput: ${throughput.requestsPerSecond.toFixed(2)} req/s`);
      if (totalJsonBytes > 0) {
        console.log(`  Total JSON Size: ${(totalJsonBytes / 1024).toFixed(2)} KB`);
        console.log(`  Total TOON Size: ${(totalToonBytes / 1024).toFixed(2)} KB`);
        console.log(`  Bytes Saved: ${((totalJsonBytes - totalToonBytes) / 1024).toFixed(2)} KB`);
      }
    }
    
    console.log('\n' + '='.repeat(60));
    
  } catch (error) {
    console.error('Benchmark error:', error);
  } finally {
    bridge.destroy();
  }
}

// Run benchmarks
runBenchmarks().catch(console.error);

