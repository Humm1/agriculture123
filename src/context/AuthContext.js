import React, { createContext, useState, useEffect, useContext } from 'react';
import { 
  getCurrentUser, 
  getCurrentSession,
  loginUser as authLogin, 
  registerUser as authRegister, 
  logoutUser as authLogout,
  onAuthStateChange,
  updateUserProfile as authUpdateProfile,
  resetPassword as authResetPassword,
  updatePassword as authUpdatePassword,
  refreshSession as authRefreshSession,
} from '../services/supabase';
import locationService from '../services/locationService';
import { locationAPI } from '../services/api';

// Create Auth Context
const AuthContext = createContext({
  user: null,
  profile: null,
  session: null,
  loading: true,
  error: null,
  login: async () => {},
  register: async () => {},
  logout: async () => {},
  updateProfile: async () => {},
  resetPassword: async () => {},
  updatePassword: async () => {},
  refreshSession: async () => {},
});

// Export context as named export too
export { AuthContext };

// Auth Provider Component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize authentication state
  useEffect(() => {
    const initAuth = async () => {
      try {
        setLoading(true);
        
        // Check if Supabase is properly configured
        const supabaseUrl = process.env.SUPABASE_URL || 'https://your-project-id.supabase.co';
        if (supabaseUrl.includes('your-project-id')) {
          console.warn('Supabase not configured - using offline mode');
          setLoading(false);
          return;
        }
        
        // Get current session
        const { session: currentSession } = await getCurrentSession();
        setSession(currentSession);

        // Get current user if session exists
        if (currentSession) {
          const { user: currentUser, profile: currentProfile } = await getCurrentUser();
          setUser(currentUser);
          setProfile(currentProfile);
        }
      } catch (err) {
        console.error('Auth initialization error:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    initAuth();

    // Listen for auth state changes
    const { data: authListener } = onAuthStateChange(async (event, newSession) => {
      console.log('🔔 Auth event:', event);
      console.log('🔔 Session:', newSession ? 'Active' : 'None');
      
      setSession(newSession);

      if (newSession) {
        // User signed in or session refreshed
        const { user: newUser, profile: newProfile } = await getCurrentUser();
        console.log('👤 User loaded:', newUser?.id);
        console.log('📋 Profile loaded:', {
          id: newProfile?.id,
          email: newProfile?.email,
          user_type: newProfile?.user_type,
          full_name: newProfile?.full_name
        });
        setUser(newUser);
        setProfile(newProfile);
      } else {
        // User signed out
        console.log('👋 User signed out');
        setUser(null);
        setProfile(null);
      }

      setLoading(false);
    });

    // Cleanup listener on unmount
    return () => {
      authListener?.subscription?.unsubscribe();
    };
  }, []);

  // Login function
  const login = async (email, password) => {
    try {
      setLoading(true);
      setError(null);

      const { user: loggedInUser, session: newSession, error: loginError } = await authLogin(email, password);

      if (loginError) {
        setError(loginError);
        return { success: false, error: loginError };
      }

      setUser(loggedInUser);
      setSession(newSession);

      // Fetch profile
      const { user: currentUser, profile: currentProfile } = await getCurrentUser();
      setProfile(currentProfile);

      // Automatically track location on login (for farmers)
      if (currentProfile?.user_type === 'farmer') {
        try {
          await initializeLocationTracking(loggedInUser.id);
        } catch (locError) {
          console.warn('Location tracking error (non-blocking):', locError);
          // Don't fail login if location tracking fails
        }
      }

      return { success: true, user: loggedInUser, profile: currentProfile };
    } catch (err) {
      console.error('Login error:', err);
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  // Initialize location tracking
  const initializeLocationTracking = async (userId) => {
    try {
      // Request permissions
      const hasPermission = await locationService.hasPermissions();
      if (!hasPermission) {
        const permissions = await locationService.requestPermissions();
        if (!permissions.foreground) {
          console.log('Location permission not granted');
          return;
        }
      }

      // Get current location
      const location = await locationService.getCurrentLocation();

      // Update location on server
      if (location && userId) {
        await locationAPI.updateLocation(userId, {
          latitude: location.latitude,
          longitude: location.longitude,
          accuracy: location.accuracy,
          altitude: location.altitude,
        });
        
        console.log('Location updated on login:', location);
      }

      // Start continuous tracking
      await locationService.startWatching(async (newLocation) => {
        try {
          await locationAPI.updateLocation(userId, {
            latitude: newLocation.latitude,
            longitude: newLocation.longitude,
            accuracy: newLocation.accuracy,
            altitude: newLocation.altitude,
          });
        } catch (error) {
          console.error('Location update error:', error);
        }
      });

    } catch (error) {
      console.error('Initialize location tracking error:', error);
      throw error;
    }
  };

  // Register function
  const register = async (email, password, userType, profileData = {}) => {
    try {
      setLoading(true);
      setError(null);

      const { user: newUser, session: newSession, error: registerError } = await authRegister(
        email, 
        password, 
        userType, 
        profileData
      );

      if (registerError) {
        setError(registerError);
        return { success: false, error: registerError };
      }

      // DON'T automatically log the user in after registration
      // Let them go to the login screen instead
      // This ensures proper flow: Register → Login → Dashboard
      
      // Optional: Log out immediately if Supabase auto-logged them in
      if (newSession) {
        await authLogout();
      }

      return { success: true, user: newUser, profile: null };
    } catch (err) {
      console.error('Registration error:', err);
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = async () => {
    try {
      console.log('🚪 Starting logout process...');
      setLoading(true);
      setError(null);

      // Stop location tracking
      try {
        locationService.stopWatching();
        await locationService.clearLocation();
        console.log('✅ Location tracking stopped');
      } catch (locError) {
        console.warn('⚠️ Location cleanup error (non-blocking):', locError);
      }

      // Sign out from Supabase
      const { error: logoutError } = await authLogout();

      if (logoutError) {
        console.error('❌ Logout error:', logoutError);
        setError(logoutError);
        // Don't return error - still clear local state
      }

      // Clear local state
      console.log('🧹 Clearing local state...');
      setUser(null);
      setProfile(null);
      setSession(null);
      
      console.log('✅ Logout successful');
      return { success: true };
    } catch (err) {
      console.error('❌ Logout error:', err);
      setError(err.message);
      
      // Even if there's an error, clear local state
      setUser(null);
      setProfile(null);
      setSession(null);
      
      // Return success to allow navigation to login screen
      return { success: true };
    } finally {
      setLoading(false);
    }
  };

  // Update profile function
  const updateProfile = async (updates) => {
    try {
      setLoading(true);
      setError(null);

      if (!user) {
        return { success: false, error: 'No user logged in' };
      }

      const { profile: updatedProfile, error: updateError } = await authUpdateProfile(user.id, updates);

      if (updateError) {
        setError(updateError);
        return { success: false, error: updateError };
      }

      setProfile(updatedProfile);

      return { success: true, profile: updatedProfile };
    } catch (err) {
      console.error('Update profile error:', err);
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  // Reset password function
  const resetPassword = async (email) => {
    try {
      setLoading(true);
      setError(null);

      const { error: resetError } = await authResetPassword(email);

      if (resetError) {
        setError(resetError);
        return { success: false, error: resetError };
      }

      return { success: true };
    } catch (err) {
      console.error('Password reset error:', err);
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  // Update password function
  const updatePassword = async (newPassword) => {
    try {
      setLoading(true);
      setError(null);

      const { error: updateError } = await authUpdatePassword(newPassword);

      if (updateError) {
        setError(updateError);
        return { success: false, error: updateError };
      }

      return { success: true };
    } catch (err) {
      console.error('Password update error:', err);
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  // Refresh session function
  const refreshSession = async () => {
    try {
      const { session: newSession, error: refreshError } = await authRefreshSession();

      if (refreshError) {
        setError(refreshError);
        return { success: false, error: refreshError };
      }

      setSession(newSession);

      return { success: true, session: newSession };
    } catch (err) {
      console.error('Session refresh error:', err);
      setError(err.message);
      return { success: false, error: err.message };
    }
  };

  // Check authentication status (for page reloads)
  const checkAuth = async () => {
    try {
      setLoading(true);
      
      // Get current session from storage
      const { session: currentSession } = await getCurrentSession();
      
      if (currentSession) {
        // Session exists, get user and profile
        const { user: currentUser, profile: currentProfile } = await getCurrentUser();
        setUser(currentUser);
        setProfile(currentProfile);
        setSession(currentSession);
        console.log('✅ Session restored from storage');
      } else {
        // No session found
        console.log('❌ No session found');
        setUser(null);
        setProfile(null);
        setSession(null);
      }
    } catch (err) {
      console.error('Check auth error:', err);
      setError(err.message);
      setUser(null);
      setProfile(null);
      setSession(null);
    } finally {
      setLoading(false);
    }
  };

  // Context value
  const value = {
    user,
    profile,
    session,
    loading,
    error,
    login,
    register,
    logout,
    updateProfile,
    resetPassword,
    updatePassword,
    refreshSession,
    checkAuth,
    isAuthenticated: !!user,
    isLoading: loading,
    isFarmer: profile?.user_type === 'farmer',
    isBuyer: profile?.user_type === 'buyer',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};

export default AuthContext;
