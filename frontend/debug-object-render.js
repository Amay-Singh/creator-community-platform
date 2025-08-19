/**
 * 4-Agent System: Object Rendering Debug Script
 * CodeSync Agent: Systematic identification of all object rendering issues
 */

const fs = require('fs');
const path = require('path');

// Find all JSX files
function findJSXFiles(dir) {
  const files = [];
  const items = fs.readdirSync(dir);
  
  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);
    
    if (stat.isDirectory() && !item.startsWith('.') && item !== 'node_modules') {
      files.push(...findJSXFiles(fullPath));
    } else if (item.endsWith('.jsx') || item.endsWith('.js')) {
      files.push(fullPath);
    }
  }
  
  return files;
}

// Check for potential object rendering issues
function checkObjectRendering(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const issues = [];
  
  // Pattern 1: Direct object in JSX
  const directObjectPattern = /\{[^}]*\w+\s*\?\s*[^}]*\s*:\s*[^}]*\}/g;
  let match;
  
  while ((match = directObjectPattern.exec(content)) !== null) {
    const line = content.substring(0, match.index).split('\n').length;
    if (match[0].includes('JSON.stringify') || 
        match[0].includes('current_usage') ||
        match[0].includes('limit') ||
        match[0].includes('usage_percentage')) {
      issues.push({
        line,
        code: match[0],
        type: 'Potential object rendering'
      });
    }
  }
  
  return issues;
}

// Main execution
const srcDir = '/Users/amays/Desktop/Work/Colab/creator-platform/frontend/src';
const jsxFiles = findJSXFiles(srcDir);

console.log('🔍 CodeSync Agent: Scanning for object rendering issues...\n');

let totalIssues = 0;
for (const file of jsxFiles) {
  const issues = checkObjectRendering(file);
  if (issues.length > 0) {
    console.log(`📄 ${file.replace(srcDir, '')}:`);
    issues.forEach(issue => {
      console.log(`  Line ${issue.line}: ${issue.type}`);
      console.log(`    ${issue.code}`);
      totalIssues++;
    });
    console.log('');
  }
}

console.log(`\n📊 Total potential issues found: ${totalIssues}`);
console.log('🛠️  CodeSync Agent scan complete.');
