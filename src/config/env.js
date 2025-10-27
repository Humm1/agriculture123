/**
 * Environment Configuration
 * This file properly loads environment variables for all platforms (web, iOS, Android)
 */

// For Expo, we need to use the expo-constants package to access environment variables
// However, for web builds, we need to define them directly or use process.env with proper webpack config

// Hardcoded values from .env file (for web compatibility)
// TODO: Move these to a secure backend configuration service in production
const ENV_CONFIG = {
  SUPABASE_URL: 'https://rwspbvgmmxabglptljkg.supabase.co',
  SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ3c3BidmdtbXhhYmdscHRsamtnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzODg1NDQsImV4cCI6MjA3Njk2NDU0NH0.rlQRK_u6DT8AH0_786T1w9SfxKLIGFQwkOylNMCLsV0',
  API_BASE_URL: 'https://urchin-app-86rjy.ondigitalocean.app/api',
};

// Export configuration
export const getEnvVar = (key) => {
  // Try to get from process.env first (native apps)
  if (process.env[key]) {
    return process.env[key];
  }
  
  // Fallback to hardcoded config (web)
  return ENV_CONFIG[key];
};

export const SUPABASE_URL = getEnvVar('SUPABASE_URL');
export const SUPABASE_ANON_KEY = getEnvVar('SUPABASE_ANON_KEY');
export const API_BASE_URL = getEnvVar('API_BASE_URL');

// Validate that required environment variables are set
if (!SUPABASE_URL || SUPABASE_URL.includes('your-project-id')) {
  console.warn('⚠️ SUPABASE_URL is not properly configured');
}

if (!SUPABASE_ANON_KEY || SUPABASE_ANON_KEY.includes('your_supabase')) {
  console.warn('⚠️ SUPABASE_ANON_KEY is not properly configured');
}

export default {
  SUPABASE_URL,
  SUPABASE_ANON_KEY,
  API_BASE_URL,
};
