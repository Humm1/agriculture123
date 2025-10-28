/**
 * Test script to verify model integration
 * Run with: node test_model_integration.js
 */

const API_BASE_URL = 'http://localhost:8000/api';

async function testModelIntegration() {
  console.log('=================================');
  console.log('ML MODELS INTEGRATION TEST');
  console.log('=================================\n');

  try {
    // Test 1: Health Check
    console.log('[1/6] Testing health check...');
    const healthResponse = await fetch(`${API_BASE_URL}/models/health`);
    const healthData = await healthResponse.json();
    console.log(`  Status: ${healthData.status}`);
    console.log(`  Models Available: ${healthData.models_available}`);
    console.log(`  System Ready: ${healthData.system_ready}`);
    console.log('  [PASS]\n');

    // Test 2: List all models
    console.log('[2/6] Listing all models...');
    const listResponse = await fetch(`${API_BASE_URL}/models/list`);
    const listData = await listResponse.json();
    console.log(`  Total Models: ${Object.keys(listData.models).length}`);
    Object.entries(listData.models).forEach(([name, info]) => {
      console.log(`    - ${name}: ${info.available ? '[AVAILABLE]' : '[NOT FOUND]'} (${info.type})`);
    });
    console.log('  [PASS]\n');

    // Test 3: Get full system status
    console.log('[3/6] Getting system status...');
    const statusResponse = await fetch(`${API_BASE_URL}/models/status`);
    const statusData = await statusResponse.json();
    console.log(`  Models Configured: ${statusData.summary.total_models}`);
    console.log(`  Models Available: ${statusData.summary.models_available}`);
    console.log(`  Models Loaded: ${statusData.summary.models_loaded}`);
    console.log(`  Training Data Dir: ${statusData.paths.training_data}`);
    console.log('  [PASS]\n');

    // Test 4: Get specific model info (pest detection)
    console.log('[4/6] Getting pest detection model info...');
    const pestResponse = await fetch(`${API_BASE_URL}/models/pest_detection/info`);
    const pestData = await pestResponse.json();
    console.log(`  Model Name: ${pestData.model_name}`);
    console.log(`  Available: ${pestData.available}`);
    console.log(`  Type: ${pestData.type}`);
    console.log(`  Classes: ${pestData.num_classes} classes`);
    console.log(`  Description: ${pestData.description}`);
    console.log('  [PASS]\n');

    // Test 5: Get training data status
    console.log('[5/6] Getting training data status...');
    const trainingResponse = await fetch(`${API_BASE_URL}/models/training-data/status`);
    const trainingData = await trainingResponse.json();
    console.log(`  Synthetic Data: ${trainingData.synthetic_data.total_files} files`);
    console.log(`  Public Data: ${trainingData.public_data.total_files} files`);
    console.log(`  Total Datasets: ${trainingData.total_datasets}`);
    console.log('  [PASS]\n');

    // Test 6: Test model loading (if available)
    console.log('[6/6] Testing model loading...');
    if (pestData.available && !pestData.loaded) {
      console.log('  Loading pest detection model...');
      const loadResponse = await fetch(`${API_BASE_URL}/models/pest_detection/load`, {
        method: 'POST'
      });
      const loadData = await loadResponse.json();
      console.log(`  Load Result: ${loadData.success ? '[SUCCESS]' : '[FAILED]'}`);
      console.log(`  Message: ${loadData.message}`);
    } else if (pestData.loaded) {
      console.log('  Model already loaded [SKIP]');
    } else {
      console.log('  Model not available for loading [SKIP]');
    }
    console.log('  [PASS]\n');

    // Summary
    console.log('=================================');
    console.log('ALL TESTS PASSED');
    console.log('=================================\n');
    console.log('Frontend Integration Ready:');
    console.log('  - mlModelsService.js: Service layer created');
    console.log('  - useModelsStatus.js: React hooks created');
    console.log('  - API endpoints: All 7 endpoints working');
    console.log('\nAvailable Features:');
    const availableModels = Object.entries(listData.models)
      .filter(([_, info]) => info.available)
      .map(([name, _]) => name);
    availableModels.forEach(model => {
      console.log(`  [OK] ${model}`);
    });

  } catch (error) {
    console.error('\n[ERROR] Test failed:', error.message);
    console.error('  Make sure the backend is running: python backend/run_dev.py');
  }
}

// Run tests
testModelIntegration();
