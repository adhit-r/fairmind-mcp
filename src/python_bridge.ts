// src/python_bridge.ts
import { spawn, ChildProcess } from 'child_process';
import { encode, decode } from '@toon-format/toon';
import { join } from 'path';

export class PythonBridge {
  private process: ChildProcess | null = null;
  private messageQueue: Array<{ resolve: (value: any) => void; reject: (error: Error) => void }> = [];
  private buffer: string = '';

  constructor() {
    const pythonPath = join(process.cwd(), 'py_engine', '.venv', 'bin', 'python');
    const scriptPath = join(process.cwd(), 'py_engine', 'main.py');
    
    this.process = spawn(pythonPath, [scriptPath], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: join(process.cwd(), 'py_engine'),
    });

    this.process.stdout?.on('data', (data: Buffer) => {
      this.buffer += data.toString();
      // Python outputs JSON, one per line
      // Process complete lines
      const lines = this.buffer.split('\n');
      
      // Keep the last incomplete line in buffer
      this.buffer = lines.pop() || '';
      
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;
        
        const pending = this.messageQueue.shift();
        if (!pending) continue;
        
        try {
          // Try JSON first (Python outputs JSON)
          let decoded;
          try {
            decoded = JSON.parse(trimmed);
          } catch (jsonError) {
            // If JSON fails, try TOON decode
            try {
              decoded = decode(trimmed);
            } catch (toonError) {
              // If both fail, try Python codec's simple format
              decoded = this.parseSimpleFormat(trimmed);
            }
          }
          
          pending.resolve(decoded);
        } catch (error) {
          pending.reject(error as Error);
        }
      }
    });

    this.process.stderr?.on('data', (data: Buffer) => {
      console.error('[Python]', data.toString());
    });

    this.process.on('exit', (code) => {
      console.error(`[Python] Process exited with code ${code}`);
      this.process = null;
    });
  }

  async sendCommand(command: string, payload: any): Promise<any> {
    if (!this.process) {
      throw new Error('Python process not initialized');
    }

    return new Promise((resolve, reject) => {
      this.messageQueue.push({ resolve, reject });
      
      const request = {
        command,
        ...payload,
      };
      
      // Use JSON for requests to Python (simpler and more reliable)
      // Python will convert to TOON for responses
      this.process?.stdin?.write(JSON.stringify(request) + '\n');
    });
  }

  async evaluateBias(content: string, protectedAttribute: string, taskType: 'generative' | 'classification'): Promise<any> {
    return this.sendCommand('evaluate_bias', {
      content,
      protected_attribute: protectedAttribute,
      task_type: taskType,
    });
  }

  async generateCounterfactuals(content: string, sensitiveGroup: string): Promise<any> {
    return this.sendCommand('generate_counterfactuals', {
      content,
      sensitive_group: sensitiveGroup,
    });
  }

  private parseSimpleFormat(text: string): any {
    // Fallback parser for Python codec's simple key:value format
    const result: any = {};
    const lines = text.split('\n');
    for (const line of lines) {
      if (line.includes(':')) {
        const [key, ...valueParts] = line.split(':');
        const value = valueParts.join(':').trim();
        // Try to parse as number or boolean
        if (value === 'true') result[key.trim()] = true;
        else if (value === 'false') result[key.trim()] = false;
        else if (!isNaN(Number(value)) && value !== '') result[key.trim()] = Number(value);
        else result[key.trim()] = value;
      }
    }
    return result;
  }

  destroy() {
    if (this.process) {
      this.process.kill();
      this.process = null;
    }
  }
}
