import React from 'react';
import { StyleSheet, Text, View, SafeAreaView, ScrollView, Platform, Dimensions } from 'react-native';
import { StatusBar } from 'expo-status-bar';

const { width } = Dimensions.get('window');
const isWeb = Platform.OS === 'web';

export default function App() {
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />
      
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <Text style={styles.headerTitle}>🌾 Agropulse AI</Text>
          <Text style={styles.headerSubtitle}>AI-Powered Agricultural Platform</Text>
          {isWeb && (
            <Text style={styles.headerDescription}>
              Empowering 50,000+ smallholder farmers across Africa
            </Text>
          )}
        </View>
      </View>

      <ScrollView style={styles.content} contentContainerStyle={styles.contentContainer}>
        <View style={styles.wrapper}>
        <View style={styles.card}>
          <Text style={styles.cardIcon}>🤖</Text>
          <Text style={styles.cardTitle}>AI Crop Diagnostics</Text>
          <Text style={styles.cardDescription}>
            Scan crops for diseases with 92% accuracy
          </Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardIcon}>🛒</Text>
          <Text style={styles.cardTitle}>Digital Marketplace</Text>
          <Text style={styles.cardDescription}>
            Connect directly with buyers for better prices
          </Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardIcon}>📦</Text>
          <Text style={styles.cardTitle}>Smart Storage</Text>
          <Text style={styles.cardDescription}>
            Monitor storage conditions and prevent losses
          </Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardIcon}>🌍</Text>
          <Text style={styles.cardTitle}>Regional Data</Text>
          <Text style={styles.cardDescription}>
            Weather, market prices, and satellite insights
          </Text>
        </View>

        <View style={styles.infoBox}>
          <Text style={styles.infoTitle}>✅ Frontend Setup Complete!</Text>
          <Text style={styles.infoText}>
            • 50,000+ farmers using Agropulse AI{'\n'}
            • 35% average yield increase{'\n'}
            • 60% reduction in post-harvest losses{'\n'}
            • KES 2.5B in marketplace transactions
          </Text>
        </View>

        <View style={styles.setupBox}>
          <Text style={styles.setupTitle}>📱 Next Steps:</Text>
          <Text style={styles.setupText}>
            1. Update API_BASE_URL in screen files{'\n'}
            2. Navigate to src/screens/ to see features{'\n'}
            3. Test FarmerMarketplace.js and BuyerMarketplace.js{'\n'}
            4. Configure backend connection (localhost:8000)
          </Text>
        </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#4CAF50',
    paddingVertical: isWeb ? 60 : 20,
    paddingHorizontal: 20,
    paddingTop: isWeb ? 60 : 40,
    alignItems: 'center',
    ...(isWeb && {
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    }),
  },
  headerContent: {
    maxWidth: isWeb ? 1200 : '100%',
    width: '100%',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: isWeb ? 48 : 32,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
    textAlign: 'center',
  },
  headerSubtitle: {
    fontSize: isWeb ? 20 : 16,
    color: 'rgba(255,255,255,0.95)',
    textAlign: 'center',
    marginBottom: isWeb ? 10 : 0,
  },
  headerDescription: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.85)',
    textAlign: 'center',
    marginTop: 5,
  },
  content: {
    flex: 1,
  },
  contentContainer: {
    padding: isWeb ? 40 : 15,
    alignItems: 'center',
  },
  wrapper: {
    maxWidth: isWeb ? 1200 : '100%',
    width: '100%',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: isWeb ? 30 : 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    ...(isWeb && {
      boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
      transition: 'transform 0.2s, box-shadow 0.2s',
      cursor: 'default',
    }),
  },
  cardIcon: {
    fontSize: isWeb ? 48 : 40,
    marginBottom: 12,
  },
  cardTitle: {
    fontSize: isWeb ? 24 : 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  cardDescription: {
    fontSize: isWeb ? 16 : 14,
    color: '#666',
    lineHeight: isWeb ? 24 : 20,
  },
  infoBox: {
    backgroundColor: '#E8F5E9',
    borderRadius: 12,
    padding: isWeb ? 30 : 20,
    marginBottom: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#4CAF50',
    ...(isWeb && {
      boxShadow: '0 2px 6px rgba(76, 175, 80, 0.1)',
    }),
  },
  infoTitle: {
    fontSize: isWeb ? 22 : 18,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginBottom: 12,
  },
  infoText: {
    fontSize: isWeb ? 16 : 14,
    color: '#1B5E20',
    lineHeight: isWeb ? 26 : 22,
  },
  setupBox: {
    backgroundColor: '#FFF3E0',
    borderRadius: 12,
    padding: isWeb ? 30 : 20,
    marginBottom: 30,
    borderLeftWidth: 4,
    borderLeftColor: '#FF9800',
    ...(isWeb && {
      boxShadow: '0 2px 6px rgba(255, 152, 0, 0.1)',
    }),
  },
  setupTitle: {
    fontSize: isWeb ? 22 : 18,
    fontWeight: 'bold',
    color: '#E65100',
    marginBottom: 12,
  },
  setupText: {
    fontSize: isWeb ? 16 : 14,
    color: '#BF360C',
    lineHeight: isWeb ? 26 : 22,
  },
});
