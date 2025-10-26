# Testing & Monitoring Guide
**AgroShield AI Platform - Quality Assurance & Performance Monitoring**

---

## 📋 Table of Contents

1. [Testing Suite Overview](#testing-suite-overview)
2. [Running Tests](#running-tests)
3. [Test Coverage Goals](#test-coverage-goals)
4. [Monitoring System](#monitoring-system)
5. [Dashboard API](#dashboard-api)
6. [CI/CD Integration](#cicd-integration)

---

## 🧪 Testing Suite Overview

### Test Files Created

| Test File | Coverage Area | Tests Count | Target Coverage |
|-----------|--------------|-------------|-----------------|
| `test_ai_hyperlocal_prediction.py` | Weather fusion, disease predictions | 30+ | 90% |
| `test_ai_smart_recommendations.py` | Planting optimization, financial scenarios | 25+ | 90% |
| `test_ai_field_scout.py` | Diagnostic triage, contagion modeling | 30+ | 90% |
| `test_satellite_integration.py` | NDVI, elevation APIs | 15+ | 85% |
| `test_weather_integration.py` | LCRS, BLE sensors, SMS alerts | 20+ | 85% |
| `test_computer_vision.py` | Soil classification, disease detection | 15+ | 85% |

### Test Categories

- **Unit Tests**: Test individual functions in isolation
- **Integration Tests**: Test multiple components working together
- **Performance Tests**: Measure speed and load handling
- **End-to-End Tests**: Complete farmer workflows

---

## 🚀 Running Tests

### Quick Start

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
python run_tests.py

# Run with coverage report
python run_tests.py --coverage
```

### Test Execution Options

```bash
# Unit tests only (fast)
python run_tests.py --unit

# Integration tests
python run_tests.py --integration

# Performance tests
python run_tests.py --performance

# Skip slow tests
python run_tests.py --fast

# Run specific test file
python run_tests.py --test-file test_ai_hyperlocal_prediction.py

# Verbose output
python run_tests.py --verbose

# Generate HTML report
python run_tests.py --report
```

### Using Pytest Directly

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_ai_hyperlocal_prediction.py

# Run specific test class
pytest tests/test_ai_hyperlocal_prediction.py::TestWeatherDataFusion

# Run specific test
pytest tests/test_ai_hyperlocal_prediction.py::TestWeatherDataFusion::test_synthesize_basic_forecast

# Run tests matching pattern
pytest -k "weather"

# Run with coverage
pytest --cov=app.services --cov-report=html

# Run tests in parallel (faster)
pytest -n auto
```

---

## 📊 Test Coverage Goals

### Current Coverage Targets

| Module | Target | Current | Status |
|--------|--------|---------|--------|
| `ai_hyperlocal_prediction.py` | 90% | TBD | 🎯 |
| `ai_smart_recommendations.py` | 90% | TBD | 🎯 |
| `ai_field_scout.py` | 90% | TBD | 🎯 |
| `satellite_integration.py` | 85% | TBD | 🎯 |
| `weather_integration.py` | 85% | TBD | 🎯 |
| `computer_vision.py` | 85% | TBD | 🎯 |
| `monitoring.py` | 80% | TBD | 🎯 |

### Viewing Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=app.services --cov-report=html

# Open in browser (Windows)
start htmlcov/index.html

# Open in browser (Mac)
open htmlcov/index.html

# Open in browser (Linux)
xdg-open htmlcov/index.html
```

### Coverage Report Interpretation

- **Green**: Well-covered code (good)
- **Yellow**: Partially covered (needs more tests)
- **Red**: Uncovered code (critical - add tests)

**Coverage commands:**
```bash
# Terminal coverage summary
pytest --cov=app.services --cov-report=term-missing

# XML coverage (for CI/CD)
pytest --cov=app.services --cov-report=xml

# Multiple formats
pytest --cov=app.services --cov-report=html --cov-report=term --cov-report=xml
```

---

## 📈 Monitoring System

### Overview

The monitoring system (`app/services/monitoring.py`) tracks:

1. **AI Confidence Scores**: Trend analysis over time
2. **Prediction Accuracy**: Compare predictions vs actual outcomes
3. **Practice Adoption**: How often farmers follow AI recommendations
4. **Fertilizer Savings**: Cost and environmental impact
5. **Harvest Predictions**: Date and yield accuracy
6. **Farmer Feedback**: Satisfaction ratings and comments

### Key Functions

#### 1. Track AI Predictions

```python
from app.services.monitoring import track_ai_prediction

# Track a weather prediction
track_ai_prediction(
    prediction_id="pred_12345",
    engine="brain",
    prediction_type="weather",
    prediction_data={
        "temperature_c": 24.5,
        "rainfall_mm": 12.0,
        "date": "2025-10-25"
    },
    confidence=0.85,
    farmer_id="farmer_001",
    field_id="field_001"
)
```

#### 2. Record Actual Outcomes

```python
from app.services.monitoring import record_prediction_outcome

# Record what actually happened
result = record_prediction_outcome(
    prediction_id="pred_12345",
    actual_outcome={
        "temperature_c": 25.0,  # Actual temp
        "rainfall_mm": 10.5     # Actual rainfall
    },
    outcome_date="2025-10-25"
)

# Result contains accuracy calculation
print(f"Accuracy: {result['accuracy']:.2%}")
print(f"Met target: {result['met_target']}")
```

#### 3. Get Confidence Trends

```python
from app.services.monitoring import get_confidence_trends

# Get 30-day confidence trends
trends = get_confidence_trends(
    engine="brain",
    prediction_type="weather",
    days=30
)

print(f"Mean confidence: {trends['confidence_stats']['mean']}")
print(f"Trend: {trends['trend']}")  # improving, stable, declining
```

#### 4. Track Practice Adjustments

```python
from app.services.monitoring import track_practice_adjustment

# Track if farmer followed recommendation
track_practice_adjustment(
    farmer_id="farmer_001",
    field_id="field_001",
    recommendation_id="rec_456",
    recommended_action="irrigate_immediately",
    actual_action="irrigated_within_3_hours",
    outcome="crop_recovered"
)
```

#### 5. Track Fertilizer Savings

```python
from app.services.monitoring import track_fertilizer_savings

# Track savings from AI optimization
savings = track_fertilizer_savings(
    farmer_id="farmer_001",
    field_id="field_001",
    crop="maize",
    traditional_amount_kg=50.0,
    optimized_amount_kg=35.0,
    cost_per_kg=150,  # KES
    leaching_prevented_percent=40
)

print(f"Saved: {savings['cost_saved']} KES")
print(f"Saved: {savings['amount_saved_kg']} kg fertilizer")
```

#### 6. Collect Farmer Feedback

```python
from app.services.monitoring import collect_farmer_feedback

# Collect rating and comment
collect_farmer_feedback(
    farmer_id="farmer_001",
    feature="weather_forecast",
    rating=4.5,  # 1-5 scale
    comment="Very accurate! Helped me plan irrigation.",
    context={"prediction_id": "pred_12345"}
)
```

---

## 🎯 Dashboard API

### Complete Dashboard Summary

```python
from app.services.monitoring import get_dashboard_summary

# Get all metrics in one call
dashboard = get_dashboard_summary()

print(dashboard)
# Returns:
# {
#   "confidence_trends": {...},
#   "accuracy_report": {...},
#   "adoption_rate": {...},
#   "fertilizer_savings": {...},
#   "farmer_satisfaction": {...},
#   "system_health": {...},
#   "alerts": [...]
# }
```

### Individual Reports

```python
from app.services.monitoring import (
    get_confidence_trends,
    get_accuracy_report,
    get_adoption_rate,
    get_fertilizer_savings_report,
    get_farmer_satisfaction_report
)

# Confidence trends (30 days)
confidence = get_confidence_trends(days=30)

# Accuracy report (90 days)
accuracy = get_accuracy_report(days=90)

# Adoption rate (30 days)
adoption = get_adoption_rate(days=30)

# Fertilizer savings (90 days)
savings = get_fertilizer_savings_report(days=90)

# Farmer satisfaction (30 days)
satisfaction = get_farmer_satisfaction_report(days=30)
```

### Dashboard Metrics

#### Confidence Trends Output
```json
{
  "period_days": 30,
  "total_predictions": 1250,
  "confidence_stats": {
    "mean": 0.823,
    "median": 0.850,
    "min": 0.620,
    "max": 0.980,
    "std_dev": 0.092
  },
  "distribution": {
    "excellent": 450,  # ≥0.90
    "good": 600,       # 0.75-0.90
    "acceptable": 150, # 0.65-0.75
    "poor": 50         # <0.65
  },
  "trend": "improving"
}
```

#### Accuracy Report Output
```json
{
  "period_days": 90,
  "total_measurements": 856,
  "accuracy_stats": {
    "mean": 0.847,
    "median": 0.870,
    "min": 0.520,
    "max": 0.990
  },
  "target_comparison": {
    "target": 0.850,
    "actual": 0.847,
    "difference": -0.003,
    "meeting_target": false
  },
  "confidence_correlation": {
    "high_confidence_avg": 0.895,
    "low_confidence_avg": 0.720,
    "correlation": "positive"
  }
}
```

#### Fertilizer Savings Output
```json
{
  "period_days": 90,
  "total_optimizations": 342,
  "total_fertilizer_saved_kg": 5130.50,
  "total_cost_saved": 769575.00,  # KES
  "avg_cost_saved_per_farmer": 2250.22,
  "avg_leaching_prevented_percent": 38.5,
  "environmental_impact": {
    "nitrogen_runoff_prevented_kg": 769.58,
    "water_pollution_reduction": "significant"
  }
}
```

#### Farmer Satisfaction Output
```json
{
  "period_days": 30,
  "total_responses": 428,
  "overall_rating": 4.3,
  "rating_distribution": {
    "5_star": 210,
    "4_star": 150,
    "3_star": 50,
    "2_star": 15,
    "1_star": 3
  },
  "by_feature": {
    "weather_forecast": {"avg_rating": 4.5, "total_responses": 150},
    "pest_detection": {"avg_rating": 4.2, "total_responses": 120},
    "recommendations": {"avg_rating": 4.1, "total_responses": 158}
  },
  "satisfaction_level": "excellent"
}
```

---

## 🔧 CI/CD Integration

### GitHub Actions Workflow

Create `.github/workflows/tests.yml`:

```yaml
name: AgroShield Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests with coverage
      run: |
        cd backend
        pytest --cov=app.services --cov-report=xml --cov-report=term
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        fail_ci_if_error: true
    
    - name: Run linting
      run: |
        cd backend
        flake8 app/ --max-line-length=120
        pylint app/ --max-line-length=120 --disable=C0111,R0913
```

### Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: python backend/run_tests.py --fast
        language: system
        pass_filenames: false
        always_run: true
```

Install pre-commit:
```bash
pip install pre-commit
pre-commit install
```

---

## 📊 Performance Benchmarks

### Target Performance

| Operation | Target Time | Load Test |
|-----------|-------------|-----------|
| Weather forecast generation | <2.0s | 50 farmers concurrently |
| Disease outbreak prediction | <1.0s | 100 predictions/minute |
| Planting window optimization | <2.0s | 50 fields/minute |
| Financial scenario generation | <1.0s | 100 scenarios/minute |
| Diagnostic triage | <0.5s | 200 images/minute |

### Running Performance Tests

```bash
# Run performance tests
python run_tests.py --performance

# Run with benchmark profiling
pytest tests/test_ai_hyperlocal_prediction.py::TestPerformance --benchmark-only

# Load testing with Locust
locust -f tests/locustfile.py --host=http://localhost:8000
```

---

## 🚨 Monitoring Alerts

### Alert Thresholds

| Alert Type | Threshold | Action |
|------------|-----------|--------|
| Confidence drop | >10% decline | Review data quality |
| Accuracy decline | >15% drop | Retrain models |
| Low satisfaction | Rating <3.0 | Review farmer feedback |
| High error rate | >5% failures | Check system logs |

### Alert Configuration

```python
from app.services.monitoring import MONITORING_CONFIG

# Customize thresholds
MONITORING_CONFIG["alert_thresholds"] = {
    "confidence_drop": 0.10,
    "accuracy_decline": 0.15,
    "farmer_satisfaction": 3.0
}
```

---

## 🎓 Best Practices

### Writing Tests

1. **Test one thing**: Each test should verify one specific behavior
2. **Use descriptive names**: `test_weather_fusion_weights_by_proximity` not `test_1`
3. **Arrange-Act-Assert**: Clear test structure
4. **Mock external APIs**: Don't hit real APIs in tests
5. **Use fixtures**: Reuse common test data

### Monitoring Best Practices

1. **Track everything**: All AI predictions should be logged
2. **Record outcomes**: Always record actual results for accuracy
3. **Collect feedback**: Regular farmer satisfaction surveys
4. **Review trends**: Weekly review of confidence/accuracy trends
5. **Act on alerts**: Respond promptly to monitoring alerts

---

## 📞 Support

For testing issues:
- Check test output for specific error messages
- Review coverage report to find untested code
- Run tests with `--verbose` flag for detailed output

For monitoring issues:
- Check dashboard for system health status
- Review alerts for actionable insights
- Analyze trends to identify degradation

---

**Last Updated**: October 2025  
**Version**: 1.0.0  
**Maintainers**: AgroShield AI Team
