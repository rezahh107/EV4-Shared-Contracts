const fs = require('fs');
const { spawnSync } = require('child_process');

const requiredFiles = [
  'README.md',
  'docs/EV4_SHARED_CONTRACTS_STATUS.md',
  'docs/ROLE_BOUNDARY_MAP.md',
  'docs/CONTRACT_INVENTORY.md',
  'docs/COMPATIBILITY_MAP.md',
  'docs/MIGRATION_READINESS_CHECKLIST.md',
  'docs/VALIDATION_STRATEGY.md',
  'docs/PROMOTION_RULES.md',
  'docs/ADR/0001-non-authoritative-skeleton.md',
  'schemas/README.md',
  'fixtures/README.md',
  'scripts/README.md',
  'scripts/update-status-after-merge.js',
  '.github/workflows/status-after-merge.yml'
];

for (const path of requiredFiles) {
  if (!fs.existsSync(path)) {
    console.error(`Missing required file: ${path}`);
    process.exit(1);
  }
}

const syntaxCheck = spawnSync(process.execPath, ['--check', 'scripts/update-status-after-merge.js'], {
  encoding: 'utf8'
});

if (syntaxCheck.status !== 0) {
  process.stderr.write(syntaxCheck.stderr || syntaxCheck.stdout);
  process.exit(syntaxCheck.status || 1);
}

console.log('Skeleton validation only: no canonical schema validation is active yet.');
console.log('Status-after-merge automation syntax ok.');
