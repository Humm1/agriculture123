# Farm-to-Business Digital Marketplace - Frontend Integration Guide

## Overview
Complete React Native implementation for the AgroShield Farm-to-Business (F2B) Digital Marketplace with AI-driven market optimization.

## New Frontend Screens Created

### 1. FarmerMarketplace.js
**Location:** `frontend/src/screens/FarmerMarketplace.js`

**Features:**
- **4 Main Tabs:**
  - My Listings: View and manage sale listings
  - Offers: Incoming buyer offers dashboard
  - Contracts: Active and completed contracts with payment tracking
  - AI Insights: AI-powered market recommendations for all fields

**Key Functionality:**
- ✅ Create new listings with photo uploads (up to 5 images)
- ✅ AI price suggestions if target price not provided
- ✅ Real-time offer notifications with pending count
- ✅ Accept/Counter/Decline offer responses
- ✅ M-Pesa deposit tracking for accepted contracts
- ✅ Delivery confirmation with photo evidence
- ✅ Payment status tracking (deposit + final payment)
- ✅ AI market insights showing optimal selling windows
- ✅ Net profit calculations for each strategy

**API Endpoints Used:**
```
POST   /api/marketplace/farmer/create-listing
GET    /api/marketplace/farmer/my-listings/{farmer_id}
PUT    /api/marketplace/farmer/update-listing/{listing_id}
DELETE /api/marketplace/farmer/delete-listing/{listing_id}
GET    /api/marketplace/farmer/offers/{farmer_id}
POST   /api/marketplace/farmer/respond-to-offer
GET    /api/marketplace/farmer/contracts/{farmer_id}
POST   /api/marketplace/farmer/confirm-delivery/{contract_id}
GET    /api/marketplace/farmer/payment-status/{contract_id}
GET    /api/marketplace/farmer/market-insights/{farmer_id}
```

**User Flow:**
1. Farmer creates listing → AI suggests optimal price
2. Buyer makes offer → Farmer receives notification
3. Farmer accepts offer → Digital contract created
4. Buyer pays 10% deposit via M-Pesa
5. Farmer delivers produce → Confirms delivery with photos
6. Buyer confirms receipt → Final 90% payment released automatically

---

### 2. BuyerMarketplace.js
**Location:** `frontend/src/screens/BuyerMarketplace.js`

**Features:**
- **4 Main Tabs:**
  - Search: Intelligent location-based search with filters
  - Requirements: Define product needs for AI matching
  - My Offers: Track all submitted offers and responses
  - Orders: Active contracts and delivery tracking

**Key Functionality:**
- ✅ Business registration with KYB (Know Your Business) verification
- ✅ PostGIS location-based search (50km/100km/150km radius)
- ✅ AI supply forecasting (predict available supply in 30/60 days)
- ✅ Product requirement system for automated matching
- ✅ Make offers to farmer listings
- ✅ M-Pesa deposit payment integration
- ✅ Delivery tracking and quality confirmation
- ✅ Dispute resolution for quality issues
- ✅ Automatic final payment release after confirmation

**API Endpoints Used:**
```
POST   /api/marketplace/buyer/register-buyer
GET    /api/marketplace/buyer/buyer-profile/{buyer_id}
POST   /api/marketplace/buyer/add-product-requirement
GET    /api/marketplace/buyer/search-listings
GET    /api/marketplace/buyer/predicted-supply
POST   /api/marketplace/buyer/make-offer
GET    /api/marketplace/buyer/my-offers/{buyer_id}
GET    /api/marketplace/buyer/my-orders/{buyer_id}
POST   /api/marketplace/buyer/pay-deposit/{contract_id}
POST   /api/marketplace/buyer/confirm-receipt/{contract_id}
```

**User Flow:**
1. Business registers → KYB verification (24-48 hours)
2. Search listings by location, crop, quality, price
3. View AI supply forecast for upcoming 30/60 days
4. Make offer to farmer → Wait for response (72 hours)
5. Offer accepted → Pay 10% deposit via M-Pesa
6. Track delivery → Confirm receipt and quality
7. Quality OK → Final payment released to farmer
8. Quality issue → Open dispute for mediation

---

## Installation & Setup

### 1. Install Dependencies
```bash
cd frontend
npm install axios @react-native-async-storage/async-storage @react-native-picker/picker expo-image-picker expo-document-picker
```

### 2. Update Navigation
Add new screens to your navigation stack:

```javascript
// App.js or navigation/AppNavigator.js
import FarmerMarketplace from './src/screens/FarmerMarketplace';
import BuyerMarketplace from './src/screens/BuyerMarketplace';

// Add to stack navigator
<Stack.Screen name="FarmerMarketplace" component={FarmerMarketplace} />
<Stack.Screen name="BuyerMarketplace" component={BuyerMarketplace} />
```

### 3. Configure API Base URL
Update the API_BASE_URL in both files:

```javascript
// FarmerMarketplace.js
const API_BASE_URL = 'http://YOUR_BACKEND_IP:8000/api/marketplace/farmer';

// BuyerMarketplace.js
const API_BASE_URL = 'http://YOUR_BACKEND_IP:8000/api/marketplace/buyer';
```

### 4. Add Navigation Links
Update existing farmer/buyer screens to navigate to marketplace:

```javascript
// In your main farmer dashboard
<TouchableOpacity onPress={() => navigation.navigate('FarmerMarketplace')}>
  <Text>🛒 Marketplace - Sell Your Produce</Text>
</TouchableOpacity>

// In your main buyer/business dashboard
<TouchableOpacity onPress={() => navigation.navigate('BuyerMarketplace')}>
  <Text>🛒 Marketplace - Source Produce</Text>
</TouchableOpacity>
```

---

## Key Features Implementation

### 1. AI Market Insights Display
```javascript
// Renders AI recommendations with optimal selling windows
{marketInsights.insights.map((insight) => (
  <View>
    <Text>{insight.optimal_strategy.ai_recommendation}</Text>
    <Text>Best Window: {insight.optimal_strategy.optimal_sale_window.start_date}</Text>
    <Text>Expected Price: {insight.optimal_strategy.optimal_sale_window.max_price_kes}</Text>
    <Text>Top Option: {insight.optimal_strategy.market_recommendations[0].channel}</Text>
  </View>
))}
```

### 2. Location-Based Search with Distance
```javascript
// PostGIS calculates distance, frontend displays
{searchResults.map((listing) => (
  <View>
    <Text>{listing.crop} - {listing.distance_km.toFixed(1)} km away</Text>
    <Text>Transport: {listing.estimated_transport_cost_kes} KES</Text>
  </View>
))}
```

### 3. M-Pesa Payment Integration
```javascript
// Farmer receives deposit notification
const payDeposit = async (contractId) => {
  Alert.prompt('Enter M-Pesa phone number:', async (phone) => {
    const response = await axios.post(`/pay-deposit/${contractId}`, {
      buyer_id: buyerId,
      phone_number: phone
    });
    // STK Push sent to buyer's phone
  });
};
```

### 4. Supply Forecasting
```javascript
// AI predicts supply in 30/60 days
const viewPredictedSupply = async (crop) => {
  const response = await axios.get('/predicted-supply', {
    params: { buyer_id, crop, days_ahead: 30 }
  });
  
  Alert.alert(
    'Supply Forecast',
    `${response.data.ai_recommendation}\n
    Expected Supply: ${response.data.supply_forecast.total_supply_kg} kg\n
    Price Impact: ${response.data.supply_forecast.expected_price_impact_percent}%`
  );
};
```

### 5. Offer Response System
```javascript
// Farmer can Accept/Counter/Decline offers
const handleOfferResponse = async () => {
  const payload = {
    offer_id: selectedOffer.offer_id,
    action: offerAction, // 'accept', 'counter', or 'decline'
    farmer_notes: farmerNotes
  };
  
  if (offerAction === 'counter') {
    payload.counter_price_kes_per_kg = parseFloat(counterPrice);
    payload.counter_quantity_kg = parseFloat(counterQuantity);
  }
  
  const response = await axios.post('/respond-to-offer', payload);
  
  if (offerAction === 'accept') {
    // Contract created, buyer pays deposit
  } else if (offerAction === 'counter') {
    // Counter-offer sent, 48-hour expiry
  }
};
```

---

## Color Scheme & Status Indicators

### Status Colors
```javascript
// Listing statuses
active: '#4CAF50'      // Green
sold_out: '#FF9800'    // Orange
expired: '#9E9E9E'     // Gray
deleted: '#F44336'     // Red

// Offer statuses
pending: '#FF9800'     // Orange
accepted: '#4CAF50'    // Green
countered: '#2196F3'   // Blue
declined: '#F44336'    // Red

// Contract statuses
pending_deposit: '#FF9800'              // Orange
deposit_paid: '#2196F3'                 // Blue
in_transit: '#00BCD4'                   // Cyan
awaiting_buyer_confirmation: '#9C27B0'  // Purple
completed: '#4CAF50'                    // Green
quality_dispute: '#F44336'              // Red
```

---

## Testing Checklist

### Farmer Portal Testing
- [ ] Create listing with photos
- [ ] AI price suggestion appears
- [ ] View all listings with offer counts
- [ ] Receive offer notification
- [ ] Accept offer → Contract created
- [ ] Counter offer with new price
- [ ] Decline offer with reason
- [ ] View contracts with payment status
- [ ] Confirm delivery with photos
- [ ] View AI market insights

### Buyer Portal Testing
- [ ] Business registration submission
- [ ] Verification status check
- [ ] Search listings by location
- [ ] Filter by crop, quality, price
- [ ] View supply forecast
- [ ] Make offer to listing
- [ ] Receive counter-offer notification
- [ ] Pay deposit via M-Pesa
- [ ] View order tracking
- [ ] Confirm receipt (quality OK)
- [ ] Report quality issue (dispute)

---

## Performance Optimizations

### 1. Lazy Loading
```javascript
// Load data only when tab is active
useEffect(() => {
  if (farmerId && activeTab === 'listings') {
    loadListings();
  }
}, [farmerId, activeTab]);
```

### 2. Pull-to-Refresh
```javascript
<ScrollView
  refreshControl={
    <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
  }
>
  {/* Content */}
</ScrollView>
```

### 3. Caching with AsyncStorage
```javascript
// Cache farmer/buyer ID
await AsyncStorage.setItem('farmer_id', farmerId);
const cachedId = await AsyncStorage.getItem('farmer_id');
```

---

## Security Considerations

1. **API Key Storage**: Store API keys securely using `react-native-dotenv`
2. **Authentication**: Implement JWT token authentication for all API calls
3. **Input Validation**: Validate all user inputs before sending to backend
4. **Image Upload Limits**: Restrict to 5 images max per listing
5. **M-Pesa PINs**: Never store M-Pesa PINs in app (handled by Safaricom SDK)

---

## Next Steps for Full Integration

### 1. Database Setup
Create tables for marketplace data (see backend schema in `buyer_marketplace.py`)

### 2. M-Pesa Integration
Implement M-Pesa SDK callbacks:
```python
# backend/app/routes/payments.py
@router.post("/mpesa-callback")
async def mpesa_callback(request: Request):
    data = await request.json()
    # Update contract payment status
    persistence.update_contract_payment(
        contract_id=data['AccountReference'],
        status='completed'
    )
```

### 3. Push Notifications
Implement Firebase Cloud Messaging for:
- New offers received
- Offer responses (accepted/countered/declined)
- Deposit paid confirmation
- Delivery notifications
- Payment release confirmations

### 4. E-Logistics Integration
Add tracking screens for:
- Driver assignment
- Real-time GPS tracking
- Delivery ETA
- Proof of delivery (POD)

### 5. Rating System
Add post-transaction rating screens:
- Farmer rates buyer (payment speed, communication)
- Buyer rates farmer (quality, timeliness, honesty)

---

## Troubleshooting

### Common Issues

1. **"Buyer not verified" error**
   - Solution: Wait for business verification (24-48 hours) or contact admin

2. **M-Pesa payment fails**
   - Solution: Check phone number format (+254...), ensure sufficient balance

3. **Listings not appearing in search**
   - Solution: Check location permissions, increase search radius

4. **Images not uploading**
   - Solution: Grant camera/gallery permissions, reduce image size

5. **"Contract not found" error**
   - Solution: Refresh contracts list, check buyer/farmer ID matches

---

## Support & Contact

For technical issues:
- Backend API: Check `/api/docs` for Swagger documentation
- Frontend bugs: Check console logs for error details
- M-Pesa issues: Contact Safaricom support

---

## License & Credits

- **AgroShield Platform**: Farm-to-Business Digital Marketplace
- **AI Market Optimizer**: Powered by machine learning price prediction models
- **Payment Gateway**: M-Pesa Integration (Safaricom)
- **Geolocation**: PostGIS for location-based matching

---

**Last Updated:** October 24, 2025
**Version:** 1.0.0
