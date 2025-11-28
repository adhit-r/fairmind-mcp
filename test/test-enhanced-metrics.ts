#!/usr/bin/env bun
/**
 * Test script for enhanced metrics features
 * Tests multi-attribute detection, MetricFrame, and advanced evaluation
 */

import { PythonBridge } from '../src/python_bridge.js';

const bridge = new PythonBridge();

async function testEnhancedMetrics() {
  console.log('='.repeat(60));
  console.log('Testing Enhanced Metrics Features');
  console.log('='.repeat(60));

  try {
    // Test 1: Multi-attribute detection
    console.log('\n1. Testing Multi-Attribute Detection');
    console.log('-'.repeat(60));
    const multiAttrResult = await bridge.evaluateBias(
      'Seeking a young, energetic female nurse',
      '', // Not used when protected_attributes provided
      'generative',
      'text',
      ['gender', 'age']
    );
    console.log('Result:', JSON.stringify(multiAttrResult, null, 2));
    console.log('✓ Multi-attribute test passed');

    // Test 2: Advanced evaluation with MetricFrame
    console.log('\n2. Testing Advanced Evaluation with MetricFrame');
    console.log('-'.repeat(60));
    const advancedResult = await bridge.evaluateBiasAdvanced(
      'Nurses are gentle women who care for patients',
      ['gender'],
      'generative',
      true, // use_metricframe
      false, // use_aif360
      undefined, // metric_names
      'text'
    );
    console.log('Result:', JSON.stringify(advancedResult, null, 2));
    console.log('✓ Advanced evaluation test passed');

    // Test 3: Backward compatibility
    console.log('\n3. Testing Backward Compatibility');
    console.log('-'.repeat(60));
    const backwardResult = await bridge.evaluateBias(
      'Nurses are gentle women',
      'gender',
      'generative',
      'text'
    );
    console.log('Result:', JSON.stringify(backwardResult, null, 2));
    console.log('✓ Backward compatibility test passed');

    // Test 4: Multiple attributes with advanced
    console.log('\n4. Testing Multiple Attributes with Advanced');
    console.log('-'.repeat(60));
    const multiAdvancedResult = await bridge.evaluateBiasAdvanced(
      'Seeking a young, energetic female nurse',
      ['gender', 'age'],
      'generative',
      true,
      false,
      undefined,
      'text'
    );
    console.log('Result:', JSON.stringify(multiAdvancedResult, null, 2));
    console.log('✓ Multiple attributes advanced test passed');

    console.log('\n' + '='.repeat(60));
    console.log('All tests completed successfully!');
    console.log('='.repeat(60));

  } catch (error) {
    console.error('Test failed:', error);
    process.exit(1);
  } finally {
    bridge.destroy();
  }
}

testEnhancedMetrics();


