#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { isAbsolute, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const BRIDGE_SCHEMA_VERSION = 'project-gate-kernel-l2-bridge.v1';

function argument(name) {
  const index = process.argv.indexOf(name);
  if (index < 0 || index + 1 >= process.argv.length) throw new Error(`Missing required argument ${name}`);
  return process.argv[index + 1];
}

function inside(root, relativePath) {
  const candidate = resolve(root, relativePath);
  const prefix = `${resolve(root)}/`;
  if (candidate !== resolve(root) && !candidate.startsWith(prefix)) throw new Error('Path escaped Kernel checkout.');
  return candidate;
}

function readJson(path) { return JSON.parse(readFileSync(path, 'utf8')); }

async function main() {
  const kernelRoot = resolve(argument('--kernel-repo'));
  const inputArg = argument('--input');
  const inputPath = isAbsolute(inputArg) ? inputArg : resolve(process.cwd(), inputArg);
  const input = readJson(inputPath);
  const schemaPath = inside(kernelRoot, 'kernel/schemas/decision-record.v2.schema.json');
  const registryPath = inside(kernelRoot, 'kernel/decision-governance/resolver-rule-registry.v0.json');
  const auditPath = inside(kernelRoot, 'kernel/validator/validate-l2-decision-correctness.mjs');
  const ajvPath = inside(kernelRoot, 'node_modules/ajv/dist/2020.js');
  const formatsPath = inside(kernelRoot, 'node_modules/ajv-formats/dist/index.js');
  const [{ auditDecisionRecord }, AjvModule, FormatsModule] = await Promise.all([
    import(pathToFileURL(auditPath).href),
    import(pathToFileURL(ajvPath).href),
    import(pathToFileURL(formatsPath).href),
  ]);
  if (typeof auditDecisionRecord !== 'function') throw new Error('Pinned Kernel auditDecisionRecord export is unavailable.');
  const ajv = new AjvModule.default({ allErrors: true, strict: false });
  FormatsModule.default(ajv);
  const validateDecisionRecordSchema = ajv.compile(readJson(schemaPath));
  const registry = readJson(registryPath);
  if (!registry || !Array.isArray(registry.active_rules)) throw new Error('Pinned Resolver registry active_rules is malformed.');
  const coveredFamilies = new Set(registry.active_rules.map((entry) => entry?.decision_family_id).filter((value) => typeof value === 'string' && value.length > 0));
  const kernelAudit = auditDecisionRecord({ decisionRecord: input.decision_record, resolverInput: input.resolver_input, auditContext: input.audit_context, validateDecisionRecordSchema, coveredFamilies });
  process.stdout.write(`${JSON.stringify({ bridge_schema_version: BRIDGE_SCHEMA_VERSION, execution_status: 'completed', kernel_audit: kernelAudit })}\n`);
}

main().catch(() => {
  process.stdout.write(`${JSON.stringify({ bridge_schema_version: BRIDGE_SCHEMA_VERSION, execution_status: 'failed', error_code: 'PG_KERNEL_BRIDGE_EXECUTION_FAILED' })}\n`);
  process.exit(2);
});
