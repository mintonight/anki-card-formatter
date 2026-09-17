#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const command = args[0];

const skillPath = path.join(__dirname, '..', 'SKILL.md');

function showHelp() {
  const helpText = [
    '',
    'anki-card-formatter - Anki card LaTeX (MathJax) & code block pipeline tool',
    '',
    'Usage:',
    '  npx anki-card-formatter install [--global|-g]   Install SKILL.md into local agent directories',
    '  npx anki-card-formatter print                   Print SKILL.md content to stdout',
    '  npx anki-card-formatter help                    Show this help message',
    '',
    'Quick Install for AI Agents:',
    '  # Via standard skills CLI (Cursor, Claude-Code, Codex, Antigravity):',
    '  npx skills add mintonight/anki-card-formatter -y',
    '',
    '  # Or globally for all agents:',
    '  npx skills add mintonight/anki-card-formatter -g -y',
    ''
  ].join('\n');
  console.log(helpText);
}

if (!command || command === 'help' || command === '--help' || command === '-h') {
  showHelp();
  process.exit(0);
}

if (command === 'print') {
  if (fs.existsSync(skillPath)) {
    console.log(fs.readFileSync(skillPath, 'utf-8'));
  } else {
    console.error('SKILL.md not found.');
    process.exit(1);
  }
} else if (command === 'install') {
  const isGlobal = args.includes('--global') || args.includes('-g');
  const homeDir = process.env.USERPROFILE || process.env.HOME;
  
  let targetDirs = [];
  if (isGlobal) {
    targetDirs = [
      path.join(homeDir, '.gemini', 'config', 'skills', 'anki-card-formatter'),
      path.join(homeDir, '.codex', 'skills', 'anki-card-formatter'),
      path.join(homeDir, '.claude', 'skills', 'anki-card-formatter'),
      path.join(homeDir, '.cursor', 'skills', 'anki-card-formatter')
    ];
  } else {
    targetDirs = [
      path.join(process.cwd(), '.agents', 'skills', 'anki-card-formatter'),
      path.join(process.cwd(), '.gemini', 'skills', 'anki-card-formatter'),
      path.join(process.cwd(), '.codex', 'skills', 'anki-card-formatter'),
      path.join(process.cwd(), '.cursor', 'skills', 'anki-card-formatter')
    ];
  }

  const skillContent = fs.readFileSync(skillPath, 'utf-8');
  let installedCount = 0;

  for (const dir of targetDirs) {
    try {
      fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(path.join(dir, 'SKILL.md'), skillContent, 'utf-8');
      console.log('[✓] Installed to ' + dir);
      installedCount++;
    } catch (err) {
      // ignore
    }
  }

  console.log('\nSuccessfully installed anki-card-formatter skill to ' + installedCount + ' agent directory locations!');
} else {
  console.error('Unknown command: ' + command);
  showHelp();
  process.exit(1);
}
