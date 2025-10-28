/**
 * GrowthCalendarCard Component
 * Displays AI calendar features in growth tracking screen
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';

export const CurrentStageCard = ({ currentStage, daysSincePlanting }) => {
  if (!currentStage) {
    return (
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Current Growth Stage</Text>
        <Text style={styles.noDataText}>Stage information not available</Text>
      </View>
    );
  }

  return (
    <View style={[styles.card, styles.stageCard]}>
      <Text style={styles.cardTitle}>Current Growth Stage</Text>
      <Text style={styles.stageName}>{currentStage.name}</Text>
      <Text style={styles.stageDays}>
        Day {daysSincePlanting} of {currentStage.dap_end}
      </Text>
      
      <View style={styles.progressContainer}>
        <View style={styles.progressBar}>
          <View 
            style={[
              styles.progressFill, 
              { width: `${currentStage.progress_percentage}%` }
            ]} 
          />
        </View>
        <Text style={styles.progressText}>
          {currentStage.progress_percentage.toFixed(0)}% Complete
        </Text>
      </View>

      {currentStage.practices && currentStage.practices.length > 0 && (
        <View style={styles.stagePractices}>
          <Text style={styles.practicesLabel}>Stage Practices:</Text>
          {currentStage.practices.slice(0, 3).map((practice, idx) => (
            <Text key={idx} style={styles.practiceItem}>
              • {practice.description || practice.practice}
            </Text>
          ))}
        </View>
      )}
    </View>
  );
};

export const UpcomingPracticesCard = ({ practices, onViewAll }) => {
  if (!practices || practices.length === 0) {
    return (
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Upcoming Practices</Text>
        <Text style={styles.noDataText}>No practices scheduled</Text>
      </View>
    );
  }

  return (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.cardTitle}>Upcoming Practices</Text>
        {practices.length > 3 && (
          <TouchableOpacity onPress={onViewAll}>
            <Text style={styles.viewAllText}>View All ({practices.length})</Text>
          </TouchableOpacity>
        )}
      </View>

      {practices.slice(0, 3).map((practice, index) => (
        <View key={index} style={styles.practiceCard}>
          <View style={styles.practiceHeader}>
            <Text style={styles.practiceName}>
              {practice.practice?.replace(/_/g, ' ').toUpperCase()}
            </Text>
            {practice.ai_optimized && (
              <Text style={styles.aiTag}>✨ AI</Text>
            )}
          </View>
          <Text style={styles.practiceDescription}>{practice.description}</Text>
          <View style={styles.practiceFooter}>
            <Text style={styles.practiceDate}>
              📅 {new Date(practice.scheduled_date).toLocaleDateString()}
            </Text>
            <Text style={styles.practiceDays}>
              {practice.days_until} day{practice.days_until !== 1 ? 's' : ''}
            </Text>
          </View>
          <View style={styles.practiceMetrics}>
            <Text style={styles.metricItem}>⏱️ {practice.estimated_hours}h</Text>
            <Text style={styles.metricItem}>💰 ${practice.estimated_cost}</Text>
            <Text style={[
              styles.metricItem,
              styles.priority,
              practice.priority === 'high' && styles.priorityHigh,
              practice.priority === 'medium' && styles.priorityMedium
            ]}>
              {practice.priority?.toUpperCase() || 'MODERATE'}
            </Text>
          </View>
        </View>
      ))}
    </View>
  );
};

export const MilestonesTimeline = ({ milestones }) => {
  if (!milestones || milestones.length === 0) {
    return null;
  }

  const now = new Date();

  return (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>Growth Milestones</Text>
      
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <View style={styles.timelineContainer}>
          {milestones.map((milestone, index) => {
            const milestoneDate = new Date(milestone.date);
            const isPast = milestoneDate < now;
            const isToday = milestoneDate.toDateString() === now.toDateString();
            
            return (
              <View key={index} style={styles.milestoneItem}>
                <View style={[
                  styles.milestoneIcon,
                  isPast && styles.milestoneIconPast,
                  isToday && styles.milestoneIconToday
                ]}>
                  <Text style={styles.milestoneEmoji}>{milestone.icon}</Text>
                </View>
                <Text style={styles.milestoneName}>{milestone.name}</Text>
                <Text style={styles.milestoneDate}>
                  {milestoneDate.toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric' 
                  })}
                </Text>
                <Text style={styles.milestoneDap}>DAP {milestone.dap}</Text>
                {index < milestones.length - 1 && (
                  <View style={[
                    styles.timelineConnector,
                    isPast && styles.timelineConnectorPast
                  ]} />
                )}
              </View>
            );
          })}
        </View>
      </ScrollView>
    </View>
  );
};

export const AICalendarBadge = ({ aiStatus }) => {
  if (!aiStatus) return null;

  const { features, summary } = aiStatus;
  const percentage = summary?.percentage_ready || 0;

  return (
    <View style={styles.aiBadgeContainer}>
      <View style={styles.aiBadge}>
        <Text style={styles.aiBadgeIcon}>✨</Text>
        <Text style={styles.aiBadgeText}>
          AI Calendar: {percentage.toFixed(0)}% Ready
        </Text>
      </View>
      
      {features && (
        <View style={styles.featuresRow}>
          {features.lifecycle_calendar && <FeaturePill icon="📅" label="Lifecycle" />}
          {features.pest_detection && <FeaturePill icon="🐛" label="Pest Detection" />}
          {features.disease_detection && <FeaturePill icon="🦠" label="Disease" />}
          {features.health_monitoring && <FeaturePill icon="🌿" label="Health" />}
          {features.yield_prediction && <FeaturePill icon="📊" label="Yield" />}
        </View>
      )}
    </View>
  );
};

const FeaturePill = ({ icon, label }) => (
  <View style={styles.featurePill}>
    <Text style={styles.featurePillIcon}>{icon}</Text>
    <Text style={styles.featurePillText}>{label}</Text>
  </View>
);

export const ResourceSummaryCard = ({ resourcePlan }) => {
  if (!resourcePlan) return null;

  return (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>Season Resources</Text>
      
      <View style={styles.resourceRow}>
        <View style={styles.resourceItem}>
          <Text style={styles.resourceIcon}>⏱️</Text>
          <Text style={styles.resourceLabel}>Labor</Text>
          <Text style={styles.resourceValue}>{resourcePlan.total_labor_hours}h</Text>
        </View>
        
        <View style={styles.resourceItem}>
          <Text style={styles.resourceIcon}>💰</Text>
          <Text style={styles.resourceLabel}>Cost</Text>
          <Text style={styles.resourceValue}>${resourcePlan.total_estimated_cost}</Text>
        </View>
      </View>

      {resourcePlan.inputs_needed && resourcePlan.inputs_needed.length > 0 && (
        <View style={styles.inputsContainer}>
          <Text style={styles.inputsLabel}>Inputs Needed:</Text>
          <View style={styles.inputsRow}>
            {resourcePlan.inputs_needed.slice(0, 4).map((input, idx) => (
              <Text key={idx} style={styles.inputTag}>
                {input.replace(/_/g, ' ')}
              </Text>
            ))}
          </View>
        </View>
      )}
    </View>
  );
};

export const RiskAlertsCard = ({ riskCalendar, currentDap }) => {
  if (!riskCalendar || riskCalendar.length === 0) return null;

  // Find current and upcoming risks
  const relevantRisks = riskCalendar.filter(risk => {
    const startDap = risk.dap_start || 0;
    const endDap = risk.dap_end || 999;
    return currentDap >= startDap - 7 && currentDap <= endDap + 7;
  });

  if (relevantRisks.length === 0) return null;

  return (
    <View style={[styles.card, styles.riskCard]}>
      <Text style={styles.cardTitle}>⚠️ Risk Alerts</Text>
      
      {relevantRisks.slice(0, 2).map((risk, index) => (
        <View key={index} style={styles.riskItem}>
          <Text style={styles.riskStage}>{risk.stage_name}</Text>
          {risk.risks && risk.risks.length > 0 && (
            <View style={styles.risksList}>
              {risk.risks.map((r, idx) => (
                <Text key={idx} style={styles.riskName}>
                  • {r.replace(/_/g, ' ').toUpperCase()}
                </Text>
              ))}
            </View>
          )}
          {risk.ai_detection_available && (
            <Text style={styles.aiDetection}>✨ AI Detection Available</Text>
          )}
        </View>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  stageCard: {
    borderLeftWidth: 4,
    borderLeftColor: '#4CAF50',
  },
  riskCard: {
    borderLeftWidth: 4,
    borderLeftColor: '#FF9800',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#212121',
    marginBottom: 12,
  },
  noDataText: {
    fontSize: 14,
    color: '#9E9E9E',
    fontStyle: 'italic',
  },
  stageName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginBottom: 4,
  },
  stageDays: {
    fontSize: 14,
    color: '#757575',
    marginBottom: 16,
  },
  progressContainer: {
    marginBottom: 16,
  },
  progressBar: {
    height: 8,
    backgroundColor: '#E0E0E0',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 4,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#4CAF50',
  },
  progressText: {
    fontSize: 12,
    color: '#757575',
    textAlign: 'right',
  },
  stagePractices: {
    marginTop: 12,
    padding: 12,
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
  },
  practicesLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#424242',
    marginBottom: 8,
  },
  practiceItem: {
    fontSize: 12,
    color: '#616161',
    marginBottom: 4,
  },
  viewAllText: {
    fontSize: 14,
    color: '#4CAF50',
    fontWeight: '600',
  },
  practiceCard: {
    backgroundColor: '#F5F5F5',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  practiceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  practiceName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#212121',
  },
  aiTag: {
    fontSize: 11,
    color: '#4CAF50',
    fontWeight: '600',
  },
  practiceDescription: {
    fontSize: 13,
    color: '#616161',
    marginBottom: 8,
  },
  practiceFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  practiceDate: {
    fontSize: 12,
    color: '#757575',
  },
  practiceDays: {
    fontSize: 12,
    color: '#4CAF50',
    fontWeight: '600',
  },
  practiceMetrics: {
    flexDirection: 'row',
    gap: 12,
  },
  metricItem: {
    fontSize: 11,
    color: '#616161',
  },
  priority: {
    fontWeight: '600',
  },
  priorityHigh: {
    color: '#D32F2F',
  },
  priorityMedium: {
    color: '#F57C00',
  },
  timelineContainer: {
    flexDirection: 'row',
    paddingVertical: 8,
  },
  milestoneItem: {
    alignItems: 'center',
    marginRight: 16,
    position: 'relative',
  },
  milestoneIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#E0E0E0',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  milestoneIconPast: {
    backgroundColor: '#4CAF50',
  },
  milestoneIconToday: {
    backgroundColor: '#2196F3',
  },
  milestoneEmoji: {
    fontSize: 28,
  },
  milestoneName: {
    fontSize: 12,
    fontWeight: '600',
    color: '#212121',
    textAlign: 'center',
    marginBottom: 2,
  },
  milestoneDate: {
    fontSize: 11,
    color: '#757575',
    marginBottom: 2,
  },
  milestoneDap: {
    fontSize: 10,
    color: '#9E9E9E',
  },
  timelineConnector: {
    position: 'absolute',
    top: 28,
    left: 56,
    width: 16,
    height: 2,
    backgroundColor: '#E0E0E0',
  },
  timelineConnectorPast: {
    backgroundColor: '#4CAF50',
  },
  aiBadgeContainer: {
    marginBottom: 16,
  },
  aiBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E8F5E9',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  aiBadgeIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  aiBadgeText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2E7D32',
  },
  featuresRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  featurePill: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  featurePillIcon: {
    fontSize: 14,
    marginRight: 4,
  },
  featurePillText: {
    fontSize: 11,
    color: '#616161',
    fontWeight: '500',
  },
  resourceRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  resourceItem: {
    alignItems: 'center',
  },
  resourceIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  resourceLabel: {
    fontSize: 12,
    color: '#757575',
    marginBottom: 4,
  },
  resourceValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#212121',
  },
  inputsContainer: {
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
    paddingTop: 12,
  },
  inputsLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#424242',
    marginBottom: 8,
  },
  inputsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  inputTag: {
    fontSize: 11,
    color: '#616161',
    backgroundColor: '#F5F5F5',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  riskItem: {
    marginBottom: 12,
  },
  riskStage: {
    fontSize: 14,
    fontWeight: '600',
    color: '#212121',
    marginBottom: 6,
  },
  risksList: {
    marginLeft: 8,
    marginBottom: 6,
  },
  riskName: {
    fontSize: 12,
    color: '#616161',
    marginBottom: 2,
  },
  aiDetection: {
    fontSize: 11,
    color: '#4CAF50',
    fontStyle: 'italic',
  },
});

export default {
  CurrentStageCard,
  UpcomingPracticesCard,
  MilestonesTimeline,
  AICalendarBadge,
  ResourceSummaryCard,
  RiskAlertsCard
};
