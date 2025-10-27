import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { theme, layout, typography, gradients } from '../../theme/theme';

/**
 * Professional Card Component for AgroShield
 * Supports various agricultural-themed card styles
 */
export const ProfessionalCard = ({
  children,
  style,
  onPress,
  variant = 'default', // default, elevated, gradient, farm, market
  gradientColors,
  shadow = true,
  padding = true,
  ...props
}) => {
  const cardStyles = [
    styles.baseCard,
    shadow && layout.shadow.medium,
    padding && { padding: layout.cardSpacing },
    getCardVariantStyle(variant),
    style,
  ];

  const CardWrapper = onPress ? TouchableOpacity : View;

  if (variant === 'gradient' && gradientColors) {
    return (
      <CardWrapper
        onPress={onPress}
        style={[styles.baseCard, shadow && layout.shadow.medium, style]}
        {...props}
      >
        <LinearGradient
          colors={gradientColors}
          style={[styles.gradientCard, padding && { padding: layout.cardSpacing }]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
        >
          {children}
        </LinearGradient>
      </CardWrapper>
    );
  }

  return (
    <CardWrapper onPress={onPress} style={cardStyles} {...props}>
      {children}
    </CardWrapper>
  );
};

/**
 * Agricultural Metric Card - For displaying farm data
 */
export const MetricCard = ({
  title,
  value,
  unit,
  icon,
  trend,
  trendDirection = 'up', // up, down, stable
  color = theme.colors.primary,
  onPress,
  style,
}) => {
  const trendColor = getTrendColor(trendDirection);
  
  return (
    <ProfessionalCard 
      onPress={onPress} 
      style={[styles.metricCard, style]}
      variant="elevated"
    >
      <View style={styles.metricHeader}>
        {icon && <View style={[styles.metricIcon, { backgroundColor: `${color}20` }]}>
          {icon}
        </View>}
        <Text style={[styles.metricTitle, { color: theme.colors.textSecondary }]}>
          {title}
        </Text>
      </View>
      
      <View style={styles.metricContent}>
        <Text style={[styles.metricValue, { color }]}>
          {value}
          {unit && <Text style={styles.metricUnit}> {unit}</Text>}
        </Text>
        
        {trend !== undefined && (
          <Text style={[styles.metricTrend, { color: trendColor }]}>
            {trendDirection === 'up' ? '↗' : trendDirection === 'down' ? '↘' : '→'} {trend}%
          </Text>
        )}
      </View>
    </ProfessionalCard>
  );
};

/**
 * Farm Status Card - For crop and field status
 */
export const FarmStatusCard = ({
  cropName,
  status,
  health,
  daysToHarvest,
  imageUri,
  onPress,
  style,
}) => {
  const statusColor = getStatusColor(status);
  
  return (
    <ProfessionalCard onPress={onPress} style={[styles.farmStatusCard, style]}>
      <View style={styles.farmStatusHeader}>
        <Text style={styles.farmStatusCrop}>{cropName}</Text>
        <View style={[styles.farmStatusBadge, { backgroundColor: statusColor }]}>
          <Text style={styles.farmStatusBadgeText}>{status}</Text>
        </View>
      </View>
      
      <View style={styles.farmStatusContent}>
        <View style={styles.farmStatusMetrics}>
          <View style={styles.farmStatusMetric}>
            <Text style={styles.farmStatusMetricLabel}>Health</Text>
            <Text style={[styles.farmStatusMetricValue, { color: getHealthColor(health) }]}>
              {health}%
            </Text>
          </View>
          
          {daysToHarvest && (
            <View style={styles.farmStatusMetric}>
              <Text style={styles.farmStatusMetricLabel}>Harvest</Text>
              <Text style={styles.farmStatusMetricValue}>
                {daysToHarvest} days
              </Text>
            </View>
          )}
        </View>
      </View>
    </ProfessionalCard>
  );
};

// Helper functions
const getCardVariantStyle = (variant) => {
  switch (variant) {
    case 'elevated':
      return {
        backgroundColor: theme.colors.surface,
        elevation: 6,
        shadowOpacity: 0.15,
      };
    case 'farm':
      return {
        backgroundColor: theme.colors.backgroundSecondary,
        borderLeftWidth: 4,
        borderLeftColor: theme.colors.primary,
      };
    case 'market':
      return {
        backgroundColor: theme.colors.surface,
        borderWidth: 1,
        borderColor: theme.colors.accent,
      };
    default:
      return {
        backgroundColor: theme.colors.surface,
      };
  }
};

const getTrendColor = (direction) => {
  switch (direction) {
    case 'up':
      return theme.colors.success;
    case 'down':
      return theme.colors.error;
    default:
      return theme.colors.textSecondary;
  }
};

const getStatusColor = (status) => {
  switch (status?.toLowerCase()) {
    case 'healthy':
    case 'growing':
      return theme.colors.success;
    case 'warning':
    case 'attention':
      return theme.colors.warning;
    case 'critical':
    case 'disease':
      return theme.colors.error;
    default:
      return theme.colors.info;
  }
};

const getHealthColor = (health) => {
  if (health >= 80) return theme.colors.success;
  if (health >= 60) return theme.colors.warning;
  return theme.colors.error;
};

const styles = StyleSheet.create({
  baseCard: {
    borderRadius: layout.borderRadius.medium,
    marginBottom: layout.componentSpacing,
  },
  
  gradientCard: {
    borderRadius: layout.borderRadius.medium,
  },
  
  // Metric Card Styles
  metricCard: {
    minHeight: 120,
  },
  
  metricHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  
  metricIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    marginRight: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  
  metricTitle: {
    ...typography.body2,
    flex: 1,
  },
  
  metricContent: {
    flex: 1,
    justifyContent: 'space-between',
  },
  
  metricValue: {
    ...typography.metric,
    marginBottom: 4,
  },
  
  metricUnit: {
    ...typography.body2,
    color: theme.colors.textSecondary,
  },
  
  metricTrend: {
    ...typography.caption,
    fontWeight: '600',
  },
  
  // Farm Status Card Styles
  farmStatusCard: {
    minHeight: 140,
  },
  
  farmStatusHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  
  farmStatusCrop: {
    ...typography.h5,
    color: theme.colors.text,
  },
  
  farmStatusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  
  farmStatusBadgeText: {
    ...typography.caption,
    color: theme.colors.textOnPrimary,
    fontWeight: '600',
  },
  
  farmStatusContent: {
    flex: 1,
  },
  
  farmStatusMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  
  farmStatusMetric: {
    alignItems: 'center',
  },
  
  farmStatusMetricLabel: {
    ...typography.caption,
    color: theme.colors.textSecondary,
    marginBottom: 4,
  },
  
  farmStatusMetricValue: {
    ...typography.h6,
    color: theme.colors.text,
    fontWeight: '600',
  },
});

export default ProfessionalCard;