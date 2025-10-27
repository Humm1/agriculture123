import { createClient } from '@supabase/supabase-js';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { SUPABASE_URL, SUPABASE_ANON_KEY } from '../config/env';

// Log configuration for debugging (remove in production)
console.log('🔧 Supabase Configuration:');
console.log('URL:', SUPABASE_URL);
console.log('Key:', SUPABASE_ANON_KEY ? `${SUPABASE_ANON_KEY.substring(0, 20)}...` : 'NOT SET');

// Create Supabase client with AsyncStorage for session persistence
export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    storage: AsyncStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
});

/**
 * Authentication service functions
 */

// Register a new user
export const registerUser = async (email, password, userType, profileData = {}) => {
  try {
    console.log('📝 Starting registration for:', email, 'as', userType);
    console.log('📝 Profile data:', profileData);
    
    // Sign up the user
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: undefined, // Disable email confirmation redirect
        data: {
          user_type: userType, // 'farmer' or 'buyer'
          full_name: profileData.full_name || '',
          phone_number: profileData.phone_number || '',
          ...profileData,
        },
      },
    });

    if (error) {
      console.error('❌ Supabase signup error:', error);
      throw error;
    }

    console.log('✅ Signup response:', {
      user: data.user?.id,
      session: data.session ? 'Session created' : 'No session (email confirmation required)',
      identities: data.user?.identities?.length || 0
    });

    // Check if user already exists
    if (data.user && data.user.identities && data.user.identities.length === 0) {
      console.error('❌ User already registered with this email');
      return { 
        user: null, 
        session: null, 
        error: 'This email is already registered. Please try logging in instead.' 
      };
    }

    // Create user profile in profiles table
    if (data.user) {
      console.log('📊 Creating profile in profiles table...');
      console.log('📊 User ID:', data.user.id);
      
      const profileInsert = {
        id: data.user.id,
        email: email,
        user_type: userType,
        full_name: profileData.full_name || '',
        phone_number: profileData.phone_number || '',
        location: profileData.location || '',
        county: profileData.county || '',
        subcounty: profileData.subcounty || '',
        village: profileData.village || '',
        latitude: profileData.latitude || null,
        longitude: profileData.longitude || null,
        created_at: new Date().toISOString(),
      };
      
      console.log('📊 Profile insert data:', profileInsert);
      
      const { data: profileData, error: profileError } = await supabase
        .from('profiles')
        .insert([profileInsert])
        .select();

      if (profileError) {
        console.error('❌ Profile creation error:', profileError);
        console.error('❌ Error details:', {
          message: profileError.message,
          details: profileError.details,
          hint: profileError.hint,
          code: profileError.code
        });
        // Don't throw here, user is still registered in auth
      } else {
        console.log('✅ Profile created successfully:', profileData);
      }
    }

    return { user: data.user, session: data.session, error: null };
  } catch (error) {
    console.error('❌ Registration error:', error);
    return { user: null, session: null, error: error.message };
  }
};

// Login user
export const loginUser = async (email, password) => {
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) throw error;

    return { user: data.user, session: data.session, error: null };
  } catch (error) {
    console.error('Login error:', error);
    return { user: null, session: null, error: error.message };
  }
};

// Logout user
export const logoutUser = async () => {
  try {
    console.log('🚪 Logging out user...');
    
    // Sign out from Supabase (this will clear session from storage)
    const { error } = await supabase.auth.signOut();
    
    if (error) {
      console.error('❌ Supabase signOut error:', error);
      // Even if Supabase returns an error, we should still clear local data
    } else {
      console.log('✅ Supabase signOut successful');
    }
    
    // Force clear any remaining session data from AsyncStorage
    try {
      await AsyncStorage.removeItem('supabase.auth.token');
      console.log('✅ Cleared auth token from AsyncStorage');
    } catch (storageError) {
      console.warn('⚠️ Could not clear AsyncStorage:', storageError);
    }
    
    return { error: null };
  } catch (error) {
    console.error('❌ Logout error:', error);
    // Return success anyway to allow client-side cleanup
    return { error: null };
  }
};

// Get current user
export const getCurrentUser = async () => {
  try {
    const { data: { user }, error } = await supabase.auth.getUser();
    
    if (error) throw error;
    
    if (!user) {
      console.log('❌ No user found in session');
      return { user: null, profile: null, error: null };
    }

    console.log('👤 Fetching profile for user:', user.id);

    // Fetch user profile
    const { data: profile, error: profileError } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', user.id)
      .single();

    if (profileError) {
      if (profileError.code === 'PGRST116') {
        console.warn('⚠️ Profile not found in database for user:', user.id);
      } else {
        console.error('❌ Profile fetch error:', profileError);
      }
    } else {
      console.log('✅ Profile fetched:', {
        id: profile.id,
        email: profile.email,
        user_type: profile.user_type,
        full_name: profile.full_name
      });
    }

    return { user, profile, error: null };
  } catch (error) {
    console.error('❌ Get current user error:', error);
    return { user: null, profile: null, error: error.message };
  }
};

// Get current session
export const getCurrentSession = async () => {
  try {
    const { data: { session }, error } = await supabase.auth.getSession();
    if (error) throw error;
    return { session, error: null };
  } catch (error) {
    console.error('Get session error:', error);
    return { session: null, error: error.message };
  }
};

// Refresh session
export const refreshSession = async () => {
  try {
    const { data: { session }, error } = await supabase.auth.refreshSession();
    if (error) throw error;
    return { session, error: null };
  } catch (error) {
    console.error('Refresh session error:', error);
    return { session: null, error: error.message };
  }
};

// Update user profile
export const updateUserProfile = async (userId, updates) => {
  try {
    const { data, error } = await supabase
      .from('profiles')
      .update(updates)
      .eq('id', userId)
      .select()
      .single();

    if (error) throw error;

    return { profile: data, error: null };
  } catch (error) {
    console.error('Update profile error:', error);
    return { profile: null, error: error.message };
  }
};

// Request password reset
export const resetPassword = async (email) => {
  try {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: 'agropulseai://reset-password',
    });

    if (error) throw error;

    return { error: null };
  } catch (error) {
    console.error('Password reset error:', error);
    return { error: error.message };
  }
};

// Update password
export const updatePassword = async (newPassword) => {
  try {
    const { error } = await supabase.auth.updateUser({
      password: newPassword,
    });

    if (error) throw error;

    return { error: null };
  } catch (error) {
    console.error('Update password error:', error);
    return { error: error.message };
  }
};

// Listen to auth state changes
export const onAuthStateChange = (callback) => {
  return supabase.auth.onAuthStateChange((event, session) => {
    callback(event, session);
  });
};

export default supabase;
