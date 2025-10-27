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

// Fix all service imports to use correct relative paths
function fixServiceImports() {
  const srcDir = path.join(__dirname, 'src');
  const files = findJSFiles(srcDir);
  let fixedCount = 0;
  
  files.forEach(file => {
    let content = fs.readFileSync(file, 'utf8');
    const originalContent = content;
    const fileDir = path.dirname(file);
    
    // List of services to fix
    const services = [
      'api',
      'aiFarmIntelligenceService',
      'aiPredictionService',
      'droneIntelligenceService',
      'exchangeService',
      'locationService',
      'marketLinkagesService',
      'supabase'
    ];
    
    services.forEach(service => {
      const servicePath = path.join(srcDir, 'services', service + '.js');
      if (fs.existsSync(servicePath)) {
        let relativePath = path.relative(fileDir, servicePath);
        
        // Convert Windows paths to Unix style
        relativePath = relativePath.replace(/\\/g, '/');
        
        // Ensure it starts with ./ or ../
        if (!relativePath.startsWith('.')) {
          relativePath = './' + relativePath;
        }
        
        // Remove .js extension from the relative path for the replacement
        const relativePathWithoutExt = relativePath.replace(/\.js$/, '');
        
        // Fix imports with or without .js extension
        const importPattern = new RegExp(`from ['"](.*)\/services\/${service}(\\.js)?['"]`, 'g');
        
        if (importPattern.test(content)) {
          content = content.replace(
            new RegExp(`from ['"](.*)\/services\/${service}(\\.js)?['"]`, 'g'),
            `from '${relativePathWithoutExt}'`
          );
        }
      }
    });
    
    if (content !== originalContent) {
      fs.writeFileSync(file, content, 'utf8');
      console.log(`✓ Fixed: ${path.relative(__dirname, file)}`);
      fixedCount++;
    }
  });
  
  console.log(`\n✓ Fixed ${fixedCount} files`);
}

fixServiceImports();
