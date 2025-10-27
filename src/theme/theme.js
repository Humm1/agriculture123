import { DefaultTheme } from 'react-native-paper';

export const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    // Primary Agricultural Palette
    primary: '#1B5E20',        // Deep Forest Green - Professional
    primaryLight: '#4CAF50',   // Vibrant Green - Growth
    primaryDark: '#0D2818',    // Dark Forest - Depth
    
    // Secondary Earth Tones
    secondary: '#8BC34A',      // Fresh Crop Green
    secondaryLight: '#DCEDC8', // Light Leaf Green
    secondaryDark: '#689F38',  // Mature Plant Green
    
    // Accent Colors - Agricultural Elements
    accent: '#FF8F00',         // Golden Wheat
    accentLight: '#FFB74D',    // Warm Harvest
    accentDark: '#E65100',     // Rich Amber
    
    // Background & Surfaces
    background: '#FAFAFA',     // Clean White
    backgroundSecondary: '#F1F8E9', // Soft Green Tint
    surface: '#FFFFFF',        // Pure White
    surfaceVariant: '#E8F5E8', // Subtle Green Surface
    
    // Text Colors
    text: '#1B1B1B',           // Almost Black - High Contrast
    textSecondary: '#424242',  // Medium Gray
    textLight: '#757575',      // Light Gray
    textOnPrimary: '#FFFFFF',  // White on Primary
    
    // Status Colors
    success: '#2E7D32',        // Success Green
    successLight: '#81C784',   // Light Success
    error: '#C62828',          // Deep Red
    errorLight: '#EF5350',     // Light Red
    warning: '#F57C00',        // Orange Warning
    warningLight: '#FFB74D',   // Light Orange
    info: '#1565C0',           // Blue Info
    infoLight: '#42A5F5',      // Light Blue
    
    // Functional Colors
    disabled: '#BDBDBD',
    placeholder: '#9E9E9E',
    backdrop: 'rgba(27, 94, 32, 0.6)', // Green-tinted backdrop
    border: '#E0E0E0',
    borderLight: '#F5F5F5',
    
    // Agricultural Specific Colors
    soil: '#6D4C41',           // Rich Soil Brown
    water: '#0277BD',          // Clean Water Blue
    sun: '#FFC107',            // Bright Sun Yellow
    growth: '#66BB6A',         // Healthy Growth Green
    harvest: '#FF6F00',        // Harvest Orange
    organic: '#795548',        // Organic Brown
  },
  roundness: 12, // More modern rounded corners
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
  xxxl: 64,
};

// Professional Layout Spacing
export const layout = {
  // Screen Padding
  screenPadding: 20,
  screenPaddingHorizontal: 24,
  screenPaddingVertical: 16,
  
  // Component Spacing
  componentSpacing: 16,
  sectionSpacing: 24,
  cardSpacing: 12,
  
  // Header Heights
  headerHeight: 64,
  tabBarHeight: 60,
  
  // Border Radius
  borderRadius: {
    small: 6,
    medium: 12,
    large: 16,
    xlarge: 24,
  },
  
  // Shadows
  shadow: {
    small: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 3,
    },
    medium: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.15,
      shadowRadius: 8,
      elevation: 6,
    },
    large: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 0.2,
      shadowRadius: 16,
      elevation: 10,
    },
  },
};

export const typography = {
  // Headlines - Professional and Clear
  h1: {
    fontSize: 32,
    fontWeight: '700', // Bold
    lineHeight: 40,
    letterSpacing: 0.5,
  },
  h2: {
    fontSize: 28,
    fontWeight: '700',
    lineHeight: 36,
    letterSpacing: 0.25,
  },
  h3: {
    fontSize: 24,
    fontWeight: '600', // Semi-bold
    lineHeight: 32,
    letterSpacing: 0.15,
  },
  h4: {
    fontSize: 20,
    fontWeight: '600',
    lineHeight: 28,
    letterSpacing: 0.1,
  },
  h5: {
    fontSize: 18,
    fontWeight: '500', // Medium
    lineHeight: 24,
  },
  h6: {
    fontSize: 16,
    fontWeight: '500',
    lineHeight: 22,
  },
  
  // Body Text - Professional and Readable
  body1: {
    fontSize: 16,
    fontWeight: '400', // Regular
    lineHeight: 24,
    letterSpacing: 0.5,
  },
  body2: {
    fontSize: 14,
    fontWeight: '400',
    lineHeight: 20,
    letterSpacing: 0.25,
  },
  
  // UI Elements
  button: {
    fontSize: 16,
    fontWeight: '600',
    lineHeight: 20,
    letterSpacing: 0.75,
    textTransform: 'uppercase',
  },
  caption: {
    fontSize: 12,
    fontWeight: '400',
    lineHeight: 16,
    letterSpacing: 0.4,
  },
  overline: {
    fontSize: 10,
    fontWeight: '500',
    lineHeight: 14,
    letterSpacing: 1.5,
    textTransform: 'uppercase',
  },
  
  // Agricultural Specific
  farmData: {
    fontSize: 18,
    fontWeight: '600',
    lineHeight: 24,
    fontFamily: 'monospace', // For data display
  },
  metric: {
    fontSize: 24,
    fontWeight: '700',
    lineHeight: 28,
    fontFamily: 'monospace', // For metrics and numbers
  },
};

// Professional Gradients for Agricultural Theme
export const gradients = {
  primary: ['#1B5E20', '#4CAF50'], // Deep to bright green
  secondary: ['#8BC34A', '#DCEDC8'], // Fresh crop gradient
  accent: ['#FF8F00', '#FFB74D'], // Golden harvest gradient
  success: ['#2E7D32', '#81C784'], // Success gradient
  earth: ['#6D4C41', '#8D6E63'], // Soil gradient
  sky: ['#0277BD', '#81D4FA'], // Water/sky gradient
  sunrise: ['#FF6F00', '#FFC107'], // Sunrise/harvest gradient
  organic: ['#795548', '#A1887F'], // Organic brown gradient
  growth: ['#1B5E20', '#66BB6A', '#C8E6C9'], // Growth stages
};

// Professional Component Styles
export const components = {
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  
  button: {
    primary: {
      backgroundColor: '#1B5E20',
      borderRadius: 8,
      paddingVertical: 12,
      paddingHorizontal: 24,
    },
    secondary: {
      backgroundColor: '#8BC34A',
      borderRadius: 8,
      paddingVertical: 12,
      paddingHorizontal: 24,
    },
    outline: {
      backgroundColor: 'transparent',
      borderColor: '#1B5E20',
      borderWidth: 2,
      borderRadius: 8,
      paddingVertical: 10,
      paddingHorizontal: 22,
    },
  },
  
  input: {
    backgroundColor: '#FFFFFF',
    borderColor: '#E0E0E0',
    borderWidth: 1,
    borderRadius: 8,
    paddingVertical: 14,
    paddingHorizontal: 16,
    fontSize: 16,
  },
  
  chip: {
    backgroundColor: '#E8F5E8',
    borderRadius: 16,
    paddingVertical: 6,
    paddingHorizontal: 12,
  },
  
  badge: {
    backgroundColor: '#FF8F00',
    borderRadius: 12,
    minWidth: 24,
    height: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
};

// Agricultural Icons Mapping (for future use with vector icons)
export const iconMap = {
  // Navigation
  home: 'home',
  dashboard: 'dashboard',
  farm: 'agriculture',
  marketplace: 'storefront',
  profile: 'account-circle',
  
  // Agricultural
  crop: 'grain',
  plant: 'leaf',
  tree: 'tree',
  soil: 'terrain',
  water: 'water',
  weather: 'weather-sunny',
  rain: 'weather-rainy',
  temperature: 'thermometer',
  humidity: 'water-percent',
  
  // Farm Management
  tractor: 'tractor',
  seed: 'seed',
  harvest: 'basket',
  storage: 'warehouse',
  fertilizer: 'flask',
  pesticide: 'spray',
  
  // Monitoring
  sensor: 'radar',
  camera: 'camera',
  drone: 'airplane',
  gps: 'map-marker',
  chart: 'chart-line',
  analytics: 'chart-bar',
  
  // Marketplace
  sell: 'currency-usd',
  buy: 'shopping',
  price: 'tag',
  quality: 'star',
  organic: 'leaf-circle',
  certified: 'certificate',
};
