// test/python-bridge-test.ts
/**
 * Direct test of the Python bridge without MCP protocol
 * This tests the TOON communication layer
 */
import { PythonBridge } from '../src/python_bridge.js';

async function testPythonBridge() {
  console.log('Testing Python Bridge (Direct)...\n');

  const bridge = new PythonBridge();

  try {
    // Test 1: Evaluate bias
    console.log('Test 1: Testing evaluate_bias...');
    const biasResult = await bridge.evaluateBias(
      'Nurses are gentle women who care for patients',
      'gender',
      'generative'
    );
    console.log('Result:', JSON.stringify(biasResult, null, 2));

    // Test 2: Generate counterfactuals
    console.log('\nTest 2: Testing generate_counterfactuals...');
    const counterfactuals = await bridge.generateCounterfactuals(
      'The nurse was gentle',
      'gender'
    );
    console.log('Result:', JSON.stringify(counterfactuals, null, 2));

    console.log('\nAll Python bridge tests passed!');
  } catch (error) {
    console.error('Error:', error);
  } finally {
    bridge.destroy();
  }
}

testPythonBridge().catch(console.error);

