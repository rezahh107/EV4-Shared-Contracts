#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

function fail(code, message) {
  process.stdout.write(JSON.stringify({ bridge_status: 'execution_failure', code, message }));
  process.exit(2);
}

try {
  const [kernelRoot, inputPath] = process.argv.slice(2);
  if (!kernelRoot || !inputPath) fail('PG.KERNEL.BRIDGE_ARGUMENTS_REQUIRED', 'kernelRoot and inputPath are required.');

  const requireFromKernel = createRequire(join(kernelRoot, 'package.json'));
  const Ajv2020Module = requireFromKernel('ajv/dist/2020.js');
  const addFormatsModule = requireFromKernel('ajv-formats');
  const Ajv2020 = Ajv2020Module.default || Ajv2020Module;
  const addFormats = addFormatsModule.default || addFormatsModule;

  const validatorUrl = pathToFileURL(join(kernelRoot, 'kernel/validator/validate-l2-decision-correctness.mjs')).href;
  const { auditDecisionRecord } = await import(validatorUrl);
  const schema = JSON.parse(readFileSync(join(kernelRoot, 'kernel/schemas/decision-record.v2.schema.json'), 'utf8'));
  const registry = JSON.parse(readFileSync(join(kernelRoot, 'kernel/decision-governance/resolver-rule-registry.v0.json'), 'utf8'));
  const input = JSON.parse(readFileSync(inputPath, 'utf8'));

  const ajv = new Ajv2020({ allErrors: true, strict: false });
  addFormats(ajv);
  const validateDecisionRecordSchema = ajv.compile(schema);
  const coveredFamilies = new Set((registry.active_rules || []).map((entry) => entry?.decision_family_id).filter(Boolean));

  const result = auditDecisionRecord({
    decisionRecord: input.decision_record,
    resolverInput: input.resolver_input,
    auditContext: input.audit_context || {},
    validateDecisionRecordSchema,
    coveredFamilies
  });
  process.stdout.write(JSON.stringify({ bridge_status: 'ok', result }));
} catch (error) {
  fail('PG.KERNEL.BRIDGE_EXECUTION_FAILED', error instanceof Error ? error.message : String(error));
}
