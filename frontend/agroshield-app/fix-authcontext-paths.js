const fs = require('fs');
const path = require('path');

// Find all JS files recursively
function findJSFiles(dir, fileList = []) {
  const files = fs.readdirSync(dir);
  
  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory() && !file.includes('node_modules') && !file.includes('.expo')) {
      findJSFiles(filePath, fileList);
    } else if (file.endsWith('.js') || file.endsWith('.jsx')) {
      fileList.push(filePath);
    }
  });
  
  return fileList;
}

// Fix AuthContext imports based on actual file location
function fixAuthContextImports() {
  const srcDir = path.join(__dirname, 'src');
  const files = findJSFiles(srcDir);
  let fixedCount = 0;
  
  files.forEach(file => {
    let content = fs.readFileSync(file, 'utf8');
    const originalContent = content;
    
    // Calculate the correct relative path to AuthContext
    const fileDir = path.dirname(file);
    const contextPath = path.join(srcDir, 'context', 'AuthContext.js');
    let relativePath = path.relative(fileDir, contextPath);
    
    // Convert Windows paths to Unix style for imports
    relativePath = relativePath.replace(/\\/g, '/');
    
    // Ensure it starts with ./ or ../
    if (!relativePath.startsWith('.')) {
      relativePath = './' + relativePath;
    }
    
    // Fix any existing AuthContext imports
    const importRegex = /from ['"](.*)\/context\/AuthContext(\.js)?['"]/g;
    
    if (importRegex.test(content)) {
      content = content.replace(
        /from ['"](.*)\/context\/AuthContext(\.js)?['"]/g,
        `from '${relativePath}'`
      );
      
      if (content !== originalContent) {
        fs.writeFileSync(file, content, 'utf8');
        console.log(`✓ Fixed: ${path.relative(__dirname, file)} -> ${relativePath}`);
        fixedCount++;
      }
    }
  });
  
  console.log(`\n✓ Fixed ${fixedCount} files`);
}

fixAuthContextImports();
