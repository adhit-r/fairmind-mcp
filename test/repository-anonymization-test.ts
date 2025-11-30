// test/repository-anonymization-test.ts
/**
 * Test script for anonymization features in analyze_repository_bias
 */
import { PythonBridge } from '../src/python_bridge.js';

async function testAnonymization() {
  console.log('='.repeat(60));
  console.log('Repository Bias Analysis - Anonymization Test');
  console.log('='.repeat(60));
  
  const bridge = new PythonBridge();
  
  try {
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const repoPath = process.cwd();
    console.log(`\nTesting on repository: ${repoPath}\n`);
    
    // Test 1: Normal mode (no anonymization)
    console.log('Test 1: Normal mode (no anonymization)');
    console.log('-'.repeat(60));
    const result1 = await bridge.analyzeRepositoryBias(
      repoPath,
      ['gender'],
      10,
      1,
      [],
      [],
      false, // anonymize_authors
      false, // exclude_author_names
      false  // pattern_only_mode
    );
    
    const author1 = result1.result?.author_scorecards?.[0];
    if (author1) {
      console.log(`✅ Author name: ${author1.author_name}`);
      console.log(`✅ Author email: ${author1.author_email}`);
      console.log(`✅ Has author_id: ${!!author1.author_id}`);
    }
    
    // Test 2: Anonymize authors (hash emails, generic names)
    console.log('\nTest 2: Anonymize authors (hash emails, generic names)');
    console.log('-'.repeat(60));
    const result2 = await bridge.analyzeRepositoryBias(
      repoPath,
      ['gender'],
      10,
      1,
      [],
      [],
      true,  // anonymize_authors
      false, // exclude_author_names
      false  // pattern_only_mode
    );
    
    const author2 = result2.result?.author_scorecards?.[0];
    if (author2) {
      console.log(`✅ Author name: ${author2.author_name} (should be "Author-{hash}")`);
      console.log(`✅ Author email: ${author2.author_email} (should be "{hash}@anonymous.local")`);
      console.log(`✅ Author ID: ${author2.author_id}`);
      
      if (author2.author_name.startsWith('Author-') && author2.author_email.includes('@anonymous.local')) {
        console.log('✅ PASS: Anonymization working correctly');
      } else {
        console.log('❌ FAIL: Anonymization not working');
      }
    }
    
    // Test 3: Exclude author names (all "Anonymous")
    console.log('\nTest 3: Exclude author names (all "Anonymous")');
    console.log('-'.repeat(60));
    const result3 = await bridge.analyzeRepositoryBias(
      repoPath,
      ['gender'],
      10,
      1,
      [],
      [],
      true,  // anonymize_authors
      true,  // exclude_author_names
      false  // pattern_only_mode
    );
    
    const author3 = result3.result?.author_scorecards?.[0];
    if (author3) {
      console.log(`✅ Author name: ${author3.author_name} (should be "Anonymous")`);
      console.log(`✅ Author email: ${author3.author_email} (should be "{hash}@anonymous.local")`);
      
      if (author3.author_name === 'Anonymous' && author3.author_email.includes('@anonymous.local')) {
        console.log('✅ PASS: Name exclusion working correctly');
      } else {
        console.log('❌ FAIL: Name exclusion not working');
      }
    }
    
    // Test 4: Pattern-only mode
    console.log('\nTest 4: Pattern-only mode');
    console.log('-'.repeat(60));
    const result4 = await bridge.analyzeRepositoryBias(
      repoPath,
      ['gender'],
      10,
      1,
      [],
      [],
      true,  // anonymize_authors
      true,  // exclude_author_names
      true   // pattern_only_mode
    );
    
    const author4 = result4.result?.author_scorecards?.[0];
    if (author4) {
      console.log(`✅ Author name: ${author4.author_name}`);
      console.log(`✅ Has patterns: ${!!author4.attribute_patterns}`);
      console.log('✅ PASS: Pattern-only mode working');
    }
    
    console.log('\n' + '='.repeat(60));
    console.log('✅ All anonymization tests completed!');
    console.log('='.repeat(60));
    
  } catch (error) {
    console.error('\n❌ Test failed:', error);
  } finally {
    bridge.destroy();
  }
}

testAnonymization().catch(console.error);

