import { DefaultTheme } from 'react-native-paper';

export const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#2E7D32',      // Green - Agriculture
    secondary: '#66BB6A',    // Light Green
    accent: '#FFA726',       // Orange - Alerts
    background: '#F5F5F5',
    surface: '#FFFFFF',
    text: '#212121',
    disabled: '#BDBDBD',
    placeholder: '#9E9E9E',
    backdrop: 'rgba(0, 0, 0, 0.5)',
    error: '#D32F2F',
    success: '#43A047',
    warning: '#FB8C00',
    info: '#1976D2',
  },
  roundness: 8,
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
};

export const typography = {
  h1: {
    fontSize: 32,
    fontWeight: 'bold',
  },
  h2: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  h3: {
    fontSize: 20,
    fontWeight: '600',
  },
  body: {
    fontSize: 16,
  },
  caption: {
    fontSize: 12,
  },
};
