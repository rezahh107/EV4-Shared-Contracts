#!/usr/bin/env node

const fs = require('fs');

const STATUS_PATH = 'docs/EV4_SHARED_CONTRACTS_STATUS.md';

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

function replaceKnownLine(lines, startsWith, replacement) {
  const index = lines.findIndex(line => line.startsWith(startsWith));
  if (index === -1) {
    throw new Error(`Could not find line starting with: ${startsWith}`);
  }
  lines[index] = replacement;
}

function replaceFirstPrLine(lines, labelText, replacement, insertAfterPrefix) {
  const index = lines.findIndex(line => line.startsWith('- PR #') && line.includes(labelText));
  if (index !== -1) {
    lines[index] = replacement;
    return;
  }

  const anchor = lines.findIndex(line => line.startsWith(insertAfterPrefix));
  if (anchor === -1) {
    throw new Error(`Could not find anchor for ${labelText}: ${insertAfterPrefix}`);
  }
  lines.splice(anchor + 1, 0, replacement);
}

function replacePhaseLine(lines, phaseName, replacementStatus) {
  const index = lines.findIndex(line => line.startsWith(`| ${phaseName} |`));
  if (index !== -1) {
    lines[index] = `| ${phaseName} | ${replacementStatus} |`;
  }
}

function ensureLedger(lines) {
  const hasLedger = lines.some(line => line === '## Automated Merge Ledger');
  if (hasLedger) {
    return;
  }

  const insertAt = lines.findIndex(line => line === '## Remaining Blockers');
  if (insertAt === -1) {
    throw new Error('Could not find Remaining Blockers section.');
  }

  const ledgerLines = [
    '## Automated Merge Ledger',
    '',
    'This section is updated by GitHub Actions after a pull request is merged. It records merge facts only. It must not be treated as schema promotion, CI proof, or canonical migration approval.',
    '',
    '| PR | Title | Head branch | Head commit | Merge commit | Skeleton Health | Recorded by |',
    '|---|---|---|---|---|---|---|',
    ''
  ];

  lines.splice(insertAt, 0, ...ledgerLines);
}

function ensureLedgerHeader(lines) {
  const oldHeaderIndex = lines.findIndex(line => line === '| PR | Title | Head branch | Head commit | Merge commit | Recorded by |');
  if (oldHeaderIndex !== -1) {
    lines[oldHeaderIndex] = '| PR | Title | Head branch | Head commit | Merge commit | Skeleton Health | Recorded by |';
    if (lines[oldHeaderIndex + 1] === '|---|---|---|---|---|---|') {
      lines[oldHeaderIndex + 1] = '|---|---|---|---|---|---|---|';
    }
  }
}

function upsertLedgerRow(lines, prNumber, row) {
  const headerIndex = lines.findIndex(line => line === '| PR | Title | Head branch | Head commit | Merge commit | Skeleton Health | Recorded by |');
  if (headerIndex === -1) {
    throw new Error('Could not find Automated Merge Ledger table header.');
  }

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
  const skeletonHealth = normalizeCiStatus(envOptional('MERGED_PR_SKELETON_HEALTH', 'CI_NOT_VERIFIED'));

  const lines = fs.readFileSync(STATUS_PATH, 'utf8').split('\n');

  replaceKnownLine(lines, '- Last merged PR:', `- Last merged PR: \`#${prNumber}\` — \`${escapeCell(prTitle)}\``);
  replaceFirstPrLine(lines, 'merge commit:', `- PR #${prNumber} merge commit: \`${mergeSha}\``, '- Last merged PR:');
  replaceFirstPrLine(lines, 'head commit:', `- PR #${prNumber} head commit: \`${headSha}\``, `- PR #${prNumber} merge commit:`);
  replaceFirstPrLine(lines, '`Skeleton Health`:', `- PR #${prNumber} \`Skeleton Health\`: \`${skeletonHealth}\``, `- PR #${prNumber} head commit:`);
  replaceKnownLine(lines, '- Current work branch:', '- Current work branch: `main`');
  replaceKnownLine(lines, '- Active PR:', '- Active PR: `none`');
  replaceKnownLine(lines, '- Current status:', `- Current status: \`PR #${prNumber} merge fully recorded automatically; governance interpretation remains evidence-based; canonical migration remains blocked\``);
  replacePhaseLine(lines, 'Phase 5.1 — Status-after-merge automation', 'completed and active');

  ensureLedger(lines);
  ensureLedgerHeader(lines);

  const row = `| \`#${prNumber}\` | \`${escapeCell(prTitle)}\` | \`${escapeCell(headBranch)}\` | \`${headSha}\` | \`${mergeSha}\` | \`${skeletonHealth}\` | \`${escapeCell(actor)} on ${escapeCell(repo)}\` |`;
  upsertLedgerRow(lines, prNumber, row);

  fs.writeFileSync(STATUS_PATH, lines.join('\n'));
}

main();
