#!/usr/bin/env node

const fs = require('fs');

const STATUS_PATH = 'docs/EV4_SHARED_CONTRACTS_STATUS.md';

function requiredEnv(name) {
  const value = process.env[name];
  if (!value || !value.trim()) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value.trim();
}

function replaceLine(content, prefix, nextLine) {
  const pattern = new RegExp(`^- ${prefix.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}: .*$`, 'm');
  if (!pattern.test(content)) {
    throw new Error(`Could not find status line with prefix: ${prefix}`);
  }
  return content.replace(pattern, nextLine);
}

function ensureLedger(content) {
  const marker = '## Automated Merge Ledger';
  if (content.includes(marker)) {
    return content;
  }

  const insertBefore = '\n## Remaining Blockers\n';
  const ledger = `\n## Automated Merge Ledger\n\nThis section is updated by GitHub Actions after a pull request is merged. It records merge facts only. It must not be treated as schema promotion, CI proof, or canonical migration approval.\n\n| PR | Title | Head branch | Head commit | Merge commit | Recorded by |\n|---|---|---|---|---|---|\n`;

  if (!content.includes(insertBefore)) {
    throw new Error('Could not find Remaining Blockers section for ledger insertion.');
  }

  return content.replace(insertBefore, `${ledger}${insertBefore}`);
}

function appendLedgerRow(content, row) {
  const header = '| PR | Title | Head branch | Head commit | Merge commit | Recorded by |\n|---|---|---|---|---|---|\n';
  const index = content.indexOf(header);
  if (index === -1) {
    throw new Error('Could not find automated merge ledger table.');
  }

  const insertAt = index + header.length;
  return content.slice(0, insertAt) + row + content.slice(insertAt);
}

function escapeCell(value) {
  return value.replace(/\|/g, '\\|').replace(/\r?\n/g, ' ').trim();
}

function main() {
  const prNumber = requiredEnv('MERGED_PR_NUMBER');
  const prTitle = requiredEnv('MERGED_PR_TITLE');
  const headBranch = requiredEnv('MERGED_PR_HEAD_BRANCH');
  const headSha = requiredEnv('MERGED_PR_HEAD_SHA');
  const mergeSha = requiredEnv('MERGED_PR_MERGE_SHA');
  const repo = requiredEnv('GITHUB_REPOSITORY');
  const actor = requiredEnv('GITHUB_ACTOR');

  let content = fs.readFileSync(STATUS_PATH, 'utf8');

  content = replaceLine(content, 'Last merged PR', `- Last merged PR: \`#${prNumber}\` — \`${escapeCell(prTitle)}\``);
  content = replaceLine(content, 'Current work branch', '- Current work branch: `main`');
  content = replaceLine(content, 'Active PR', '- Active PR: `none`');
  content = replaceLine(
    content,
    'Current status',
    `- Current status: \`PR #${prNumber} merge recorded automatically; governance state still requires human/agent review\``
  );

  content = ensureLedger(content);

  const row = `| \`#${prNumber}\` | \`${escapeCell(prTitle)}\` | \`${escapeCell(headBranch)}\` | \`${headSha}\` | \`${mergeSha}\` | \`${escapeCell(actor)} on ${escapeCell(repo)}\` |\n`;
  content = appendLedgerRow(content, row);

  fs.writeFileSync(STATUS_PATH, content);
}

main();
