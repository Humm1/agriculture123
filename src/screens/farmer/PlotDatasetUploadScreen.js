import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Image,
  Alert,
  ActivityIndicator,
  TextInput
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useAuth } from '../../context/AuthContext';

const BACKEND_URL = 'https://urchin-app-86rjy.ondigitalocean.app/api';

export default function PlotDatasetUploadScreen({ route, navigation }) {
  const { plotId, plotName } = route.params;
  const { user } = useAuth();
  
  const [images, setImages] = useState([]);
  const [dataCategory, setDataCategory] = useState('whole_plant');
  const [growthStage, setGrowthStage] = useState('vegetative');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [gpsLocation, setGpsLocation] = useState(null);
  const [notes, setNotes] = useState('');
  
  const dataCategoryOptions = [
    { value: 'whole_plant', label: '🌱 Whole Plant', icon: 'flower' },
    { value: 'leaf', label: '🍃 Leaf Close-up', icon: 'leaf' },
    { value: 'stem', label: '🌿 Stem/Branch', icon: 'barley' },
    { value: 'fruit', label: '🍅 Fruit/Produce', icon: 'fruit-cherries' },
    { value: 'soil', label: '🟤 Soil Condition', icon: 'terrain' },
    { value: 'aerial', label: '🚁 Aerial View', icon: 'quadcopter' }
  ];
  
  const growthStageOptions = [
    { value: 'seedling', label: '🌱 Seedling' },
    { value: 'vegetative', label: '🌿 Vegetative' },
    { value: 'flowering', label: '🌸 Flowering' },
    { value: 'fruiting', label: '🍅 Fruiting' },
    { value: 'harvest', label: '🌾 Harvest Ready' }
  ];
  
  // Get GPS location
  const getLocation = async () => {
    try {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission denied', 'Location permission is required');
        return;
      }
      
      const location = await Location.getCurrentPositionAsync({});
      setGpsLocation({
        lat: location.coords.latitude,
        lng: location.coords.longitude,
        accuracy: location.coords.accuracy
      });
      
      Alert.alert('Success', `Location captured: ${location.coords.latitude.toFixed(4)}, ${location.coords.longitude.toFixed(4)}`);
    } catch (error) {
      console.error('Error getting location:', error);
      Alert.alert('Error', 'Failed to get location');
    }
  };
  
  // Pick images from library
  const pickImages = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsMultipleSelection: true,
        quality: 0.8,
        allowsEditing: false
      });
      
      if (!result.canceled) {
        const newImages = result.assets || [result];
        setImages([...images, ...newImages]);
      }
    } catch (error) {
      console.error('Error picking images:', error);
      Alert.alert('Error', 'Failed to pick images');
    }
  };
  
  // Take photo with camera
  const takePhoto = async () => {
    try {
      const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
      
      if (permissionResult.status !== 'granted') {
        Alert.alert('Permission denied', 'Camera permission is required');
        return;
      }
      
      const result = await ImagePicker.launchCameraAsync({
        quality: 0.8,
        allowsEditing: false
      });
      
      if (!result.canceled) {
        const newImage = result.assets ? result.assets[0] : result;
        setImages([...images, newImage]);
      }
    } catch (error) {
      console.error('Error taking photo:', error);
      Alert.alert('Error', 'Failed to take photo');
    }
  };
  
  // Remove image
  const removeImage = (index) => {
    const newImages = images.filter((_, i) => i !== index);
    setImages(newImages);
  };
  
  // Upload images
  const uploadImages = async () => {
    if (images.length === 0) {
      Alert.alert('No Images', 'Please select at least one image to upload');
      return;
    }
    
    if (!gpsLocation) {
      Alert.alert(
        'No GPS Location',
        'GPS location is recommended for better analysis. Continue without it?',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Continue', onPress: () => performUpload() }
        ]
      );
      return;
    }
    
    await performUpload();
  };
  
  const performUpload = async () => {
    setUploading(true);
    setUploadProgress(0);
    
    try {
      const formData = new FormData();
      formData.append('plot_id', plotId);
      formData.append('user_id', user.id);
      formData.append('data_category', dataCategory);
      formData.append('growth_stage', growthStage);
      formData.append('analyze_immediately', 'true');
      
      if (gpsLocation) {
        formData.append('gps_location', JSON.stringify(gpsLocation));
      }
      
      // Add images
      for (let i = 0; i < images.length; i++) {
        const image = images[i];
        const filename = image.uri.split('/').pop();
        const match = /\.(\w+)$/.exec(filename);
        const type = match ? `image/${match[1]}` : 'image/jpeg';
        
        formData.append('files', {
          uri: image.uri,
          name: filename,
          type
        });
        
        setUploadProgress(((i + 1) / images.length) * 50);
      }
      
      const response = await fetch(`${BACKEND_URL}/plot-analytics/upload-images`, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setUploadProgress(75);
      
      const data = await response.json();
      
      setUploadProgress(100);
      
      if (data.success) {
        Alert.alert(
          'Upload Successful',
          `Uploaded ${data.total_images} images. ${data.analysis_results.length} images analyzed.`,
          [
            {
              text: 'View Analytics',
              onPress: () => navigation.navigate('PlotAnalytics', { plotId, plotName })
            },
            {
              text: 'Upload More',
              onPress: () => {
                setImages([]);
                setUploadProgress(0);
              }
            }
          ]
        );
      } else {
        Alert.alert('Error', data.message || 'Upload failed');
      }
      
    } catch (error) {
      console.error('Upload error:', error);
      Alert.alert('Upload Failed', error.message || 'Please try again');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };
  
  return (
    <ScrollView style={styles.container}>
      {/* Header with Back Button */}
      <View style={styles.headerContainer}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <MaterialCommunityIcons name="arrow-left" size={24} color="#fff" />
        </TouchableOpacity>
        <View style={styles.headerTitleContainer}>
          <Text style={styles.headerTitle}>Upload Plot Images</Text>
          <Text style={styles.headerSubtitle}>{plotName}</Text>
        </View>
        <View style={styles.headerRight} />
      </View>

      <View style={styles.header}>
        <Text style={styles.infoText}>
          Upload multiple images for AI analysis, disease detection, and health monitoring
        </Text>
      </View>
      
      {/* GPS Location */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📍 GPS Location</Text>
        <TouchableOpacity
          style={[styles.locationButton, gpsLocation && styles.locationButtonActive]}
          onPress={getLocation}
        >
          <MaterialCommunityIcons
            name={gpsLocation ? 'map-marker-check' : 'crosshairs-gps'}
            size={24}
            color={gpsLocation ? '#4CAF50' : '#666'}
          />
          <Text style={[styles.locationText, gpsLocation && styles.locationTextActive]}>
            {gpsLocation
              ? `Lat: ${gpsLocation.lat.toFixed(4)}, Lng: ${gpsLocation.lng.toFixed(4)}`
              : 'Capture GPS Location (Recommended)'}
          </Text>
        </TouchableOpacity>
      </View>
      
      {/* Data Category */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📸 Image Type</Text>
        <View style={styles.optionsGrid}>
          {dataCategoryOptions.map((option) => (
            <TouchableOpacity
              key={option.value}
              style={[
                styles.optionCard,
                dataCategory === option.value && styles.optionCardActive
              ]}
              onPress={() => setDataCategory(option.value)}
            >
              <MaterialCommunityIcons
                name={option.icon}
                size={32}
                color={dataCategory === option.value ? '#4CAF50' : '#666'}
              />
              <Text style={[
                styles.optionLabel,
                dataCategory === option.value && styles.optionLabelActive
              ]}>
                {option.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
      
      {/* Growth Stage */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🌱 Growth Stage</Text>
        <View style={styles.stageRow}>
          {growthStageOptions.map((option) => (
            <TouchableOpacity
              key={option.value}
              style={[
                styles.stageButton,
                growthStage === option.value && styles.stageButtonActive
              ]}
              onPress={() => setGrowthStage(option.value)}
            >
              <Text style={[
                styles.stageText,
                growthStage === option.value && styles.stageTextActive
              ]}>
                {option.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
      
      {/* Image Picker */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📷 Images ({images.length})</Text>
        <View style={styles.pickerButtons}>
          <TouchableOpacity style={styles.pickerButton} onPress={takePhoto}>
            <MaterialCommunityIcons name="camera" size={24} color="#fff" />
            <Text style={styles.pickerButtonText}>Take Photo</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.pickerButton} onPress={pickImages}>
            <MaterialCommunityIcons name="image-multiple" size={24} color="#fff" />
            <Text style={styles.pickerButtonText}>Choose from Library</Text>
          </TouchableOpacity>
        </View>
        
        {/* Image Grid */}
        {images.length > 0 && (
          <View style={styles.imageGrid}>
            {images.map((image, index) => (
              <View key={index} style={styles.imageContainer}>
                <Image source={{ uri: image.uri }} style={styles.imagePreview} />
                <TouchableOpacity
                  style={styles.removeButton}
                  onPress={() => removeImage(index)}
                >
                  <MaterialCommunityIcons name="close-circle" size={24} color="#f44336" />
                </TouchableOpacity>
              </View>
            ))}
          </View>
        )}
      </View>
      
      {/* Upload Button */}
      <TouchableOpacity
        style={[styles.uploadButton, uploading && styles.uploadButtonDisabled]}
        onPress={uploadImages}
        disabled={uploading}
      >
        {uploading ? (
          <View style={styles.uploadingContainer}>
            <ActivityIndicator size="small" color="#fff" />
            <Text style={styles.uploadButtonText}>
              Uploading... {uploadProgress.toFixed(0)}%
            </Text>
          </View>
        ) : (
          <>
            <MaterialCommunityIcons name="cloud-upload" size={24} color="#fff" />
            <Text style={styles.uploadButtonText}>
              Upload & Analyze {images.length} Image{images.length !== 1 ? 's' : ''}
            </Text>
          </>
        )}
      </TouchableOpacity>
      
      {/* Info Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>
          ℹ️ Images will be analyzed using AI to detect diseases, assess health, and provide recommendations
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5'
  },
  header: {
    backgroundColor: '#fff',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0'
  },
  headerContainer: {
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
  headerTitleContainer: {
    flex: 1,
    marginLeft: 10
  },
  headerRight: {
    width: 34
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff'
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#e8f5e9'
  },
  infoText: {
    fontSize: 14,
    color: '#888',
    fontStyle: 'italic'
  },
  section: {
    backgroundColor: '#fff',
    padding: 15,
    marginTop: 10
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15
  },
  locationButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#ddd'
  },
  locationButtonActive: {
    backgroundColor: '#e8f5e9',
    borderColor: '#4CAF50'
  },
  locationText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 10
  },
  locationTextActive: {
    color: '#4CAF50',
    fontWeight: '600'
  },
  optionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between'
  },
  optionCard: {
    width: '48%',
    padding: 15,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#ddd',
    alignItems: 'center',
    marginBottom: 10
  },
  optionCardActive: {
    backgroundColor: '#e8f5e9',
    borderColor: '#4CAF50'
  },
  optionLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
    textAlign: 'center'
  },
  optionLabelActive: {
    color: '#4CAF50',
    fontWeight: '600'
  },
  stageRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8
  },
  stageButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: '#f0f0f0',
    borderRadius: 20,
    borderWidth: 2,
    borderColor: '#ddd'
  },
  stageButtonActive: {
    backgroundColor: '#4CAF50',
    borderColor: '#4CAF50'
  },
  stageText: {
    fontSize: 13,
    color: '#666'
  },
  stageTextActive: {
    color: '#fff',
    fontWeight: '600'
  },
  pickerButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15
  },
  pickerButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#2196F3',
    padding: 12,
    borderRadius: 8,
    marginHorizontal: 5
  },
  pickerButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 8
  },
  imageGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'flex-start'
  },
  imageContainer: {
    width: '30%',
    aspectRatio: 1,
    margin: '1.5%',
    position: 'relative'
  },
  imagePreview: {
    width: '100%',
    height: '100%',
    borderRadius: 8
  },
  removeButton: {
    position: 'absolute',
    top: -8,
    right: -8,
    backgroundColor: '#fff',
    borderRadius: 12
  },
  uploadButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#4CAF50',
    padding: 16,
    margin: 15,
    borderRadius: 8
  },
  uploadButtonDisabled: {
    backgroundColor: '#9E9E9E'
  },
  uploadingContainer: {
    flexDirection: 'row',
    alignItems: 'center'
  },
  uploadButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 10
  },
  footer: {
    padding: 15,
    backgroundColor: '#fff3cd',
    marginTop: 10,
    marginBottom: 20
  },
  footerText: {
    fontSize: 13,
    color: '#856404',
    textAlign: 'center'
  }
});
