import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

export interface Assertion {
  id: string;
  description: string;
  type: string;
  keywords?: string[];
  must_not_contain?: string[];
}

export interface EvalCase {
  id: string;
  title: string;
  prompt: string;
  categories?: string[];
  assertions: Assertion[];
  expected_score_range?: {
    with_skill?: number[];
    without_skill?: number[];
  };
}

export interface EvalsFile {
  skill: string;
  version?: string;
  description?: string;
  /** Quality eval cases (cli-admin-automation style) */
  cases?: EvalCase[];
}

export interface SkillEvals {
  skillName: string;
  skillPath: string;
  evalsPath: string;
  evals: EvalsFile;
}

const SKILLS_DIR = join(import.meta.dirname, '../../skills');

/**
 * Load evals.json for a specific skill by name.
 */
export function loadSkillEvals(skillName: string): SkillEvals {
  const skillPath = join(SKILLS_DIR, skillName);
  const evalsPath = join(skillPath, 'evals', 'evals.json');

  if (!existsSync(evalsPath)) {
    throw new Error(`No evals.json found for skill '${skillName}' at ${evalsPath}`);
  }

  const evals: EvalsFile = JSON.parse(readFileSync(evalsPath, 'utf8'));
  return { skillName, skillPath, evalsPath, evals };
}

/**
 * Load evals for all skills that have an evals/evals.json with quality cases.
 * Skips skills whose evals.json uses a different schema (e.g., trigger-only evals).
 */
export function loadAllSkillEvals(): SkillEvals[] {
  const skills = readdirSync(SKILLS_DIR, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name);

  return skills
    .filter(name => existsSync(join(SKILLS_DIR, name, 'evals', 'evals.json')))
    .map(name => loadSkillEvals(name))
    .filter(({ evals }) => Array.isArray(evals.cases) && evals.cases.length > 0);
}

/**
 * Convert an eval case's assertions to JudgeAgent criteria strings.
 * Includes both the assertion description and keyword hints.
 */
export function assertionsToCriteria(assertions: Assertion[]): string[] {
  return assertions.map(a => {
    let criterion = a.description;

    if (a.must_not_contain && a.must_not_contain.length > 0) {
      criterion += `. Must NOT mention or include: ${a.must_not_contain.join(', ')}`;
    }

    if (a.keywords && a.keywords.length > 0 && a.type !== 'optional') {
      criterion += `. Should reference concepts like: ${a.keywords.join(', ')}`;
    }

    return criterion;
  });
}
