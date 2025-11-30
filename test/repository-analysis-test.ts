// test/repository-analysis-test.ts
/**
 * Test script for analyze_repository_bias tool
 * Tests the repository analysis feature on a real repository
 */
import { PythonBridge } from '../src/python_bridge.js';

async function testRepositoryAnalysis() {
  console.log('='.repeat(60));
  console.log('Repository Bias Analysis Test');
  console.log('='.repeat(60));
  
  const bridge = new PythonBridge();
  
  try {
    // Wait for Python process to initialize
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const repoPath = process.cwd(); // Test on current repo
    console.log(`\nTesting on repository: ${repoPath}`);
    console.log('This may take a few minutes...\n');
    
    const startTime = performance.now();
    
    // Test with limited commits for faster testing
    const result = await bridge.analyzeRepositoryBias(
      repoPath,
      ['gender', 'race'], // Test with 2 attributes first
      50, // Limit to last 50 commits for testing
      3,  // Minimum 3 commits per author
      ['.ts', '.py', '.js'], // Only analyze code files
      ['node_modules/', 'vendor/', '.git/', 'dist/', 'build/', '.venv/'],
      false, // anonymize_authors
      false, // exclude_author_names
      false  // pattern_only_mode
    );
    
    const endTime = performance.now();
    const duration = ((endTime - startTime) / 1000).toFixed(2);
    
    console.log(`\n✅ Analysis completed in ${duration} seconds\n`);
    console.log('='.repeat(60));
    console.log('RESULTS');
    console.log('='.repeat(60));
    
    if (result.error) {
      console.error('❌ Error:', result.error);
      return;
    }
    
    const analysis = result.result;
    
    // Print summary
    console.log('\n📊 Analysis Summary:');
    console.log(`   Total commits analyzed: ${analysis.analysis_summary?.total_commits_analyzed || 0}`);
    console.log(`   Total authors: ${analysis.analysis_summary?.total_authors || 0}`);
    console.log(`   Protected attributes: ${analysis.analysis_summary?.protected_attributes?.join(', ') || 'N/A'}`);
    
    // Print repository bias summary
    if (analysis.repository_bias_summary) {
      console.log('\n📈 Repository Bias Summary:');
      for (const [attr, data] of Object.entries(analysis.repository_bias_summary)) {
        console.log(`   ${attr}: ${data.total_failures} failures (${(data.failure_rate * 100).toFixed(1)}% failure rate)`);
      }
    }
    
    // Print top biased authors
    if (analysis.top_biased_authors && analysis.top_biased_authors.length > 0) {
      console.log('\n🔴 Top Biased Authors:');
      analysis.top_biased_authors.slice(0, 5).forEach((author: any, idx: number) => {
        console.log(`   ${idx + 1}. ${author.author_name} (${author.author_email})`);
        console.log(`      Bias Score: ${author.overall_bias_score} (${author.bias_level})`);
        console.log(`      Commits: ${author.total_commits}`);
        if (author.explanations && author.explanations.length > 0) {
          console.log(`      Issues: ${author.explanations[0]}`);
        }
      });
    }
    
    // Print least biased authors
    if (analysis.least_biased_authors && analysis.least_biased_authors.length > 0) {
      console.log('\n🟢 Least Biased Authors:');
      analysis.least_biased_authors.slice(0, 3).forEach((author: any, idx: number) => {
        console.log(`   ${idx + 1}. ${author.author_name} (${author.author_email})`);
        console.log(`      Bias Score: ${author.overall_bias_score} (${author.bias_level})`);
        console.log(`      Commits: ${author.total_commits}`);
      });
    }
    
    // Print sample author scorecard
    if (analysis.author_scorecards && analysis.author_scorecards.length > 0) {
      const sampleAuthor = analysis.author_scorecards[0];
      console.log('\n📋 Sample Author Scorecard:');
      console.log(`   Author: ${sampleAuthor.author_name}`);
      console.log(`   Email: ${sampleAuthor.author_email}`);
      console.log(`   Overall Bias Score: ${sampleAuthor.overall_bias_score}`);
      console.log(`   Bias Level: ${sampleAuthor.bias_level}`);
      console.log(`   Total Commits: ${sampleAuthor.total_commits}`);
      
      if (sampleAuthor.attribute_scores) {
        console.log('\n   Attribute Scores:');
        for (const [attr, score] of Object.entries(sampleAuthor.attribute_scores)) {
          const s = score as any;
          console.log(`     ${attr}: ${s.bias_score} (${s.fail_count}/${s.total_commits} commits failed)`);
        }
      }
      
      if (sampleAuthor.recommendations && sampleAuthor.recommendations.length > 0) {
        console.log('\n   Recommendations:');
        sampleAuthor.recommendations.forEach((rec: string) => {
          console.log(`     - ${rec}`);
        });
      }
    }
    
    console.log('\n' + '='.repeat(60));
    console.log('✅ Test completed successfully!');
    console.log('='.repeat(60));
    
  } catch (error) {
    console.error('\n❌ Test failed with error:');
    console.error(error);
    
    if (error instanceof Error) {
      console.error('\nError details:');
      console.error('  Message:', error.message);
      console.error('  Stack:', error.stack);
    }
  } finally {
    bridge.destroy();
  }
}

// Run test
testRepositoryAnalysis().catch(console.error);

