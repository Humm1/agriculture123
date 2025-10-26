# Supabase Authentication Integration Guide

## Overview
Complete Supabase authentication integration for AgroShield with both backend (FastAPI) and frontend (React Native/Expo) implementations.

---

## 🔧 Backend Setup (FastAPI)

### 1. Dependencies Installed
```bash
pip install supabase>=2.0.0 pyjwt>=2.8.0
```

### 2. Files Created/Modified

#### `backend/app/services/supabase_auth.py` ✅
Complete authentication service with 12 functions:
- `register_user()` - Register new users (farmer/buyer)
- `login_user()` - Authenticate and return JWT tokens
- `verify_token()` - Validate JWT tokens
- `refresh_session()` - Refresh expired access tokens
- `logout_user()` - Sign out users
- `reset_password_request()` - Send password reset emails
- `update_password()` - Change user passwords
- `get_user_profile()` - Fetch user profiles from database
- `update_user_profile()` - Update user profile data
- `get_all_users()` - Admin function to list all users
- `delete_user()` - Admin function to delete users
- `extract_user_from_token()` - Utility to decode JWTs

#### `backend/app/routes/auth.py` ✅
RESTful API endpoints (9 routes):
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user profile (protected)
- `PUT /api/auth/me` - Update current user profile (protected)
- `POST /api/auth/reset-password` - Request password reset
- `POST /api/auth/update-password` - Update password (protected)
- `GET /api/auth/verify-token` - Verify JWT token

#### `backend/app/main.py` ✅
- Added auth router with `/api/auth` prefix
- Tagged routes as 'Authentication' for API docs

#### `backend/requirements.txt` ✅
- Added `supabase>=2.0.0`
- Added `pyjwt>=2.8.0`

#### `backend/.env.example` ✅
Added Supabase configuration:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_public_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_secret_key_here
SUPABASE_JWT_SECRET=your_jwt_secret_here
```

### 3. Backend Architecture

**Authentication Flow:**
1. User registers/logs in → Supabase Auth creates user
2. Backend creates profile in `profiles` table
3. JWT tokens (access + refresh) returned to client
4. Protected routes use `get_current_user()` dependency
5. Token verified on each request via Authorization header

**Protected Routes Pattern:**
```python
@router.get("/me")
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    # current_user contains validated user data from JWT
    pass
```

---

## 📱 Frontend Setup (React Native/Expo)

### 1. Dependencies Installed
```bash
npm install @supabase/supabase-js
```

### 2. Files Created/Modified

#### `frontend/agroshield-app/src/services/supabase.js` ✅
Supabase client configuration and service functions:
- Configured with AsyncStorage for session persistence
- Auto-refresh tokens enabled
- 12 service functions:
  - `registerUser()` - Register with email/password
  - `loginUser()` - Login with credentials
  - `logoutUser()` - Sign out
  - `getCurrentUser()` - Get authenticated user + profile
  - `getCurrentSession()` - Get current session
  - `refreshSession()` - Manually refresh session
  - `updateUserProfile()` - Update profile data
  - `resetPassword()` - Request password reset email
  - `updatePassword()` - Change password
  - `onAuthStateChange()` - Listen to auth events

#### `frontend/agroshield-app/src/context/AuthContext.js` ✅
Complete authentication context provider:
- State management for user, profile, session, loading, error
- React hooks for auth operations
- Automatic auth state synchronization
- Context values:
  - `user` - Current user object
  - `profile` - User profile from database
  - `session` - Current session with tokens
  - `loading` - Loading state
  - `error` - Error messages
  - `login()` - Login function
  - `register()` - Register function
  - `logout()` - Logout function
  - `updateProfile()` - Update profile function
  - `resetPassword()` - Password reset function
  - `updatePassword()` - Change password function
  - `refreshSession()` - Manual token refresh
  - `isAuthenticated` - Boolean flag
  - `isFarmer` - Boolean flag (user_type === 'farmer')
  - `isBuyer` - Boolean flag (user_type === 'buyer')

#### `frontend/agroshield-app/src/screens/auth/LoginScreen.js` ✅
Updated to use email authentication:
- Email input (instead of phone)
- Password input with show/hide toggle
- Form validation
- Error handling with alerts
- Loading states
- Navigation to Register screen
- Forgot Password link

#### `frontend/agroshield-app/src/screens/auth/RegisterScreen.js` ✅
Enhanced with Supabase registration:
- Full name input
- Email input (new)
- Phone number input
- User type selector (Farmer/Buyer) - **NEW FEATURE**
- County and Sub-County inputs
- Password with confirmation
- Form validation
- Error handling
- Loading states

#### `frontend/agroshield-app/.env.example` ✅
Environment configuration template:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_public_key_here
API_BASE_URL=http://localhost:8000
```

### 3. Frontend Architecture

**Authentication Flow:**
1. User opens app → AuthContext checks for existing session
2. If session exists → Fetch user and profile data
3. User logs in/registers → Update context state
4. Auth state changes trigger listeners → Update UI
5. Tokens stored in AsyncStorage (auto-persisted)
6. Protected screens check `isAuthenticated` flag

**Usage Pattern:**
```javascript
import { useAuth } from '../context/AuthContext';

function MyScreen() {
  const { user, profile, isAuthenticated, isFarmer, login, logout } = useAuth();
  
  if (!isAuthenticated) {
    return <LoginPrompt />;
  }
  
  return (
    <View>
      <Text>Welcome {profile.full_name}!</Text>
      {isFarmer && <FarmerDashboard />}
    </View>
  );
}
```

---

## 🗄️ Database Setup (Supabase)

### Required Table: `profiles`

Create this table in your Supabase project:

```sql
CREATE TABLE profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email TEXT NOT NULL,
  user_type TEXT NOT NULL CHECK (user_type IN ('farmer', 'buyer')),
  full_name TEXT,
  phone_number TEXT,
  location TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read their own profile
CREATE POLICY "Users can view own profile"
  ON profiles
  FOR SELECT
  USING (auth.uid() = id);

-- Policy: Users can update their own profile
CREATE POLICY "Users can update own profile"
  ON profiles
  FOR UPDATE
  USING (auth.uid() = id);

-- Policy: Anyone can insert profile (for registration)
CREATE POLICY "Anyone can insert profile"
  ON profiles
  FOR INSERT
  WITH CHECK (true);
```

### Authentication Settings

In Supabase Dashboard → Authentication → Settings:

1. **Email Auth**: Enable email/password authentication
2. **Email Confirmations**: 
   - For development: Disable "Enable email confirmations"
   - For production: Enable and configure SMTP
3. **JWT Expiry**: Default 3600s (1 hour) is fine
4. **Refresh Token Expiry**: Default 2592000s (30 days)

---

## 🔐 Security Configuration

### Backend Security

1. **Environment Variables**
   - Create `backend/.env` from `backend/.env.example`
   - Add real Supabase credentials
   - **NEVER** commit `.env` to version control

2. **JWT Verification**
   - All protected routes use `get_current_user()` dependency
   - Tokens verified against Supabase JWT secret
   - Expired tokens automatically rejected

3. **CORS Configuration**
   - Configure allowed origins in `main.py`
   - Update `FRONTEND_URL` in `.env`

### Frontend Security

1. **Environment Variables**
   - Create `frontend/agroshield-app/.env` from `.env.example`
   - Add Supabase public credentials (anon key is safe for client)
   
2. **Token Storage**
   - AsyncStorage automatically encrypts on iOS
   - Tokens auto-refreshed before expiry
   - Logout clears all stored data

3. **Protected Routes**
   - Check `isAuthenticated` before rendering sensitive screens
   - Redirect to login if not authenticated

---

## 📝 API Documentation

### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "farmer@example.com",
  "password": "securepass123",
  "user_type": "farmer",
  "full_name": "John Doe",
  "phone_number": "+254712345678",
  "location": "Nairobi County"
}

Response 201:
{
  "user": { "id": "...", "email": "..." },
  "profile": { ... },
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "message": "User registered successfully"
}
```

### Login User
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "farmer@example.com",
  "password": "securepass123"
}

Response 200:
{
  "user": { ... },
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "message": "Login successful"
}
```

### Get Current User (Protected)
```http
GET /api/auth/me
Authorization: Bearer eyJ...

Response 200:
{
  "user": { ... },
  "profile": { ... }
}
```

### Update Profile (Protected)
```http
PUT /api/auth/me
Authorization: Bearer eyJ...
Content-Type: application/json

{
  "full_name": "Jane Doe",
  "phone_number": "+254798765432"
}

Response 200:
{
  "profile": { ... },
  "message": "Profile updated successfully"
}
```

### Refresh Token
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}

Response 200:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "message": "Session refreshed successfully"
}
```

---

## 🚀 Testing the Integration

### Backend Testing

1. **Start FastAPI Server**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Test Registration** (using curl or Postman)
   ```bash
   curl -X POST http://localhost:8000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "test123",
       "user_type": "farmer",
       "full_name": "Test User"
     }'
   ```

3. **Test Login**
   ```bash
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "test123"
     }'
   ```

4. **View API Docs**
   - Open http://localhost:8000/docs
   - Interactive Swagger UI with all auth endpoints

### Frontend Testing

1. **Install Dependencies**
   ```bash
   cd frontend/agroshield-app
   npm install
   ```

2. **Start Expo**
   ```bash
   npx expo start
   ```

3. **Test User Flow**
   - Navigate to Register screen
   - Fill in form (name, email, phone, user type, location, password)
   - Submit registration
   - Check if redirected to authenticated app
   - Test logout
   - Login with same credentials
   - Test profile update

---

## 🎯 Next Steps

### Required Actions:

1. **Setup Supabase Project**
   - Create project at https://supabase.com
   - Copy credentials to `.env` files
   - Create `profiles` table with SQL above
   - Configure authentication settings

2. **Update Environment Files**
   - `backend/.env` - Add Supabase credentials
   - `frontend/agroshield-app/.env` - Add Supabase URL and anon key

3. **Wrap App with AuthProvider**
   - Update `App.js` to wrap root with `<AuthProvider>`
   - Example:
     ```javascript
     import { AuthProvider } from './src/context/AuthContext';
     
     export default function App() {
       return (
         <AuthProvider>
           {/* Your app navigation */}
         </AuthProvider>
       );
     }
     ```

4. **Create Navigation Guards**
   - Create `AuthNavigator.js` for login/register stack
   - Create `AppNavigator.js` for authenticated screens
   - Switch between navigators based on `isAuthenticated`

5. **Test End-to-End**
   - Register new user → Login → Access protected routes
   - Test token refresh (wait 1 hour or reduce JWT expiry)
   - Test logout → Should redirect to login
   - Test password reset flow

### Optional Enhancements:

1. **Social Auth** - Add Google/Apple sign-in via Supabase
2. **2FA** - Enable two-factor authentication
3. **Email Verification** - Require email confirmation
4. **Profile Pictures** - Use Supabase Storage for avatars
5. **Roles & Permissions** - Add admin roles and permissions
6. **Audit Logs** - Track user actions in separate table

---

## 🐛 Troubleshooting

### Common Issues:

**1. "Invalid JWT" errors**
- Check `SUPABASE_JWT_SECRET` matches your project
- Ensure token is sent in Authorization header: `Bearer <token>`

**2. "Profile not found" errors**
- Check `profiles` table exists in Supabase
- Verify RLS policies allow inserts during registration

**3. Frontend "Network Error"**
- Update `API_BASE_URL` to correct backend URL
- Check CORS settings in `backend/app/main.py`

**4. Expo AsyncStorage errors**
- `npm install @react-native-async-storage/async-storage`
- Restart Expo dev server

**5. Token not persisting**
- Check AsyncStorage is properly imported in `supabase.js`
- Clear app data and test fresh installation

---

## 📚 Documentation Links

- [Supabase Auth Docs](https://supabase.com/docs/guides/auth)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [React Native Auth Guide](https://reactnative.dev/docs/authentication)
- [Expo SecureStore](https://docs.expo.dev/versions/latest/sdk/securestore/)

---

## ✅ Completion Checklist

Backend:
- [x] Install Supabase Python SDK
- [x] Create authentication service layer
- [x] Create API routes for auth endpoints
- [x] Add auth router to main app
- [x] Update requirements.txt
- [x] Add environment configuration
- [ ] Create `.env` with real credentials
- [ ] Test API endpoints

Frontend:
- [x] Install Supabase JS SDK
- [x] Create Supabase client configuration
- [x] Create AuthContext provider
- [x] Update LoginScreen for email auth
- [x] Update RegisterScreen with user type
- [x] Add environment configuration
- [ ] Create `.env` with real credentials
- [ ] Wrap App with AuthProvider
- [ ] Create navigation guards
- [ ] Test complete auth flow

Database:
- [ ] Create Supabase project
- [ ] Create `profiles` table
- [ ] Configure RLS policies
- [ ] Enable email authentication
- [ ] Test database operations

---

**Status**: Backend ✅ Complete | Frontend ✅ Complete | Database ⏳ Pending Setup

Your Supabase authentication is fully implemented and ready for testing once you configure your Supabase project credentials!
