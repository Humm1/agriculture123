# Fix AuthContext imports by adding .js extension
$files = @(
    "src\screens\auth\LoginScreen.js",
    "src\screens\auth\RegisterScreen.js",
    "src\screens\auth\WelcomeScreen.js",
    "src\navigation\RootNavigator.js",
    "src\screens\farmer\FarmerDashboardScreen.js",
    "src\screens\farmer\SoilScanScreen.js",
    "src\screens\farmer\BudgetCalculatorScreen.js",
    "src\screens\farmer\EditLocationScreen.js",
    "src\screens\AIFarmIntelligenceScreen.js",
    "src\screens\home\HomeScreen.js",
    "src\navigation\AppNavigator.js",
    "src\screens\farm\FarmListScreen.js",
    "src\screens\farm\AddFarmScreen.js",
    "src\screens\campaigns\CampaignDetailScreen.js",
    "src\screens\campaigns\ExpertHelpScreen.js",
    "src\screens\premium\YieldForecastScreen.js",
    "src\screens\subscription\TransactionsScreen.js",
    "src\screens\profile\ProfileScreen.js",
    "src\screens\Notifications.js",
    "src\screens\premium\MarketAlertsScreen.js",
    "src\screens\subscription\SubscriptionScreen.js",
    "src\screens\home\NotificationsScreen.js",
    "src\screens\groups\PostDetailScreen.js",
    "src\screens\groups\ShowcaseScreen.js",
    "src\screens\groups\CreatePostScreen.js",
    "src\screens\groups\GroupFeedScreen.js",
    "src\screens\groups\PollsScreen.js"
)

Write-Host "Fixing AuthContext imports..." -ForegroundColor Green

foreach ($file in $files) {
    $fullPath = "C:\Users\Codeternal\Desktop\agroshield\frontend\agroshield-app\$file"
    if (Test-Path $fullPath) {
        $content = Get-Content $fullPath -Raw
        $newContent = $content -replace "from ['`"](.*/context/AuthContext)['`"]", "from '`$1.js'"
        Set-Content -Path $fullPath -Value $newContent -NoNewline
        Write-Host "  ✓ Fixed: $file" -ForegroundColor Gray
    } else {
        Write-Host "  ✗ Not found: $file" -ForegroundColor Yellow
    }
}

Write-Host "`nDone! All AuthContext imports now have .js extension" -ForegroundColor Green
Write-Host "Run 'npm start' to test the app" -ForegroundColor Cyan
