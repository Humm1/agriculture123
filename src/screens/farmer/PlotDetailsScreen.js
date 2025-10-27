import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
  Image,
  Alert
} from "react-native";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import { useAuth } from "../../context/AuthContext";

const API_BASE = "https://urchin-app-86rjy.ondigitalocean.app/api/advanced-growth";

export default function PlotDetailsScreen({ route, navigation }) {
  const { user } = useAuth();
  const { plotId } = route.params;
  const [plotData, setPlotData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview'); // overview, health, pests, calendar

  useEffect(() => {
    loadPlotDetails();
  }, [plotId]);

  const loadPlotDetails = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/plots/${plotId}?user_id=${user.id}`);
      const data = await response.json();
      
      if (data.success) {
        setPlotData(data);
      } else {
        Alert.alert("Error", "Failed to load plot details");
      }
    } catch (error) {
      console.error("Error loading plot details:", error);
      Alert.alert("Error", "Failed to load plot details");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#4CAF50" />
        <Text style={styles.loadingText}>Loading plot details...</Text>
      </View>
    );
  }

  if (!plotData || !plotData.plot) {
    return (
      <View style={styles.centerContainer}>
        <MaterialCommunityIcons name="alert-circle" size={64} color="#FF9800" />
        <Text style={styles.errorText}>Plot not found</Text>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backButtonText}>Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const { plot, images, upcoming_events, recent_logs } = plotData;

  // Extract AI analysis from the most recent images
  const soilAnalysis = images.find(img => img.image_type === 'soil' && img.ai_analysis);
  const pestAnalysis = images.find(img => img.image_type === 'initial' && img.ai_analysis);

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backIcon}>
          <MaterialCommunityIcons name="arrow-left" size={24} color="#fff" />
        </TouchableOpacity>
        <View style={styles.headerInfo}>
          <Text style={styles.headerTitle}>{plot.crop_type}</Text>
          <Text style={styles.headerSubtitle}>
            {plot.area_size} {plot.area_unit} • Planted: {new Date(plot.planting_date).toLocaleDateString()}
          </Text>
        </View>
        {plot.is_demo && (
          <View style={styles.demoBadge}>
            <Text style={styles.demoBadgeText}>DEMO</Text>
          </View>
        )}
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'overview' && styles.activeTab]}
          onPress={() => setActiveTab('overview')}
        >
          <MaterialCommunityIcons 
            name="view-dashboard" 
            size={20} 
            color={activeTab === 'overview' ? '#4CAF50' : '#666'} 
          />
          <Text style={[styles.tabText, activeTab === 'overview' && styles.activeTabText]}>
            Overview
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tab, activeTab === 'health' && styles.activeTab]}
          onPress={() => setActiveTab('health')}
        >
          <MaterialCommunityIcons 
            name="heart-pulse" 
            size={20} 
            color={activeTab === 'health' ? '#4CAF50' : '#666'} 
          />
          <Text style={[styles.tabText, activeTab === 'health' && styles.activeTabText]}>
            Health
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tab, activeTab === 'pests' && styles.activeTab]}
          onPress={() => setActiveTab('pests')}
        >
          <MaterialCommunityIcons 
            name="bug" 
            size={20} 
            color={activeTab === 'pests' ? '#4CAF50' : '#666'} 
          />
          <Text style={[styles.tabText, activeTab === 'pests' && styles.activeTabText]}>
            Pests
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tab, activeTab === 'calendar' && styles.activeTab]}
          onPress={() => setActiveTab('calendar')}
        >
          <MaterialCommunityIcons 
            name="calendar-check" 
            size={20} 
            color={activeTab === 'calendar' ? '#4CAF50' : '#666'} 
          />
          <Text style={[styles.tabText, activeTab === 'calendar' && styles.activeTabText]}>
            Calendar
          </Text>
        </TouchableOpacity>
      </View>

      {/* Content */}
      <ScrollView style={styles.content}>
        {activeTab === 'overview' && <OverviewTab plot={plot} images={images} logs={recent_logs} />}
        {activeTab === 'health' && <HealthTab soilAnalysis={soilAnalysis} plot={plot} />}
        {activeTab === 'pests' && <PestsTab pestAnalysis={pestAnalysis} images={images} />}
        {activeTab === 'calendar' && <CalendarTab events={upcoming_events} plotId={plotId} />}
      </ScrollView>
    </View>
  );
}

// ============================================================
// OVERVIEW TAB
// ============================================================
function OverviewTab({ plot, images, logs }) {
  return (
    <View style={styles.tabContent}>
      {/* Plot Info Card */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Plot Information</Text>
        <InfoRow icon="sprout" label="Crop" value={plot.crop_type} />
        {plot.variety && <InfoRow icon="leaf" label="Variety" value={plot.variety} />}
        <InfoRow icon="calendar" label="Planted" value={new Date(plot.planting_date).toLocaleDateString()} />
        <InfoRow icon="ruler-square" label="Area" value={`${plot.area_size} ${plot.area_unit}`} />
        <InfoRow icon="map-marker" label="Location" value={`${plot.latitude?.toFixed(4)}, ${plot.longitude?.toFixed(4)}`} />
      </View>

      {/* Images Gallery */}
      {images.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Plot Images ({images.length})</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.imageGallery}>
            {images.map((img, index) => (
              <View key={index} style={styles.imageContainer}>
                <Image source={{ uri: img.image_url }} style={styles.galleryImage} />
                <Text style={styles.imageLabel}>{img.image_type}</Text>
                <Text style={styles.imageDate}>{new Date(img.captured_at).toLocaleDateString()}</Text>
              </View>
            ))}
          </ScrollView>
        </View>
      )}

      {/* Recent Activity */}
      {logs.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Recent Activity</Text>
          {logs.map((log, index) => (
            <View key={index} style={styles.logItem}>
              <Text style={styles.logDate}>{new Date(log.timestamp).toLocaleDateString()}</Text>
              <Text style={styles.logText}>{log.notes || 'Growth log entry'}</Text>
            </View>
          ))}
        </View>
      )}
    </View>
  );
}

// ============================================================
// HEALTH METRICS TAB
// ============================================================
function HealthTab({ soilAnalysis, plot }) {
  const soilData = soilAnalysis?.ai_analysis?.soil_health;

  return (
    <View style={styles.tabContent}>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Soil Health Analysis</Text>
        
        {soilData ? (
          <>
            {/* Fertility Score */}
            <View style={styles.metricContainer}>
              <Text style={styles.metricLabel}>Fertility Score</Text>
              <View style={styles.scoreContainer}>
                <View style={[styles.scoreBar, { width: `${(soilData.fertility_score / 10) * 100}%` }]} />
                <Text style={styles.scoreText}>{soilData.fertility_score}/10</Text>
              </View>
            </View>

            {/* Soil Type */}
            <InfoRow icon="layers" label="Soil Type" value={soilData.soil_type || 'Unknown'} />
            
            {/* Nutrients */}
            {soilData.nutrients && (
              <>
                <Text style={styles.sectionTitle}>Nutrient Levels</Text>
                <InfoRow icon="alpha-n-circle" label="Nitrogen (N)" value={soilData.nutrients.nitrogen || 'N/A'} />
                <InfoRow icon="alpha-p-circle" label="Phosphorus (P)" value={soilData.nutrients.phosphorus || 'N/A'} />
                <InfoRow icon="alpha-k-circle" label="Potassium (K)" value={soilData.nutrients.potassium || 'N/A'} />
              </>
            )}

            {/* pH & Texture */}
            {soilData.ph_estimate && (
              <InfoRow icon="ph" label="pH Level" value={soilData.ph_estimate} />
            )}
            {soilData.texture && (
              <InfoRow icon="texture" label="Texture" value={soilData.texture} />
            )}
          </>
        ) : (
          <View style={styles.emptyState}>
            <MaterialCommunityIcons name="test-tube" size={48} color="#ccc" />
            <Text style={styles.emptyText}>No soil analysis available</Text>
            <Text style={styles.emptySubtext}>Upload soil images to get AI-powered insights</Text>
          </View>
        )}
      </View>

      {/* Recommendations */}
      {soilData?.recommendations && soilData.recommendations.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Recommendations</Text>
          {soilData.recommendations.map((rec, index) => (
            <View key={index} style={styles.recommendationItem}>
              <MaterialCommunityIcons name="lightbulb" size={20} color="#FFC107" />
              <Text style={styles.recommendationText}>{rec}</Text>
            </View>
          ))}
        </View>
      )}
    </View>
  );
}

// ============================================================
// PESTS & DISEASE TAB
// ============================================================
function PestsTab({ pestAnalysis, images }) {
  const pestData = pestAnalysis?.ai_analysis?.pest_disease_scan;

  return (
    <View style={styles.tabContent}>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Pest & Disease Detection</Text>
        
        {pestData ? (
          <>
            {/* Health Status */}
            <View style={styles.healthStatusContainer}>
              <MaterialCommunityIcons 
                name={pestData.health_status === 'healthy' ? 'check-circle' : 'alert-circle'} 
                size={48} 
                color={pestData.health_status === 'healthy' ? '#4CAF50' : '#FF5722'} 
              />
              <Text style={[
                styles.healthStatusText,
                { color: pestData.health_status === 'healthy' ? '#4CAF50' : '#FF5722' }
              ]}>
                {pestData.health_status?.toUpperCase() || 'UNKNOWN'}
              </Text>
              <Text style={styles.confidenceText}>
                Confidence: {(pestData.confidence * 100).toFixed(0)}%
              </Text>
            </View>

            {/* Risk Level */}
            {pestData.risk_level && (
              <View style={[
                styles.riskBadge,
                { backgroundColor: getRiskColor(pestData.risk_level) }
              ]}>
                <Text style={styles.riskText}>Risk Level: {pestData.risk_level}</Text>
              </View>
            )}

            {/* Detected Issues */}
            {pestData.detected_issues && pestData.detected_issues.length > 0 && (
              <>
                <Text style={styles.sectionTitle}>Detected Issues</Text>
                {pestData.detected_issues.map((issue, index) => (
                  <View key={index} style={styles.issueItem}>
                    <MaterialCommunityIcons name="bug" size={20} color="#FF5722" />
                    <View style={styles.issueContent}>
                      <Text style={styles.issueName}>{issue.name || issue}</Text>
                      {issue.severity && (
                        <Text style={styles.issueSeverity}>Severity: {issue.severity}</Text>
                      )}
                      {issue.treatment && (
                        <Text style={styles.issueTreatment}>{issue.treatment}</Text>
                      )}
                    </View>
                  </View>
                ))}
              </>
            )}
          </>
        ) : (
          <View style={styles.emptyState}>
            <MaterialCommunityIcons name="bug-outline" size={48} color="#ccc" />
            <Text style={styles.emptyText}>No pest analysis available</Text>
            <Text style={styles.emptySubtext}>Upload crop images to detect pests and diseases</Text>
          </View>
        )}
      </View>

      {/* Scan History */}
      {images.filter(img => img.ai_analysis?.pest_disease_scan).length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Scan History</Text>
          {images
            .filter(img => img.ai_analysis?.pest_disease_scan)
            .map((img, index) => (
              <View key={index} style={styles.scanHistoryItem}>
                <Image source={{ uri: img.image_url }} style={styles.scanThumb} />
                <View style={styles.scanInfo}>
                  <Text style={styles.scanDate}>{new Date(img.captured_at).toLocaleDateString()}</Text>
                  <Text style={styles.scanStatus}>
                    {img.ai_analysis.pest_disease_scan.health_status}
                  </Text>
                </View>
              </View>
            ))}
        </View>
      )}
    </View>
  );
}

// ============================================================
// CALENDAR TAB
// ============================================================
function CalendarTab({ events, plotId }) {
  return (
    <View style={styles.tabContent}>
      {events.length > 0 ? (
        <>
          <Text style={styles.sectionHeader}>Upcoming Tasks ({events.length})</Text>
          {events.map((event, index) => (
            <View key={index} style={styles.eventCard}>
              <View style={styles.eventHeader}>
                <MaterialCommunityIcons 
                  name={getEventIcon(event.event_type)} 
                  size={24} 
                  color="#4CAF50" 
                />
                <View style={styles.eventInfo}>
                  <Text style={styles.eventTitle}>{event.practice_name}</Text>
                  <Text style={styles.eventDate}>
                    {new Date(event.scheduled_date).toLocaleDateString()} 
                    {event.days_after_planting && ` (Day ${event.days_after_planting})`}
                  </Text>
                </View>
              </View>
              
              {event.description && (
                <Text style={styles.eventDescription}>{event.description}</Text>
              )}
              
              {event.estimated_labor_hours && (
                <View style={styles.eventMeta}>
                  <MaterialCommunityIcons name="clock-outline" size={16} color="#666" />
                  <Text style={styles.eventMetaText}>
                    Est. {event.estimated_labor_hours} hours
                  </Text>
                </View>
              )}

              {event.local_methods && (
                <View style={styles.methodsContainer}>
                  <Text style={styles.methodsTitle}>Local Methods:</Text>
                  <Text style={styles.methodsText}>{event.local_methods}</Text>
                </View>
              )}
            </View>
          ))}
        </>
      ) : (
        <View style={styles.emptyState}>
          <MaterialCommunityIcons name="calendar-blank" size={48} color="#ccc" />
          <Text style={styles.emptyText}>No scheduled events</Text>
          <Text style={styles.emptySubtext}>Events will appear here as you manage your plot</Text>
        </View>
      )}
    </View>
  );
}

// ============================================================
// UTILITY COMPONENTS
// ============================================================
function InfoRow({ icon, label, value }) {
  return (
    <View style={styles.infoRow}>
      <MaterialCommunityIcons name={icon} size={20} color="#666" />
      <Text style={styles.infoLabel}>{label}:</Text>
      <Text style={styles.infoValue}>{value}</Text>
    </View>
  );
}

function getRiskColor(risk) {
  const colors = {
    low: '#4CAF50',
    medium: '#FFC107',
    high: '#FF9800',
    critical: '#FF5722'
  };
  return colors[risk?.toLowerCase()] || '#999';
}

function getEventIcon(eventType) {
  const icons = {
    farm_practice: 'shovel',
    photo_reminder: 'camera',
    treatment_applications: 'spray',
    urgent_practices: 'alert-circle',
    alert_actions: 'bell-alert'
  };
  return icons[eventType] || 'calendar';
}

// ============================================================
// STYLES
// ============================================================
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  header: {
    backgroundColor: '#4CAF50',
    padding: 15,
    paddingTop: 40,
    flexDirection: 'row',
    alignItems: 'center',
  },
  backIcon: {
    marginRight: 10,
  },
  headerInfo: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.9,
    marginTop: 2,
  },
  demoBadge: {
    backgroundColor: '#FF9800',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  demoBadgeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  tab: {
    flex: 1,
    flexDirection: 'column',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  activeTab: {
    borderBottomColor: '#4CAF50',
  },
  tabText: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  activeTabText: {
    color: '#4CAF50',
    fontWeight: '600',
  },
  content: {
    flex: 1,
  },
  tabContent: {
    padding: 15,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginTop: 15,
    marginBottom: 10,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  infoLabel: {
    fontSize: 14,
    color: '#666',
    marginLeft: 8,
    flex: 1,
  },
  infoValue: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
    flex: 2,
  },
  imageGallery: {
    marginTop: 10,
  },
  imageContainer: {
    marginRight: 10,
    alignItems: 'center',
  },
  galleryImage: {
    width: 120,
    height: 120,
    borderRadius: 8,
  },
  imageLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  imageDate: {
    fontSize: 10,
    color: '#999',
  },
  logItem: {
    borderLeftWidth: 3,
    borderLeftColor: '#4CAF50',
    paddingLeft: 10,
    marginBottom: 10,
  },
  logDate: {
    fontSize: 12,
    color: '#666',
    fontWeight: '600',
  },
  logText: {
    fontSize: 14,
    color: '#333',
    marginTop: 2,
  },
  metricContainer: {
    marginBottom: 15,
  },
  metricLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  scoreContainer: {
    position: 'relative',
    height: 30,
    backgroundColor: '#f0f0f0',
    borderRadius: 15,
    overflow: 'hidden',
  },
  scoreBar: {
    height: '100%',
    backgroundColor: '#4CAF50',
  },
  scoreText: {
    position: 'absolute',
    right: 10,
    top: 5,
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
  },
  healthStatusContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  healthStatusText: {
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 10,
  },
  confidenceText: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  riskBadge: {
    padding: 10,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 15,
  },
  riskText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 14,
  },
  issueItem: {
    flexDirection: 'row',
    marginBottom: 15,
    padding: 10,
    backgroundColor: '#FFF3E0',
    borderRadius: 8,
  },
  issueContent: {
    marginLeft: 10,
    flex: 1,
  },
  issueName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  issueSeverity: {
    fontSize: 12,
    color: '#FF5722',
    marginTop: 2,
  },
  issueTreatment: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  recommendationItem: {
    flexDirection: 'row',
    marginBottom: 10,
    padding: 10,
    backgroundColor: '#FFFDE7',
    borderRadius: 8,
  },
  recommendationText: {
    marginLeft: 10,
    fontSize: 14,
    color: '#333',
    flex: 1,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
    marginTop: 15,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#bbb',
    marginTop: 5,
    textAlign: 'center',
  },
  eventCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    marginBottom: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#4CAF50',
  },
  eventHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  eventInfo: {
    marginLeft: 10,
    flex: 1,
  },
  eventTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  eventDate: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  eventDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  eventMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
  },
  eventMetaText: {
    fontSize: 12,
    color: '#666',
    marginLeft: 5,
  },
  methodsContainer: {
    marginTop: 10,
    padding: 10,
    backgroundColor: '#F1F8E9',
    borderRadius: 6,
  },
  methodsTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#558B2F',
    marginBottom: 5,
  },
  methodsText: {
    fontSize: 12,
    color: '#333',
  },
  sectionHeader: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  scanHistoryItem: {
    flexDirection: 'row',
    marginBottom: 10,
    padding: 10,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
  },
  scanThumb: {
    width: 60,
    height: 60,
    borderRadius: 8,
  },
  scanInfo: {
    marginLeft: 10,
    justifyContent: 'center',
  },
  scanDate: {
    fontSize: 14,
    color: '#333',
    fontWeight: '600',
  },
  scanStatus: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  errorText: {
    fontSize: 18,
    color: '#666',
    marginTop: 15,
  },
  backButton: {
    marginTop: 20,
    backgroundColor: '#4CAF50',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  backButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
