const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const { exec } = require('child_process');

const execAsync = promisify(exec);

async function fixToDirectAuthContext() {
  console.log('🔧 Fixing all imports to use direct AuthContext path...');
  
  try {
    const { stdout } = await execAsync('dir /s /b src\\*.js', { shell: 'cmd.exe' });
    const files = stdout.trim().split('\n').map(f => f.trim()).filter(Boolean);
    
    let fixedCount = 0;
    
    for (const file of files) {
      try {
        let content = fs.readFileSync(file, 'utf8');
        let updated = content;
        
        // Fix ../../context to ../../context/AuthContext
        updated = updated.replace(
          /import\s+{\s*useAuth\s*}\s+from\s+['"]\.\.\/\.\.\/context['"]/g,
          "import { useAuth } from '../../context/AuthContext'"
        );
        
        // Fix ../context to ../context/AuthContext
        updated = updated.replace(
          /import\s+{\s*useAuth\s*}\s+from\s+['"]\.\.\/context['"]/g,
          "import { useAuth } from '../context/AuthContext'"
        );
        
        // Fix ./src/context to ./src/context/AuthContext (for App.js)
        updated = updated.replace(
          /import\s+{\s*AuthProvider\s*}\s+from\s+['"]\.\/src\/context['"]/g,
          "import { AuthProvider } from './src/context/AuthContext'"
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
    console.log('🚀 All imports now use direct AuthContext path');
  } catch (err) {
    console.error('Error:', err.message);
  }
}

fixToDirectAuthContext();
