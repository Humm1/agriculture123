const fs = require('fs');
const path = require('path');

console.log('🔧 Fixing AuthContext imports to use full path with .js extension...');

const files = [
  'src/navigation/RootNavigator.js',
  'src/navigation/FarmerTabs.js',
  'src/navigation/BuyerTabs.js',
  'src/screens/Login.js',
  'src/screens/Dashboard.js',
  'src/screens/FarmerDashboard.js',
  'src/screens/BuyerDashboard.js',
  'src/screens/Notifications.js',
  'src/screens/Profile.js',
  'src/screens/SubscriptionPlans.js',
  'src/screens/Farms.js',
  'src/screens/Farm.js',
  'src/screens/AddFarm.js',
  'src/screens/AIAnalytics.js',
  'src/screens/CropProfileList.js',
  'src/screens/CropProfileDetail.js',
  'src/screens/CropTasksCalendar.js',
  'src/screens/IPMPestsList.js',
  'src/screens/IPMDiseasesList.js',
  'src/screens/IPMTreatmentPlan.js',
  'src/screens/FarmMap.js',
  'src/screens/Settings.js',
  'src/screens/FarmerMarketplace.js',
  'src/screens/BuyerMarketplace.js',
  'src/screens/DroneIntelligence.js',
  'src/screens/DigitalAlmanac.js',
  'src/screens/ExchangeRates.js',
  'src/screens/VillageGroups.js'
];

let fixedCount = 0;

files.forEach(file => {
  const filePath = path.join(__dirname, file);
  
  if (!fs.existsSync(filePath)) {
    console.log(`⚠️  File not found: ${file}`);
    return;
  }
  
  let content = fs.readFileSync(filePath, 'utf8');
  
  // Replace the import statement with full path including .js extension
  const updated = content.replace(
    /import\s+{\s*useAuth\s*}\s+from\s+['"]\.\.\/\.\.\/context['"]/g,
    "import { useAuth } from '../../context/AuthContext.js'"
  );
  
  if (updated !== content) {
    fs.writeFileSync(filePath, updated, 'utf8');
    console.log(`✓ Fixed: ${file}`);
    fixedCount++;
  }
});

console.log('==================================================');
console.log(`✅ Fixed: ${fixedCount} files`);
console.log('==================================================');
console.log('🚀 All imports now use full path: ../../context/AuthContext.js');
