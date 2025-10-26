# 🌍 AgroShield Regional Data API Reference

## Quick Reference for Mobile App Developers

### Base URL
```
Production: https://your-domain.com/api/regional
Development: http://localhost:8000/api/regional
```

---

## 📱 Essential Endpoint: Login Data

### Get All Regional Data on Login
```http
GET /comprehensive/{user_id}
```

**When to call:** Immediately after user login/app startup

**Response (500ms):**
```json
{
  "location": {
    "latitude": -1.2921,
    "longitude": 36.8219
  },
  "timestamp": "2025-10-24T10:30:00Z",
  
  "weather": {
    "current": {
      "temperature": 24.5,
      "feels_like": 26.0,
      "humidity": 65,
      "pressure": 1013,
      "wind_speed": 3.2,
      "wind_direction": 180,
      "clouds": 40,
      "visibility": 10000,
      "description": "scattered clouds",
      "icon": "02d",
      "rain_1h": 0,
      "uv_index": 8.5,
      "timestamp": "2025-10-24T10:00:00Z"
    },
    "forecast": [
      {
        "date": "2025-10-25",
        "temp_min": 18,
        "temp_max": 28,
        "temp_day": 25,
        "humidity": 60,
        "wind_speed": 3.5,
        "clouds": 35,
        "rain": 2.5,
        "description": "light rain",
        "icon": "10d",
        "uv_index": 7.0,
        "pop": 45
      }
    ],
    "alerts": [
      {
        "event": "Heavy Rain Warning",
        "description": "Heavy rainfall expected...",
        "start": "2025-10-25T06:00:00Z",
        "end": "2025-10-25T18:00:00Z"
      }
    ]
  },
  
  "climate": {
    "period": {
      "start": "2025-09-24",
      "end": "2025-10-24"
    },
    "temperature": {
      "average": 23.5,
      "daily": {
        "2025-10-24": 24.5,
        "2025-10-23": 23.0
      }
    },
    "precipitation": {
      "total_mm": 85.5,
      "daily": {
        "2025-10-24": 5.2,
        "2025-10-23": 0.0
      }
    },
    "humidity": {
      "average": 68.5
    },
    "wind_speed": {
      "average": 3.2
    },
    "solar_radiation": {
      "average": 185.5
    }
  },
  
  "satellite": {
    "vegetation_health": 0.78,
    "ndvi_proxy": 0.70,
    "precipitation_16day": {
      "total_mm": 45.5,
      "average_daily": 2.8
    },
    "temperature_16day": {
      "average": 24.2,
      "min": 18.5,
      "max": 29.0
    },
    "drought_risk": "low",
    "data_source": "NASA POWER (satellite-derived)",
    "period": {
      "start": "2025-10-08",
      "end": "2025-10-24"
    }
  },
  
  "market": {
    "nearest_market": "Nairobi",
    "distance_km": 12.5,
    "prices": {
      "maize": {
        "price_kes_per_kg": 48,
        "market": "Nairobi",
        "currency": "KES",
        "unit": "kg",
        "last_updated": "2025-10-24"
      },
      "beans": {
        "price_kes_per_kg": 125,
        "market": "Nairobi",
        "currency": "KES",
        "unit": "kg",
        "last_updated": "2025-10-24"
      },
      "tomatoes": {
        "price_kes_per_kg": 65,
        "market": "Nairobi",
        "currency": "KES",
        "unit": "kg",
        "last_updated": "2025-10-24"
      },
      "potatoes": {
        "price_kes_per_kg": 52,
        "market": "Nairobi",
        "currency": "KES",
        "unit": "kg",
        "last_updated": "2025-10-24"
      },
      "cabbage": {
        "price_kes_per_kg": 38,
        "market": "Nairobi",
        "currency": "KES",
        "unit": "kg",
        "last_updated": "2025-10-24"
      }
    },
    "data_source": "Regional market data",
    "last_updated": "2025-10-24T10:30:00Z"
  },
  
  "pest_alerts": [
    {
      "pest": "Fall Armyworm",
      "risk_level": "high",
      "reason": "Favorable temperature and humidity conditions",
      "recent_reports": 12,
      "recommended_action": "Scout fields regularly, consider early intervention"
    },
    {
      "pest": "Late Blight",
      "risk_level": "medium",
      "reason": "Cool and wet conditions favor late blight",
      "recent_reports": 5,
      "recommended_action": "Apply preventive fungicide if potatoes/tomatoes present"
    }
  ]
}
```

**Example Usage (React Native):**
```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

// Call on login
export const loadRegionalDataOnLogin = async (userId) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/regional/comprehensive/${userId}`
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch regional data');
    }
    
    const data = await response.json();
    
    // Cache locally
    await AsyncStorage.setItem(
      'regional_data',
      JSON.stringify({
        data,
        cached_at: new Date().toISOString()
      })
    );
    
    return data;
  } catch (error) {
    console.error('Regional data error:', error);
    
    // Try to use cached data
    const cached = await AsyncStorage.getItem('regional_data');
    if (cached) {
      const { data, cached_at } = JSON.parse(cached);
      const cacheAge = Date.now() - new Date(cached_at).getTime();
      
      // Use cache if less than 1 hour old
      if (cacheAge < 3600000) {
        console.log('Using cached regional data');
        return data;
      }
    }
    
    // Return empty structure if all fails
    return {
      weather: null,
      climate: null,
      satellite: null,
      market: null,
      pest_alerts: []
    };
  }
};

// Display on dashboard
export const DashboardScreen = () => {
  const [regionalData, setRegionalData] = useState(null);
  
  useEffect(() => {
    const userId = getCurrentUserId();
    loadRegionalDataOnLogin(userId).then(data => {
      setRegionalData(data);
    });
  }, []);
  
  if (!regionalData) {
    return <LoadingSpinner />;
  }
  
  return (
    <ScrollView>
      {/* Weather Card */}
      <WeatherCard 
        current={regionalData.weather?.current}
        forecast={regionalData.weather?.forecast}
      />
      
      {/* Market Prices Card */}
      <MarketPricesCard 
        prices={regionalData.market?.prices}
        nearestMarket={regionalData.market?.nearest_market}
      />
      
      {/* Pest Alerts */}
      {regionalData.pest_alerts?.length > 0 && (
        <PestAlertsCard alerts={regionalData.pest_alerts} />
      )}
      
      {/* Vegetation Health */}
      <VegetationCard 
        health={regionalData.satellite?.vegetation_health}
        droughtRisk={regionalData.satellite?.drought_risk}
      />
    </ScrollView>
  );
};
```

---

## 🌤️ Individual Endpoints

### 1. Weather Only
```http
GET /weather?lat={latitude}&lon={longitude}
```

**Use when:** Need to refresh weather without full data reload

**Example:**
```javascript
const refreshWeather = async (lat, lon) => {
  const response = await fetch(
    `${API_BASE_URL}/api/regional/weather?lat=${lat}&lon=${lon}`
  );
  return await response.json();
};
```

---

### 2. Market Prices Only
```http
GET /market-prices?lat={latitude}&lon={longitude}
```

**Use when:** User views market prices screen

**Example:**
```javascript
const getMarketPrices = async (lat, lon) => {
  const response = await fetch(
    `${API_BASE_URL}/api/regional/market-prices?lat=${lat}&lon=${lon}`
  );
  return await response.json();
};
```

---

### 3. Pest Alerts Only
```http
GET /pest-alerts?lat={latitude}&lon={longitude}
```

**Use when:** User views pest monitoring screen

**Example:**
```javascript
const getPestAlerts = async (lat, lon) => {
  const response = await fetch(
    `${API_BASE_URL}/api/regional/pest-alerts?lat=${lat}&lon=${lon}`
  );
  const { alerts } = await response.json();
  return alerts;
};
```

---

### 4. Update User Location
```http
POST /update-user-location
Content-Type: application/json

{
  "user_id": "user123",
  "lat": -1.2921,
  "lon": 36.8219
}
```

**Use when:**
- User enables location services
- User manually sets their location
- User adds/edits a field with GPS

**Example:**
```javascript
const updateLocation = async (userId, lat, lon) => {
  const response = await fetch(
    `${API_BASE_URL}/api/regional/update-user-location`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId,
        lat,
        lon
      })
    }
  );
  
  const result = await response.json();
  
  // Returns fresh regional data for new location
  return result.regional_data;
};
```

---

## 🚦 Health Check

### Check API Status
```http
GET /health
```

**Use when:** 
- App startup (check if services are operational)
- Troubleshooting data issues
- Before making important API calls

**Response:**
```json
{
  "timestamp": "2025-10-24T10:30:00Z",
  "services": {
    "openweathermap": {
      "status": "operational",
      "response_time_ms": "<1000"
    },
    "nasa_power": {
      "status": "operational",
      "response_time_ms": "<3000"
    },
    "market_api": {
      "status": "operational",
      "response_time_ms": "<2000"
    }
  },
  "overall_status": "operational"
}
```

**Example:**
```javascript
const checkAPIHealth = async () => {
  const response = await fetch(`${API_BASE_URL}/api/regional/health`);
  const health = await response.json();
  
  if (health.overall_status !== 'operational') {
    showAlert('Some services are currently unavailable. Using cached data.');
  }
  
  return health;
};
```

---

## 📊 Data Display Guidelines

### Weather Display:
```javascript
// Current weather
const WeatherCard = ({ current, forecast }) => (
  <Card>
    <Title>Current Weather</Title>
    <Text>{current.temperature}°C</Text>
    <Text>Feels like {current.feels_like}°C</Text>
    <Text>{current.description}</Text>
    <Image source={{ uri: `https://openweathermap.org/img/wn/${current.icon}@2x.png` }} />
    
    <Text>Humidity: {current.humidity}%</Text>
    <Text>Wind: {current.wind_speed} m/s</Text>
    {current.rain_1h > 0 && <Text>Rain: {current.rain_1h}mm</Text>}
    <Text>UV Index: {current.uv_index}</Text>
    
    {/* 7-day forecast */}
    {forecast.map(day => (
      <ForecastDay key={day.date} day={day} />
    ))}
  </Card>
);
```

### Market Prices Display:
```javascript
const MarketPricesCard = ({ prices, nearestMarket }) => (
  <Card>
    <Title>Market Prices - {nearestMarket}</Title>
    {Object.entries(prices).map(([crop, info]) => (
      <PriceRow key={crop}>
        <CropName>{crop.charAt(0).toUpperCase() + crop.slice(1)}</CropName>
        <Price>{info.price_kes_per_kg} KES/kg</Price>
        <LastUpdated>Updated: {info.last_updated}</LastUpdated>
      </PriceRow>
    ))}
  </Card>
);
```

### Pest Alerts Display:
```javascript
const PestAlertsCard = ({ alerts }) => (
  <Card>
    <Title>⚠️ Pest Alerts in Your Area</Title>
    {alerts.map((alert, index) => (
      <AlertRow 
        key={index}
        severity={alert.risk_level}
        style={alert.risk_level === 'high' ? styles.highRisk : styles.mediumRisk}
      >
        <AlertTitle>{alert.pest}</AlertTitle>
        <RiskBadge level={alert.risk_level}>
          {alert.risk_level.toUpperCase()}
        </RiskBadge>
        <AlertReason>{alert.reason}</AlertReason>
        <ReportsCount>{alert.recent_reports} reports in 50km</ReportsCount>
        <ActionButton>
          {alert.recommended_action}
        </ActionButton>
      </AlertRow>
    ))}
  </Card>
);
```

### Vegetation Health Display:
```javascript
const VegetationCard = ({ health, droughtRisk }) => {
  const healthPercent = Math.round(health * 100);
  const healthColor = health > 0.7 ? 'green' : health > 0.5 ? 'yellow' : 'red';
  
  return (
    <Card>
      <Title>Vegetation Health (Satellite)</Title>
      <ProgressBar 
        value={healthPercent}
        color={healthColor}
      />
      <Text>{healthPercent}% Healthy</Text>
      
      <DroughtRiskBadge risk={droughtRisk}>
        Drought Risk: {droughtRisk.toUpperCase()}
      </DroughtRiskBadge>
    </Card>
  );
};
```

---

## ⏱️ Refresh Guidelines

### Data Freshness:
- **Weather**: Refresh every 30 minutes
- **Market Prices**: Refresh every 6 hours
- **Pest Alerts**: Refresh every hour
- **Satellite Data**: Refresh daily

### Example Refresh Logic:
```javascript
const shouldRefreshWeather = (lastUpdate) => {
  const THIRTY_MINUTES = 30 * 60 * 1000;
  return Date.now() - new Date(lastUpdate).getTime() > THIRTY_MINUTES;
};

const shouldRefreshMarket = (lastUpdate) => {
  const SIX_HOURS = 6 * 60 * 60 * 1000;
  return Date.now() - new Date(lastUpdate).getTime() > SIX_HOURS;
};

// In your component
useEffect(() => {
  const interval = setInterval(() => {
    if (shouldRefreshWeather(weatherLastUpdate)) {
      refreshWeather();
    }
  }, 60000); // Check every minute
  
  return () => clearInterval(interval);
}, [weatherLastUpdate]);
```

---

## 🎯 Best Practices

### 1. Cache Everything
```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

const CACHE_KEYS = {
  REGIONAL_DATA: 'regional_data',
  WEATHER: 'weather_data',
  MARKET: 'market_data'
};

// Cache data
await AsyncStorage.setItem(
  CACHE_KEYS.REGIONAL_DATA,
  JSON.stringify({ data, timestamp: Date.now() })
);

// Retrieve cache
const cached = await AsyncStorage.getItem(CACHE_KEYS.REGIONAL_DATA);
```

### 2. Handle Offline Mode
```javascript
import NetInfo from '@react-native-community/netinfo';

const fetchWithOfflineSupport = async (url, cacheKey) => {
  const netInfo = await NetInfo.fetch();
  
  if (!netInfo.isConnected) {
    // Use cached data
    const cached = await AsyncStorage.getItem(cacheKey);
    if (cached) {
      return JSON.parse(cached).data;
    }
    throw new Error('No internet and no cached data');
  }
  
  // Fetch fresh data
  const response = await fetch(url);
  const data = await response.json();
  
  // Cache for offline use
  await AsyncStorage.setItem(
    cacheKey,
    JSON.stringify({ data, timestamp: Date.now() })
  );
  
  return data;
};
```

### 3. Show Data Freshness
```javascript
const DataFreshnessIndicator = ({ timestamp }) => {
  const age = Date.now() - new Date(timestamp).getTime();
  const minutes = Math.floor(age / 60000);
  
  return (
    <View style={styles.freshnessIndicator}>
      <Icon name="clock" size={12} />
      <Text style={styles.freshnessText}>
        Updated {minutes < 1 ? 'just now' : `${minutes}m ago`}
      </Text>
    </View>
  );
};
```

### 4. Error Handling
```javascript
const fetchRegionalData = async (userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/regional/comprehensive/${userId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    // Log error for debugging
    console.error('Regional data error:', error);
    
    // Try cache
    const cached = await getCachedData();
    if (cached) {
      showToast('Using cached data (offline)');
      return cached;
    }
    
    // Show user-friendly error
    showAlert('Unable to load weather data. Please check your connection.');
    
    // Return safe defaults
    return getDefaultRegionalData();
  }
};
```

---

## 🔍 Debugging

### Check if APIs are configured:
```bash
curl http://localhost:8000/api/regional/health
```

### Test specific location:
```bash
# Nairobi
curl "http://localhost:8000/api/regional/weather?lat=-1.2921&lon=36.8219"

# Mombasa
curl "http://localhost:8000/api/regional/weather?lat=-4.0435&lon=39.6682"
```

### Check comprehensive data:
```bash
curl http://localhost:8000/api/regional/comprehensive/test_user
```

---

## 📞 Support

- **Setup Guide**: See `REGIONAL_DATA_SETUP.md`
- **Integration Complete**: See `INTEGRATION_COMPLETE.md`
- **Health Check**: `GET /api/regional/health`
- **Data Sources**: `GET /api/regional/data-sources`

---

**Ready to integrate! Start with the `/comprehensive/{user_id}` endpoint on login.**
