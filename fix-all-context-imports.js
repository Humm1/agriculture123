const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const { exec } = require('child_process');

const execAsync = promisify(exec);

async function fixAllAuthContextImports() {
  console.log('🔧 Fixing ALL AuthContext imports to use index.js...\n');
  
  try {
    const { stdout } = await execAsync('dir /s /b src\\*.js', { shell: 'cmd.exe' });
    const files = stdout.trim().split('\n').map(f => f.trim()).filter(Boolean);
    
    let fixedCount = 0;
    
    for (const file of files) {
      try {
        let content = fs.readFileSync(file, 'utf8');
        let wasModified = false;
        
        // Fix imports from ../../context/AuthContext (for subdirectory files)
        const updated1 = content.replace(
          /import\s+{\s*useAuth\s*}\s+from\s+['"]\.\.\/\.\.\/context\/AuthContext['"]/g,
          "import { useAuth } from '../../context'"
        );
        
        if (updated1 !== content) {
          content = updated1;
          wasModified = true;
        }
        
        // Fix imports from ../context/AuthContext (for direct src/screens files)
        const updated2 = content.replace(
          /import\s+{\s*useAuth\s*}\s+from\s+['"]\.\.\/context\/AuthContext['"]/g,
          "import { useAuth } from '../context'"
        );
        
        if (updated2 !== content) {
          content = updated2;
          wasModified = true;
        }
        
        if (wasModified) {
          fs.writeFileSync(file, content, 'utf8');
          console.log(`✓ Fixed: ${path.relative(process.cwd(), file)}`);
          fixedCount++;
        }
      } catch (err) {
        console.log(`⚠️  Error processing ${file}: ${err.message}`);
      }
    }
    
    console.log('\n==================================================');
    console.log(`✅ Fixed: ${fixedCount} files`);
    console.log('==================================================');
    console.log('🚀 All imports now use context index.js');
    console.log('   - Files in subdirectories use: ../../context');
    console.log('   - Files in src/screens use: ../context');
  } catch (err) {
    console.error('Error:', err.message);
  }
}

fixAllAuthContextImports();
