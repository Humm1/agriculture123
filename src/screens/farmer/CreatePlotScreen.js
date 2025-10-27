import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  ScrollView,
  TouchableOpacity,
  Image,
  StyleSheet,
  Alert,
  ActivityIndicator,
  Platform,
} from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';
import { useAuth } from '../../context/AuthContext';

export default function CreatePlotScreen({ navigation }) {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    plotName: '',
    cropName: '',
    plantingDate: new Date().toISOString().split('T')[0],
    areaSize: '',
    notes: '',
    soilType: '',
    latitude: null,
    longitude: null,
  });
  const [initialImage, setInitialImage] = useState(null);
  const [soilImage, setSoilImage] = useState(null);

  // Helper to convert URI to File/Blob for web uploads
  const uriToBlob = async (uri) => {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.onload = function() {
        resolve(xhr.response);
      };
      xhr.onerror = function() {
        reject(new Error('uriToBlob failed'));
      };
      xhr.responseType = 'blob';
      xhr.open('GET', uri, true);
      xhr.send(null);
    });
  };

  const pickImage = async (type) => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Required', 'Please grant camera roll permissions to continue');
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      console.log('Image picker result:', result);

      if (!result.canceled && result.assets && result.assets.length > 0) {
        if (type === 'initial') {
          setInitialImage(result.assets[0]);
          console.log('Initial image set:', result.assets[0].uri);
        } else {
          setSoilImage(result.assets[0]);
          console.log('Soil image set:', result.assets[0].uri);
        }
      }
    } catch (error) {
      console.error('Error picking image:', error);
      Alert.alert('Error', 'Failed to pick image: ' + error.message);
    }
  };

  const getLocation = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Required', 'Please grant location permissions');
        return;
      }

      const location = await Location.getCurrentPositionAsync({});
      setFormData({
        ...formData,
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
      });
      Alert.alert('Success', 'Location captured successfully!');
    } catch (error) {
      console.error('Error getting location:', error);
      Alert.alert('Error', 'Failed to get location');
    }
  };

  const handleSubmit = async () => {
    console.log('=== CREATE PLOT SUBMIT STARTED ===');
    console.log('Current timestamp:', new Date().toISOString());
    console.log('Form data:', formData);
    console.log('Initial image:', initialImage);
    console.log('Soil image:', soilImage);
    console.log('User:', user);
    
    // Validation
    if (!formData.plotName || !formData.cropName) {
      console.log('Validation failed: Missing plot name or crop name');
      Alert.alert('Required Fields', 'Please enter plot name and crop name');
      return;
    }

    if (!formData.latitude || !formData.longitude) {
      console.log('Validation failed: Missing location');
      Alert.alert('Location Required', 'Please capture your location first');
      return;
    }

    if (!user || !user.id) {
      console.log('Validation failed: User not authenticated');
      Alert.alert('Error', 'User not authenticated. Please log in again.');
      return;
    }

    console.log('All validations passed, proceeding with submission...');
    setLoading(true);

    try {
      console.log('Building form data...');
      const formDataToSend = new FormData();
      
      // Add text fields
      formDataToSend.append('user_id', user.id);
      formDataToSend.append('plot_name', formData.plotName);
      formDataToSend.append('crop_name', formData.cropName);
      formDataToSend.append('planting_date', formData.plantingDate);
      formDataToSend.append('latitude', formData.latitude.toString());
      formDataToSend.append('longitude', formData.longitude.toString());
      formDataToSend.append('is_demo', 'false'); // This is a real plot, not a demo
      
      if (formData.areaSize) {
        formDataToSend.append('area_size', formData.areaSize);
      }
      if (formData.notes) {
        formDataToSend.append('notes', formData.notes);
      }
      if (formData.soilType) {
        formDataToSend.append('soil_type', formData.soilType);
      }

      // Add images if selected - with web compatibility
      console.log('Processing images for upload...');
      console.log('Initial image:', initialImage ? 'Present' : 'None');
      console.log('Soil image:', soilImage ? 'Present' : 'None');
      console.log('Platform:', Platform.OS);
      
      if (initialImage && initialImage.uri) {
        console.log('Adding initial_image to FormData...');
        console.log('Initial image URI:', initialImage.uri.substring(0, 50) + '...');
        try {
          if (Platform.OS === 'web') {
            // For web, convert data URI to Blob using XMLHttpRequest
            console.log('Web platform - converting to Blob using XMLHttpRequest');
            const blob = await uriToBlob(initialImage.uri);
            console.log('Blob created:', blob.type, blob.size, 'bytes');
            formDataToSend.append('initial_image', blob, 'initial.jpg');
          } else {
            // For mobile (iOS/Android)
            const filename = initialImage.uri.split('/').pop();
            const match = /\.(\w+)$/.exec(filename);
            const type = match ? `image/${match[1]}` : `image/jpeg`;
            
            formDataToSend.append('initial_image', {
              uri: Platform.OS === 'ios' ? initialImage.uri.replace('file://', '') : initialImage.uri,
              name: filename || 'initial.jpg',
              type: type,
            });
          }
          console.log('initial_image added successfully');
        } catch (error) {
          console.error('Error adding initial_image:', error);
          throw new Error('Failed to process initial image: ' + error.message);
        }
      }

      if (soilImage && soilImage.uri) {
        console.log('Adding soil_image to FormData...');
        console.log('Soil image URI:', soilImage.uri.substring(0, 50) + '...');
        try {
          if (Platform.OS === 'web') {
            // For web, convert data URI to Blob using XMLHttpRequest
            console.log('Web platform - converting to Blob using XMLHttpRequest');
            const blob = await uriToBlob(soilImage.uri);
            console.log('Blob created:', blob.type, blob.size, 'bytes');
            formDataToSend.append('soil_image', blob, 'soil.jpg');
          } else {
            // For mobile (iOS/Android)
            const filename = soilImage.uri.split('/').pop();
            const match = /\.(\w+)$/.exec(filename);
            const type = match ? `image/${match[1]}` : `image/jpeg`;
            
            formDataToSend.append('soil_image', {
              uri: Platform.OS === 'ios' ? soilImage.uri.replace('file://', '') : soilImage.uri,
              name: filename || 'soil.jpg',
              type: type,
            });
          }
          console.log('soil_image added successfully');
        } catch (error) {
          console.error('Error adding soil_image:', error);
          throw new Error('Failed to process soil image: ' + error.message);
        }
      }

      console.log('Sending request to unified plot endpoint...');
      console.log('FormData contents:', {
        user_id: user.id,
        plot_name: formData.plotName,
        crop_name: formData.cropName,
        has_initial_image: !!initialImage,
        has_soil_image: !!soilImage,
      });
      
      const response = await fetch('https://urchin-app-86rjy.ondigitalocean.app/api/advanced-growth/plots', {
        method: 'POST',
        body: formDataToSend,
        headers: {
          'Accept': 'application/json',
          // DON'T set Content-Type - let fetch/FormData set it with boundary
        },
      });

      console.log('Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        let errorMessage = 'Failed to create plot';
        try {
          const errorData = JSON.parse(errorText);
          if (errorData.detail) {
            if (Array.isArray(errorData.detail)) {
              errorMessage = errorData.detail.map(e => e.msg).join(', ');
            } else {
              errorMessage = errorData.detail;
            }
          }
        } catch (e) {
          errorMessage = errorText.substring(0, 100);
        }
        throw new Error(errorMessage);
      }
      
      const result = await response.json();
      console.log('Response data:', result);

      if (result.plot_id || result.id) {
        const plotId = result.plot_id || result.id;
        
        // Build analysis summary
        let analysisMessage = '';
        if (result.ai_analysis) {
          const { soil_health, pest_disease_scan, recommendations } = result.ai_analysis;
          
          if (soil_health) {
            analysisMessage += `\n\n🌱 Soil Analysis:\n- Fertility: ${soil_health.fertility_score}/10\n- Type: ${soil_health.soil_type}\n- pH: ${soil_health.ph_estimate}`;
          }
          
          if (pest_disease_scan) {
            analysisMessage += `\n\n🔍 Health Scan:\n- Status: ${pest_disease_scan.health_status}\n- Confidence: ${(pest_disease_scan.confidence * 100).toFixed(0)}%`;
            if (pest_disease_scan.detected_issues && pest_disease_scan.detected_issues.length > 0) {
              analysisMessage += `\n- Issues Found: ${pest_disease_scan.detected_issues.length}`;
            }
          }
          
          if (recommendations && recommendations.length > 0) {
            analysisMessage += `\n\n💡 Recommendations:\n`;
            recommendations.slice(0, 3).forEach((rec, idx) => {
              analysisMessage += `${idx + 1}. ${rec.message}\n`;
            });
          }
        }
        
        const eventsMessage = result.calendar_events_created 
          ? `\n📅 ${result.calendar_events_created} calendar events created!`
          : '';
        
        Alert.alert(
          '✅ Plot Created Successfully!',
          `Your plot "${formData.plotName}" has been created.${eventsMessage}${analysisMessage}`,
          [
            {
              text: 'View AI Analysis',
              onPress: () => {
                navigation.navigate('GrowthTracking', { 
                  plotId: plotId,
                  showAnalysis: true 
                });
              },
            },
            {
              text: 'View Calendar',
              onPress: () => {
                navigation.navigate('GrowthTracking', { 
                  plotId: plotId,
                  showCalendar: true 
                });
              },
            },
            {
              text: 'OK',
              onPress: () => navigation.goBack(),
            },
          ]
        );
      } else {
        Alert.alert('Plot Created', 'Your plot has been created successfully!', [
          { text: 'OK', onPress: () => navigation.goBack() }
        ]);
      }
    } catch (error) {
      console.error('Error creating plot:', error);
      Alert.alert('Error', 'Failed to create plot: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Create New Plot</Text>
      <Text style={styles.subtitle}>Track your crop's growth journey</Text>

      {/* Plot Name */}
      <View style={styles.fieldContainer}>
        <Text style={styles.label}>Plot Name *</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g., North Field, Plot A"
          value={formData.plotName}
          onChangeText={(text) => setFormData({ ...formData, plotName: text })}
        />
      </View>

      {/* Crop Name */}
      <View style={styles.fieldContainer}>
        <Text style={styles.label}>Crop Name *</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g., Maize, Tomatoes"
          value={formData.cropName}
          onChangeText={(text) => setFormData({ ...formData, cropName: text })}
        />
      </View>

      {/* Planting Date */}
      <View style={styles.fieldContainer}>
        <Text style={styles.label}>Planting Date *</Text>
        <TextInput
          style={styles.input}
          placeholder="YYYY-MM-DD"
          value={formData.plantingDate}
          onChangeText={(text) => setFormData({ ...formData, plantingDate: text })}
        />
      </View>

      {/* Area Size */}
      <View style={styles.fieldContainer}>
        <Text style={styles.label}>Area Size (hectares)</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g., 2.5"
          keyboardType="decimal-pad"
          value={formData.areaSize}
          onChangeText={(text) => setFormData({ ...formData, areaSize: text })}
        />
      </View>

      {/* Soil Type */}
      <View style={styles.fieldContainer}>
        <Text style={styles.label}>Soil Type (optional)</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g., Clay, Loam, Sandy"
          value={formData.soilType}
          onChangeText={(text) => setFormData({ ...formData, soilType: text })}
        />
      </View>

      {/* Location */}
      <View style={styles.fieldContainer}>
        <Text style={styles.label}>Location *</Text>
        <TouchableOpacity style={styles.locationButton} onPress={getLocation}>
          <MaterialCommunityIcons name="map-marker" size={24} color="#4CAF50" />
          <Text style={styles.locationButtonText}>
            {formData.latitude && formData.longitude
              ? `📍 ${formData.latitude.toFixed(4)}, ${formData.longitude.toFixed(4)}`
              : 'Tap to Capture Location'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Initial Plant Image */}
      <View style={styles.fieldContainer}>
        <Text style={styles.label}>Initial Plant Image (optional)</Text>
        <TouchableOpacity
          style={styles.imagePickerButton}
          onPress={() => {
            console.log('Initial image button pressed');
            pickImage('initial');
          }}
          activeOpacity={0.7}
        >
          {initialImage ? (
            <Image source={{ uri: initialImage.uri }} style={styles.imagePreview} />
          ) : (
            <>
              <MaterialCommunityIcons name="camera-plus" size={40} color="#999" />
              <Text style={styles.imagePickerText}>Tap to add photo</Text>
            </>
          )}
        </TouchableOpacity>
      </View>

      {/* Soil Image */}
      <View style={styles.fieldContainer}>
        <Text style={styles.label}>Soil Image (optional)</Text>
        <TouchableOpacity
          style={styles.imagePickerButton}
          onPress={() => {
            console.log('Soil image button pressed');
            pickImage('soil');
          }}
          activeOpacity={0.7}
        >
          {soilImage ? (
            <Image source={{ uri: soilImage.uri }} style={styles.imagePreview} />
          ) : (
            <>
              <MaterialCommunityIcons name="image-plus" size={40} color="#999" />
              <Text style={styles.imagePickerText}>Tap to add soil photo</Text>
            </>
          )}
        </TouchableOpacity>
      </View>

      {/* Notes */}
      <View style={styles.fieldContainer}>
        <Text style={styles.label}>Notes (optional)</Text>
        <TextInput
          style={[styles.input, styles.textArea]}
          placeholder="Additional notes about this plot..."
          multiline
          numberOfLines={4}
          value={formData.notes}
          onChangeText={(text) => setFormData({ ...formData, notes: text })}
        />
      </View>

      {/* Submit Button */}
      <TouchableOpacity
        style={[styles.submitButton, loading && styles.submitButtonDisabled]}
        onPress={() => {
          console.log('===================================');
          console.log('CREATE PLOT BUTTON CLICKED!');
          console.log('===================================');
          Alert.alert('Debug', 'Button clicked! Check console for details.');
          handleSubmit();
        }}
        disabled={loading}
        activeOpacity={0.8}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <>
            <MaterialCommunityIcons name="check" size={24} color="#fff" />
            <Text style={styles.submitButtonText}>Create Plot</Text>
          </>
        )}
      </TouchableOpacity>

      <View style={styles.bottomSpace} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 20,
  },
  fieldContainer: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  locationButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    borderWidth: 1,
    borderColor: '#4CAF50',
    borderRadius: 8,
    backgroundColor: '#f0f8f0',
  },
  locationButtonText: {
    fontSize: 16,
    color: '#333',
    marginLeft: 10,
  },
  imagePickerButton: {
    height: 200,
    borderWidth: 2,
    borderColor: '#ddd',
    borderRadius: 8,
    borderStyle: 'dashed',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f9f9f9',
  },
  imagePickerText: {
    fontSize: 14,
    color: '#999',
    marginTop: 10,
  },
  imagePreview: {
    width: '100%',
    height: '100%',
    borderRadius: 8,
  },
  submitButton: {
    flexDirection: 'row',
    backgroundColor: '#4CAF50',
    padding: 16,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 10,
  },
  submitButtonDisabled: {
    backgroundColor: '#ccc',
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  bottomSpace: {
    height: 40,
  },
});
