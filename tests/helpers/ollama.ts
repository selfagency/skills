import type { ScriptStep } from '@langwatch/scenario';
import { Ollama } from 'ollama';

const ollama = new Ollama({ host: 'http://localhost:11434' });

/**
 * Model to use for judging — granite3.2:8b has strong instruction following.
 * Falls back to qwen2.5-coder:7b.
 */
const JUDGE_MODEL = 'granite3.2:8b';

const verdictSchema = {
  type: 'object',
  properties: {
    pass: {
      type: 'boolean',
      description: 'true if all criteria are met, false otherwise',
    },
    reasoning: {
      type: 'string',
      description: 'Concise explanation of the verdict',
    },
    unmet_criteria: {
      type: 'array',
      items: { type: 'string' },
      description: 'List of criteria that were NOT met',
    },
  },
  required: ['pass', 'reasoning', 'unmet_criteria'],
};

/**
 * Custom judge that uses native Ollama structured output (JSON schema format).
 * Avoids tool-calling requirement that breaks with local models.
 */
export function makeJudgeStep(criteria: string[]): ScriptStep {
  return async (state, executor) => {
    const conversationText = state.messages
      .filter(m => m.role !== 'system')
      .map(m => {
        const content = typeof m.content === 'string' ? m.content : JSON.stringify(m.content);
        return `[${m.role.toUpperCase()}]: ${content}`;
      })
      .join('\n\n');

    const criteriaText = criteria.map((c, i) => `${i + 1}. ${c}`).join('\n');

    const prompt = `You are evaluating an AI assistant's response against quality criteria.

## Conversation
${conversationText}

## Criteria to evaluate
${criteriaText}

## Instructions
Evaluate whether the assistant's response meets ALL of the criteria above.
Return a JSON object with:
- "pass": true only if ALL criteria are satisfied
- "reasoning": brief explanation of your verdict
- "unmet_criteria": list any criteria that were NOT met (empty array if all passed)`;

    try {
      const response = await withTimeout(
        ollama.chat({
          model: JUDGE_MODEL,
          messages: [{ role: 'user', content: prompt }],
          format: verdictSchema,
          options: { temperature: 0 },
        }),
        120_000,
        'Ollama judge timed out',
      );

      const verdict = JSON.parse(response.message.content) as {
        pass: boolean;
        reasoning: string;
        unmet_criteria: string[];
      };

      if (verdict.pass) {
        await executor.succeed(verdict.reasoning);
      } else {
        const unmet = verdict.unmet_criteria.join('; ');
        await executor.fail(`${verdict.reasoning}. Unmet: ${unmet}`);
      }
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : String(error);
      await executor.fail(`Judge execution error: ${msg}`);
    }
  };
}

async function withTimeout<T>(promise: Promise<T>, ms: number, timeoutMessage: string): Promise<T> {
  let timeoutId: NodeJS.Timeout | undefined;

  const timeoutPromise = new Promise<never>((_, reject) => {
    timeoutId = setTimeout(() => reject(new Error(timeoutMessage)), ms);
  });

  try {
    return await Promise.race([promise, timeoutPromise]);
  } finally {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
  }
}
