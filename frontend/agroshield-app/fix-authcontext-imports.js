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

// Fix AuthContext imports
function fixAuthContextImports() {
  const srcDir = path.join(__dirname, 'src');
  const files = findJSFiles(srcDir);
  let fixedCount = 0;
  
  files.forEach(file => {
    let content = fs.readFileSync(file, 'utf8');
    const originalContent = content;
    
    // Fix AuthContext imports without .js extension
    content = content.replace(
      /from ['"](.*)\/context\/AuthContext['"]/g,
      "from '$1/context/AuthContext.js'"
    );
    
    if (content !== originalContent) {
      fs.writeFileSync(file, content, 'utf8');
      console.log(`✓ Fixed: ${path.relative(__dirname, file)}`);
      fixedCount++;
    }
  });
  
  console.log(`\n✓ Fixed ${fixedCount} files`);
}

fixAuthContextImports();
