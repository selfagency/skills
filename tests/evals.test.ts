/**
 * Skill eval runner using langwatch/scenario + Ollama as the judge.
 *
 * Each skill's evals/evals.json is loaded and run as a scenario test,
 * comparing copilot CLI responses with and without the skill loaded.
 *
 * Run:  pnpm test:evals
 * Debug: pnpm test:evals -- --reporter=verbose
 */
import scenario from '@langwatch/scenario';
import { describe, expect, it } from 'vitest';
import { makeCopilotAgent } from './helpers/copilot-agent';
import { assertionsToCriteria, loadAllSkillEvals } from './helpers/load-evals';
import { makeJudgeStep } from './helpers/ollama';

const allSkillEvals = loadAllSkillEvals();

// Run each skill as a describe block
for (const { skillName, skillPath, evals } of allSkillEvals) {
  describe(`Skill: ${skillName}`, () => {
    for (const evalCase of evals.cases ?? []) {
      const criteria = assertionsToCriteria(evalCase.assertions);

      it(`[with-skill] ${evalCase.id}: ${evalCase.title}`, async () => {
        const result = await scenario.run({
          name: `${skillName}/${evalCase.id} (with skill)`,
          description: evalCase.prompt,
          agents: [makeCopilotAgent({ skillPath, withSkill: true })],
          script: [
            state => state.addMessage({ role: 'user', content: evalCase.prompt }),
            (_state, executor) => executor.agent(),
            makeJudgeStep(criteria),
          ],
          setId: `${skillName}-with-skill`,
        });

        // Infrastructure assertion: the scenario executed and produced judge output.
        expect(result.messages.length, `[with-skill] ${evalCase.id}: no messages produced`).toBeGreaterThan(0);
        expect(typeof result.success, `[with-skill] ${evalCase.id}: missing success flag`).toBe('boolean');
        expect(Array.isArray(result.metCriteria), `[with-skill] ${evalCase.id}: metCriteria missing`).toBe(true);
        expect(Array.isArray(result.unmetCriteria), `[with-skill] ${evalCase.id}: unmetCriteria missing`).toBe(true);

        if (!result.success) {
          console.warn(formatFailure(result, evalCase.id, 'with-skill'));
        }
      });

      it(`[baseline] ${evalCase.id}: ${evalCase.title}`, async () => {
        const result = await scenario.run({
          name: `${skillName}/${evalCase.id} (baseline)`,
          description: evalCase.prompt,
          agents: [makeCopilotAgent({ skillPath, withSkill: false })],
          script: [
            state => state.addMessage({ role: 'user', content: evalCase.prompt }),
            (_state, executor) => executor.agent(),
            makeJudgeStep(criteria),
          ],
          setId: `${skillName}-baseline`,
        });

        // Infrastructure assertion: baseline run also executes end-to-end.
        expect(result.messages.length, `[baseline] ${evalCase.id}: no messages produced`).toBeGreaterThan(0);
        expect(typeof result.success, `[baseline] ${evalCase.id}: missing success flag`).toBe('boolean');
        expect(Array.isArray(result.metCriteria), `[baseline] ${evalCase.id}: metCriteria missing`).toBe(true);
        expect(Array.isArray(result.unmetCriteria), `[baseline] ${evalCase.id}: unmetCriteria missing`).toBe(true);

        // Baseline is expected to be weaker — we record but don't hard-fail
        // so the test suite shows the delta clearly
        if (!result.success) {
          console.log(
            `[baseline expected weaker] ${skillName}/${evalCase.id}: unmet criteria = ${result.unmetCriteria.join('; ')}`,
          );
        }
      });
    }
  });
}

function formatFailure(result: Awaited<ReturnType<typeof scenario.run>>, id: string, mode: string): string {
  const unmet = result.unmetCriteria.length > 0 ? result.unmetCriteria.join('; ') : 'none';
  return `[${mode}] ${id} failed. Unmet criteria: ${unmet}\nReasoning: ${result.reasoning ?? 'none'}`;
}
