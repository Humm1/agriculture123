import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { View, Text, StyleSheet } from 'react-native';

import { theme, layout, typography } from '../theme/theme';

// Stack Navigators
import HomeStack from './HomeStack';
import FarmStack from './FarmStack';
import GroupsStack from './GroupsStack';
import CampaignsStack from './CampaignsStack';
import ProfileStack from './ProfileStack';

const Tab = createBottomTabNavigator();

const MainTabNavigator = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;
          let iconColor = focused ? theme.colors.primary : theme.colors.textSecondary;

          // Agricultural-themed icons
          switch (route.name) {
            case 'HomeTab':
              iconName = 'home-variant';
              break;
            case 'FarmTab':
              iconName = 'sprout'; // Agricultural sprout icon
              break;
            case 'GroupsTab':
              iconName = 'account-group';
              break;
            case 'CampaignsTab':
              iconName = 'megaphone'; // Changed from bullhorn
              break;
            case 'ProfileTab':
              iconName = 'account-circle';
              break;
            default:
              iconName = 'help-circle';
          }

          return (
            <View style={[styles.tabIconContainer, focused && styles.tabIconFocused]}>
              <MaterialCommunityIcons 
                name={iconName} 
                size={focused ? 26 : 24} 
                color={iconColor} 
              />
            </View>
          );
        },
        tabBarLabel: ({ focused, color }) => {
          let label;
          switch (route.name) {
            case 'HomeTab':
              label = 'Dashboard';
              break;
            case 'FarmTab':
              label = 'My Farm';
              break;
            case 'GroupsTab':
              label = 'Groups';
              break;
            case 'CampaignsTab':
              label = 'Market';
              break;
            case 'ProfileTab':
              label = 'Profile';
              break;
            default:
              label = route.name;
          }
          
          return (
            <Text style={[
              styles.tabLabel,
              { color: focused ? theme.colors.primary : theme.colors.textSecondary },
              focused && styles.tabLabelFocused
            ]}>
              {label}
            </Text>
          );
        },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: theme.colors.textSecondary,
        tabBarStyle: {
          backgroundColor: theme.colors.surface,
          borderTopColor: theme.colors.borderLight,
          borderTopWidth: 1,
          height: layout.tabBarHeight,
          paddingBottom: 8,
          paddingTop: 8,
          paddingHorizontal: 8,
          ...layout.shadow.small, // Add subtle shadow
        },
        tabBarShowLabel: false, // We'll render custom labels
      })}
    >
      <Tab.Screen 
        name="HomeTab" 
        component={HomeStack}
        options={{ 
          tabBarLabel: 'Dashboard',
          tabBarAccessibilityLabel: 'Dashboard - View farm overview and metrics'
        }}
      />
      <Tab.Screen 
        name="FarmTab" 
        component={FarmStack}
        options={{ 
          tabBarLabel: 'My Farm',
          tabBarAccessibilityLabel: 'My Farm - Manage crops and farm operations'
        }}
      />
      <Tab.Screen 
        name="GroupsTab" 
        component={GroupsStack}
        options={{ 
          tabBarLabel: 'Groups',
          tabBarAccessibilityLabel: 'Groups - Connect with other farmers'
        }}
      />
      <Tab.Screen 
        name="CampaignsTab" 
        component={CampaignsStack}
        options={{ 
          tabBarLabel: 'Market',
          tabBarAccessibilityLabel: 'Market - Buy and sell agricultural products'
        }}
      />
      <Tab.Screen 
        name="ProfileTab" 
        component={ProfileStack}
        options={{ 
          tabBarLabel: 'Profile',
          tabBarAccessibilityLabel: 'Profile - Account settings and information'
        }}
      />
    </Tab.Navigator>
  );
};

// Professional Agricultural Tab Navigation Styles
const styles = StyleSheet.create({
  tabIconContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    width: 40,
    height: 32,
    borderRadius: layout.borderRadius.small,
    marginBottom: 2,
  },
  
  tabIconFocused: {
    backgroundColor: `${theme.colors.primary}15`, // Light background for focused state
    transform: [{ scale: 1.05 }], // Subtle scale animation
  },
  
  tabLabel: {
    ...typography.caption,
    fontSize: 11,
    fontWeight: '500',
    textAlign: 'center',
    marginTop: 2,
  },
  
  tabLabelFocused: {
    fontWeight: '600',
    color: theme.colors.primary,
  },
});

export default MainTabNavigator;
