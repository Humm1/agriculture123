import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Image,
  Alert,
} from 'react-native';
import { Text, Card, Button, Chip } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';

import { theme, spacing, typography } from '../../theme/theme';
import { farmAPI, uploadPhoto } from '../../services/api';

const SoilAnalysisScreen = ({ route, navigation }) => {
  const { field } = route.params;
  const [loading, setLoading] = useState(false);
  const [wetPhoto, setWetPhoto] = useState(null);
  const [dryPhoto, setDryPhoto] = useState(null);
  const [analysis, setAnalysis] = useState(field.soil_snapshots?.[0] || null);

  const handleTakePhoto = async (type) => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission Denied', 'Camera permission is required');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 0.8,
    });

    if (!result.canceled) {
      if (type === 'wet') {
        setWetPhoto(result.assets[0].uri);
      } else {
        setDryPhoto(result.assets[0].uri);
      }
    }
  };

  const handleAnalyze = async () => {
    if (!wetPhoto || !dryPhoto) {
      Alert.alert('Photos Required', 'Please take both wet and dry soil photos');
      return;
    }

    setLoading(true);
    try {
      const wetPhotoUrl = await uploadPhoto(wetPhoto);
      const dryPhotoUrl = await uploadPhoto(dryPhoto);

      const result = await farmAPI.addSoilSnapshot(field.id, {
        wet: wetPhotoUrl,
        dry: dryPhotoUrl,
      });

      setAnalysis(result);
      Alert.alert('Success', 'Soil analysis completed!');
    } catch (error) {
      console.error('Error analyzing soil:', error);
      Alert.alert('Error', 'Failed to analyze soil. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent}>
      {/* Field Info */}
      <Card style={styles.card}>
        <Card.Content>
          <Text style={styles.fieldName}>{field.field_name}</Text>
          <Text style={styles.fieldDetails}>
            {field.field_size_acres} acres • {field.soil_type}
          </Text>
        </Card.Content>
      </Card>

      {/* Photo Capture */}
      <Card style={styles.card}>
        <Card.Title title="Capture Soil Photos" titleStyle={styles.cardTitle} />
        <Card.Content>
          <Text style={styles.instructions}>
            Take photos of soil samples when wet (after rain) and dry for accurate AI analysis
          </Text>

          <View style={styles.photoGrid}>
            <View style={styles.photoContainer}>
              <Text style={styles.photoLabel}>Wet Soil</Text>
              {wetPhoto ? (
                <Image source={{ uri: wetPhoto }} style={styles.photoPreview} />
              ) : (
                <View style={styles.photoPlaceholder}>
                  <MaterialCommunityIcons
                    name="water"
                    size={48}
                    color={theme.colors.primary}
                  />
                </View>
              )}
              <Button
                mode="outlined"
                icon="camera"
                onPress={() => handleTakePhoto('wet')}
                style={styles.photoButton}
              >
                {wetPhoto ? 'Retake' : 'Take Photo'}
              </Button>
            </View>

            <View style={styles.photoContainer}>
              <Text style={styles.photoLabel}>Dry Soil</Text>
              {dryPhoto ? (
                <Image source={{ uri: dryPhoto }} style={styles.photoPreview} />
              ) : (
                <View style={styles.photoPlaceholder}>
                  <MaterialCommunityIcons
                    name="weather-sunny"
                    size={48}
                    color={theme.colors.accent}
                  />
                </View>
              )}
              <Button
                mode="outlined"
                icon="camera"
                onPress={() => handleTakePhoto('dry')}
                style={styles.photoButton}
              >
                {dryPhoto ? 'Retake' : 'Take Photo'}
              </Button>
            </View>
          </View>

          <Button
            mode="contained"
            onPress={handleAnalyze}
            loading={loading}
            disabled={loading || !wetPhoto || !dryPhoto}
            style={styles.analyzeButton}
            contentStyle={styles.buttonContent}
          >
            Analyze Soil with AI
          </Button>
        </Card.Content>
      </Card>

      {/* Analysis Results */}
      {analysis && (
        <>
          {/* ML Prediction Section */}
          {analysis.ml_prediction && (
            <Card style={styles.card}>
              <Card.Title title="🤖 ML Soil Classification" titleStyle={styles.cardTitle} />
              <Card.Content>
                <View style={styles.mlHeader}>
                  <MaterialCommunityIcons
                    name="brain"
                    size={32}
                    color={theme.colors.primary}
                  />
                  <View style={styles.mlInfo}>
                    <Text style={styles.soilType}>{analysis.soil_type?.toUpperCase()}</Text>
                    <View style={styles.confidenceRow}>
                      <Text style={styles.confidenceLabel}>Confidence:</Text>
                      <Text style={styles.confidenceValue}>
                        {(analysis.ml_confidence * 100).toFixed(1)}%
                      </Text>
                    </View>
                    {analysis.ml_prediction.model_used && (
                      <Text style={styles.modelText}>
                        Model: {analysis.ml_prediction.model_used}
                      </Text>
                    )}
                  </View>
                </View>

                {/* Soil Characteristics */}
                {analysis.characteristics && (
                  <View style={styles.characteristicsSection}>
                    <Text style={styles.sectionTitle}>Characteristics:</Text>
                    <View style={styles.charGrid}>
                      {Object.entries(analysis.characteristics).map(([key, value]) => (
                        <View key={key} style={styles.charItem}>
                          <Text style={styles.charLabel}>{key.replace('_', ' ')}:</Text>
                          <Text style={styles.charValue}>{value}</Text>
                        </View>
                      ))}
                    </View>
                  </View>
                )}

                {/* Fertility Estimate */}
                {analysis.fertility_estimate && (
                  <View style={styles.fertilitySection}>
                    <Text style={styles.sectionTitle}>Fertility Estimate:</Text>
                    <View style={styles.fertilityBar}>
                      <View
                        style={[
                          styles.fertilityFill,
                          {
                            width: `${analysis.fertility_estimate.fertility_score * 100}%`,
                            backgroundColor:
                              analysis.fertility_estimate.fertility_score > 0.7
                                ? theme.colors.success
                                : analysis.fertility_estimate.fertility_score > 0.4
                                ? theme.colors.accent
                                : theme.colors.error,
                          },
                        ]}
                      />
                    </View>
                    <Text style={styles.fertilityText}>
                      {analysis.fertility_estimate.description} ({(analysis.fertility_estimate.fertility_score * 100).toFixed(0)}%)
                    </Text>
                  </View>
                )}

                {/* Crop Recommendations */}
                {analysis.recommendations?.suitable_crops && (
                  <View style={styles.cropsSection}>
                    <Text style={styles.sectionTitle}>🌾 Suitable Crops:</Text>
                    <View style={styles.cropsList}>
                      {analysis.recommendations.suitable_crops.map((crop, index) => (
                        <Chip key={index} style={styles.cropChip}>
                          {crop}
                        </Chip>
                      ))}
                    </View>
                  </View>
                )}

                {/* Amendments */}
                {analysis.recommendations?.amendments && (
                  <View style={styles.amendmentsSection}>
                    <Text style={styles.sectionTitle}>💊 Recommended Amendments:</Text>
                    {analysis.recommendations.amendments.map((amendment, index) => (
                      <View key={index} style={styles.amendmentItem}>
                        <MaterialCommunityIcons
                          name="check-circle"
                          size={18}
                          color={theme.colors.success}
                        />
                        <Text style={styles.amendmentText}>{amendment}</Text>
                      </View>
                    ))}
                  </View>
                )}
              </Card.Content>
            </Card>
          )}

          <Card style={styles.card}>
            <Card.Title title="Soil Texture Analysis" titleStyle={styles.cardTitle} />
            <Card.Content>
              <View style={styles.textureRow}>
                <View style={styles.textureItem}>
                  <Text style={styles.textureLabel}>Clay</Text>
                  <Text style={styles.textureValue}>
                    {analysis.ai_analysis?.clay_percent || 0}%
                  </Text>
                </View>
                <View style={styles.textureItem}>
                  <Text style={styles.textureLabel}>Sand</Text>
                  <Text style={styles.textureValue}>
                    {analysis.ai_analysis?.sand_percent || 0}%
                  </Text>
                </View>
                <View style={styles.textureItem}>
                  <Text style={styles.textureLabel}>Silt</Text>
                  <Text style={styles.textureValue}>
                    {analysis.ai_analysis?.silt_percent || 0}%
                  </Text>
                </View>
              </View>
              <View style={styles.textureClassification}>
                <Text style={styles.classificationLabel}>Texture Class:</Text>
                <Chip style={styles.classificationChip}>
                  {analysis.ai_analysis?.texture_class || 'Unknown'}
                </Chip>
              </View>
            </Card.Content>
          </Card>

          <Card style={styles.card}>
            <Card.Title title="Nutrient Levels" titleStyle={styles.cardTitle} />
            <Card.Content>
              <NutrientBar
                label="Nitrogen (N)"
                level={analysis.ai_analysis?.nitrogen || 'medium'}
              />
              <NutrientBar
                label="Phosphorus (P)"
                level={analysis.ai_analysis?.phosphorus || 'medium'}
              />
              <NutrientBar
                label="Potassium (K)"
                level={analysis.ai_analysis?.potassium || 'medium'}
              />
            </Card.Content>
          </Card>

          <Card style={styles.card}>
            <Card.Title title="Recommendations" titleStyle={styles.cardTitle} />
            <Card.Content>
              <View style={styles.recommendations}>
                {analysis.ai_analysis?.recommendations?.map((rec, index) => (
                  <View key={index} style={styles.recommendationItem}>
                    <MaterialCommunityIcons
                      name="check-circle"
                      size={20}
                      color={theme.colors.success}
                    />
                    <Text style={styles.recommendationText}>{rec}</Text>
                  </View>
                ))}
              </View>
            </Card.Content>
          </Card>
        </>
      )}
    </ScrollView>
  );
};

const NutrientBar = ({ label, level }) => {
  const getColor = () => {
    if (level === 'high') return theme.colors.success;
    if (level === 'medium') return theme.colors.accent;
    return theme.colors.error;
  };

  const getWidth = () => {
    if (level === 'high') return '100%';
    if (level === 'medium') return '60%';
    return '30%';
  };

  return (
    <View style={styles.nutrientBar}>
      <View style={styles.nutrientHeader}>
        <Text style={styles.nutrientLabel}>{label}</Text>
        <Chip style={[styles.levelChip, { backgroundColor: getColor() + '30' }]}>
          <Text style={[styles.levelText, { color: getColor() }]}>
            {level.toUpperCase()}
          </Text>
        </Chip>
      </View>
      <View style={styles.progressBar}>
        <View
          style={[styles.progressFill, { width: getWidth(), backgroundColor: getColor() }]}
        />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  scrollContent: {
    padding: spacing.md,
  },
  card: {
    marginBottom: spacing.md,
    elevation: 2,
  },
  cardTitle: {
    ...typography.h3,
    fontWeight: 'bold',
  },
  fieldName: {
    ...typography.h3,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  fieldDetails: {
    ...typography.caption,
    color: theme.colors.placeholder,
    marginTop: spacing.xs,
  },
  instructions: {
    ...typography.body,
    color: theme.colors.text,
    marginBottom: spacing.md,
    textAlign: 'center',
  },
  photoGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.md,
  },
  photoContainer: {
    flex: 1,
    marginHorizontal: spacing.xs,
    alignItems: 'center',
  },
  photoLabel: {
    ...typography.caption,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: spacing.sm,
  },
  photoPlaceholder: {
    width: '100%',
    aspectRatio: 1,
    backgroundColor: theme.colors.surface,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: theme.colors.border,
    borderStyle: 'dashed',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  photoPreview: {
    width: '100%',
    aspectRatio: 1,
    borderRadius: 8,
    marginBottom: spacing.sm,
  },
  photoButton: {
    width: '100%',
  },
  analyzeButton: {
    marginTop: spacing.md,
  },
  buttonContent: {
    paddingVertical: spacing.sm,
  },
  textureRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: spacing.md,
  },
  textureItem: {
    alignItems: 'center',
  },
  textureLabel: {
    ...typography.caption,
    color: theme.colors.placeholder,
    marginBottom: spacing.xs,
  },
  textureValue: {
    ...typography.h2,
    fontWeight: 'bold',
    color: theme.colors.primary,
  },
  textureClassification: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderColor: theme.colors.border,
  },
  classificationLabel: {
    ...typography.body,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginRight: spacing.sm,
  },
  classificationChip: {
    backgroundColor: theme.colors.primary + '30',
  },
  nutrientBar: {
    marginBottom: spacing.lg,
  },
  nutrientHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  nutrientLabel: {
    ...typography.body,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  levelChip: {
    paddingHorizontal: spacing.sm,
  },
  levelText: {
    ...typography.caption,
    fontWeight: 'bold',
  },
  progressBar: {
    height: 8,
    backgroundColor: theme.colors.border,
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 4,
  },
  recommendations: {
    marginTop: spacing.sm,
  },
  recommendationItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: spacing.md,
  },
  recommendationText: {
    ...typography.body,
    color: theme.colors.text,
    marginLeft: spacing.sm,
    flex: 1,
  },
  mlHeader: {
    flexDirection: 'row',
    marginBottom: spacing.md,
    alignItems: 'center',
  },
  mlInfo: {
    flex: 1,
    marginLeft: spacing.md,
  },
  soilType: {
    ...typography.h3,
    fontWeight: 'bold',
    color: theme.colors.text,
    textTransform: 'capitalize',
  },
  confidenceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: spacing.xs,
  },
  confidenceLabel: {
    ...typography.caption,
    color: theme.colors.placeholder,
    marginRight: spacing.xs,
  },
  confidenceValue: {
    ...typography.body,
    fontWeight: 'bold',
    color: theme.colors.primary,
  },
  modelText: {
    ...typography.caption,
    color: '#666',
    fontStyle: 'italic',
    marginTop: spacing.xs,
  },
  characteristicsSection: {
    marginTop: spacing.md,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
  },
  sectionTitle: {
    ...typography.body,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: spacing.sm,
  },
  charGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: spacing.xs,
  },
  charItem: {
    width: '50%',
    marginBottom: spacing.sm,
  },
  charLabel: {
    ...typography.caption,
    color: theme.colors.placeholder,
    textTransform: 'capitalize',
  },
  charValue: {
    ...typography.body,
    fontWeight: '600',
    color: theme.colors.text,
    textTransform: 'capitalize',
  },
  fertilitySection: {
    marginTop: spacing.md,
  },
  fertilityBar: {
    height: 20,
    backgroundColor: theme.colors.border,
    borderRadius: 10,
    overflow: 'hidden',
    marginVertical: spacing.sm,
  },
  fertilityFill: {
    height: '100%',
    borderRadius: 10,
  },
  fertilityText: {
    ...typography.caption,
    color: theme.colors.text,
    textAlign: 'center',
  },
  cropsSection: {
    marginTop: spacing.md,
  },
  cropsList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: spacing.xs,
  },
  cropChip: {
    marginRight: spacing.xs,
    marginBottom: spacing.xs,
    backgroundColor: theme.colors.primary + '20',
  },
  amendmentsSection: {
    marginTop: spacing.md,
  },
  amendmentItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: spacing.sm,
  },
  amendmentText: {
    ...typography.body,
    color: theme.colors.text,
    marginLeft: spacing.sm,
    flex: 1,
  },
});

export default SoilAnalysisScreen;

