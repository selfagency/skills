import type { AgentAdapter, AgentInput } from '@langwatch/scenario';
import { AgentRole } from '@langwatch/scenario';
import { execSync } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

export interface CopilotAgentOptions {
  /** Path to the skill's SKILL.md (and optional references) to inject */
  skillPath?: string;
  /** If false, run without skill context (baseline comparison) */
  withSkill?: boolean;
  /** Extra flags to pass to copilot CLI */
  extraFlags?: string[];
  /** Model to use (default: uses copilot's default) */
  model?: string;
}

/**
 * Wraps `copilot -p "..." -s --no-ask-user` as a scenario AgentAdapter.
 *
 * With skill: creates a temp dir with AGENTS.md containing SKILL.md content,
 * runs copilot from that dir so it picks up the skill instructions.
 *
 * Without skill: runs with --no-custom-instructions to get baseline behavior.
 */
export function makeCopilotAgent(opts: CopilotAgentOptions = {}): AgentAdapter {
  const { skillPath, withSkill = true, extraFlags = [], model } = opts;

  return {
    role: AgentRole.AGENT,

    call: async (input: AgentInput): Promise<string> => {
      // Build the prompt from the last user message in the conversation
      const lastUserMsg = [...input.messages].reverse().find(m => m.role === 'user');

      if (!lastUserMsg) {
        return 'No user message provided.';
      }

      const userPrompt =
        typeof lastUserMsg.content === 'string' ? lastUserMsg.content : JSON.stringify(lastUserMsg.content);

      let tmpDir: string | null = null;
      let cwd: string = process.cwd();

      try {
        if (withSkill && skillPath) {
          // Create a temp dir and write AGENTS.md with the skill content
          tmpDir = mkdtempSync(join(tmpdir(), 'copilot-skill-eval-'));
          const skillContent = buildAgentsMd(skillPath);
          writeFileSync(join(tmpDir, 'AGENTS.md'), skillContent, 'utf8');
          cwd = tmpDir;
        }

        const flags = buildFlags({ withSkill, model, extraFlags });

        // Escape the prompt for shell safety
        const escapedPrompt = userPrompt.replace(/'/g, "'\\''");
        const cmd = `copilot -p '${escapedPrompt}' -s --no-ask-user ${flags}`;

        const result = execSync(cmd, {
          cwd,
          timeout: 120_000,
          maxBuffer: 1024 * 1024 * 10, // 10MB
          encoding: 'utf8',
        });

        return result.trim();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        // execSync throws on non-zero exit; stdout may still be in the error
        const stdout =
          err && typeof err === 'object' && 'stdout' in err ? String((err as { stdout: unknown }).stdout).trim() : '';
        return stdout || `[copilot CLI error: ${msg}]`;
      } finally {
        if (tmpDir) {
          rmSync(tmpDir, { recursive: true, force: true });
        }
      }
    },
  };
}

function buildFlags(opts: { withSkill: boolean; model?: string; extraFlags: string[] }): string {
  const parts: string[] = [];

  if (!opts.withSkill) {
    parts.push('--no-custom-instructions');
  }

  if (opts.model) {
    parts.push(`--model '${opts.model}'`);
  }

  // Restrict to read-only tools for evals — no file writes, no shell mutations
  parts.push('--allow-tool=read');

  parts.push(...opts.extraFlags);

  return parts.join(' ');
}

function buildAgentsMd(skillPath: string): string {
  const { readFileSync, existsSync } = require('node:fs');
  const { resolve } = require('node:path');

  const skillMdPath = existsSync(join(skillPath, 'SKILL.md')) ? join(skillPath, 'SKILL.md') : resolve(skillPath);

  const skillContent = readFileSync(skillMdPath, 'utf8');

  return `# Agent Instructions\n\n${skillContent}\n`;
}
