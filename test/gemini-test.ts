// test/gemini-test.ts
/**
 * Test FairMind MCP tools with Google Gemini API
 * This simulates how an LLM agent would use the fairness tools
 */
import { GoogleGenerativeAI } from '@google/generative-ai';
import { PythonBridge } from '../src/python_bridge.js';

async function testWithGemini(apiKey: string) {
  console.log('🤖 Testing FairMind MCP with Gemini API...\n');

  const genAI = new GoogleGenerativeAI(apiKey);
  const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });

  // Initialize Python bridge
  const bridge = new PythonBridge();

  // Define the tools as Gemini functions
  const tools = [
    {
      name: 'evaluate_bias',
      description: 'Evaluates text or data for bias against protected attributes using Fairlearn metrics. Returns a token-optimized fairness report.',
      parameters: {
        type: 'object',
        properties: {
          content: {
            type: 'string',
            description: 'The text or dataset row to evaluate for bias',
          },
          protected_attribute: {
            type: 'string',
            description: 'The protected attribute to check',
            enum: ['gender', 'race', 'age', 'disability'],
          },
          task_type: {
            type: 'string',
            description: 'The type of task being evaluated',
            enum: ['generative', 'classification'],
          },
        },
        required: ['content', 'protected_attribute', 'task_type'],
      },
    },
    {
      name: 'generate_counterfactuals',
      description: 'Generates alternative text suggestions to reduce bias using LiteRT-powered inference.',
      parameters: {
        type: 'object',
        properties: {
          content: {
            type: 'string',
            description: 'The text to generate counterfactuals for',
          },
          sensitive_group: {
            type: 'string',
            description: 'The sensitive group to focus on',
            enum: ['gender', 'race', 'age'],
          },
        },
        required: ['content', 'sensitive_group'],
      },
    },
  ];

  try {
    // Test 1: Ask Gemini to evaluate a biased text
    console.log('1️⃣  Testing: Gemini evaluating biased text\n');
    
    const prompt1 = `Please evaluate this job description for gender bias: "We are looking for a nurse who is gentle and nurturing. The ideal candidate is a woman who cares deeply about patients." Use the evaluate_bias tool to check for bias.`;

    const result1 = await model.generateContent({
      contents: [{ role: 'user', parts: [{ text: prompt1 }] }],
      tools: [{ functionDeclarations: tools }],
    });

    const response1 = result1.response;
    console.log('📝 Gemini Response:', response1.text());
    
    // Check if Gemini wants to call a function
    const functionCalls = response1.functionCalls();
    if (functionCalls && functionCalls.length > 0) {
      for (const call of functionCalls) {
        console.log(`\n🔧 Gemini wants to call: ${call.name}`);
        console.log('📥 Arguments:', JSON.stringify(call.args, null, 2));

        // Execute the tool call
        let toolResult;
        if (call.name === 'evaluate_bias') {
          toolResult = await bridge.evaluateBias(
            call.args.content as string,
            call.args.protected_attribute as string,
            call.args.task_type as 'generative' | 'classification'
          );
        } else if (call.name === 'generate_counterfactuals') {
          toolResult = await bridge.generateCounterfactuals(
            call.args.content as string,
            call.args.sensitive_group as string
          );
        }

        console.log('✅ Tool Result:', JSON.stringify(toolResult, null, 2));

        // Send result back to Gemini
        const result2 = await model.generateContent({
          contents: [
            { role: 'user', parts: [{ text: prompt1 }] },
            { role: 'model', parts: response1.candidates?.[0]?.content?.parts || [] },
            {
              role: 'function',
              parts: [
                {
                  functionResponse: {
                    name: call.name,
                    response: toolResult,
                  },
                },
              ],
            },
          ],
          tools: [{ functionDeclarations: tools }],
        });

        console.log('\n🤖 Gemini Final Response:', result2.response.text());
      }
    }

    // Test 2: Ask Gemini to generate counterfactuals
    console.log('\n\n2️⃣  Testing: Gemini generating counterfactuals\n');
    
    const prompt2 = `The text "The nurse was gentle" contains potential gender bias. Please use the generate_counterfactuals tool to suggest alternative wording.`;

    const result3 = await model.generateContent({
      contents: [{ role: 'user', parts: [{ text: prompt2 }] }],
      tools: [{ functionDeclarations: tools }],
    });

    const response2 = result3.response;
    console.log('📝 Gemini Response:', response2.text());
    
    const functionCalls2 = response2.functionCalls();
    if (functionCalls2 && functionCalls2.length > 0) {
      for (const call of functionCalls2) {
        console.log(`\n🔧 Gemini wants to call: ${call.name}`);
        console.log('📥 Arguments:', JSON.stringify(call.args, null, 2));

        const toolResult = await bridge.generateCounterfactuals(
          call.args.content as string,
          call.args.sensitive_group as string
        );

        console.log('✅ Tool Result:', JSON.stringify(toolResult, null, 2));

        const result4 = await model.generateContent({
          contents: [
            { role: 'user', parts: [{ text: prompt2 }] },
            { role: 'model', parts: response2.candidates?.[0]?.content?.parts || [] },
            {
              role: 'function',
              parts: [
                {
                  functionResponse: {
                    name: call.name,
                    response: toolResult,
                  },
                },
              ],
            },
          ],
          tools: [{ functionDeclarations: tools }],
        });

        console.log('\n🤖 Gemini Final Response:', result4.response.text());
      }
    }

    console.log('\n✅ All Gemini tests completed!');
  } catch (error) {
    console.error('❌ Error:', error);
  } finally {
    bridge.destroy();
  }
}

// Get API key from environment or command line
const apiKey = process.env.GEMINI_API_KEY || process.argv[2];

if (!apiKey) {
  console.error('❌ Please provide a Gemini API key:');
  console.error('   Option 1: Set GEMINI_API_KEY environment variable');
  console.error('   Option 2: Pass as argument: bun run test:gemini YOUR_API_KEY');
  process.exit(1);
}

testWithGemini(apiKey).catch(console.error);

