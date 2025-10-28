/**
 * AI Features Modal
 * Detailed view of available AI capabilities
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator
} from 'react-native';
import { useGrowthAIStatus, useAvailableFeatures } from '../hooks/useGrowthAI';
import growthTrackingAI from '../services/growthTrackingAI';

export default function AIFeaturesModal({ visible, onClose }) {
  const { status, loading } = useGrowthAIStatus();
  const { features, percentageReady } = useAvailableFeatures();

  if (loading) {
    return (
      <Modal visible={visible} transparent animationType="slide">
        <View style={styles.overlay}>
          <View style={styles.modal}>
            <ActivityIndicator size="large" color="#4CAF50" />
            <Text style={styles.loadingText}>Loading AI Features...</Text>
          </View>
        </View>
      </Modal>
    );
  }

  return (
    <Modal visible={visible} transparent animationType="slide">
      <View style={styles.overlay}>
        <View style={styles.modal}>
          <View style={styles.header}>
            <Text style={styles.headerTitle}>AI Features</Text>
            <TouchableOpacity onPress={onClose} style={styles.closeButton}>
              <Text style={styles.closeText}>✕</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.summary}>
            <Text style={styles.summaryTitle}>System Status</Text>
            <View style={styles.progressBar}>
              <View 
                style={[styles.progressFill, { width: `${percentageReady}%` }]} 
              />
            </View>
            <Text style={styles.summaryText}>
              {percentageReady.toFixed(0)}% Ready • {features.length} Features Available
            </Text>
          </View>

          <ScrollView style={styles.content}>
            {status?.features && Object.entries(status.features).map(([key, available]) => {
              const display = growthTrackingAI.getFeatureDisplay(key);
              return (
                <FeatureCard
                  key={key}
                  name={key}
                  display={display}
                  available={available}
                />
              );
            })}
          </ScrollView>

          <View style={styles.footer}>
            <TouchableOpacity 
              style={styles.button} 
              onPress={onClose}
            >
              <Text style={styles.buttonText}>Close</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}

function FeatureCard({ name, display, available }) {
  const [showCapabilities, setShowCapabilities] = useState(false);
  const [capabilities, setCapabilities] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadCapabilities = async () => {
    if (showCapabilities || !available) return;
    
    setLoading(true);
    try {
      const caps = await growthTrackingAI.getFeatureCapabilities(name);
      setCapabilities(caps);
      setShowCapabilities(true);
    } catch (error) {
      console.error('Error loading capabilities:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <TouchableOpacity 
      style={styles.featureCard}
      onPress={loadCapabilities}
      disabled={!available}
    >
      <View style={styles.featureHeader}>
        <Text style={styles.featureIcon}>{display.icon}</Text>
        <View style={styles.featureInfo}>
          <Text style={styles.featureTitle}>{display.title}</Text>
          <Text style={styles.featureDescription}>{display.description}</Text>
        </View>
        <View style={[
          styles.statusBadge,
          available ? styles.statusAvailable : styles.statusUnavailable
        ]}>
          <Text style={styles.statusText}>
            {available ? '✓' : '✗'}
          </Text>
        </View>
      </View>

      {showCapabilities && (
        <View style={styles.capabilities}>
          <Text style={styles.capabilitiesTitle}>Capabilities:</Text>
          {capabilities.map((cap, idx) => (
            <Text key={idx} style={styles.capabilityItem}>
              • {cap}
            </Text>
          ))}
        </View>
      )}

      {loading && (
        <ActivityIndicator size="small" color="#4CAF50" style={{ marginTop: 8 }} />
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modal: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '80%',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#212121',
  },
  closeButton: {
    padding: 8,
  },
  closeText: {
    fontSize: 24,
    color: '#757575',
  },
  summary: {
    padding: 16,
    backgroundColor: '#F5F5F5',
  },
  summaryTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#424242',
    marginBottom: 8,
  },
  progressBar: {
    height: 8,
    backgroundColor: '#E0E0E0',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 8,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#4CAF50',
  },
  summaryText: {
    fontSize: 12,
    color: '#757575',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  featureCard: {
    backgroundColor: '#FAFAFA',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  featureHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  featureIcon: {
    fontSize: 32,
    marginRight: 12,
  },
  featureInfo: {
    flex: 1,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#212121',
    marginBottom: 4,
  },
  featureDescription: {
    fontSize: 12,
    color: '#757575',
  },
  statusBadge: {
    width: 32,
    height: 32,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  statusAvailable: {
    backgroundColor: '#E8F5E9',
  },
  statusUnavailable: {
    backgroundColor: '#FFEBEE',
  },
  statusText: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  capabilities: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  capabilitiesTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#424242',
    marginBottom: 8,
  },
  capabilityItem: {
    fontSize: 12,
    color: '#616161',
    marginBottom: 4,
    paddingLeft: 8,
  },
  footer: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  button: {
    backgroundColor: '#4CAF50',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#757575',
  },
});
