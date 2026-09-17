const fs = require('fs');
const path = require('path');

const skillPath = path.join(__dirname, 'SKILL.md');

module.exports = {
  skillPath,
  getSkillContent: function() {
    return fs.readFileSync(skillPath, 'utf-8');
  }
};
