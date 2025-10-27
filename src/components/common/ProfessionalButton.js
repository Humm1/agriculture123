import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { theme, layout, typography, gradients, components } from '../../theme/theme';

/**
 * Professional Button Component for Agricultural Applications
 */
export const ProfessionalButton = ({
  title,
  onPress,
  variant = 'primary', // primary, secondary, outline, ghost, gradient
  size = 'medium', // small, medium, large
  disabled = false,
  loading = false,
  icon,
  iconPosition = 'left', // left, right
  gradient,
  style,
  textStyle,
  ...props
}) => {
  const buttonStyles = [
    styles.baseButton,
    styles[`${variant}Button`],
    styles[`${size}Button`],
    disabled && styles.disabledButton,
    style,
  ];

  const textStyles = [
    styles.baseButtonText,
    styles[`${variant}ButtonText`],
    styles[`${size}ButtonText`],
    disabled && styles.disabledButtonText,
    textStyle,
  ];

  const renderContent = () => {
    if (loading) {
      return (
        <ActivityIndicator 
          size="small" 
          color={variant === 'outline' ? theme.colors.primary : theme.colors.textOnPrimary} 
        />
      );
    }

    return (
      <View style={styles.buttonContent}>
        {icon && iconPosition === 'left' && (
          <View style={[styles.buttonIcon, styles.buttonIconLeft]}>
            {icon}
          </View>
        )}
        <Text style={textStyles}>{title}</Text>
        {icon && iconPosition === 'right' && (
          <View style={[styles.buttonIcon, styles.buttonIconRight]}>
            {icon}
          </View>
        )}
      </View>
    );
  };

  if (variant === 'gradient' && gradient) {
    return (
      <TouchableOpacity
        onPress={onPress}
        disabled={disabled || loading}
        style={[styles.baseButton, styles.gradientButton, style]}
        {...props}
      >
        <LinearGradient
          colors={gradient}
          style={[styles.gradientContainer, styles[`${size}Button`]]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
        >
          {renderContent()}
        </LinearGradient>
      </TouchableOpacity>
    );
  }

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled || loading}
      style={buttonStyles}
      {...props}
    >
      {renderContent()}
    </TouchableOpacity>
  );
};

/**
 * Floating Action Button for Agricultural Actions
 */
export const AgricultureFAB = ({
  onPress,
  icon,
  size = 'medium', // small, medium, large
  color = theme.colors.primary,
  style,
  ...props
}) => {
  const fabStyles = [
    styles.fab,
    styles[`fab${size.charAt(0).toUpperCase() + size.slice(1)}`],
    { backgroundColor: color },
    style,
  ];

  return (
    <TouchableOpacity style={fabStyles} onPress={onPress} {...props}>
      {icon}
    </TouchableOpacity>
  );
};

/**
 * Chip Component for Tags and Categories
 */
export const AgricultureChip = ({
  label,
  onPress,
  onDelete,
  selected = false,
  variant = 'default', // default, outline, filled
  color = theme.colors.primary,
  icon,
  style,
  textStyle,
  ...props
}) => {
  const chipStyles = [
    styles.chip,
    styles[`chip${variant.charAt(0).toUpperCase() + variant.slice(1)}`],
    selected && styles.chipSelected,
    { borderColor: color },
    selected && { backgroundColor: color },
    style,
  ];

  const chipTextStyles = [
    styles.chipText,
    selected && styles.chipSelectedText,
    textStyle,
  ];

  return (
    <TouchableOpacity style={chipStyles} onPress={onPress} {...props}>
      {icon && <View style={styles.chipIcon}>{icon}</View>}
      <Text style={chipTextStyles}>{label}</Text>
      {onDelete && (
        <TouchableOpacity onPress={onDelete} style={styles.chipDeleteButton}>
          <Text style={styles.chipDeleteText}>×</Text>
        </TouchableOpacity>
      )}
    </TouchableOpacity>
  );
};

/**
 * Badge Component for Notifications and Status
 */
export const StatusBadge = ({
  children,
  count,
  status = 'default', // default, success, warning, error, info
  size = 'medium', // small, medium, large
  style,
  ...props
}) => {
  const badgeStyles = [
    styles.badge,
    styles[`badge${status.charAt(0).toUpperCase() + status.slice(1)}`],
    styles[`badge${size.charAt(0).toUpperCase() + size.slice(1)}`],
    style,
  ];

  return (
    <View style={badgeStyles} {...props}>
      {count !== undefined ? (
        <Text style={styles.badgeText}>{count > 99 ? '99+' : count}</Text>
      ) : (
        children
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  // Base Button Styles
  baseButton: {
    borderRadius: layout.borderRadius.medium,
    justifyContent: 'center',
    alignItems: 'center',
    flexDirection: 'row',
  },

  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },

  buttonIcon: {
    justifyContent: 'center',
    alignItems: 'center',
  },

  buttonIconLeft: {
    marginRight: 8,
  },

  buttonIconRight: {
    marginLeft: 8,
  },

  // Button Variants
  primaryButton: {
    backgroundColor: theme.colors.primary,
    ...layout.shadow.small,
  },

  secondaryButton: {
    backgroundColor: theme.colors.secondary,
    ...layout.shadow.small,
  },

  outlineButton: {
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: theme.colors.primary,
  },

  ghostButton: {
    backgroundColor: 'transparent',
  },

  gradientButton: {
    backgroundColor: 'transparent',
    overflow: 'hidden',
  },

  gradientContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: layout.borderRadius.medium,
  },

  disabledButton: {
    backgroundColor: theme.colors.disabled,
    opacity: 0.6,
  },

  // Button Sizes
  smallButton: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    minHeight: 32,
  },

  mediumButton: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    minHeight: 44,
  },

  largeButton: {
    paddingVertical: 16,
    paddingHorizontal: 32,
    minHeight: 56,
  },

  // Button Text Styles
  baseButtonText: {
    ...typography.button,
    textAlign: 'center',
  },

  primaryButtonText: {
    color: theme.colors.textOnPrimary,
  },

  secondaryButtonText: {
    color: theme.colors.textOnPrimary,
  },

  outlineButtonText: {
    color: theme.colors.primary,
  },

  ghostButtonText: {
    color: theme.colors.primary,
  },

  disabledButtonText: {
    color: theme.colors.textSecondary,
  },

  // Button Text Sizes
  smallButtonText: {
    fontSize: 14,
  },

  mediumButtonText: {
    fontSize: 16,
  },

  largeButtonText: {
    fontSize: 18,
  },

  // FAB Styles
  fab: {
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    ...layout.shadow.medium,
  },

  fabSmall: {
    width: 40,
    height: 40,
  },

  fabMedium: {
    width: 56,
    height: 56,
  },

  fabLarge: {
    width: 72,
    height: 72,
  },

  // Chip Styles
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 16,
    marginRight: 8,
    marginBottom: 8,
  },

  chipDefault: {
    backgroundColor: theme.colors.surfaceVariant,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },

  chipOutline: {
    backgroundColor: 'transparent',
    borderWidth: 1,
  },

  chipFilled: {
    backgroundColor: theme.colors.primary,
    borderWidth: 0,
  },

  chipSelected: {
    shadowColor: theme.colors.primary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
  },

  chipText: {
    ...typography.caption,
    color: theme.colors.text,
    fontWeight: '500',
  },

  chipSelectedText: {
    color: theme.colors.textOnPrimary,
  },

  chipIcon: {
    marginRight: 4,
  },

  chipDeleteButton: {
    marginLeft: 4,
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: theme.colors.textSecondary,
    justifyContent: 'center',
    alignItems: 'center',
  },

  chipDeleteText: {
    color: theme.colors.textOnPrimary,
    fontSize: 12,
    fontWeight: 'bold',
  },

  // Badge Styles
  badge: {
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    minWidth: 24,
  },

  badgeDefault: {
    backgroundColor: theme.colors.accent,
  },

  badgeSuccess: {
    backgroundColor: theme.colors.success,
  },

  badgeWarning: {
    backgroundColor: theme.colors.warning,
  },

  badgeError: {
    backgroundColor: theme.colors.error,
  },

  badgeInfo: {
    backgroundColor: theme.colors.info,
  },

  badgeSmall: {
    height: 16,
    minWidth: 16,
  },

  badgeMedium: {
    height: 24,
    minWidth: 24,
  },

  badgeLarge: {
    height: 32,
    minWidth: 32,
  },

  badgeText: {
    ...typography.caption,
    color: theme.colors.textOnPrimary,
    fontWeight: '600',
    fontSize: 10,
  },
});

export { ProfessionalButton as default };