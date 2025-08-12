#!/usr/bin/env node
/**
 * Vibe MCP Workflow Server
 *
 * Provides MCP tools for step-by-step workflow execution using Vibe.
 * This server acts as a lightweight wrapper around Vibe's CLI commands,
 * enabling token-efficient workflow orchestration for AI agents.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { spawn } from 'child_process';

/**
 * Execute a Vibe CLI command and return parsed JSON result.
 *
 * @param {string[]} args - Command arguments to pass to vibe CLI
 * @param {string|null} workingDir - Optional working directory for the command
 * @returns {Promise<Object>} Parsed JSON response
 */
async function executeVibeCommand(args, workingDir = null) {
  return new Promise((resolve, reject) => {
    // Get the directory of this MCP server (should be in vibe/mcp-server/)
    const mcpServerDir = new URL('.', import.meta.url).pathname;
    const vibeProjectDir = mcpServerDir + '../';

    // Use caller's working directory if provided, otherwise use vibe project dir
    const commandWorkingDir = workingDir || vibeProjectDir;

    // Try UV first, then fall back to direct vibe command
    const useUV = process.env.USE_UV !== 'false';
    const command = useUV ? 'uv' : 'vibe';
    const commandArgs = useUV ? ['run', 'vibe', ...args] : args;

    const childProcess = spawn(command, commandArgs, {
      stdio: ['ignore', 'pipe', 'pipe'],
      cwd: commandWorkingDir,
      env: {
        ...process.env,
        // Set UV_PROJECT_ENVIRONMENT to point to vibe's environment when using UV
        ...(useUV && { UV_PROJECT_ENVIRONMENT: vibeProjectDir + '.venv' }),
        // Add vibe project to Python path as fallback
        PYTHONPATH: vibeProjectDir + ':' + (process.env.PYTHONPATH || '')
      }
    });

    let stdout = '';
    let stderr = '';

    childProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    childProcess.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    childProcess.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Vibe command failed with code ${code}: ${stderr}`));
        return;
      }

      try {
        const result = JSON.parse(stdout);
        resolve(result);
      } catch (e) {
        reject(new Error(`Failed to parse Vibe output as JSON: ${e.message}\\nOutput: ${stdout}`));
      }
    });

    childProcess.on('error', (error) => {
      reject(new Error(`Failed to spawn Vibe process: ${error.message}`));
    });
  });
}

/**
 * Validate session ID format.
 *
 * @param {string} sessionId - Session ID to validate
 * @returns {boolean} True if valid
 */
function isValidSessionId(sessionId) {
  // Session IDs should be 8-character hex strings
  return /^[a-f0-9]{8}$/.test(sessionId);
}

// Create MCP server
const server = new Server(
  {
    name: 'vibe-workflow-server',
    version: '0.1.1',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Tool: Start Workflow Session
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'start_workflow': {
        const { prompt, config, project_type, working_dir } = args;

        if (!prompt || typeof prompt !== 'string') {
          throw new Error('prompt is required and must be a string');
        }

        const vibeArgs = ['mcp', 'start', prompt];
        if (config) vibeArgs.push('--config', config);
        if (project_type) vibeArgs.push('--project-type', project_type);

        // Use provided working directory or default to process.cwd()
        const workingDir = working_dir || process.cwd();
        const result = await executeVibeCommand(vibeArgs, workingDir);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2)
            }
          ]
        };
      }

      case 'get_workflow_status': {
        const { session_id } = args;

        if (!session_id || !isValidSessionId(session_id)) {
          throw new Error('session_id is required and must be a valid 8-character hex string');
        }

        const result = await executeVibeCommand(['mcp', 'status', session_id]);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2)
            }
          ]
        };
      }

      case 'advance_workflow': {
        const { session_id } = args;

        if (!session_id || !isValidSessionId(session_id)) {
          throw new Error('session_id is required and must be a valid 8-character hex string');
        }

        const result = await executeVibeCommand(['mcp', 'next', session_id]);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2)
            }
          ]
        };
      }

      case 'break_workflow': {
        const { session_id } = args;

        if (!session_id || !isValidSessionId(session_id)) {
          throw new Error('session_id is required and must be a valid 8-character hex string');
        }

        const result = await executeVibeCommand(['mcp', 'break', session_id]);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2)
            }
          ]
        };
      }

      case 'back_workflow': {
        const { session_id } = args;

        if (!session_id || !isValidSessionId(session_id)) {
          throw new Error('session_id is required and must be a valid 8-character hex string');
        }

        const result = await executeVibeCommand(['mcp', 'back', session_id]);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2)
            }
          ]
        };
      }

      case 'restart_workflow': {
        const { session_id } = args;

        if (!session_id || !isValidSessionId(session_id)) {
          throw new Error('session_id is required and must be a valid 8-character hex string');
        }

        const result = await executeVibeCommand(['mcp', 'restart', session_id]);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2)
            }
          ]
        };
      }

      case 'list_workflow_sessions': {
        const result = await executeVibeCommand(['mcp', 'list']);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2)
            }
          ]
        };
      }

      case 'init_vibe_project': {
        const { project_type, working_dir } = args;

        const vibeArgs = ['mcp', 'init'];
        if (project_type) vibeArgs.push('--project-type', project_type);

        // Use provided working directory or default to process.cwd()
        const workingDir = working_dir || process.cwd();
        const result = await executeVibeCommand(vibeArgs, workingDir);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2)
            }
          ]
        };
      }

      case 'check_vibe_environment': {
        const { working_dir } = args;

        // Use provided working directory or default to process.cwd()
        const workingDir = working_dir || process.cwd();
        const result = await executeVibeCommand(['mcp', 'check'], workingDir);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2)
            }
          ]
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            success: false,
            error: error.message
          }, null, 2)
        }
      ],
      isError: true
    };
  }
});

// Tool definitions
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'start_workflow',
        description: 'Start a new step-by-step workflow session based on a natural language prompt',
        inputSchema: {
          type: 'object',
          properties: {
            prompt: {
              type: 'string',
              description: 'Natural language prompt describing what you want to accomplish'
            },
            config: {
              type: 'string',
              description: 'Optional path to Vibe configuration file'
            },
            project_type: {
              type: 'string',
              description: 'Optional project type override (e.g., python, vue_typescript, generic)'
            },
            working_dir: {
              type: 'string',
              description: 'Optional working directory to run commands in (defaults to current directory)'
            }
          },
          required: ['prompt']
        }
      },
      {
        name: 'get_workflow_status',
        description: 'Get the current status and step information for a workflow session',
        inputSchema: {
          type: 'object',
          properties: {
            session_id: {
              type: 'string',
              description: 'The session ID returned from start_workflow'
            }
          },
          required: ['session_id']
        }
      },
      {
        name: 'advance_workflow',
        description: 'Mark the current step as complete and advance to the next step in the workflow',
        inputSchema: {
          type: 'object',
          properties: {
            session_id: {
              type: 'string',
              description: 'The session ID for the workflow to advance'
            }
          },
          required: ['session_id']
        }
      },
      {
        name: 'break_workflow',
        description: 'Break out of the current workflow and return to the parent workflow (if any)',
        inputSchema: {
          type: 'object',
          properties: {
            session_id: {
              type: 'string',
              description: 'The session ID for the workflow to break out of'
            }
          },
          required: ['session_id']
        }
      },
      {
        name: 'back_workflow',
        description: 'Go back to the previous step in the current workflow',
        inputSchema: {
          type: 'object',
          properties: {
            session_id: {
              type: 'string',
              description: 'The session ID for the workflow to go back a step'
            }
          },
          required: ['session_id']
        }
      },
      {
        name: 'restart_workflow',
        description: 'Restart the session from the beginning, keeping the same prompt but resetting all progress',
        inputSchema: {
          type: 'object',
          properties: {
            session_id: {
              type: 'string',
              description: 'The session ID for the workflow to restart'
            }
          },
          required: ['session_id']
        }
      },
      {
        name: 'list_workflow_sessions',
        description: 'List all active workflow sessions',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'init_vibe_project',
        description: 'Initialize vibe configuration and provide setup guidance for a project',
        inputSchema: {
          type: 'object',
          properties: {
            project_type: {
              type: 'string',
              description: 'Optional project type (python, vue_typescript, generic)'
            },
            working_dir: {
              type: 'string',
              description: 'Optional working directory to run commands in (defaults to current directory)'
            }
          }
        }
      },
      {
        name: 'check_vibe_environment',
        description: 'Validate vibe environment, configuration, and tool dependencies',
        inputSchema: {
          type: 'object',
          properties: {
            working_dir: {
              type: 'string',
              description: 'Optional working directory to run commands in (defaults to current directory)'
            }
          }
        }
      }
    ]
  };
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Vibe MCP Workflow Server running on stdio');
}

// Handle process termination
process.on('SIGINT', async () => {
  console.error('Shutting down Vibe MCP Workflow Server...');
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.error('Shutting down Vibe MCP Workflow Server...');
  process.exit(0);
});

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error('Server error:', error);
    process.exit(1);
  });
}
