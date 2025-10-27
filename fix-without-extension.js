const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const { exec } = require('child_process');

const execAsync = promisify(exec);

async function fixWithoutExtension() {
  console.log('🔧 Fixing imports to use path WITHOUT .js extension...');
  
  try {
    const { stdout } = await execAsync('dir /s /b src\\*.js', { shell: 'cmd.exe' });
    const files = stdout.trim().split('\n').map(f => f.trim()).filter(Boolean);
    
    let fixedCount = 0;
    
    for (const file of files) {
      try {
        let content = fs.readFileSync(file, 'utf8');
        
        // Replace imports with .js extension
        let updated = content.replace(
          /import\s+{\s*useAuth\s*}\s+from\s+['"]\.\.\/\.\.\/context\/AuthContext\.js['"]/g,
          "import { useAuth } from '../../context/AuthContext'"
        );
        
        // Also fix single dot imports
        updated = updated.replace(
          /import\s+{\s*useAuth\s*}\s+from\s+['"]\.\.\/context\/AuthContext\.js['"]/g,
          "import { useAuth } from '../context/AuthContext'"
        );
        
        if (updated !== content) {
          fs.writeFileSync(file, updated, 'utf8');
          console.log(`✓ Fixed: ${path.relative(process.cwd(), file)}`);
          fixedCount++;
        }
      } catch (err) {
        console.log(`⚠️  Error processing ${file}: ${err.message}`);
      }
    }
    
    console.log('==================================================');
    console.log(`✅ Fixed: ${fixedCount} files`);
    console.log('==================================================');
    console.log('🚀 All imports now use path WITHOUT .js extension');
  } catch (err) {
    console.error('Error:', err.message);
  }
}

fixWithoutExtension();
