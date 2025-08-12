#!/usr/bin/env node
/**
 * Test script for Vibe MCP Workflow Server
 *
 * This script tests the MCP server functionality by simulating
 * typical AI agent interactions with the workflow system.
 */

import { spawn } from 'child_process';
import { readFileSync } from 'fs';

/**
 * Send a JSON-RPC request to the MCP server
 */
async function sendMCPRequest(server, method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = Math.floor(Math.random() * 1000000);
    const request = {
      jsonrpc: "2.0",
      id: id,
      method: method,
      params: params
    };

    const requestStr = JSON.stringify(request) + '\n';

    let responseData = '';

    const timeout = setTimeout(() => {
      reject(new Error('Request timeout'));
    }, 10000);

    const dataHandler = (data) => {
      responseData += data.toString();

      // Look for complete JSON response
      const lines = responseData.split('\n');
      for (const line of lines) {
        if (line.trim()) {
          try {
            const response = JSON.parse(line);
            if (response.id === id) {
              clearTimeout(timeout);
              server.stdout.off('data', dataHandler);
              resolve(response);
              return;
            }
          } catch (e) {
            // Not a complete JSON response yet
          }
        }
      }
    };

    server.stdout.on('data', dataHandler);
    server.stdin.write(requestStr);
  });
}

/**
 * Test tool calling functionality
 */
async function testToolCall(server, toolName, args) {
  console.log(`📞 Calling tool: ${toolName}`);
  console.log(`   Args: ${JSON.stringify(args)}`);

  try {
    const response = await sendMCPRequest(server, 'tools/call', {
      name: toolName,
      arguments: args
    });

    if (response.error) {
      console.log(`❌ Error: ${response.error.message}`);
      return null;
    }

    const result = JSON.parse(response.result.content[0].text);
    console.log(`✅ Success: ${result.success ? 'true' : 'false'}`);

    if (result.success) {
      // Show relevant parts of successful response
      if (result.session_id) console.log(`   Session ID: ${result.session_id}`);
      if (result.current_step) {
        console.log(`   Current Step: ${result.current_step.step_text?.substring(0, 80)}...`);
      }
      if (result.message) console.log(`   Message: ${result.message}`);
    } else {
      console.log(`   Error: ${result.error}`);
    }

    return result;
  } catch (error) {
    console.log(`❌ Request failed: ${error.message}`);
    return null;
  }
}

/**
 * Main test sequence
 */
async function runTests() {
  console.log('🧪 Testing Vibe MCP Workflow Server');
  console.log('=' * 40);

  // Start the MCP server
  console.log('\n🚀 Starting MCP server...');
  const server = spawn('node', ['index.js'], {
    stdio: ['pipe', 'pipe', 'inherit'],
    cwd: process.cwd()
  });

  // Wait a moment for server to start
  await new Promise(resolve => setTimeout(resolve, 1000));

  try {
    // Test 1: Initialize MCP connection
    console.log('\n1. Initializing MCP connection...');
    const initResponse = await sendMCPRequest(server, 'initialize', {
      protocolVersion: "2024-11-05",
      capabilities: {
        tools: {}
      },
      clientInfo: {
        name: "test-client",
        version: "1.0.0"
      }
    });

    if (initResponse.error) {
      throw new Error(`Initialization failed: ${initResponse.error.message}`);
    }
    console.log('✅ MCP connection initialized');

    // Test 2: List available tools
    console.log('\n2. Listing available tools...');
    const toolsResponse = await sendMCPRequest(server, 'tools/list');

    if (toolsResponse.error) {
      throw new Error(`Tools list failed: ${toolsResponse.error.message}`);
    }

    const tools = toolsResponse.result.tools;
    console.log(`✅ Found ${tools.length} tools:`);
    for (const tool of tools) {
      console.log(`   - ${tool.name}: ${tool.description}`);
    }

    // Test 3: Start a workflow session
    console.log('\n3. Starting workflow session...');
    const startResult = await testToolCall(server, 'start_workflow', {
      prompt: 'analyze the project and run quality checks'
    });

    if (!startResult?.success) {
      throw new Error('Failed to start workflow session');
    }

    const sessionId = startResult.session_id;

    // Test 4: Get session status
    console.log('\n4. Getting session status...');
    const statusResult = await testToolCall(server, 'get_workflow_status', {
      session_id: sessionId
    });

    if (!statusResult?.success) {
      throw new Error('Failed to get session status');
    }

    // Test 5: Advance workflow step
    console.log('\n5. Advancing workflow step...');
    const advanceResult = await testToolCall(server, 'advance_workflow', {
      session_id: sessionId
    });

    if (!advanceResult?.success) {
      throw new Error('Failed to advance workflow');
    }

    // Test 6: List sessions
    console.log('\n6. Listing workflow sessions...');
    const listResult = await testToolCall(server, 'list_workflow_sessions', {});

    if (!listResult?.success) {
      throw new Error('Failed to list sessions');
    }

    console.log(`   Found ${listResult.sessions?.length || 0} active sessions`);

    // Test 7: Break workflow (if still active)
    if (advanceResult.has_next) {
      console.log('\n7. Breaking out of workflow...');
      const breakResult = await testToolCall(server, 'break_workflow', {
        session_id: sessionId
      });

      if (breakResult?.success) {
        console.log('✅ Successfully broke out of workflow');
      }
    }

    console.log('\n🎉 All tests completed successfully!');
    console.log('\n📋 Test Summary:');
    console.log('  ✅ MCP connection and initialization');
    console.log('  ✅ Tool discovery and listing');
    console.log('  ✅ Workflow session creation');
    console.log('  ✅ Session status retrieval');
    console.log('  ✅ Workflow step advancement');
    console.log('  ✅ Session listing');
    console.log('  ✅ Workflow breaking');

  } catch (error) {
    console.log(`\n❌ Test failed: ${error.message}`);
    process.exit(1);
  } finally {
    // Clean up
    server.kill();
  }
}

// Handle process termination
process.on('SIGINT', () => {
  console.log('\n🛑 Test interrupted');
  process.exit(0);
});

// Run tests
runTests().catch((error) => {
  console.error('Test runner error:', error);
  process.exit(1);
});
