/**
 * Test Backend Connection
 * Run this script to verify your React Native app can connect to the live backend
 * 
 * Usage: node test-backend-connection.js
 */

const axios = require('axios');

const BACKEND_URL = 'https://urchin-app-86rjy.ondigitalocean.app';

console.log('🧪 Testing AgroShield Backend Connection...\n');
console.log(`Backend URL: ${BACKEND_URL}\n`);

async function testEndpoint(name, endpoint) {
  try {
    console.log(`Testing ${name}...`);
    const response = await axios.get(`${BACKEND_URL}${endpoint}`, {
      timeout: 10000
    });
    console.log(`✅ ${name} - Status: ${response.status}`);
    console.log(`   Response:`, JSON.stringify(response.data).substring(0, 100));
    return true;
  } catch (error) {
    if (error.response) {
      console.log(`❌ ${name} - Status: ${error.response.status}`);
      console.log(`   Error:`, error.response.data);
    } else {
      console.log(`❌ ${name} - Error:`, error.message);
    }
    return false;
  }
}

async function runTests() {
  const tests = [
    { name: 'Farms API', endpoint: '/api/farms' },
    { name: 'Village Groups Health', endpoint: '/api/village-groups/groups/health' },
    { name: 'Upload Stats', endpoint: '/api/upload/stats' },
    { name: 'Subscription Tiers', endpoint: '/api/subscription/tiers' },
    { name: 'Drone Aggregation Bundles', endpoint: '/api/drone/marketplace/aggregation-bundles' },
  ];

  let passed = 0;
  let failed = 0;

  for (const test of tests) {
    const result = await testEndpoint(test.name, test.endpoint);
    if (result) passed++;
    else failed++;
    console.log('');
  }

  console.log('═══════════════════════════════════════');
  console.log(`Test Results: ${passed} passed, ${failed} failed`);
  console.log('═══════════════════════════════════════\n');

  if (passed === tests.length) {
    console.log('🎉 All tests passed! Your backend is ready.\n');
    console.log('Next steps:');
    console.log('1. Start your React Native app: npm start');
    console.log('2. Open on your device/emulator');
    console.log('3. Test API calls from the app\n');
  } else {
    console.log('⚠️  Some tests failed. Check your backend configuration.\n');
  }
}

runTests();
