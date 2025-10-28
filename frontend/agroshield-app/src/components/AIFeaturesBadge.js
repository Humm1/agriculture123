/**
 * AI Features Badge Component
 * Shows AI capabilities status in Growth Tracking
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useGrowthFeatureFlags } from '../hooks/useGrowthAI';

export default function AIFeaturesBadge({ onPress }) {
  const { flags, loading, summary } = useGrowthFeatureFlags();

  if (loading) {
    return (
      <View style={styles.badge}>
        <Text style={styles.loadingText}>Loading AI...</Text>
      </View>
    );
  }

  if (!flags.aiEnabled) {
    return (
      <View style={[styles.badge, styles.badgeInactive]}>
        <Text style={styles.icon}>🤖</Text>
        <Text style={styles.text}>Rule-Based Analysis</Text>
      </View>
    );
  }

  const percentage = summary?.percentage_ready || 0;
  const availableCount = summary?.available_features || 0;
  const totalCount = summary?.total_features || 0;

  return (
    <TouchableOpacity 
      style={[styles.badge, styles.badgeActive]} 
      onPress={onPress}
      activeOpacity={0.7}
    >
      <Text style={styles.icon}>✨</Text>
      <View style={styles.content}>
        <Text style={styles.title}>AI-Powered</Text>
        <Text style={styles.subtitle}>
          {availableCount}/{totalCount} features • {percentage.toFixed(0)}%
        </Text>
      </View>
      <View style={styles.indicators}>
        {flags.canAnalyzeSoil && <FeatureIcon icon="🌱" />}
        {flags.canCheckHealth && <FeatureIcon icon="🌿" />}
        {flags.canDetectPests && <FeatureIcon icon="🐛" />}
        {flags.canDetectDiseases && <FeatureIcon icon="🦠" />}
      </View>
    </TouchableOpacity>
  );
}

function FeatureIcon({ icon }) {
  return (
    <View style={styles.featureIcon}>
      <Text style={styles.featureIconText}>{icon}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 8,
    marginVertical: 8,
  },
  badgeActive: {
    backgroundColor: '#E8F5E9',
    borderWidth: 1,
    borderColor: '#4CAF50',
  },
  badgeInactive: {
    backgroundColor: '#F5F5F5',
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  icon: {
    fontSize: 24,
    marginRight: 12,
  },
  content: {
    flex: 1,
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2E7D32',
  },
  subtitle: {
    fontSize: 12,
    color: '#66BB6A',
    marginTop: 2,
  },
  text: {
    fontSize: 14,
    color: '#757575',
  },
  loadingText: {
    fontSize: 14,
    color: '#9E9E9E',
  },
  indicators: {
    flexDirection: 'row',
    gap: 4,
  },
  featureIcon: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#FFFFFF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  featureIconText: {
    fontSize: 14,
  },
});
