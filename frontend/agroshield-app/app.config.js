export default {
  expo: {
    name: "AgroShield",
    slug: "agroshield-app",
    version: "1.0.0",
    orientation: "portrait",
    icon: "./assets/icon.png",
    userInterfaceStyle: "light",
    splash: {
      image: "./assets/splash.png",
      resizeMode: "contain",
      backgroundColor: "#ffffff"
    },
    assetBundlePatterns: [
      "**/*"
    ],
    ios: {
      supportsTablet: true
    },
    android: {
      adaptiveIcon: {
        foregroundImage: "./assets/adaptive-icon.png",
        backgroundColor: "#ffffff"
      }
    },
    web: {
      favicon: "./assets/favicon.png"
    },
    extra: {
      supabaseUrl: process.env.SUPABASE_URL || "https://rwspbvgmmxabglptljkg.supabase.co",
      supabaseAnonKey: process.env.SUPABASE_ANON_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ3c3BidmdtbXhhYmdscHRsamtnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzODg1NDQsImV4cCI6MjA3Njk2NDU0NH0.rlQRK_u6DT8AH0_786T1w9SfxKLIGFQwkOylNMCLsV0",
      apiBaseUrl: process.env.API_BASE_URL || "http://localhost:8000"
    }
  }
};
