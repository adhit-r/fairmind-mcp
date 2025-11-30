import { spawn, ChildProcess } from 'child_process';
import { encode, decode } from '@toon-format/toon';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const DEFAULT_TIMEOUT = 30000; // 30 seconds
const MAX_RESTARTS = 3;

interface QueueItem {
  resolve: (value: any) => void;
  reject: (error: Error) => void;
  timeout?: NodeJS.Timeout;
}

export class PythonBridge {
  private process: ChildProcess | null = null;
  private messageQueue: QueueItem[] = [];
  private buffer: string = '';
  private restartCount: number = 0;
  private isShuttingDown: boolean = false;
  private pythonPath: string;
  private scriptPath: string;
  private pyEngineDir: string;

  private warmupPromise: Promise<void> | null = null;

  constructor() {
    // Get the project root directory (where this file is located)
    // Use fileURLToPath to convert import.meta.url to a file path
    const currentFile = fileURLToPath(import.meta.url);
    const srcDir = dirname(currentFile);
    const projectRoot = join(srcDir, '..');
    
    this.pyEngineDir = process.env.FAIRMIND_PY_DIR || join(projectRoot, 'py_engine');
    
    // Resolve Python path: Env var > venv > fallback
    this.pythonPath = process.env.FAIRMIND_PYTHON_PATH || join(this.pyEngineDir, '.venv', 'bin', 'python');
    this.scriptPath = join(this.pyEngineDir, 'main.py');
    
    console.error(`[FairMind] Project root: ${projectRoot}`);
    console.error(`[FairMind] Python path: ${this.pythonPath}`);
    console.error(`[FairMind] Script path: ${this.scriptPath}`);
    console.error(`[FairMind] Working directory: ${this.pyEngineDir}`);
    
    this.startProcess();
    
    // Perform warm-up request to eliminate first-request penalty
    this.warmup();
  }

  private async warmup(): Promise<void> {
    // Only warm up once
    if (this.warmupPromise) {
      return this.warmupPromise;
    }

    this.warmupPromise = (async () => {
      try {
        // Wait a bit for process to be ready
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Send a minimal warm-up request
        await this.evaluateBias(
          'test',
          'gender',
          'generative',
          'text'
        ).catch(() => {
          // Ignore warm-up errors - process might not be ready yet
        });
        
        console.error('[FairMind] Warm-up completed');
      } catch (error) {
        // Warm-up failures are non-critical
        console.error('[FairMind] Warm-up failed (non-critical):', error);
      }
    })();

    return this.warmupPromise;
  }

  private startProcess() {
    if (this.isShuttingDown) return;

    if (this.process) {
        try {
            this.process.kill();
        } catch (e) {
            // ignore
        }
    }

    try {
        this.process = spawn(this.pythonPath, [this.scriptPath], {
            stdio: ['pipe', 'pipe', 'pipe'],
            cwd: this.pyEngineDir,
        });
        
        console.error('[FairMind] Python process started, pid:', this.process.pid);

        this.process.stdout?.on('data', (data: Buffer) => {
          this.handleStdout(data);
        });

        this.process.stderr?.on('data', (data: Buffer) => {
          console.error('[Python]', data.toString());
        });

        this.process.on('exit', (code, signal) => {
          console.error(`[Python] Process exited with code ${code}, signal ${signal}`);
          this.process = null;
          this.handleExit(code);
        });

        this.process.on('error', (error) => {
          console.error('[Python] Process error:', error);
          this.process = null;
          // Trigger restart logic via exit handler or directly
          if (!this.process) { 
              this.handleExit(1);
          }
        });

    } catch (error) {
        console.error('[FairMind] Failed to spawn python process:', error);
        this.handleExit(1);
    }
  }

  private handleStdout(data: Buffer) {
    this.buffer += data.toString();
    
    // Process complete lines
    let lines = this.buffer.split('\n');
    
    if (this.buffer.endsWith('\n')) {
        // Complete lines only (last one is empty)
        lines.pop(); // remove the empty string
        this.buffer = '';
    } else {
        // Last line is incomplete, put it back in buffer
        this.buffer = lines.pop() || '';
    }
    
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      
      const pending = this.messageQueue.shift();
      if (!pending) {
          // Unsolicited output? Log it
          console.error('[Python Unexpected]', trimmed);
          continue;
      }
      
      if (pending.timeout) clearTimeout(pending.timeout);

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
  }

  private handleExit(code: number | null) {
      // Reject all pending requests
      while (this.messageQueue.length > 0) {
          const p = this.messageQueue.shift();
          if (p?.timeout) clearTimeout(p.timeout);
          p?.reject(new Error(`Python process exited unexpectedly with code ${code}`));
      }

      if (this.isShuttingDown) return;

      // Auto-restart if not intentional and within limits
      if (this.restartCount < MAX_RESTARTS) {
          this.restartCount++;
          const delay = 1000 * this.restartCount; // Exponential backoffish
          console.error(`[FairMind] Restarting Python process (${this.restartCount}/${MAX_RESTARTS}) in ${delay}ms...`);
          setTimeout(() => this.startProcess(), delay);
      } else {
          console.error('[FairMind] Max restarts reached. Python bridge is down.');
      }
  }

  async sendCommand(command: string, payload: any, timeoutMs: number = DEFAULT_TIMEOUT): Promise<any> {
    if (!this.process) {
        throw new Error('Python process not initialized/available');
    }

    return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
            // Remove from queue if possible (O(n) but queue is small)
            const idx = this.messageQueue.findIndex(item => item.resolve === resolve);
            if (idx !== -1) {
                this.messageQueue.splice(idx, 1);
                reject(new Error(`Command ${command} timed out after ${timeoutMs}ms`));
            }
        }, timeoutMs);

        this.messageQueue.push({ resolve, reject, timeout });

        const request = {
            command,
            ...payload,
        };
      
        try {
            this.process?.stdin?.write(JSON.stringify(request) + '\n');
        } catch (e) {
            // Write failed
            const idx = this.messageQueue.findIndex(item => item.resolve === resolve);
            if (idx !== -1) {
                this.messageQueue.splice(idx, 1);
            }
            clearTimeout(timeout);
            reject(e as Error);
        }
    });
  }

  async evaluateBias(
    content: string, 
    protectedAttribute: string, 
    taskType: 'generative' | 'classification',
    contentType: 'text' | 'code' = 'text',
    protectedAttributes?: string[]
  ): Promise<any> {
    const payload: any = {
      content,
      task_type: taskType,
      content_type: contentType,
    };
    
    // Support both single and multiple attributes
    if (protectedAttributes && Array.isArray(protectedAttributes)) {
      payload.protected_attributes = protectedAttributes;
    } else {
      payload.protected_attribute = protectedAttribute;
    }
    
    return this.sendCommand('evaluate_bias', payload);
  }

  async generateCounterfactuals(content: string, sensitiveGroup: string): Promise<any> {
    return this.sendCommand('generate_counterfactuals', {
      content,
      sensitive_group: sensitiveGroup,
    });
  }

  async compareCodeBias(
    codeA: string,
    codeB: string,
    personaA: string = 'Persona A',
    personaB: string = 'Persona B',
    languageA?: string,
    languageB?: string
  ): Promise<any> {
    return this.sendCommand('compare_code_bias', {
      code_a: codeA,
      code_b: codeB,
      persona_a: personaA,
      persona_b: personaB,
      language_a: languageA,
      language_b: languageB,
    });
  }

  async evaluateModelOutputs(
    outputs: string[],
    protectedAttributes: string[],
    taskType: 'generative' | 'classification',
    contentType: 'text' | 'code' = 'text',
    aggregation: 'summary' | 'detailed' = 'summary'
  ): Promise<any> {
    return this.sendCommand('evaluate_model_outputs', {
      outputs,
      protected_attributes: protectedAttributes,
      task_type: taskType,
      content_type: contentType,
      aggregation,
    });
  }

  async evaluatePromptSuite(
    prompts: string[],
    modelOutputs: string[],
    protectedAttributes: string[],
    suiteName?: string,
    taskType: 'generative' | 'classification' = 'generative',
    contentType: 'text' | 'code' = 'text',
    previousResults?: any
  ): Promise<any> {
    return this.sendCommand('evaluate_prompt_suite', {
      prompts,
      model_outputs: modelOutputs,
      protected_attributes: protectedAttributes,
      suite_name: suiteName,
      task_type: taskType,
      content_type: contentType,
      previous_results: previousResults,
    });
  }

  async evaluateModelResponse(
    prompt: string,
    response: string,
    protectedAttributes: string[],
    taskType: 'generative' | 'classification' = 'generative',
    contentType: 'text' | 'code' = 'text'
  ): Promise<any> {
    return this.sendCommand('evaluate_model_response', {
      prompt,
      response,
      protected_attributes: protectedAttributes,
      task_type: taskType,
      content_type: contentType,
    });
  }

  async evaluateBiasAdvanced(
    content: string,
    protectedAttributes: string[],
    taskType: 'generative' | 'classification' = 'generative',
    useMetricFrame: boolean = true,
    useAif360: boolean = false,
    metricNames?: string[],
    contentType: 'text' | 'code' = 'text'
  ): Promise<any> {
    return this.sendCommand('evaluate_bias_advanced', {
      content,
      protected_attributes: protectedAttributes,
      task_type: taskType,
      use_metricframe: useMetricFrame,
      use_aif360: useAif360,
      metric_names: metricNames,
      content_type: contentType,
    });
  }

  async analyzeRepositoryBias(
    repositoryPath: string,
    protectedAttributes: string[],
    maxCommits: number = 0,
    minCommitsPerAuthor: number = 5,
    fileExtensions: string[] = [],
    excludePaths: string[] = [],
    anonymizeAuthors: boolean = false,
    excludeAuthorNames: boolean = false,
    patternOnlyMode: boolean = false
  ): Promise<any> {
    return this.sendCommand('analyze_repository_bias', {
      repository_path: repositoryPath,
      protected_attributes: protectedAttributes,
      max_commits: maxCommits,
      min_commits_per_author: minCommitsPerAuthor,
      file_extensions: fileExtensions,
      exclude_paths: excludePaths,
      anonymize_authors: anonymizeAuthors,
      exclude_author_names: excludeAuthorNames,
      pattern_only_mode: patternOnlyMode,
    }, 300000); // 5 minute timeout for large repos
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
    this.isShuttingDown = true;
    if (this.process) {
      this.process.kill();
      this.process = null;
    }
  }
}