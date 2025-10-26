# AgroPulse Exchange - Decentralized Marketplace with Escrow

## Overview

The AgroPulse Exchange is a comprehensive trading platform similar to cryptocurrency exchanges (like OKX), designed specifically for agricultural products. It provides **AI-verified asset listings**, **secure escrow transactions**, **fraud prevention**, and **payment finality** through data-driven arbitration.

## Core Features

### 1. Data-Verified Asset Tokenization

Every asset listed on the exchange is "tokenized" (digitally represented) and linked directly to verifiable data from the AgroPulse AI system:

#### AI Verification Components

- **Harvest Health Score** (0-100%): Photo-based assessment of crop quality and maturity
- **Spoilage Risk Visualization**: Color-coded risk trend with predicted shelf life
- **Storage Condition Proof**: Real-time BLE sensor data (temperature, humidity) proving proper storage
- **GPS Geo-Tagged Traceability**: Verified farm location and field registration
- **Pest Management History**: Pest scan records and pest-free certification
- **Soil Health Score**: NPK status and fertility metrics
- **NDVI Satellite Analysis**: Vegetation health and growth patterns

#### Quality Grades

Assets are automatically classified into quality grades based on verification completeness:

1. **Grade A Premium** (90%+ verification)
   - Full AI verification with complete traceability
   - GPS, sensors, pest-free certification, harvest photos
   - Premium pricing in marketplace

2. **Grade B Standard** (60-89% verification)
   - Partial verification with basic quality controls
   - Standard market pricing

3. **Grade C Basic** (<60% verification)
   - Minimal verification, standard market grade
   - Entry-level pricing

### 2. Escrow and Smart Contract Payment Mechanism

#### Secure Fund Escrow

When a buyer agrees to purchase:
1. Payment (M-Pesa, Bank Transfer, Crypto, or Cash) is placed into a **secure escrow account**
2. Funds are **immediately locked** - buyer CANNOT unilaterally withdraw
3. Seller is protected from chargebacks and payment reversal fraud

#### AI-Triggered Release Conditions

Funds are released automatically based on verifiable milestones:

1. **Delivery Proof Submission**
   - Seller uploads time-stamped photos
   - QR code scan or digital signature
   - GPS verification of delivery location

2. **Buyer Acceptance Window**
   - Buyer has 48 hours to inspect goods
   - Can accept delivery (triggers immediate release)
   - Can raise dispute (freezes funds for arbitration)

3. **Automatic Release**
   - If acceptance window expires without dispute
   - Funds automatically released to seller
   - Transaction marked as completed

### 3. Data-Driven Dispute Resolution

When disputes arise, the system uses **unchangeable logged data** for arbitration:

#### Arbitration Data Sources

- **Pre-Harvest Health Score**: Condition at time of harvest
- **Storage Condition History**: Complete BLE sensor logs
- **Spoilage Risk Model**: Prediction at time of sale
- **GPS Verification**: Location data for all parties
- **Photo Evidence**: Time-stamped images from both parties

#### Third-Party Vetting

- Approved extension officers or quality inspectors review
- Similar to "Expert Triage System" for AI diagnoses
- Issue binding arbitration decisions:
  - Full refund (100% to buyer)
  - Partial refund (split based on fault)
  - Seller wins (0% refund, seller receives full amount)

### 4. Inventory and Market Linkages

#### Storage-to-Market Integration

- **AI Storage Intelligence Engine** feeds available inventory directly to marketplace
- Solves "Poor Market Linkages" problem
- Real-time stock updates from BLE sensors

#### Predictive Sales Modeling

- **Harvest Predictions** + **Spoilage Modeling**
- Proactive matching with bulk buyers (processors, distributors)
- **Forward Sales Contracts**: Secure guaranteed market access before harvest

---

## Technical Implementation

### Backend API Endpoints

#### Asset Management

```
POST   /api/exchange/assets/create
PUT    /api/exchange/assets/{asset_id}/publish
GET    /api/exchange/assets/active
GET    /api/exchange/assets/{asset_id}
```

#### Transactions

```
POST   /api/exchange/transactions/create
POST   /api/exchange/transactions/{transaction_id}/escrow-funds
POST   /api/exchange/transactions/{transaction_id}/submit-delivery-proof
POST   /api/exchange/transactions/{transaction_id}/buyer-accept
POST   /api/exchange/transactions/{transaction_id}/auto-release
```

#### Disputes

```
POST   /api/exchange/disputes/create
PUT    /api/exchange/disputes/{dispute_id}/assign-arbitrator
POST   /api/exchange/disputes/{dispute_id}/resolve
```

#### Inventory & Orders

```
POST   /api/exchange/inventory/sync-from-storage
GET    /api/exchange/inventory/farm/{farm_id}
POST   /api/exchange/orders/create-bulk-order
GET    /api/exchange/orders/bulk/{buyer_id}
```

#### Analytics

```
GET    /api/exchange/analytics/marketplace-stats
```

### Frontend Screens

1. **ExchangeMarketplaceScreen.js**
   - Browse active listings with filters
   - View marketplace statistics
   - Manage personal listings
   - View transaction history

2. **CreateAssetListingScreen.js**
   - Form-based asset creation
   - Real-time AI verification scoring
   - Quality grade assignment
   - GPS and sensor data integration

3. **AssetDetailsScreen.js**
   - Full asset information display
   - Complete AI verification data
   - Buy now with escrow
   - Raise dispute capability

### Services

**exchangeService.js**
- Complete API integration
- Local caching (5 minutes for market data)
- Quality grade helpers
- Payment method constants

**aiFarmIntelligenceService.js**
- GPS-based micro-climate profiling
- NDVI satellite analysis
- BLE sensor data fetching
- Soil analysis integration
- Pest management tracking

---

## User Workflows

### Farmer: Listing an Asset

1. Navigate to Exchange → "My Listings"
2. Click "Create Listing"
3. **System automatically loads AI verification:**
   - GPS location from expo-location
   - BLE sensor data from storage system
   - Soil analysis from backend
   - NDVI from satellite
   - Pest scan history
4. Fill in basic details:
   - Crop type
   - Quantity (kg)
   - Unit price (KES)
   - Listing title & description
   - Pickup location
   - Delivery options
5. **System calculates verification score**
6. **Quality grade assigned automatically**
7. Submit → Asset published to marketplace

### Buyer: Purchasing an Asset

1. Browse marketplace with filters:
   - Crop type
   - Quality grade
   - Price range
   - Location (within radius)
2. Click asset to view full details
3. Review AI verification data:
   - Harvest health
   - Storage conditions
   - Spoilage risk
   - GPS traceability
   - Pest history
4. Click "Buy Now"
5. Enter purchase details:
   - Quantity
   - Payment method (M-Pesa, Bank, Crypto)
   - Delivery method (Pickup, Delivery, 3rd Party)
   - Delivery address (if applicable)
6. **Escrow transaction created**
7. Proceed to payment → **Funds locked in escrow**
8. Wait for delivery

### Seller: Completing Delivery

1. Deliver goods to buyer
2. Submit delivery proof:
   - Upload photos of delivered goods
   - QR code scan (optional)
   - Digital signature (optional)
3. **48-hour acceptance window starts**
4. If buyer accepts → **Funds released immediately**
5. If window expires → **Automatic fund release**
6. If dispute raised → **Arbitration process**

### Buyer: Accepting Delivery

1. Receive goods
2. Inspect within 48 hours
3. Options:
   - **Accept**: Click "Accept Delivery" → Funds released to seller
   - **Dispute**: Raise dispute with evidence → Arbitration
   - **Do Nothing**: Window expires → Funds auto-released

### Dispute Resolution Process

1. **Dispute Raised**:
   - Party provides category (quality, quantity, condition, non-delivery)
   - Upload evidence photos
   - Describe issue

2. **System Pulls AI Data**:
   - Pre-harvest health score
   - Complete storage condition logs
   - Spoilage risk at time of sale
   - GPS verification data

3. **Arbitrator Assigned**:
   - Extension officer or quality inspector
   - Reviews data + physical inspection
   - Issues binding decision

4. **Resolution Options**:
   - Full refund to buyer (100%)
   - Partial refund (e.g., 50/50 split)
   - Seller wins (0% refund)

---

## Security Features

### Fraud Prevention

1. **No Unilateral Withdrawals**: Once funds are escrowed, buyer cannot withdraw without seller/arbitrator approval
2. **Data Immutability**: All AI verification data is logged and cannot be altered
3. **GPS Verification**: Location data proves physical presence
4. **Time-Stamped Evidence**: All photos and actions are time-stamped
5. **Third-Party Arbitration**: Neutral parties resolve disputes

### Payment Finality

1. **Automatic Release**: Reduces human error and delays
2. **Escrow Protection**: Seller guaranteed payment upon delivery
3. **Buyer Protection**: 48-hour inspection window
4. **Platform Fee**: 2% fee covers arbitration costs

---

## Data Flow

### Asset Listing Creation

```
1. Farmer initiates listing
2. System fetches GPS location (expo-location)
3. System fetches BLE sensor data (aiFarmIntelligenceService)
4. System fetches soil analysis (backend API)
5. System fetches NDVI data (satellite API)
6. System builds AI verification object (exchangeService.buildAIVerification)
7. System calculates confidence score
8. System assigns quality grade
9. Asset created in backend
10. Asset published to marketplace
```

### Transaction Flow

```
1. Buyer browses marketplace
2. Buyer selects asset
3. Buyer initiates purchase
4. System creates escrow transaction
5. Buyer makes payment → Funds locked
6. Seller delivers goods
7. Seller submits delivery proof
8. 48-hour acceptance window starts
9. Buyer accepts OR window expires
10. Funds released to seller
11. Platform fee deducted (2%)
12. Transaction completed
```

### Dispute Flow

```
1. Party raises dispute
2. System pulls AI data (immutable logs)
3. Arbitrator assigned
4. Arbitrator reviews data + physical inspection
5. Arbitrator issues binding decision
6. Funds distributed per decision
7. Dispute resolved
```

---

## Integration with AgroPulse Features

### 1. Storage BLE Monitoring
- Provides real-time sensor data for asset listings
- Proves proper storage conditions
- Builds buyer trust

### 2. Photo-Based Harvest Refinement
- Harvest health score
- Maturity level assessment
- Visual proof of quality

### 3. GPS Field Registration
- Verifiable farm origin
- Field-level traceability
- Location-based matching

### 4. Pest Management Scans
- Pest-free certification
- Scan history
- Integrated Pest Management (IPM) compliance

### 5. Soil Analysis
- Soil health score
- NPK status
- Fertility metrics

### 6. NDVI Satellite Analysis
- Vegetation health
- Growth patterns
- Field condition verification

### 7. Harvest Predictions
- Forward sales contracts
- Pre-harvest buyer matching
- Guaranteed market access

### 8. Spoilage Modeling
- Shelf life predictions
- Urgent sales prioritization
- Storage duration optimization

---

## Configuration

### Backend Setup

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install fastapi pydantic
   ```

2. **Import Exchange Router**:
   ```python
   # backend/app/main.py
   from app.routes import exchange
   app.include_router(exchange.router, prefix='/api/exchange', tags=['Exchange'])
   ```

3. **Run Backend**:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. **Install Dependencies**:
   ```bash
   cd frontend/agroshield-app
   npm install @react-native-async-storage/async-storage
   npm install expo-location
   ```

2. **Import Screens in Navigator**:
   ```javascript
   // src/navigation/RootNavigator.js
   import ExchangeMarketplaceScreen from '../screens/ExchangeMarketplaceScreen';
   import CreateAssetListingScreen from '../screens/CreateAssetListingScreen';
   import AssetDetailsScreen from '../screens/AssetDetailsScreen';
   ```

3. **Add to Dashboard**:
   ```javascript
   <ActionButton
     icon="swap-horizontal"
     label="Exchange"
     color="#4CAF50"
     onPress={() => navigation.navigate('ExchangeMarketplace', {
       farmId: user?.farmId,
       userId: user?.id,
       userType: 'farmer'
     })}
   />
   ```

---

## Future Enhancements

### Phase 1 (Current)
- ✅ AI-verified asset listings
- ✅ Escrow transactions
- ✅ Data-driven arbitration
- ✅ GPS traceability

### Phase 2
- [ ] Blockchain integration for immutable records
- [ ] Smart contracts on Ethereum/Polygon
- [ ] Cryptocurrency payment support (USDT, DAI)
- [ ] NFT-based asset certificates

### Phase 3
- [ ] Automated quality inspection (computer vision)
- [ ] IoT integration (real-time sensor updates)
- [ ] AI price prediction models
- [ ] Cross-border trading (export/import)

### Phase 4
- [ ] Futures contracts
- [ ] Options trading
- [ ] Crop insurance integration
- [ ] Lending/credit against assets

---

## Support & Documentation

For more information:
- API Documentation: `http://localhost:8000/docs`
- Frontend Docs: `frontend/agroshield-app/README.md`
- Backend Docs: `backend/README.md`

---

## License

Copyright © 2025 AgroPulse AI. All rights reserved.
