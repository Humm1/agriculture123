# Visual Screen Guide - Editable Geolocation

## 📱 Screen Flows

### Flow 1: Registration with Auto-detect Location

```
┌─────────────────────────────────────┐
│     REGISTER SCREEN                 │
├─────────────────────────────────────┤
│                                     │
│  Name: [John Doe]                   │
│  Email: [john@example.com]          │
│  Phone: [0712345678]                │
│                                     │
│  I am a:                            │
│  ● Farmer   ○ Buyer                 │
│                                     │
│  ┌────────────────────────────┐    │
│  │ 🌍 Auto-detect my location │ ON │
│  │ Use GPS to fill details    │    │
│  └────────────────────────────┘    │
│                                     │
│  📍 Detecting location...           │
│                                     │
│  Village: [Kiambu Village]          │
│  County: [Kiambu County]  (locked)  │
│  Sub-County: [Kiambu]     (locked)  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ GPS Coordinates:             │  │
│  │ 📍 -1.2921, 36.8219          │  │
│  └──────────────────────────────┘  │
│                                     │
│  Password: [••••••••]               │
│                                     │
│  [      REGISTER      ]             │
│                                     │
└─────────────────────────────────────┘
```

### Flow 2: Farmer Dashboard - Location Card

```
┌─────────────────────────────────────┐
│   FARMER DASHBOARD                  │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 📍 Your Location   [Tracking]│   │
│  │                              │   │
│  │ Kiambu County, Central       │   │
│  │ Village: Kiambu Village      │   │
│  │ Sub-County: Kiambu           │   │
│  │ 📍 -1.2921, 36.8219          │   │
│  │ Accuracy: ±10m               │   │
│  │                              │   │
│  │ [    Edit Location    ]      │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 🌤️ Current Weather          │   │
│  │ 22°C, Clear Sky              │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 🌾 Recommended Crops         │   │
│  │ [Tea] [Maize] [Potatoes]    │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

### Flow 3: Edit Location Screen (Auto-detect ON)

```
┌─────────────────────────────────────┐
│  ← EDIT LOCATION                    │
├─────────────────────────────────────┤
│                                     │
│  ┌────────────────────────────┐    │
│  │ 🎯 Auto-detect Location    │ ON │
│  │ Use GPS to automatically   │    │
│  │ fill location details      │    │
│  └────────────────────────────┘    │
│                                     │
│  [   Refresh GPS Location   ]      │
│                                     │
│  ┌────────────────────────────┐    │
│  │ GPS COORDINATES             │    │
│  │ Auto-detected from GPS      │    │
│  │                             │    │
│  │ Latitude: -1.2921  (locked) │    │
│  │ Longitude: 36.8219 (locked) │    │
│  │                             │    │
│  │ [●] Accuracy: ±10m          │    │
│  └────────────────────────────┘    │
│                                     │
│  ┌────────────────────────────┐    │
│  │ LOCATION DETAILS            │    │
│  │ Auto-detected (editable)    │    │
│  │                             │    │
│  │ Village: [Kiambu Village]   │    │
│  │ Sub-County: [Kiambu]        │    │
│  │ County: [Kiambu County]     │    │
│  │ Region: [Central]           │    │
│  └────────────────────────────┘    │
│                                     │
│  ┌────────────────────────────┐    │
│  │ ℹ️ Why we need location?   │    │
│  │ • Accurate weather          │    │
│  │ • Crop recommendations      │    │
│  │ • Connect with farmers      │    │
│  └────────────────────────────┘    │
│                                     │
│  [    Save Location    ]           │
│  [       Cancel        ]           │
│                                     │
└─────────────────────────────────────┘
```

### Flow 4: Edit Location Screen (Manual Entry)

```
┌─────────────────────────────────────┐
│  ← EDIT LOCATION                    │
├─────────────────────────────────────┤
│                                     │
│  ┌────────────────────────────┐    │
│  │ 🎯 Auto-detect Location    │ OFF│
│  │ Use GPS to automatically   │    │
│  │ fill location details      │    │
│  └────────────────────────────┘    │
│                                     │
│  ┌────────────────────────────┐    │
│  │ GPS COORDINATES             │    │
│  │ Enter manually              │    │
│  │                             │    │
│  │ Latitude: [-1.2921____]     │    │
│  │ Longitude: [36.8219___]     │    │
│  │                             │    │
│  │ Auto-fill from Coordinates  │    │
│  └────────────────────────────┘    │
│                                     │
│  ┌────────────────────────────┐    │
│  │ LOCATION DETAILS            │    │
│  │ Enter your location info    │    │
│  │                             │    │
│  │ Village: [____________]      │    │
│  │ Sub-County: [________]      │    │
│  │ County: [___________]       │    │
│  │ Region: [___________]       │    │
│  └────────────────────────────┘    │
│                                     │
│  ┌────────────────────────────┐    │
│  │ ℹ️ Why we need location?   │    │
│  │ • Accurate weather          │    │
│  │ • Crop recommendations      │    │
│  │ • Connect with farmers      │    │
│  └────────────────────────────┘    │
│                                     │
│  [    Save Location    ]           │
│  [       Cancel        ]           │
│                                     │
└─────────────────────────────────────┘
```

## 🎯 Key UI Elements

### 1. Auto-detect Toggle
```
┌────────────────────────────────────┐
│ 🎯 Auto-detect Location        ON  │
│ Use GPS to automatically fill   ◉  │
│ location details                   │
└────────────────────────────────────┘
```

### 2. GPS Coordinates Display
```
┌────────────────────────────────┐
│ GPS Coordinates:               │
│ 📍 -1.2921, 36.8219            │
└────────────────────────────────┘
```

### 3. Location Tracking Badge
```
┌──────────────────────────────┐
│ 📍 Your Location  [Tracking]  │
└──────────────────────────────┘
```

### 4. Accuracy Indicator
```
[●] Accuracy: ±10m
```

### 5. Validation Error
```
┌──────────────────────────────────┐
│ ⚠️ LOCATION WARNING              │
│                                  │
│ The coordinates appear to be     │
│ outside Kenya. Are you sure?     │
│                                  │
│  [Cancel]      [Continue]        │
└──────────────────────────────────┘
```

## 🔄 State Transitions

### Auto-detect Toggle States

```
OFF State (Manual Entry)
  ↓ Toggle ON
  ↓ Request Permission
  ↓ Get GPS Location
  ↓ Reverse Geocode
  ↓
ON State (Auto-detect)
  ↓ Fields Locked
  ↓ Refresh Available
  
ON State (Auto-detect)
  ↓ Toggle OFF
  ↓
OFF State (Manual Entry)
  ↓ Fields Editable
```

### Location Update Flow

```
User Action
  ↓
[Edit Location Button]
  ↓
EditLocationScreen Opens
  ↓
Choose Mode:
  ├─ Auto-detect ON → GPS → Reverse Geocode → Populate Fields
  └─ Manual Entry → Type Coords → Auto-fill Button → Populate Fields
  ↓
Edit Fields (if needed)
  ↓
[Save Location]
  ↓
Validate Coordinates
  ↓
Update Backend (/api/location/update)
  ↓
Update Database (profiles table)
  ↓
Return to Dashboard
  ↓
Location Card Updated
```

## 🎨 Color Scheme

```
Primary Green:    #4CAF50  (Buttons, active states)
Success Green:    #2E7D32  (Coordinates, success text)
Light Green:      #E8F5E9  (Background, badges)
Gray:             #666666  (Secondary text)
Light Gray:       #F5F5F5  (Disabled fields)
Error Red:        #F44336  (Validation errors)
Info Blue:        #2196F3  (Info cards)
```

## 📐 Layout Structure

```
Edit Location Screen
├── Auto-detect Toggle Card
│   ├── Toggle Switch
│   └── Refresh Button (if ON)
├── GPS Coordinates Card
│   ├── Latitude Input/Display
│   ├── Longitude Input/Display
│   ├── Accuracy Badge
│   └── Auto-fill Button (if OFF)
├── Location Details Card
│   ├── Village Input
│   ├── Sub-County Input
│   ├── County Input
│   └── Region Input
├── Info Card
│   └── Benefits List
└── Action Buttons
    ├── Save Location
    └── Cancel
```

## 🎬 Animation States

### 1. Loading State
```
📍 Detecting location...
   [animated dots]
```

### 2. Success State
```
✓ Location detected automatically
  [green checkmark animation]
```

### 3. Error State
```
✗ Failed to detect location
  [red X with shake animation]
```

### 4. Refresh State
```
🔄 Refreshing GPS location...
   [rotating icon]
```

## 📱 Responsive Design

### Phone Portrait
```
┌─────────────┐
│   Header    │
├─────────────┤
│             │
│   Toggle    │
│             │
│ Coordinates │
│             │
│  Location   │
│   Details   │
│             │
│    Info     │
│             │
│   Actions   │
│             │
└─────────────┘
```

### Tablet Landscape
```
┌──────────────────────────────────┐
│          Header                  │
├──────────────┬───────────────────┤
│              │                   │
│   Toggle     │   Info Card       │
│              │                   │
│ Coordinates  │   • Weather       │
│              │   • Crops         │
│  Location    │   • Farmers       │
│   Details    │                   │
│              │                   │
├──────────────┴───────────────────┤
│        Actions (centered)        │
└──────────────────────────────────┘
```

## ✨ Interactive Elements

### 1. Switch Component
```
OFF  ○━━━━  →  Click  →  ━━━━●  ON
     Gray              Green
```

### 2. Input Fields
```
Enabled:  [___________]  White bg
Disabled: [___________]  Gray bg (auto-detected)
Error:    [___________]  Red border
```

### 3. Buttons
```
Primary:   [Save Location]     Green, white text
Outlined:  [Edit Location]     White, green border
Text:      [Auto-fill...]      Green text only
```

---

**Visual Guide Status:** ✅ Complete

These visual layouts show exactly how the editable geolocation system appears to users across different screens and states!
