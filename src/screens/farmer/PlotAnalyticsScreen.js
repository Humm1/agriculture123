import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl
} from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { LineChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';

const screenWidth = Dimensions.get('window').width;
const BACKEND_URL = 'https://urchin-app-86rjy.ondigitalocean.app/api';

export default function PlotAnalyticsScreen({ route, navigation }) {
  const { plotId, plotName } = route.params;
  
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const [healthHistory, setHealthHistory] = useState([]);
  const [diseases, setDiseases] = useState([]);
  const [fertilizer, setFertilizer] = useState(null);
  const [selectedTab, setSelectedTab] = useState('overview');
  
  useEffect(() => {
    loadAnalytics();
  }, [plotId]);
  
  const loadAnalytics = async () => {
    try {
      setLoading(true);
      
      // Fetch all data in parallel
      const [analyticsRes, healthRes, diseasesRes] = await Promise.all([
        fetch(`${BACKEND_URL}/plot-analytics/plots/${plotId}/analytics`),
        fetch(`${BACKEND_URL}/plot-analytics/plots/${plotId}/health-history?days=30`),
        fetch(`${BACKEND_URL}/plot-analytics/plots/${plotId}/disease-timeline`)
      ]);
      
      const analyticsData = await analyticsRes.json();
      const healthData = await healthRes.json();
      const diseasesData = await diseasesRes.json();
      
      if (analyticsData.success) {
        setAnalytics(analyticsData.analytics);
      }
      
      if (healthData.success) {
        setHealthHistory(healthData.history);
      }
      
      if (diseasesData.success) {
        setDiseases(diseasesData.diseases);
      }
      
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };
  
  const onRefresh = () => {
    setRefreshing(true);
    loadAnalytics();
  };
  
  const renderHealthScore = (score) => {
    const color = score > 70 ? '#4CAF50' : score > 50 ? '#FF9800' : '#f44336';
    return (
      <View style={styles.scoreContainer}>
        <Text style={[styles.scoreValue, { color }]}>{score.toFixed(0)}</Text>
        <Text style={styles.scoreLabel}>/100</Text>
      </View>
    );
  };
  
  const renderOverview = () => {
    if (!analytics) return null;
    
    const latestHealth = analytics.latest_health || {};
    const activeDiseases = analytics.active_diseases || [];
    const fertilizerPlan = analytics.fertilizer_plan || {};
    
    return (
      <View>
        {/* Health Scores */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>🩺 Crop Health Status</Text>
          <View style={styles.healthGrid}>
            <View style={styles.healthItem}>
              <Text style={styles.healthLabel}>Overall Health</Text>
              {renderHealthScore(latestHealth.overall_health_score || 0)}
            </View>
            <View style={styles.healthItem}>
              <Text style={styles.healthLabel}>Leaf Health</Text>
              {renderHealthScore(latestHealth.leaf_health_score || 0)}
            </View>
            <View style={styles.healthItem}>
              <Text style={styles.healthLabel}>Stem Health</Text>
              {renderHealthScore(latestHealth.stem_health_score || 0)}
            </View>
            <View style={styles.healthItem}>
              <Text style={styles.healthLabel}>vs Optimal</Text>
              {renderHealthScore(latestHealth.vs_optimal_percentage || 0)}
            </View>
          </View>
        </View>
        
        {/* Active Diseases */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>🦠 Active Diseases</Text>
            <View style={[
              styles.badge,
              activeDiseases.length === 0 ? styles.badgeSuccess : styles.badgeWarning
            ]}>
              <Text style={styles.badgeText}>{activeDiseases.length}</Text>
            </View>
          </View>
          
          {activeDiseases.length === 0 ? (
            <Text style={styles.emptyText}>No active diseases detected 🎉</Text>
          ) : (
            activeDiseases.map((disease, index) => (
              <View key={index} style={styles.diseaseItem}>
                <View style={styles.diseaseHeader}>
                  <Text style={styles.diseaseName}>{disease.disease_name}</Text>
                  <View style={[
                    styles.severityBadge,
                    disease.current_severity === 'high' && styles.severityHigh,
                    disease.current_severity === 'medium' && styles.severityMedium
                  ]}>
                    <Text style={styles.severityText}>{disease.current_severity}</Text>
                  </View>
                </View>
                <Text style={styles.diseaseDate}>
                  Detected: {new Date(disease.detection_date).toLocaleDateString()}
                </Text>
              </View>
            ))
          )}
        </View>
        
        {/* Fertilizer Recommendation */}
        {fertilizerPlan && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>🌾 Fertilizer Plan</Text>
            <View style={styles.fertilizerComparison}>
              <View style={styles.fertilizerOption}>
                <MaterialCommunityIcons name="leaf" size={24} color="#4CAF50" />
                <Text style={styles.fertilizerLabel}>Organic</Text>
                <Text style={styles.fertilizerCost}>
                  KES {fertilizerPlan.organic_total_cost?.toFixed(2) || 0}
                </Text>
              </View>
              
              <View style={styles.fertilizerDivider} />
              
              <View style={styles.fertilizerOption}>
                <MaterialCommunityIcons name="flask" size={24} color="#2196F3" />
                <Text style={styles.fertilizerLabel}>Inorganic</Text>
                <Text style={styles.fertilizerCost}>
                  KES {fertilizerPlan.inorganic_total_cost?.toFixed(2) || 0}
                </Text>
              </View>
            </View>
            
            <View style={styles.recommendation}>
              <Text style={styles.recommendationLabel}>Recommended:</Text>
              <Text style={styles.recommendationValue}>
                {fertilizerPlan.recommended_method?.toUpperCase() || 'N/A'}
              </Text>
            </View>
            
            <TouchableOpacity
              style={styles.detailsButton}
              onPress={() => setSelectedTab('fertilizer')}
            >
              <Text style={styles.detailsButtonText}>View Details</Text>
            </TouchableOpacity>
          </View>
        )}
        
        {/* Quick Actions */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>⚡ Quick Actions</Text>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('PlotDatasetUpload', { plotId, plotName })}
          >
            <MaterialCommunityIcons name="camera-plus" size={24} color="#4CAF50" />
            <Text style={styles.actionButtonText}>Upload New Images</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => setSelectedTab('health')}
          >
            <MaterialCommunityIcons name="chart-line" size={24} color="#2196F3" />
            <Text style={styles.actionButtonText}>View Health Trends</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  };
  
  const renderHealthTrends = () => {
    if (healthHistory.length === 0) {
      return (
        <View style={styles.card}>
          <Text style={styles.emptyText}>No health history available</Text>
        </View>
      );
    }
    
    const labels = healthHistory.map(h =>
      new Date(h.measured_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    );
    const healthScores = healthHistory.map(h => h.overall_health_score || 0);
    
    return (
      <View style={styles.card}>
        <Text style={styles.cardTitle}>📈 Health Trend (30 Days)</Text>
        <LineChart
          data={{
            labels: labels.slice(-7),  // Last 7 data points
            datasets: [{ data: healthScores.slice(-7) }]
          }}
          width={screenWidth - 60}
          height={220}
          chartConfig={{
            backgroundColor: '#fff',
            backgroundGradientFrom: '#fff',
            backgroundGradientTo: '#fff',
            decimalPlaces: 0,
            color: (opacity = 1) => `rgba(76, 175, 80, ${opacity})`,
            style: { borderRadius: 16 }
          }}
          bezier
          style={styles.chart}
        />
        
        <View style={styles.trendSummary}>
          <View style={styles.trendItem}>
            <Text style={styles.trendLabel}>Avg Health</Text>
            <Text style={styles.trendValue}>
              {(healthScores.reduce((a, b) => a + b, 0) / healthScores.length).toFixed(1)}
            </Text>
          </View>
          <View style={styles.trendItem}>
            <Text style={styles.trendLabel}>Best</Text>
            <Text style={styles.trendValue}>{Math.max(...healthScores).toFixed(1)}</Text>
          </View>
          <View style={styles.trendItem}>
            <Text style={styles.trendLabel}>Worst</Text>
            <Text style={styles.trendValue}>{Math.min(...healthScores).toFixed(1)}</Text>
          </View>
        </View>
      </View>
    );
  };
  
  const renderDiseaseTracking = () => {
    return (
      <View style={styles.card}>
        <Text style={styles.cardTitle}>🦠 Disease Timeline</Text>
        {diseases.length === 0 ? (
          <Text style={styles.emptyText}>No diseases detected</Text>
        ) : (
          diseases.map((disease, index) => (
            <View key={index} style={styles.diseaseCard}>
              <View style={styles.diseaseCardHeader}>
                <Text style={styles.diseaseCardName}>{disease.disease_name}</Text>
                <View style={[
                  styles.severityBadge,
                  disease.current_severity === 'high' && styles.severityHigh,
                  disease.current_severity === 'medium' && styles.severityMedium,
                  disease.resolution_date && styles.severityResolved
                ]}>
                  <Text style={styles.severityText}>
                    {disease.resolution_date ? 'Resolved' : disease.current_severity}
                  </Text>
                </View>
              </View>
              
              <View style={styles.diseaseInfo}>
                <Text style={styles.diseaseInfoLabel}>Detected:</Text>
                <Text style={styles.diseaseInfoValue}>
                  {new Date(disease.detection_date).toLocaleDateString()}
                </Text>
              </View>
              
              {disease.resolution_date && (
                <View style={styles.diseaseInfo}>
                  <Text style={styles.diseaseInfoLabel}>Resolved:</Text>
                  <Text style={styles.diseaseInfoValue}>
                    {new Date(disease.resolution_date).toLocaleDateString()}
                  </Text>
                </View>
              )}
              
              {disease.treatments_applied && disease.treatments_applied.length > 0 && (
                <View style={styles.treatmentsSection}>
                  <Text style={styles.treatmentsTitle}>Treatments Applied:</Text>
                  {disease.treatments_applied.map((treatment, i) => (
                    <Text key={i} style={styles.treatmentItem}>
                      • {treatment.method} (Cost: KES {treatment.cost || 'N/A'})
                    </Text>
                  ))}
                </View>
              )}
            </View>
          ))
        )}
      </View>
    );
  };
  
  const renderFertilizerDetails = () => {
    if (!fertilizer) {
      return (
        <View style={styles.card}>
          <Text style={styles.emptyText}>Loading fertilizer recommendations...</Text>
        </View>
      );
    }
    
    return (
      <View>
        <View style={styles.card}>
          <Text style={styles.cardTitle}>🌾 Nutrient Requirements</Text>
          <View style={styles.nutrientGrid}>
            <View style={styles.nutrientItem}>
              <Text style={styles.nutrientLabel}>Nitrogen (N)</Text>
              <Text style={styles.nutrientValue}>{fertilizer.nitrogen_needed} kg</Text>
            </View>
            <View style={styles.nutrientItem}>
              <Text style={styles.nutrientLabel}>Phosphorus (P)</Text>
              <Text style={styles.nutrientValue}>{fertilizer.phosphorus_needed} kg</Text>
            </View>
            <View style={styles.nutrientItem}>
              <Text style={styles.nutrientLabel}>Potassium (K)</Text>
              <Text style={styles.nutrientValue}>{fertilizer.potassium_needed} kg</Text>
            </View>
          </View>
        </View>
        
        <View style={styles.card}>
          <Text style={styles.cardTitle}>💰 Cost Comparison</Text>
          <Text style={styles.reasoning}>{fertilizer.reasoning}</Text>
          
          <View style={styles.savingsBox}>
            <Text style={styles.savingsLabel}>Potential Savings:</Text>
            <Text style={styles.savingsValue}>
              KES {Math.abs(fertilizer.cost_difference).toFixed(2)}
            </Text>
          </View>
        </View>
      </View>
    );
  };
  
  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4CAF50" />
        <Text style={styles.loadingText}>Loading analytics...</Text>
      </View>
    );
  }
  
  return (
    <View style={styles.container}>
      {/* Header with Back Button */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <MaterialCommunityIcons name="arrow-left" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{plotName} Analytics</Text>
        <View style={styles.headerRight} />
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabBar}>
        <TouchableOpacity
          style={[styles.tab, selectedTab === 'overview' && styles.tabActive]}
          onPress={() => setSelectedTab('overview')}
        >
          <Text style={[styles.tabText, selectedTab === 'overview' && styles.tabTextActive]}>
            Overview
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.tab, selectedTab === 'health' && styles.tabActive]}
          onPress={() => setSelectedTab('health')}
        >
          <Text style={[styles.tabText, selectedTab === 'health' && styles.tabTextActive]}>
            Health
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.tab, selectedTab === 'diseases' && styles.tabActive]}
          onPress={() => setSelectedTab('diseases')}
        >
          <Text style={[styles.tabText, selectedTab === 'diseases' && styles.tabTextActive]}>
            Diseases
          </Text>
        </TouchableOpacity>
      </View>
      
      {/* Content */}
      <ScrollView
        style={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {selectedTab === 'overview' && renderOverview()}
        {selectedTab === 'health' && renderHealthTrends()}
        {selectedTab === 'diseases' && renderDiseaseTracking()}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5'
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 15,
    paddingTop: 40,
    backgroundColor: '#4CAF50',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4
  },
  backButton: {
    padding: 5
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    flex: 1,
    textAlign: 'center'
  },
  headerRight: {
    width: 34
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666'
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0'
  },
  tab: {
    flex: 1,
    paddingVertical: 15,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent'
  },
  tabActive: {
    borderBottomColor: '#4CAF50'
  },
  tabText: {
    fontSize: 14,
    color: '#666'
  },
  tabTextActive: {
    color: '#4CAF50',
    fontWeight: '600'
  },
  content: {
    flex: 1,
    padding: 15
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15
  },
  healthGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between'
  },
  healthItem: {
    width: '48%',
    alignItems: 'center',
    marginBottom: 15
  },
  healthLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 5
  },
  scoreContainer: {
    flexDirection: 'row',
    alignItems: 'baseline'
  },
  scoreValue: {
    fontSize: 32,
    fontWeight: 'bold'
  },
  scoreLabel: {
    fontSize: 14,
    color: '#999',
    marginLeft: 2
  },
  badge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12
  },
  badgeSuccess: {
    backgroundColor: '#4CAF50'
  },
  badgeWarning: {
    backgroundColor: '#FF9800'
  },
  badgeText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600'
  },
  emptyText: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    padding: 20
  },
  diseaseItem: {
    padding: 12,
    backgroundColor: '#fff3cd',
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#FF9800',
    marginBottom: 10
  },
  diseaseHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5
  },
  diseaseName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333'
  },
  severityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    backgroundColor: '#4CAF50'
  },
  severityHigh: {
    backgroundColor: '#f44336'
  },
  severityMedium: {
    backgroundColor: '#FF9800'
  },
  severityResolved: {
    backgroundColor: '#9E9E9E'
  },
  severityText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase'
  },
  diseaseDate: {
    fontSize: 12,
    color: '#666'
  },
  fertilizerComparison: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15
  },
  fertilizerOption: {
    flex: 1,
    alignItems: 'center'
  },
  fertilizerLabel: {
    fontSize: 14,
    color: '#666',
    marginVertical: 5
  },
  fertilizerCost: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333'
  },
  fertilizerDivider: {
    width: 1,
    height: 60,
    backgroundColor: '#e0e0e0',
    marginHorizontal: 15
  },
  recommendation: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    backgroundColor: '#e8f5e9',
    borderRadius: 8,
    marginBottom: 10
  },
  recommendationLabel: {
    fontSize: 14,
    color: '#666',
    marginRight: 8
  },
  recommendationValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#4CAF50'
  },
  detailsButton: {
    padding: 10,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    alignItems: 'center'
  },
  detailsButtonText: {
    fontSize: 14,
    color: '#2196F3',
    fontWeight: '600'
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    marginBottom: 10
  },
  actionButtonText: {
    fontSize: 16,
    color: '#333',
    marginLeft: 15
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16
  },
  trendSummary: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 15,
    paddingTop: 15,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0'
  },
  trendItem: {
    alignItems: 'center'
  },
  trendLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 5
  },
  trendValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333'
  },
  diseaseCard: {
    padding: 15,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e0e0e0'
  },
  diseaseCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10
  },
  diseaseCardName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    flex: 1
  },
  diseaseInfo: {
    flexDirection: 'row',
    marginBottom: 5
  },
  diseaseInfoLabel: {
    fontSize: 14,
    color: '#666',
    width: 80
  },
  diseaseInfoValue: {
    fontSize: 14,
    color: '#333'
  },
  treatmentsSection: {
    marginTop: 10,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0'
  },
  treatmentsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 5
  },
  treatmentItem: {
    fontSize: 13,
    color: '#666',
    marginLeft: 5,
    marginBottom: 3
  },
  nutrientGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around'
  },
  nutrientItem: {
    alignItems: 'center'
  },
  nutrientLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 5
  },
  nutrientValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333'
  },
  reasoning: {
    fontSize: 14,
    color: '#666',
    marginBottom: 15,
    lineHeight: 20
  },
  savingsBox: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 15,
    backgroundColor: '#e8f5e9',
    borderRadius: 8
  },
  savingsLabel: {
    fontSize: 14,
    color: '#666'
  },
  savingsValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#4CAF50'
  }
});
