import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { theme, layout, typography, gradients } from '../../theme/theme';

/**
 * Professional Header Component for Agricultural Applications
 */
export const ProfessionalHeader = ({
  title,
  subtitle,
  onBackPress,
  rightActions = [],
  variant = 'default', // default, gradient, minimal, farm
  gradient,
  showBackButton = false,
  backgroundColor,
  textColor,
  style,
  titleStyle,
  subtitleStyle,
  ...props
}) => {
  const headerStyles = [
    styles.header,
    styles[`${variant}Header`],
    backgroundColor && { backgroundColor },
    style,
  ];

  const titleStyles = [
    styles.title,
    styles[`${variant}Title`],
    textColor && { color: textColor },
    titleStyle,
  ];

  const subtitleStyles = [
    styles.subtitle,
    styles[`${variant}Subtitle`],
    textColor && { color: textColor },
    subtitleStyle,
  ];

  const renderHeader = () => (
    <View style={headerStyles}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.headerContent}>
          {/* Left Section */}
          <View style={styles.leftSection}>
            {showBackButton && (
              <TouchableOpacity style={styles.backButton} onPress={onBackPress}>
                <Text style={styles.backButtonText}>←</Text>
              </TouchableOpacity>
            )}
          </View>

          {/* Center Section */}
          <View style={styles.centerSection}>
            <Text style={titleStyles} numberOfLines={1}>
              {title}
            </Text>
            {subtitle && (
              <Text style={subtitleStyles} numberOfLines={1}>
                {subtitle}
              </Text>
            )}
          </View>

          {/* Right Section */}
          <View style={styles.rightSection}>
            {rightActions.map((action, index) => (
              <TouchableOpacity
                key={index}
                style={styles.headerAction}
                onPress={action.onPress}
              >
                {action.icon ? action.icon : (
                  <Text style={styles.headerActionText}>{action.title}</Text>
                )}
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </SafeAreaView>
    </View>
  );

  if (variant === 'gradient' && gradient) {
    return (
      <LinearGradient colors={gradient} style={[styles.header, style]}>
        <SafeAreaView style={styles.safeArea}>
          <View style={styles.headerContent}>
            {/* Left Section */}
            <View style={styles.leftSection}>
              {showBackButton && (
                <TouchableOpacity style={styles.backButton} onPress={onBackPress}>
                  <Text style={[styles.backButtonText, { color: theme.colors.textOnPrimary }]}>←</Text>
                </TouchableOpacity>
              )}
            </View>

            {/* Center Section */}
            <View style={styles.centerSection}>
              <Text style={[titleStyles, { color: theme.colors.textOnPrimary }]} numberOfLines={1}>
                {title}
              </Text>
              {subtitle && (
                <Text style={[subtitleStyles, { color: theme.colors.textOnPrimary }]} numberOfLines={1}>
                  {subtitle}
                </Text>
              )}
            </View>

            {/* Right Section */}
            <View style={styles.rightSection}>
              {rightActions.map((action, index) => (
                <TouchableOpacity
                  key={index}
                  style={styles.headerAction}
                  onPress={action.onPress}
                >
                  {action.icon ? action.icon : (
                    <Text style={[styles.headerActionText, { color: theme.colors.textOnPrimary }]}>
                      {action.title}
                    </Text>
                  )}
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </SafeAreaView>
      </LinearGradient>
    );
  }

  return renderHeader();
};

/**
 * Dashboard Header with Agricultural Theme
 */
export const DashboardHeader = ({
  farmName,
  farmerName,
  weatherInfo,
  onProfilePress,
  onNotificationPress,
  onMenuPress,
  notificationCount = 0,
  style,
  ...props
}) => {
  return (
    <View style={[styles.dashboardHeader, style]}>
      <LinearGradient
        colors={gradients.primary}
        style={styles.dashboardGradient}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <SafeAreaView style={styles.safeArea}>
          <View style={styles.dashboardContent}>
            {/* Top Row */}
            <View style={styles.dashboardTopRow}>
              <TouchableOpacity style={styles.menuButton} onPress={onMenuPress}>
                <Text style={styles.menuIcon}>☰</Text>
              </TouchableOpacity>
              
              <View style={styles.dashboardActions}>
                <TouchableOpacity style={styles.notificationButton} onPress={onNotificationPress}>
                  <Text style={styles.notificationIcon}>🔔</Text>
                  {notificationCount > 0 && (
                    <View style={styles.notificationBadge}>
                      <Text style={styles.notificationBadgeText}>
                        {notificationCount > 9 ? '9+' : notificationCount}
                      </Text>
                    </View>
                  )}
                </TouchableOpacity>
                
                <TouchableOpacity style={styles.profileButton} onPress={onProfilePress}>
                  <Text style={styles.profileIcon}>👤</Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* Farm Info */}
            <View style={styles.farmInfo}>
              <Text style={styles.welcomeText}>Welcome back,</Text>
              <Text style={styles.farmerNameText}>{farmerName}</Text>
              <Text style={styles.farmNameText}>{farmName}</Text>
            </View>

            {/* Weather Info */}
            {weatherInfo && (
              <View style={styles.weatherInfo}>
                <Text style={styles.weatherIcon}>{weatherInfo.icon}</Text>
                <View style={styles.weatherDetails}>
                  <Text style={styles.weatherTemp}>{weatherInfo.temperature}°C</Text>
                  <Text style={styles.weatherDesc}>{weatherInfo.description}</Text>
                </View>
              </View>
            )}
          </View>
        </SafeAreaView>
      </LinearGradient>
    </View>
  );
};

/**
 * Section Header Component
 */
export const SectionHeader = ({
  title,
  subtitle,
  action,
  onActionPress,
  style,
  titleStyle,
  ...props
}) => {
  return (
    <View style={[styles.sectionHeader, style]} {...props}>
      <View style={styles.sectionHeaderContent}>
        <Text style={[styles.sectionTitle, titleStyle]}>{title}</Text>
        {subtitle && (
          <Text style={styles.sectionSubtitle}>{subtitle}</Text>
        )}
      </View>
      
      {action && (
        <TouchableOpacity onPress={onActionPress} style={styles.sectionAction}>
          <Text style={styles.sectionActionText}>{action}</Text>
        </TouchableOpacity>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  // Base Header Styles
  header: {
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },

  safeArea: {
    flex: 1,
  },

  headerContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: layout.screenPaddingHorizontal,
    paddingVertical: 12,
    minHeight: 56,
  },

  leftSection: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-start',
  },

  centerSection: {
    flex: 2,
    alignItems: 'center',
    justifyContent: 'center',
  },

  rightSection: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
  },

  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },

  backButtonText: {
    fontSize: 24,
    color: theme.colors.text,
  },

  title: {
    ...typography.h5,
    color: theme.colors.text,
    fontWeight: '600',
  },

  subtitle: {
    ...typography.caption,
    color: theme.colors.textSecondary,
    marginTop: 2,
  },

  headerAction: {
    marginLeft: 12,
    paddingHorizontal: 8,
    paddingVertical: 4,
  },

  headerActionText: {
    ...typography.body2,
    color: theme.colors.primary,
    fontWeight: '500',
  },

  // Header Variants
  defaultHeader: {
    backgroundColor: theme.colors.surface,
  },

  gradientHeader: {
    borderBottomWidth: 0,
  },

  minimalHeader: {
    backgroundColor: 'transparent',
    borderBottomWidth: 0,
  },

  farmHeader: {
    backgroundColor: theme.colors.backgroundSecondary,
    borderBottomColor: theme.colors.primary,
    borderBottomWidth: 2,
  },

  defaultTitle: {
    color: theme.colors.text,
  },

  gradientTitle: {
    color: theme.colors.textOnPrimary,
  },

  minimalTitle: {
    color: theme.colors.text,
  },

  farmTitle: {
    color: theme.colors.primary,
  },

  defaultSubtitle: {
    color: theme.colors.textSecondary,
  },

  gradientSubtitle: {
    color: theme.colors.textOnPrimary,
    opacity: 0.8,
  },

  minimalSubtitle: {
    color: theme.colors.textSecondary,
  },

  farmSubtitle: {
    color: theme.colors.secondary,
  },

  // Dashboard Header Styles
  dashboardHeader: {
    height: 200,
  },

  dashboardGradient: {
    flex: 1,
  },

  dashboardContent: {
    flex: 1,
    paddingHorizontal: layout.screenPaddingHorizontal,
    paddingTop: 8,
    paddingBottom: 16,
  },

  dashboardTopRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },

  menuButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },

  menuIcon: {
    fontSize: 20,
    color: theme.colors.textOnPrimary,
  },

  dashboardActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },

  notificationButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
    position: 'relative',
  },

  notificationIcon: {
    fontSize: 18,
    color: theme.colors.textOnPrimary,
  },

  notificationBadge: {
    position: 'absolute',
    top: -2,
    right: -2,
    backgroundColor: theme.colors.error,
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },

  notificationBadgeText: {
    fontSize: 10,
    color: theme.colors.textOnPrimary,
    fontWeight: 'bold',
  },

  profileButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },

  profileIcon: {
    fontSize: 18,
    color: theme.colors.textOnPrimary,
  },

  farmInfo: {
    flex: 1,
    justifyContent: 'center',
  },

  welcomeText: {
    ...typography.body2,
    color: theme.colors.textOnPrimary,
    opacity: 0.9,
  },

  farmerNameText: {
    ...typography.h4,
    color: theme.colors.textOnPrimary,
    fontWeight: '700',
    marginTop: 4,
  },

  farmNameText: {
    ...typography.body1,
    color: theme.colors.textOnPrimary,
    opacity: 0.8,
    marginTop: 2,
  },

  weatherInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    borderRadius: layout.borderRadius.medium,
    padding: 12,
    marginTop: 16,
  },

  weatherIcon: {
    fontSize: 24,
    marginRight: 12,
  },

  weatherDetails: {
    flex: 1,
  },

  weatherTemp: {
    ...typography.h6,
    color: theme.colors.textOnPrimary,
    fontWeight: '600',
  },

  weatherDesc: {
    ...typography.caption,
    color: theme.colors.textOnPrimary,
    opacity: 0.8,
    textTransform: 'capitalize',
  },

  // Section Header Styles
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: layout.screenPaddingHorizontal,
    paddingVertical: 16,
  },

  sectionHeaderContent: {
    flex: 1,
  },

  sectionTitle: {
    ...typography.h6,
    color: theme.colors.text,
    fontWeight: '600',
  },

  sectionSubtitle: {
    ...typography.caption,
    color: theme.colors.textSecondary,
    marginTop: 2,
  },

  sectionAction: {
    paddingVertical: 4,
    paddingHorizontal: 8,
  },

  sectionActionText: {
    ...typography.body2,
    color: theme.colors.primary,
    fontWeight: '500',
  },
});

export default ProfessionalHeader;