const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const { exec } = require('child_process');

const execAsync = promisify(exec);

async function fixAllImports() {
  console.log('🔧 Finding and fixing all AuthContext imports...');
  
  try {
    // Find all .js files in src directory
    const { stdout } = await execAsync('dir /s /b src\\*.js', { shell: 'cmd.exe' });
    const files = stdout.trim().split('\n').map(f => f.trim()).filter(Boolean);
    
    let fixedCount = 0;
    let skippedCount = 0;
    
    for (const file of files) {
      try {
        let content = fs.readFileSync(file, 'utf8');
        
        // Replace the import statement
        const updated = content.replace(
          /import\s+{\s*useAuth\s*}\s+from\s+['"]\.\.\/\.\.\/context['"]/g,
          "import { useAuth } from '../../context/AuthContext.js'"
        );
        
        if (updated !== content) {
          fs.writeFileSync(file, updated, 'utf8');
          console.log(`✓ Fixed: ${path.relative(process.cwd(), file)}`);
          fixedCount++;
        } else {
          skippedCount++;
        }
      } catch (err) {
        console.log(`⚠️  Error processing ${file}: ${err.message}`);
      }
    }
    
    console.log('==================================================');
    console.log(`✅ Fixed: ${fixedCount} files`);
    console.log(`⏭️  Skipped: ${skippedCount} files (no changes needed)`);
    console.log('==================================================');
    console.log('🚀 All imports now use: ../../context/AuthContext.js');
  } catch (err) {
    console.error('Error:', err.message);
  }
}

fixAllImports();
