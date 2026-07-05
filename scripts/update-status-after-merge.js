#!/usr/bin/env node

const fs = require('fs');

const LEDGER_PATH = 'docs/EV4_SHARED_CONTRACTS_STATUS.md';
const LEDGER_HEADING = '## Automated Merge Ledger';
const LEDGER_HEADER = '| PR | Title | Head branch | Head commit | Merge commit | Skeleton Health | Recorded by |';

function envRequired(name) {
  const value = process.env[name];
  if (!value || !value.trim()) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value.trim();
}

function envOptional(name, fallback) {
  const value = process.env[name];
  return value && value.trim() ? value.trim() : fallback;
}

function escapeCell(value) {
  return String(value).replaceAll('|', '\\|').replace(/\r?\n/g, ' ').trim();
}

function normalizeCiStatus(value) {
  const normalized = String(value || '').trim().toLowerCase();
  if (normalized === 'success' || normalized === 'ci_passed') return 'CI_PASSED';
  if (['failure', 'cancelled', 'timed_out', 'action_required', 'ci_failed'].includes(normalized)) return 'CI_FAILED';
  if (['queued', 'in_progress', 'waiting', 'pending', 'ci_pending'].includes(normalized)) return 'CI_PENDING';
  return 'CI_NOT_VERIFIED';
}

function ensureLedger(lines) {
  if (lines.some(line => line === LEDGER_HEADING)) {
    return;
  }

  const ledgerLines = [
    LEDGER_HEADING,
    '',
    'This section is updated by GitHub Actions after a pull request is merged. It records historical merge facts only and is not the current capability-truth source.',
    '',
    LEDGER_HEADER,
    '|---|---|---|---|---|---|---|',
    ''
  ];
  lines.push('', ...ledgerLines);
}

function ensureLedgerHeader(lines) {
  const headingIndex = lines.findIndex(line => line === LEDGER_HEADING);
  if (headingIndex === -1) {
    throw new Error('Could not find historical merge ledger heading.');
  }
  const headerIndex = lines.findIndex((line, index) => index > headingIndex && line.startsWith('| PR |'));
  if (headerIndex === -1) {
    throw new Error('Could not find historical merge ledger table header.');
  }
  lines[headerIndex] = LEDGER_HEADER;
  lines[headerIndex + 1] = '|---|---|---|---|---|---|---|';
  return headerIndex;
}

function upsertLedgerRow(lines, headerIndex, prNumber, row) {
  const existingRowIndex = lines.findIndex(line => line.startsWith(`| \`#${prNumber}\` |`));
  if (existingRowIndex !== -1) {
    lines.splice(existingRowIndex, 1);
  }
  lines.splice(headerIndex + 2, 0, row);
}

function main() {
  const prNumber = envRequired('MERGED_PR_NUMBER');
  const prTitle = envRequired('MERGED_PR_TITLE');
  const headBranch = envRequired('MERGED_PR_HEAD_BRANCH');
  const headSha = envRequired('MERGED_PR_HEAD_SHA');
  const mergeSha = envRequired('MERGED_PR_MERGE_SHA');
  const repo = envRequired('GITHUB_REPOSITORY');
  const actor = envRequired('GITHUB_ACTOR');
  const health = normalizeCiStatus(envOptional('MERGED_PR_SKELETON_HEALTH', 'CI_NOT_VERIFIED'));

  const lines = fs.readFileSync(LEDGER_PATH, 'utf8').split('\n');
  ensureLedger(lines);
  const headerIndex = ensureLedgerHeader(lines);
  const row = `| \`#${prNumber}\` | \`${escapeCell(prTitle)}\` | \`${escapeCell(headBranch)}\` | \`${headSha}\` | \`${mergeSha}\` | \`${health}\` | \`${escapeCell(actor)} on ${escapeCell(repo)}\` |`;
  upsertLedgerRow(lines, headerIndex, prNumber, row);
  fs.writeFileSync(LEDGER_PATH, lines.join('\n'));
}

main();
