const fs = require('fs');
const path = require('path');

const files = [
    "src/screens/auth/LoginScreen.js",
    "src/screens/auth/RegisterScreen.js",
    "src/screens/auth/WelcomeScreen.js",
    "src/navigation/RootNavigator.js",
    "src/screens/farmer/FarmerDashboardScreen.js",
    "src/screens/farmer/SoilScanScreen.js",
    "src/screens/farmer/BudgetCalculatorScreen.js",
    "src/screens/farmer/EditLocationScreen.js",
    "src/screens/AIFarmIntelligenceScreen.js",
    "src/screens/home/HomeScreen.js",
    "src/navigation/AppNavigator.js",
    "src/screens/farm/FarmListScreen.js",
    "src/screens/farm/AddFarmScreen.js",
    "src/screens/campaigns/CampaignDetailScreen.js",
    "src/screens/campaigns/ExpertHelpScreen.js",
    "src/screens/premium/YieldForecastScreen.js",
    "src/screens/subscription/TransactionsScreen.js",
    "src/screens/profile/ProfileScreen.js",
    "src/screens/premium/MarketAlertsScreen.js",
    "src/screens/subscription/SubscriptionScreen.js",
    "src/screens/home/NotificationsScreen.js",
    "src/screens/groups/PostDetailScreen.js",
    "src/screens/groups/ShowcaseScreen.js",
    "src/screens/groups/CreatePostScreen.js",
    "src/screens/groups/GroupFeedScreen.js",
    "src/screens/groups/PollsScreen.js",
    "src/screens/Notifications.js",
    "App.js"
];

console.log('🔧 Fixing AuthContext imports to use index.js...\n');

let fixed = 0;
let errors = 0;

files.forEach(file => {
    const fullPath = path.join(__dirname, file);
    try {
        if (fs.existsSync(fullPath)) {
            let content = fs.readFileSync(fullPath, 'utf8');
            const original = content;
            
            // Replace imports to use context folder (which will automatically use index.js)
            // This removes both AuthContext and AuthContext.js
            content = content.replace(
                /from ['"](.*)\/context\/AuthContext(\.js)?['"]/g,
                "from '$1/context'"
            );
            
            if (content !== original) {
                fs.writeFileSync(fullPath, content, 'utf8');
                console.log(`✓ Fixed: ${file}`);
                fixed++;
            } else {
                console.log(`- No changes needed: ${file}`);
            }
        } else {
            console.log(`✗ Not found: ${file}`);
            errors++;
        }
    } catch (error) {
        console.log(`✗ Error with ${file}: ${error.message}`);
        errors++;
    }
});

console.log(`\n${'='.repeat(50)}`);
console.log(`✅ Fixed: ${fixed} files`);
if (errors > 0) console.log(`❌ Errors: ${errors} files`);
console.log(`${'='.repeat(50)}\n`);
console.log('🚀 All imports now use context/index.js');
console.log('💡 Run "npx expo start -c --web" to test!');
