import React, { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  ScrollView, 
  RefreshControl,
  TouchableOpacity,
  SafeAreaView,
  Dimensions 
} from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';

// Professional Agricultural Theme
const professionalTheme = {
  colors: {
    primary: '#1B5E20',        // Deep Forest Green
    primaryLight: '#4CAF50',   // Vibrant Green
    secondary: '#8BC34A',      // Fresh Crop Green
    accent: '#FF8F00',         // Golden Wheat
    background: '#FAFAFA',     // Clean Background
    surface: '#FFFFFF',        // Pure White
    text: '#1B1B1B',           // Dark Text
    textSecondary: '#424242',  // Medium Gray
    textLight: '#757575',      // Light Gray
    textOnPrimary: '#FFFFFF',  // White on Primary
    success: '#2E7D32',        // Success Green
    warning: '#F57C00',        // Warning Orange
    error: '#C62828',          // Error Red
    info: '#1565C0',           // Info Blue
    border: '#E0E0E0',         // Light Border
    shadow: 'rgba(0,0,0,0.1)', // Shadow Color
  },
  gradients: {
    primary: ['#1B5E20', '#4CAF50'],
    harvest: ['#FF8F00', '#FFB74D'],
    earth: ['#6D4C41', '#8D6E63'],
  }
};

const { width } = Dimensions.get('window');

const HomeScreen = ({ navigation }) => {
  const [refreshing, setRefreshing] = useState(false);
  
  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 2000);
  }, []);

  const handleQuickAction = (action) => {
    switch (action) {
      case 'scan':
        // Navigate to crop scanning
        console.log('Navigate to crop scanning');
        break;
      case 'analytics':
        // Navigate to analytics
        console.log('Navigate to analytics');
        break;
      case 'marketplace':
        // Navigate to marketplace
        console.log('Navigate to marketplace');
        break;
      case 'weather':
        // Navigate to weather
        console.log('Navigate to weather');
        break;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Professional Agricultural Header */}
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <View style={styles.headerLeft}>
            <TouchableOpacity style={styles.menuButton}>
              <MaterialCommunityIcons name="menu" size={24} color={professionalTheme.colors.textOnPrimary} />
            </TouchableOpacity>
          </View>
          
          <View style={styles.headerCenter}>
            <Text style={styles.appTitle}>AgroShield</Text>
            <Text style={styles.appSubtitle}>Professional Farm Management</Text>
          </View>
          
          <View style={styles.headerRight}>
            <TouchableOpacity style={styles.notificationButton}>
              <MaterialCommunityIcons name="bell-outline" size={24} color={professionalTheme.colors.textOnPrimary} />
              <View style={styles.notificationBadge}>
                <Text style={styles.notificationBadgeText}>3</Text>
              </View>
            </TouchableOpacity>
          </View>
        </View>
        
        {/* Weather Strip */}
        <View style={styles.weatherStrip}>
          <MaterialCommunityIcons name="weather-partly-cloudy" size={20} color={professionalTheme.colors.textOnPrimary} />
          <Text style={styles.weatherText}>24°C • Partly Cloudy • Perfect for farming</Text>
        </View>
      </View>

      {/* Main Content */}
      <ScrollView 
        style={styles.content}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl 
            refreshing={refreshing} 
            onRefresh={onRefresh}
            colors={[professionalTheme.colors.primary]}
          />
        }
      >
        {/* Welcome Section */}
        <View style={styles.welcomeSection}>
          <Text style={styles.welcomeText}>Good morning,</Text>
          <Text style={styles.farmerName}>John Farmer</Text>
          <Text style={styles.farmName}>Green Valley Farm • 250 acres</Text>
        </View>

        {/* Professional Stats Cards */}
        <View style={styles.statsContainer}>
          <View style={[styles.statCard, styles.primaryStatCard]}>
            <View style={styles.statIconContainer}>
              <MaterialCommunityIcons name="sprout" size={28} color={professionalTheme.colors.primary} />
            </View>
            <Text style={styles.statNumber}>8</Text>
            <Text style={styles.statLabel}>Active Plots</Text>
            <Text style={styles.statTrend}>+2 this month</Text>
          </View>
          
          <View style={[styles.statCard, styles.successStatCard]}>
            <View style={styles.statIconContainer}>
              <MaterialCommunityIcons name="shield-check" size={28} color={professionalTheme.colors.success} />
            </View>
            <Text style={styles.statNumber}>92%</Text>
            <Text style={styles.statLabel}>Health Score</Text>
            <Text style={styles.statTrend}>+5% this week</Text>
          </View>
          
          <View style={[styles.statCard, styles.accentStatCard]}>
            <View style={styles.statIconContainer}>
              <MaterialCommunityIcons name="trending-up" size={28} color={professionalTheme.colors.accent} />
            </View>
            <Text style={styles.statNumber}>₹2.4L</Text>
            <Text style={styles.statLabel}>Est. Yield Value</Text>
            <Text style={styles.statTrend}>+12% proj.</Text>
          </View>
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.quickActionsGrid}>
            <TouchableOpacity 
              style={[styles.actionButton, styles.primaryActionButton]}
              onPress={() => handleQuickAction('scan')}
            >
              <View style={styles.actionIconContainer}>
                <MaterialCommunityIcons name="camera-iris" size={32} color={professionalTheme.colors.textOnPrimary} />
              </View>
              <Text style={styles.primaryActionButtonText}>AI Crop Scan</Text>
              <Text style={styles.actionSubtext}>Instant analysis</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.actionButton}
              onPress={() => handleQuickAction('analytics')}
            >
              <View style={styles.actionIconContainer}>
                <MaterialCommunityIcons name="chart-line" size={32} color={professionalTheme.colors.primary} />
              </View>
              <Text style={styles.actionButtonText}>Analytics</Text>
              <Text style={styles.actionSubtext}>Farm insights</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.actionButton}
              onPress={() => handleQuickAction('marketplace')}
            >
              <View style={styles.actionIconContainer}>
                <MaterialCommunityIcons name="storefront" size={32} color={professionalTheme.colors.primary} />
              </View>
              <Text style={styles.actionButtonText}>Marketplace</Text>
              <Text style={styles.actionSubtext}>Buy & sell</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.actionButton}
              onPress={() => handleQuickAction('weather')}
            >
              <View style={styles.actionIconContainer}>
                <MaterialCommunityIcons name="weather-sunny" size={32} color={professionalTheme.colors.accent} />
              </View>
              <Text style={styles.actionButtonText}>Weather</Text>
              <Text style={styles.actionSubtext}>7-day forecast</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Farm Status Overview */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Farm Overview</Text>
          
          <View style={styles.overviewCard}>
            <View style={styles.overviewHeader}>
              <MaterialCommunityIcons name="leaf" size={24} color={professionalTheme.colors.success} />
              <Text style={styles.overviewTitle}>Crop Health Status</Text>
              <Text style={styles.overviewStatus}>Excellent</Text>
            </View>
            <Text style={styles.overviewDescription}>
              All crops showing healthy growth patterns. Tomatoes ready for harvest in 14 days.
            </Text>
            <View style={styles.overviewActions}>
              <TouchableOpacity style={styles.overviewActionButton}>
                <Text style={styles.overviewActionText}>View Details</Text>
              </TouchableOpacity>
            </View>
          </View>
          
          <View style={styles.overviewCard}>
            <View style={styles.overviewHeader}>
              <MaterialCommunityIcons name="water" size={24} color={professionalTheme.colors.info} />
              <Text style={styles.overviewTitle}>Irrigation System</Text>
              <Text style={styles.overviewStatus}>Active</Text>
            </View>
            <Text style={styles.overviewDescription}>
              Smart irrigation completed for sectors A-C. Next scheduled for tomorrow 6:00 AM.
            </Text>
            <View style={styles.overviewActions}>
              <TouchableOpacity style={styles.overviewActionButton}>
                <Text style={styles.overviewActionText}>Schedule</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>

        {/* Bottom Spacing */}
        <View style={styles.bottomSpacing} />
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: professionalTheme.colors.background,
  },
  
  // Professional Header Styles
  header: {
    backgroundColor: professionalTheme.colors.primary,
    paddingTop: 10,
    paddingBottom: 16,
    shadowColor: professionalTheme.colors.shadow,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 8,
  },
  
  headerContent: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingTop: 12,
    paddingBottom: 8,
  },
  
  headerLeft: {
    flex: 1,
  },
  
  headerCenter: {
    flex: 2,
    alignItems: 'center',
  },
  
  headerRight: {
    flex: 1,
    alignItems: 'flex-end',
  },
  
  menuButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  
  appTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: professionalTheme.colors.textOnPrimary,
    textAlign: 'center',
    letterSpacing: 0.5,
  },
  
  appSubtitle: {
    fontSize: 14,
    color: professionalTheme.colors.textOnPrimary,
    opacity: 0.9,
    textAlign: 'center',
    marginTop: 2,
    fontWeight: '400',
  },
  
  notificationButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  
  notificationBadge: {
    position: 'absolute',
    top: -2,
    right: -2,
    backgroundColor: professionalTheme.colors.error,
    borderRadius: 12,
    minWidth: 24,
    height: 24,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 6,
  },
  
  notificationBadgeText: {
    color: professionalTheme.colors.textOnPrimary,
    fontSize: 12,
    fontWeight: '600',
  },
  
  weatherStrip: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    paddingHorizontal: 24,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    marginHorizontal: 24,
    borderRadius: 20,
    marginTop: 8,
  },
  
  weatherText: {
    color: professionalTheme.colors.textOnPrimary,
    fontSize: 14,
    marginLeft: 8,
    fontWeight: '500',
  },
  
  // Content Styles
  content: {
    flex: 1,
  },
  
  // Professional Welcome Section
  welcomeSection: {
    padding: 24,
    backgroundColor: professionalTheme.colors.surface,
    marginTop: -10,
    marginHorizontal: 20,
    borderRadius: 16,
    shadowColor: professionalTheme.colors.shadow,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
    marginBottom: 24,
  },
  
  welcomeText: {
    fontSize: 16,
    color: professionalTheme.colors.textSecondary,
    fontWeight: '400',
  },
  
  farmerName: {
    fontSize: 32,
    fontWeight: '700',
    color: professionalTheme.colors.text,
    marginTop: 4,
    letterSpacing: 0.5,
  },
  
  farmName: {
    fontSize: 16,
    color: professionalTheme.colors.textSecondary,
    marginTop: 4,
    fontWeight: '500',
  },
  
  // Professional Stats Cards
  statsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    marginBottom: 32,
    justifyContent: 'space-between',
  },
  
  statCard: {
    backgroundColor: professionalTheme.colors.surface,
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    flex: 1,
    marginHorizontal: 4,
    shadowColor: professionalTheme.colors.shadow,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.12,
    shadowRadius: 8,
    elevation: 6,
  },
  
  primaryStatCard: {
    borderTopWidth: 4,
    borderTopColor: professionalTheme.colors.primary,
  },
  
  successStatCard: {
    borderTopWidth: 4,
    borderTopColor: professionalTheme.colors.success,
  },
  
  accentStatCard: {
    borderTopWidth: 4,
    borderTopColor: professionalTheme.colors.accent,
  },
  
  statIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: 'rgba(27, 94, 32, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  
  statNumber: {
    fontSize: 28,
    fontWeight: '700',
    color: professionalTheme.colors.text,
    marginBottom: 4,
  },
  
  statLabel: {
    fontSize: 13,
    color: professionalTheme.colors.textSecondary,
    fontWeight: '500',
    textAlign: 'center',
  },
  
  statTrend: {
    fontSize: 11,
    color: professionalTheme.colors.success,
    fontWeight: '600',
    marginTop: 4,
    textAlign: 'center',
  },
  
  // Professional Sections
  section: {
    paddingHorizontal: 20,
    marginBottom: 32,
  },
  
  sectionTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: professionalTheme.colors.text,
    marginBottom: 20,
    letterSpacing: 0.3,
  },
  
  // Professional Quick Actions
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  
  actionButton: {
    backgroundColor: professionalTheme.colors.surface,
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    width: '48%',
    marginBottom: 16,
    shadowColor: professionalTheme.colors.shadow,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.12,
    shadowRadius: 8,
    elevation: 6,
    borderWidth: 1,
    borderColor: professionalTheme.colors.border,
  },
  
  primaryActionButton: {
    backgroundColor: professionalTheme.colors.primary,
    borderColor: professionalTheme.colors.primary,
  },
  
  actionIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'rgba(27, 94, 32, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  
  actionButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: professionalTheme.colors.text,
    textAlign: 'center',
    marginBottom: 4,
  },
  
  primaryActionButtonText: {
    color: professionalTheme.colors.textOnPrimary,
  },
  
  actionSubtext: {
    fontSize: 12,
    color: professionalTheme.colors.textSecondary,
    textAlign: 'center',
    fontWeight: '400',
  },
  
  // Professional Overview Cards
  overviewCard: {
    backgroundColor: professionalTheme.colors.surface,
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: professionalTheme.colors.shadow,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.12,
    shadowRadius: 8,
    elevation: 6,
    borderLeftWidth: 4,
    borderLeftColor: professionalTheme.colors.primary,
  },
  
  overviewHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  
  overviewTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: professionalTheme.colors.text,
    marginLeft: 12,
    flex: 1,
  },
  
  overviewStatus: {
    fontSize: 14,
    fontWeight: '600',
    color: professionalTheme.colors.success,
    backgroundColor: 'rgba(46, 125, 50, 0.1)',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  
  overviewDescription: {
    fontSize: 15,
    color: professionalTheme.colors.textSecondary,
    lineHeight: 22,
    marginBottom: 16,
    fontWeight: '400',
  },
  
  overviewActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
  },
  
  overviewActionButton: {
    backgroundColor: professionalTheme.colors.primary,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
  },
  
  overviewActionText: {
    color: professionalTheme.colors.textOnPrimary,
    fontSize: 14,
    fontWeight: '600',
  },
  
  // Bottom Spacing
  bottomSpacing: {
    height: 100,
  },
});

export default HomeScreen;