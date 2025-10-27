import React, { useState } from "react";
import { View, Text, TouchableOpacity, ScrollView, StyleSheet, Platform } from "react-native";
import { MaterialCommunityIcons } from "@expo/vector-icons";

/**
 * Comprehensive AI Analysis Dashboard Component
 * Displays JSON analysis data for Soil Health and Pest/Disease Detection
 */
export default function AIAnalysisDashboard({ soilAnalysis, pestAnalysis }) {
  const [showSoilJSON, setShowSoilJSON] = useState(false);
  const [showPestJSON, setShowPestJSON] = useState(false);
  const [activeTab, setActiveTab] = useState('visual'); // 'visual' or 'json'

  return (
    <View style={styles.container}>
      {/* Tab Selector */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'visual' && styles.activeTab]}
          onPress={() => setActiveTab('visual')}
        >
          <MaterialCommunityIcons 
            name="chart-box" 
            size={20} 
            color={activeTab === 'visual' ? '#4CAF50' : '#666'} 
          />
          <Text style={[styles.tabText, activeTab === 'visual' && styles.activeTabText]}>
            Visual Dashboard
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.tab, activeTab === 'json' && styles.activeTab]}
          onPress={() => setActiveTab('json')}
        >
          <MaterialCommunityIcons 
            name="code-json" 
            size={20} 
            color={activeTab === 'json' ? '#4CAF50' : '#666'} 
          />
          <Text style={[styles.tabText, activeTab === 'json' && styles.activeTabText]}>
            JSON Data
          </Text>
        </TouchableOpacity>
      </View>

      {/* JSON View */}
      {activeTab === 'json' && (
        <View style={styles.jsonContainer}>
          {/* Soil Health JSON */}
          {soilAnalysis && (
            <View style={styles.jsonSection}>
              <TouchableOpacity
                style={styles.jsonHeader}
                onPress={() => setShowSoilJSON(!showSoilJSON)}
              >
                <View style={styles.jsonHeaderLeft}>
                  <MaterialCommunityIcons name="leaf" size={24} color="#4CAF50" />
                  <Text style={styles.jsonHeaderTitle}>Soil Health Analysis</Text>
                </View>
                <MaterialCommunityIcons 
                  name={showSoilJSON ? "chevron-up" : "chevron-down"} 
                  size={24} 
                  color="#4CAF50" 
                />
              </TouchableOpacity>

              {showSoilJSON && (
                <View style={styles.jsonContent}>
                  <View style={styles.jsonStats}>
                    <View style={styles.statItem}>
                      <Text style={styles.statLabel}>Fertility Score</Text>
                      <Text style={styles.statValue}>{soilAnalysis.fertility_score}/10</Text>
                    </View>
                    <View style={styles.statItem}>
                      <Text style={styles.statLabel}>pH Level</Text>
                      <Text style={styles.statValue}>{soilAnalysis.ph_estimate || 'N/A'}</Text>
                    </View>
                    <View style={styles.statItem}>
                      <Text style={styles.statLabel}>Soil Type</Text>
                      <Text style={styles.statValue}>{soilAnalysis.soil_type || 'Unknown'}</Text>
                    </View>
                  </View>

                  <ScrollView 
                    horizontal 
                    style={styles.jsonScrollView}
                    nestedScrollEnabled={true}
                  >
                    <View style={styles.jsonCodeContainer}>
                      <Text style={styles.jsonCode}>
                        {JSON.stringify(soilAnalysis, null, 2)}
                      </Text>
                    </View>
                  </ScrollView>

                  <View style={styles.jsonActions}>
                    <TouchableOpacity 
                      style={styles.actionButton}
                      onPress={() => {
                        // Copy to clipboard functionality
                        console.log("Copy soil JSON:", JSON.stringify(soilAnalysis, null, 2));
                      }}
                    >
                      <MaterialCommunityIcons name="content-copy" size={16} color="#2196F3" />
                      <Text style={styles.actionButtonText}>Copy JSON</Text>
                    </TouchableOpacity>
                    
                    <TouchableOpacity 
                      style={styles.actionButton}
                      onPress={() => {
                        // Export functionality
                        console.log("Export soil JSON");
                      }}
                    >
                      <MaterialCommunityIcons name="download" size={16} color="#2196F3" />
                      <Text style={styles.actionButtonText}>Export</Text>
                    </TouchableOpacity>
                  </View>
                </View>
              )}
            </View>
          )}

          {/* Pest & Disease JSON */}
          {pestAnalysis && (
            <View style={styles.jsonSection}>
              <TouchableOpacity
                style={styles.jsonHeader}
                onPress={() => setShowPestJSON(!showPestJSON)}
              >
                <View style={styles.jsonHeaderLeft}>
                  <MaterialCommunityIcons name="bug" size={24} color="#FF5722" />
                  <Text style={styles.jsonHeaderTitle}>Pest & Disease Detection</Text>
                </View>
                <MaterialCommunityIcons 
                  name={showPestJSON ? "chevron-up" : "chevron-down"} 
                  size={24} 
                  color="#FF5722" 
                />
              </TouchableOpacity>

              {showPestJSON && (
                <View style={styles.jsonContent}>
                  <View style={styles.jsonStats}>
                    <View style={styles.statItem}>
                      <Text style={styles.statLabel}>Health Status</Text>
                      <Text style={[styles.statValue, { 
                        color: pestAnalysis.health_status === 'healthy' ? '#4CAF50' : '#FF5722' 
                      }]}>
                        {pestAnalysis.health_status?.toUpperCase()}
                      </Text>
                    </View>
                    <View style={styles.statItem}>
                      <Text style={styles.statLabel}>Pests Found</Text>
                      <Text style={styles.statValue}>
                        {pestAnalysis.detected_pests?.length || 0}
                      </Text>
                    </View>
                    <View style={styles.statItem}>
                      <Text style={styles.statLabel}>Diseases Found</Text>
                      <Text style={styles.statValue}>
                        {pestAnalysis.detected_diseases?.length || 0}
                      </Text>
                    </View>
                    <View style={styles.statItem}>
                      <Text style={styles.statLabel}>Risk Level</Text>
                      <Text style={[styles.statValue, { 
                        color: pestAnalysis.risk_level === 'high' ? '#F44336' : 
                               pestAnalysis.risk_level === 'moderate' ? '#FF9800' : '#4CAF50'
                      }]}>
                        {pestAnalysis.risk_level?.toUpperCase() || 'LOW'}
                      </Text>
                    </View>
                  </View>

                  <ScrollView 
                    horizontal 
                    style={styles.jsonScrollView}
                    nestedScrollEnabled={true}
                  >
                    <View style={styles.jsonCodeContainer}>
                      <Text style={styles.jsonCode}>
                        {JSON.stringify(pestAnalysis, null, 2)}
                      </Text>
                    </View>
                  </ScrollView>

                  <View style={styles.jsonActions}>
                    <TouchableOpacity 
                      style={styles.actionButton}
                      onPress={() => {
                        console.log("Copy pest JSON:", JSON.stringify(pestAnalysis, null, 2));
                      }}
                    >
                      <MaterialCommunityIcons name="content-copy" size={16} color="#2196F3" />
                      <Text style={styles.actionButtonText}>Copy JSON</Text>
                    </TouchableOpacity>
                    
                    <TouchableOpacity 
                      style={styles.actionButton}
                      onPress={() => {
                        console.log("Export pest JSON");
                      }}
                    >
                      <MaterialCommunityIcons name="download" size={16} color="#2196F3" />
                      <Text style={styles.actionButtonText}>Export</Text>
                    </TouchableOpacity>
                  </View>
                </View>
              )}
            </View>
          )}

          {/* Combined Analysis Summary */}
          {(soilAnalysis || pestAnalysis) && (
            <View style={styles.summarySection}>
              <View style={styles.summaryHeader}>
                <MaterialCommunityIcons name="chart-line" size={24} color="#2196F3" />
                <Text style={styles.summaryTitle}>Analysis Summary</Text>
              </View>
              
              <View style={styles.summaryGrid}>
                {soilAnalysis && (
                  <>
                    <View style={styles.summaryCard}>
                      <Text style={styles.summaryLabel}>Soil Fertility</Text>
                      <Text style={styles.summaryValue}>
                        {soilAnalysis.fertility_score}/10
                      </Text>
                      <View style={styles.progressBar}>
                        <View 
                          style={[
                            styles.progressFill, 
                            { width: `${(soilAnalysis.fertility_score / 10) * 100}%` }
                          ]} 
                        />
                      </View>
                    </View>

                    {soilAnalysis.nutrients && (
                      <>
                        <View style={styles.summaryCard}>
                          <Text style={styles.summaryLabel}>Nitrogen (N)</Text>
                          <Text style={styles.summaryValue}>
                            {soilAnalysis.nutrients.nitrogen || 'N/A'}
                          </Text>
                        </View>
                        <View style={styles.summaryCard}>
                          <Text style={styles.summaryLabel}>Phosphorus (P)</Text>
                          <Text style={styles.summaryValue}>
                            {soilAnalysis.nutrients.phosphorus || 'N/A'}
                          </Text>
                        </View>
                        <View style={styles.summaryCard}>
                          <Text style={styles.summaryLabel}>Potassium (K)</Text>
                          <Text style={styles.summaryValue}>
                            {soilAnalysis.nutrients.potassium || 'N/A'}
                          </Text>
                        </View>
                      </>
                    )}
                  </>
                )}

                {pestAnalysis && (
                  <>
                    <View style={styles.summaryCard}>
                      <Text style={styles.summaryLabel}>Health Score</Text>
                      <Text style={styles.summaryValue}>
                        {pestAnalysis.health_metrics?.health_score || 'N/A'}/100
                      </Text>
                      {pestAnalysis.health_metrics?.health_score && (
                        <View style={styles.progressBar}>
                          <View 
                            style={[
                              styles.progressFill, 
                              { 
                                width: `${pestAnalysis.health_metrics.health_score}%`,
                                backgroundColor: pestAnalysis.health_metrics.health_score > 70 ? '#4CAF50' : '#FF9800'
                              }
                            ]} 
                          />
                        </View>
                      )}
                    </View>

                    <View style={styles.summaryCard}>
                      <Text style={styles.summaryLabel}>Growth Stage</Text>
                      <Text style={styles.summaryValue}>
                        {pestAnalysis.growth_stage?.stage?.toUpperCase() || 'Unknown'}
                      </Text>
                    </View>

                    <View style={styles.summaryCard}>
                      <Text style={styles.summaryLabel}>Immediate Actions</Text>
                      <Text style={[styles.summaryValue, { color: '#F44336' }]}>
                        {pestAnalysis.immediate_actions?.length || 0}
                      </Text>
                    </View>
                  </>
                )}
              </View>
            </View>
          )}

          {!soilAnalysis && !pestAnalysis && (
            <View style={styles.emptyState}>
              <MaterialCommunityIcons name="alert-circle-outline" size={64} color="#999" />
              <Text style={styles.emptyStateText}>No AI analysis data available</Text>
              <Text style={styles.emptyStateSubtext}>
                Upload plot images to generate AI-powered insights
              </Text>
            </View>
          )}
        </View>
      )}

      {/* Visual View Placeholder */}
      {activeTab === 'visual' && (
        <View style={styles.visualContainer}>
          <Text style={styles.visualPlaceholder}>
            Visual dashboard will render charts and graphs here
          </Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  tab: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 15,
    gap: 8,
  },
  activeTab: {
    borderBottomWidth: 3,
    borderBottomColor: '#4CAF50',
  },
  tabText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  activeTabText: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  jsonContainer: {
    padding: 15,
  },
  jsonSection: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 15,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  jsonHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#f9f9f9',
  },
  jsonHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  jsonHeaderTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  jsonContent: {
    padding: 15,
  },
  jsonStats: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 15,
    gap: 10,
  },
  statItem: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#f5f5f5',
    padding: 12,
    borderRadius: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 5,
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  jsonScrollView: {
    maxHeight: 300,
    backgroundColor: '#1E1E1E',
    borderRadius: 8,
    marginBottom: 15,
  },
  jsonCodeContainer: {
    padding: 15,
  },
  jsonCode: {
    fontFamily: Platform.OS === 'ios' ? 'Courier' : 'monospace',
    fontSize: 11,
    color: '#D4D4D4',
    lineHeight: 16,
  },
  jsonActions: {
    flexDirection: 'row',
    gap: 10,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#E3F2FD',
    padding: 10,
    borderRadius: 8,
    gap: 5,
  },
  actionButtonText: {
    color: '#2196F3',
    fontWeight: '600',
    fontSize: 13,
  },
  summarySection: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  summaryHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 15,
  },
  summaryTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  summaryGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  summaryCard: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#f9f9f9',
    padding: 15,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  summaryLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
  },
  summaryValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  progressBar: {
    height: 6,
    backgroundColor: '#e0e0e0',
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#4CAF50',
    borderRadius: 3,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
  },
  emptyStateText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#666',
    marginTop: 15,
    marginBottom: 5,
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
  visualContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  visualPlaceholder: {
    fontSize: 16,
    color: '#999',
    textAlign: 'center',
  },
});
