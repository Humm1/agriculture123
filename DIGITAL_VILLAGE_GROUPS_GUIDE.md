# Digital Village Groups - Complete Feature Guide

**Hyper-local, experience-sharing farming communities**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Core Concept](#core-concept)
3. [Feature 1: Automatic Farming Zone Grouping](#feature-1-automatic-farming-zone-grouping)
4. [Feature 2: Structured "What's Working" Feed](#feature-2-structured-whats-working-feed)
5. [Feature 3: Verified Neighbor Trust System](#feature-3-verified-neighbor-trust-system)
6. [Feature 4: Digital Demo Plot & Community Polls](#feature-4-digital-demo-plot--community-polls)
7. [API Documentation](#api-documentation)
8. [Mobile App Integration](#mobile-app-integration)
9. [Success Metrics](#success-metrics)

---

## Overview

**Digital Village Groups** transform AgroShield from individual farming advice into a **community learning platform** where farmers share real experiences with neighbors facing identical farming conditions.

### The Problem
- Farmers get generic advice that doesn't apply to their specific soil, climate, or crops
- No way to know what's **actually working** for neighbors right now
- Hard to trust online information from strangers far away
- Misinformation spreads without expert validation

### The Solution
Automatic, private forums where farmers are grouped by:
1. **Location** (GPS + region)
2. **Crops** (maize, coffee, beans, etc.)
3. **Soil Type** (visual photo selection)

**Example Group**: "Bobasi - Red Clay - Maize Farmers" (50 members)

---

## Core Concept

### "Digital Village Groups"

```
┌────────────────────────────────────────────────────────┐
│  AUTOMATIC GROUPING (During Registration)             │
├────────────────────────────────────────────────────────┤
│  1. Capture GPS → Region: "Bobasi"                    │
│  2. Select Crops → "Maize" + "Beans"                  │
│  3. Identify Soil → [Photo] "Red Clay"                │
│                                                        │
│  → Auto-Assign: "Bobasi - Red Clay - Maize Farmers"  │
│     (50 members, 2 extension officers)                 │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│  STRUCTURED FEED (Organized by Topic)                 │
├────────────────────────────────────────────────────────┤
│  [Share Success] Mary: "My yield doubled!" ⭐24       │
│  [Ask Question]  Peter: "Yellow leaves?" 🤔12         │
│  [Share Problem] Jane: "Pest on maize" 🐛8            │
│  [Share Tip]     John: "Try this timing" ✓Verified    │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│  TRUST SYSTEM (Verified + Upvoted)                    │
├────────────────────────────────────────────────────────┤
│  ✓ Expert Verified (Extension Officer confirms)       │
│  ⭐ Peer Upvoted (24 farmers: "This worked!")         │
│  📊 Most Helpful Tips (Top 5 this week)               │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│  COMMUNITY FEATURES (Active Participation)            │
├────────────────────────────────────────────────────────┤
│  🏆 Weekly Showcase: "This Week's Best Crop"          │
│  📸 Problem Gallery: Photo problems + solutions       │
│  📊 Polls: "When are you planting?" (46 votes)        │
└────────────────────────────────────────────────────────┘
```

---

## Feature 1: Automatic Farming Zone Grouping

### Why It's Critical
**Relevance = Usefulness.** If farmers see advice from someone with different soil, weather, or crops, they'll ignore it. Automatic grouping ensures every post is applicable.

### Onboarding Flow

#### Step 1: Capture GPS (Automatic)
```
┌─────────────────────────────────────┐
│  📍 Location Detected               │
│                                     │
│  Region: Bobasi                     │
│  Coordinates: -0.65°, 34.80°       │
│                                     │
│  [Continue] →                       │
└─────────────────────────────────────┘
```

**Technical**: App automatically captures GPS on registration. Reverse geocode to get region name (Kenya counties/sub-counties).

---

#### Step 2: Select Main Crops (Dropdown)
```
┌─────────────────────────────────────┐
│  🌾 What do you mainly grow?        │
│                                     │
│  ☑ Maize                            │
│  ☑ Beans                            │
│  ☐ Coffee                           │
│  ☐ Bananas                          │
│  ☐ Potatoes                         │
│  ☐ Tea                              │
│                                     │
│  [Continue] →                       │
└─────────────────────────────────────┘
```

**Technical**: Multi-select dropdown. Primary crop = group identifier. Secondary crops = tags for filtering.

---

#### Step 3: Identify Soil Type (Visual Selection)
```
┌─────────────────────────────────────────────────────────┐
│  🏞️ Which soil looks most like yours?                   │
│                                                         │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐          │
│  │  [Photo]  │  │  [Photo]  │  │  [Photo]  │          │
│  │ Red Clay  │  │ Black     │  │ Brown     │          │
│  │           │  │ Cotton    │  │ Loam      │          │
│  └───────────┘  └───────────┘  └───────────┘          │
│                                                         │
│  ┌───────────┐  ┌───────────┐                          │
│  │  [Photo]  │  │  [Photo]  │                          │
│  │ Sandy     │  │ Volcanic  │                          │
│  │           │  │           │                          │
│  └───────────┘  └───────────┘                          │
│                                                         │
│  [Select] →                                             │
└─────────────────────────────────────────────────────────┘
```

**Why Photos?** Most farmers don't know scientific soil names. Visual recognition is instant and accurate.

**Soil Types**:
- **Red Clay**: Common in Western Kenya (Kisii, Nyamira)
- **Black Cotton**: Central Kenya (Nakuru, Narok)
- **Brown Loam**: Rift Valley
- **Sandy**: Coastal regions
- **Volcanic**: Mt. Kenya region

---

#### Step 4: Auto-Assignment Confirmation
```
┌─────────────────────────────────────────────────────────┐
│  🎉 Welcome to Your Village Group!                      │
│                                                         │
│  Group: Bobasi - Red Clay - Maize Farmers              │
│  Members: 47 farmers                                   │
│  Experts: 2 extension officers                         │
│                                                         │
│  You're now connected with farmers who:                │
│  ✓ Live within 5km of you                             │
│  ✓ Grow the same crops (maize, beans)                 │
│  ✓ Have the same soil type (red clay)                 │
│                                                         │
│  Start sharing experiences!                            │
│                                                         │
│  [Go to My Group] →                                    │
└─────────────────────────────────────────────────────────┘
```

---

### Grouping Algorithm

```python
def calculate_farming_zone(location, crops, soil_type):
    """
    Grouping Rules:
    1. Farmers within 5km radius (same micro-climate)
    2. At least 1 common crop
    3. Same soil type (strongest farming condition indicator)
    """
    
    # Get region from GPS
    region = reverse_geocode(location)  # "Bobasi"
    
    # Primary crop
    primary_crop = crops[0]  # "maize"
    
    # Generate zone ID
    zone_id = f"{region}_{soil_type}_{primary_crop}"
    # Example: "bobasi_red_clay_maize"
    
    # Generate friendly name
    group_name = f"{region} - {soil_type} - {primary_crop} Farmers"
    # Example: "Bobasi - Red Clay - Maize Farmers"
    
    return zone_id, group_name
```

---

## Feature 2: Structured "What's Working" Feed

### Why Structure Matters
Free-form chat becomes noise. **Templates guide farmers to share useful information** in a consistent, scannable format.

### Post Templates

#### Template 1: Share a Success ✅
```
┌─────────────────────────────────────────────────────────┐
│  ✅ Share a Success                                     │
│                                                         │
│  What worked for you?                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │ My maize yield doubled this season!             │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  Tell us more (optional):                              │
│  ┌─────────────────────────────────────────────────┐  │
│  │ I used DAP fertilizer at planting time and      │  │
│  │ weeded 3 times instead of 2...                  │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  📸 [Add Photo]  🎙️ [Record Voice]                   │
│                                                         │
│  [Post to Group] →                                     │
└─────────────────────────────────────────────────────────┘
```

**Use Case**: Farmer wants to brag about great harvest. Others learn what worked.

---

#### Template 2: Ask a Question 🤔
```
┌─────────────────────────────────────────────────────────┐
│  🤔 Ask a Question                                      │
│                                                         │
│  What do you need help with?                           │
│  ┌─────────────────────────────────────────────────┐  │
│  │ Why are my bean leaves turning yellow?         │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  More details (optional):                              │
│  ┌─────────────────────────────────────────────────┐  │
│  │ They started yellowing after heavy rain...      │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  📸 [Add Photo]  🎙️ [Record Voice]                   │
│                                                         │
│  [Ask Your Neighbors] →                                │
└─────────────────────────────────────────────────────────┘
```

**Use Case**: Farmer sees problem, doesn't know cause. Neighbors with same conditions can help.

---

#### Template 3: Share a Problem ⚠️
```
┌─────────────────────────────────────────────────────────┐
│  ⚠️ Share a Problem                                     │
│                                                         │
│  What's wrong?                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │ Strange insects on my maize leaves              │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  📸 PHOTO REQUIRED - Take a clear photo of problem    │
│                                                         │
│  [Take Photo] 📸                                       │
│                                                         │
│  🎙️ [Or record description in Swahili]               │
│                                                         │
│  [Get Help from Neighbors] →                           │
└─────────────────────────────────────────────────────────┘
```

**Use Case**: Pest/disease identification. Photo is crucial for diagnosis. Other farmers can reply with solutions.

---

#### Template 4: Share a Tip 💡
```
┌─────────────────────────────────────────────────────────┐
│  💡 Share a Tip                                         │
│                                                         │
│  What advice do you have?                              │
│  ┌─────────────────────────────────────────────────┐  │
│  │ Plant maize in early March, not late March      │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  Why does this work?                                   │
│  ┌─────────────────────────────────────────────────┐  │
│  │ Early planting catches the long rains. I've     │  │
│  │ done this for 5 years and it works.            │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  📸 [Add Photo]  🎙️ [Record Voice]                   │
│                                                         │
│  [Share Tip] →                                         │
└─────────────────────────────────────────────────────────┘
```

**Use Case**: Experienced farmer shares seasonal timing, technique, or variety recommendation.

---

### Voice-First, Photo-First Design

#### Why Voice Notes Are Critical
1. **Literacy barrier**: Not all farmers comfortable typing
2. **Speed**: 10x faster than typing on phone
3. **Language**: Can speak local language (Swahili, Kikuyu, Luo, etc.)
4. **Emotion**: Voice conveys enthusiasm, urgency, confidence

#### Voice Note UI
```
┌─────────────────────────────────────┐
│  🎙️ Record Your Message             │
│                                     │
│  ┌─────────────────────────────┐   │
│  │         🔴 REC              │   │
│  │                             │   │
│  │      [●●●●●●●●●●]          │   │
│  │                             │   │
│  │      Recording: 0:15        │   │
│  └─────────────────────────────┘   │
│                                     │
│  [Stop] 🛑  [Delete] 🗑️            │
└─────────────────────────────────────┘
```

**Technical Features**:
- Max 60 seconds (keeps messages concise)
- Auto-transcription to text (optional, for accessibility)
- Playback speed control (1x, 1.5x, 2x)
- Download for offline listening

---

### Feed Organization

#### View: Recent Posts (Default)
```
┌─────────────────────────────────────────────────────────┐
│  Bobasi - Red Clay - Maize Farmers (47 members)        │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  [Filter: All ▼]  [Sort: Recent ▼]                     │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ ✅ Mary Wanjiku • 2 hours ago                   │   │
│  │ "My maize yield doubled this season!"           │   │
│  │ [Photo: Tall healthy maize]                     │   │
│  │ ⭐24  💬8  ✓Expert Verified                     │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 🤔 Peter Mwangi • 5 hours ago                   │   │
│  │ "Why are my bean leaves turning yellow?"        │   │
│  │ [Photo: Yellow leaves]  🎙️ 0:23                │   │
│  │ ⭐5  💬12                                        │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [Load More Posts...]                                  │
└─────────────────────────────────────────────────────────┘
```

#### View: Most Helpful (Sorted by Upvotes)
```
┌─────────────────────────────────────────────────────────┐
│  🏆 Most Helpful Tips in Your Village                   │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 💡 John Kamau • 3 days ago                      │   │
│  │ "Plant in early March, not late March"          │   │
│  │ ⭐45  💬18  ✓Expert Verified                    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ ✅ Jane Wambui • 1 week ago                     │   │
│  │ "Neem oil spray worked for pests"               │   │
│  │ [Photos: Before/After]                          │   │
│  │ ⭐38  💬22                                       │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

#### View: Expert Verified Only
```
┌─────────────────────────────────────────────────────────┐
│  ✓ Expert-Approved Advice                              │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  Only showing posts verified by extension officers     │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ ✅ Mary Wanjiku • 2 days ago                    │   │
│  │ "My maize yield doubled this season!"           │   │
│  │ ✓ Verified by Extension Officer John Omondi    │   │
│  │ ⭐24  💬8                                        │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Feature 3: Verified Neighbor Trust System

### The Trust Problem
Farmers won't follow advice unless they trust it. Two trust signals:
1. **Expert Verification**: "A professional says this is correct"
2. **Peer Validation**: "24 neighbors tried this and it worked"

---

### Expert Verification

#### Who Are Experts?
- Government extension officers
- NGO agricultural advisors
- Certified agronomists
- Crop scientists

#### How Verification Works

**Step 1**: Expert sees good farmer advice
```
┌─────────────────────────────────────────────────────────┐
│  Mary Wanjiku • 2 hours ago                            │
│  "I used DAP fertilizer at planting time..."           │
│  [Photo: Healthy maize]                                │
│  ⭐12  💬5                                             │
│                                                         │
│  [As Expert: Verify This ✓]                            │
└─────────────────────────────────────────────────────────┘
```

**Step 2**: Expert taps "Verify This"
```
┌─────────────────────────────────────────────────────────┐
│  ✓ Verify This Advice                                  │
│                                                         │
│  Post: "I used DAP fertilizer at planting time..."     │
│                                                         │
│  Why is this advice correct?                           │
│  ┌─────────────────────────────────────────────────┐  │
│  │ This is scientifically sound. DAP provides      │  │
│  │ phosphorus which is crucial at planting stage.  │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  Your name: Extension Officer John Omondi              │
│                                                         │
│  [Confirm Verification] ✓                              │
└─────────────────────────────────────────────────────────┘
```

**Step 3**: Post shows verification badge
```
┌─────────────────────────────────────────────────────────┐
│  ✅ Mary Wanjiku • 2 hours ago                         │
│  "I used DAP fertilizer at planting time..."           │
│  [Photo: Healthy maize]                                │
│                                                         │
│  ✓ EXPERT VERIFIED                                     │
│  Extension Officer John Omondi confirmed this advice   │
│  is scientifically correct.                            │
│                                                         │
│  ⭐24 (↑doubled after verification)  💬8               │
└─────────────────────────────────────────────────────────┘
```

**Impact**: Verification increases trust → More farmers try the advice → More upvotes → Advice rises to top of feed.

---

### Correcting Misinformation (Gentle Approach)

**Bad Advice Example**:
```
┌─────────────────────────────────────────────────────────┐
│  💡 James Kibet • 1 day ago                            │
│  "Spray pesticide right before harvest for best        │
│   results"                                             │
│  ⭐3  💬2                                              │
└─────────────────────────────────────────────────────────┘
```

**Expert Correction** (Not deletion, but education):
```
┌─────────────────────────────────────────────────────────┐
│  💡 James Kibet • 1 day ago                            │
│  "Spray pesticide right before harvest..."            │
│  ⭐3  💬2                                              │
│                                                         │
│  ⚠️ EXPERT NOTE                                        │
│  Extension Officer Sarah Mwangi:                       │
│  "James, this is dangerous! Pesticides need 7-14 days  │
│   to break down (PHI - pre-harvest interval). Spraying │
│   right before harvest leaves toxic residue. Always    │
│   check the product label for PHI. Great question      │
│   though - many farmers don't know this!"              │
│                                                         │
│  💬 Reply from James: "Thank you! I didn't know."     │
└─────────────────────────────────────────────────────────┘
```

**Why Not Delete?**
- Transparency: Others learn from the correction
- Education: Public teaching moment
- Respect: Doesn't shame farmer, just educates

---

### Peer Upvoting

#### How Upvoting Works

**Farmer sees advice** → **Tries it on farm** → **It works!** → **Upvotes post**

```
┌─────────────────────────────────────────────────────────┐
│  💡 Mary Wanjiku • 3 days ago                          │
│  "Plant maize in early March, not late March"          │
│  Reason: Catches the long rains                        │
│  ⭐24  💬8  ✓Expert Verified                           │
│                                                         │
│  Did this advice work for you?                         │
│  [Yes, it worked! ⭐] [No] [Not tried yet]             │
└─────────────────────────────────────────────────────────┘
```

**After upvoting**:
```
┌─────────────────────────────────────────────────────────┐
│  🎉 Thank you!                                          │
│                                                         │
│  Your feedback helps other farmers in your village     │
│  know this advice is trustworthy.                      │
│                                                         │
│  25 farmers have confirmed this worked for them.       │
│                                                         │
│  [OK]                                                  │
└─────────────────────────────────────────────────────────┘
```

---

### Trust Metrics Display

```
┌─────────────────────────────────────────────────────────┐
│  💡 Mary Wanjiku • 3 days ago                          │
│  "Plant maize in early March, not late March"          │
│                                                         │
│  Trust Signals:                                        │
│  ✓ Expert Verified (Extension Officer John Omondi)    │
│  ⭐ 24 farmers: "This worked for me!"                  │
│  💬 8 replies with additional tips                     │
│  👁️ 156 farmers viewed this                           │
│                                                         │
│  [Read More] →                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Feature 4: Digital Demo Plot & Community Polls

### Digital Demo Plot: Weekly Showcase

Every week, the system highlights **1 successful farmer** with impressive results. Other farmers can learn and ask questions.

#### This Week's Showcase
```
┌─────────────────────────────────────────────────────────┐
│  🏆 THIS WEEK'S BEST CROP                              │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  Featured Farmer: Mary Wanjiku                         │
│  Crop: Maize                                           │
│  Achievement: Yield doubled (6 bags/acre → 12 bags)    │
│                                                         │
│  📸 [Photo: Tall, healthy maize field]                │
│  📸 [Photo: Harvest bags]                              │
│                                                         │
│  ──── What Worked for Mary ────                        │
│  ✓ Planted in early March (not late)                  │
│  ✓ Used DAP fertilizer at planting                    │
│  ✓ Weeded 3 times instead of 2                        │
│  ✓ Applied CAN fertilizer at knee-height stage        │
│                                                         │
│  ⭐45 upvotes  💬18 questions answered                │
│                                                         │
│  [Ask Mary a Question] →                               │
└─────────────────────────────────────────────────────────┘
```

#### Farmers Ask Mary
```
┌─────────────────────────────────────────────────────────┐
│  Questions for Mary                                    │
│                                                         │
│  Q: What brand of DAP did you use?                     │
│  A: I used Mea fertilizer, but any DAP works.         │
│                                                         │
│  Q: How much did you spend on fertilizer?              │
│  A: About 3,500 KES for 2 acres. Got it back 3x!      │
│                                                         │
│  Q: What maize variety?                                │
│  A: DH04 (drought-resistant hybrid)                    │
│                                                         │
│  [Ask Your Question] →                                 │
└─────────────────────────────────────────────────────────┘
```

**Impact**: Other farmers see **real proof** from their neighbor. Way more convincing than generic advice from a distant expert.

---

### Problem-Solving Gallery

Visual knowledge base of problems + farmer solutions.

#### Gallery View
```
┌─────────────────────────────────────────────────────────┐
│  🐛 Pest Problem-Solving Gallery                       │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  PROBLEM: "Strange insects on maize"                   │
│  Posted by: John Doe • 5 days ago                     │
│  📸 [Photo: Close-up of pest]                          │
│                                                         │
│  ──── Solutions from Neighbors ────                    │
│                                                         │
│  Solution 1: Neem Oil Spray ⭐12                       │
│  Jane Mwangi: "I had the same pest. Mixed neem oil    │
│   with soap and water. Worked in 3 days."             │
│  📸 [Before photo] → 📸 [After photo]                 │
│                                                         │
│  Solution 2: Chili + Soap Mix ⭐18                     │
│  Peter Kamau: "I blended chili peppers with soap and  │
│   water. Sprayed every 2 days. Worked in 5 days."     │
│  📸 [My spray bottle] → 📸 [Clean leaves]             │
│                                                         │
│  Solution 3: Local Ash Method ⭐8                      │
│  Grace Njeri: "Sprinkled wood ash on leaves early     │
│   morning. Kept pests away."                           │
│  📸 [Photo: Ash application]                           │
│                                                         │
│  [Try a Solution] [Add Your Solution] →                │
└─────────────────────────────────────────────────────────┘
```

**Key Feature**: Photo progression (Before → Solution → After) provides visual proof.

---

### Community Polls

Simple polls for group decision-making and consensus.

#### Poll Example 1: Planting Timing
```
┌─────────────────────────────────────────────────────────┐
│  📊 Community Poll                                      │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  Asked by Peter Mwangi • 2 days ago                    │
│  Expires in 5 days                                     │
│                                                         │
│  When is everyone planting maize?                      │
│                                                         │
│  ○ This week          [███████░░░] 15 votes (32%)      │
│  ● Next week          [████████████] 23 votes (50%)    │
│  ○ Waiting for rain   [████░░░░░░░░] 8 votes (17%)     │
│                                                         │
│  Total: 46 farmers voted                               │
│                                                         │
│  [Vote]  [View Results]                                │
│                                                         │
│  💬 Top comment:                                       │
│  "Next week looks better - forecast shows rain!"       │
└─────────────────────────────────────────────────────────┘
```

**Use Case**: Farmer unsure when to plant. Sees 50% of neighbors planting next week → Gains confidence to wait for better conditions.

---

#### Poll Example 2: Seed Variety
```
┌─────────────────────────────────────────────────────────┐
│  📊 Community Poll                                      │
│                                                         │
│  What maize variety are you planting this season?      │
│                                                         │
│  ○ DH04 (drought-resistant)    [█████████] 32 (52%)    │
│  ○ H513 (high-yield)            [████░░░░░] 18 (29%)    │
│  ○ Local variety                [███░░░░░░] 12 (19%)    │
│                                                         │
│  Total: 62 votes                                       │
│                                                         │
│  [Vote]  [View Results]                                │
│                                                         │
│  💬 Trending comment:                                  │
│  "DH04 worked great last year despite dry spell!"      │
└─────────────────────────────────────────────────────────┘
```

**Impact**: Farmers see what's popular locally → Feel confident in their choice → Reduce risk.

---

## API Documentation

### Base URL
```
https://api.agroshield.com/v1
```

### Authentication
All endpoints require farmer authentication via JWT token or API key.

---

### Endpoints

#### 1. Register Farmer to Group
```http
POST /groups/register-farmer
```

**Request Body**:
```json
{
  "farmer_id": "farmer_12345",
  "name": "John Doe",
  "phone": "+254712345678",
  "location": {"lat": -0.65, "lon": 34.80},
  "region": "Bobasi",
  "main_crops": ["maize", "beans"],
  "soil_type": "red_clay",
  "farm_size_acres": 2.5,
  "language": "swahili"
}
```

**Response**:
```json
{
  "success": true,
  "farmer_id": "farmer_12345",
  "assigned_group": {
    "group_id": "bobasi_red_clay_maize",
    "name": "Bobasi - Red Clay - Maize Farmers",
    "region": "Bobasi",
    "soil_type": "red_clay",
    "primary_crops": ["maize", "beans"],
    "member_count": 47
  },
  "message": "Welcome to Bobasi - Red Clay - Maize Farmers! You're now connected with 47 farmers in your area."
}
```

---

#### 2. Create Community Post
```http
POST /groups/{group_id}/posts
```

**Request** (multipart/form-data):
```
farmer_id: farmer_12345
post_type: success_story
title: My maize yield doubled!
description: I used DAP fertilizer at planting time...
photo: [file upload]
voice_note: [audio file upload]
language: swahili
```

**Response**:
```json
{
  "success": true,
  "post_id": "post_abc123",
  "post": {
    "post_id": "post_abc123",
    "group_id": "bobasi_red_clay_maize",
    "farmer_id": "farmer_12345",
    "farmer_name": "Mary Wanjiku",
    "post_type": "success_story",
    "title": "My maize yield doubled!",
    "description": "I used DAP fertilizer...",
    "photo_urls": ["https://cdn.agroshield.com/photos/abc123.jpg"],
    "voice_note_url": "https://cdn.agroshield.com/voice/abc123.mp3",
    "upvotes": 0,
    "expert_verified": false,
    "created_at": "2025-10-24T10:30:00Z"
  },
  "message": "Your success_story has been shared with your village group!"
}
```

---

#### 3. Get Group Feed
```http
GET /groups/{group_id}/feed?filter_type=all&sort_by=recent
```

**Query Parameters**:
- `filter_type`: `all`, `success_story`, `question`, `problem`, `tip`
- `sort_by`: `recent`, `helpful`, `verified`

**Response**:
```json
{
  "group_id": "bobasi_red_clay_maize",
  "total_posts": 45,
  "posts": [
    {
      "post_id": "post_001",
      "farmer_name": "Mary Wanjiku",
      "post_type": "success_story",
      "title": "My maize yield doubled!",
      "description": "I used DAP fertilizer...",
      "photo_urls": ["https://cdn.agroshield.com/photos/001.jpg"],
      "upvotes": 24,
      "expert_verified": true,
      "verified_by": "Extension Officer John Omondi",
      "reply_count": 8,
      "created_at": "2025-10-20T10:30:00Z"
    }
  ]
}
```

---

#### 4. Upvote Post
```http
POST /posts/{post_id}/upvote
```

**Request Body**:
```json
{
  "farmer_id": "farmer_12345"
}
```

**Response**:
```json
{
  "success": true,
  "post_id": "post_001",
  "upvotes": 25,
  "message": "Thank you for marking this as helpful!"
}
```

---

#### 5. Expert Verify Post
```http
POST /posts/{post_id}/verify
```

**Request Body**:
```json
{
  "expert_id": "expert_789",
  "expert_name": "Extension Officer John Omondi"
}
```

**Response**:
```json
{
  "success": true,
  "post_id": "post_001",
  "expert_verified": true,
  "verified_by": "Extension Officer John Omondi",
  "message": "This advice has been verified by Extension Officer John Omondi"
}
```

---

#### 6. Create Community Poll
```http
POST /groups/{group_id}/polls
```

**Request Body**:
```json
{
  "farmer_id": "farmer_12345",
  "question": "When is everyone planting maize?",
  "options": ["This week", "Next week", "Waiting for rain"],
  "duration_days": 7
}
```

**Response**:
```json
{
  "success": true,
  "poll_id": "poll_xyz789",
  "poll": {
    "poll_id": "poll_xyz789",
    "question": "When is everyone planting maize?",
    "options": ["This week", "Next week", "Waiting for rain"],
    "votes": {"This week": 0, "Next week": 0, "Waiting for rain": 0},
    "total_votes": 0,
    "expires_at": "2025-10-31T00:00:00Z"
  },
  "message": "Poll created! Your neighbors can now vote."
}
```

---

#### 7. Vote on Poll
```http
POST /polls/{poll_id}/vote
```

**Request Body**:
```json
{
  "farmer_id": "farmer_12345",
  "option": "Next week"
}
```

**Response**:
```json
{
  "success": true,
  "poll_id": "poll_xyz789",
  "your_vote": "Next week",
  "results": {
    "This week": 15,
    "Next week": 23,
    "Waiting for rain": 8
  },
  "percentages": {
    "This week": 32.6,
    "Next week": 50.0,
    "Waiting for rain": 17.4
  },
  "total_votes": 46,
  "message": "Your vote recorded! 46 farmers have voted."
}
```

---

## Mobile App Integration

### React Native Components

#### GroupFeed.js
```javascript
import React, { useState, useEffect } from 'react';
import { View, FlatList, TouchableOpacity, Text } from 'react-native';

const GroupFeed = ({ groupId }) => {
  const [posts, setPosts] = useState([]);
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('recent');

  useEffect(() => {
    fetchFeed();
  }, [filter, sortBy]);

  const fetchFeed = async () => {
    const response = await fetch(
      `https://api.agroshield.com/v1/groups/${groupId}/feed?filter_type=${filter}&sort_by=${sortBy}`
    );
    const data = await response.json();
    setPosts(data.posts);
  };

  return (
    <View>
      {/* Filter buttons */}
      <View style={styles.filterRow}>
        <TouchableOpacity onPress={() => setFilter('all')}>
          <Text>All Posts</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => setFilter('success_story')}>
          <Text>✅ Success</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => setFilter('question')}>
          <Text>🤔 Questions</Text>
        </TouchableOpacity>
      </View>

      {/* Feed list */}
      <FlatList
        data={posts}
        renderItem={({ item }) => <PostCard post={item} />}
        keyExtractor={item => item.post_id}
      />
    </View>
  );
};
```

---

#### VoiceRecorder.js
```javascript
import React, { useState } from 'react';
import { View, TouchableOpacity, Text } from 'react-native';
import { Audio } from 'expo-av';

const VoiceRecorder = ({ onRecordingComplete }) => {
  const [recording, setRecording] = useState(null);
  const [isRecording, setIsRecording] = useState(false);

  const startRecording = async () => {
    try {
      await Audio.requestPermissionsAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true
      });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RECORDING_OPTIONS_PRESET_HIGH_QUALITY
      );

      setRecording(recording);
      setIsRecording(true);
    } catch (err) {
      console.error('Failed to start recording', err);
    }
  };

  const stopRecording = async () => {
    setIsRecording(false);
    await recording.stopAndUnloadAsync();
    const uri = recording.getURI();
    onRecordingComplete(uri);
  };

  return (
    <View style={styles.voiceRecorder}>
      {!isRecording ? (
        <TouchableOpacity onPress={startRecording} style={styles.recordButton}>
          <Text style={styles.recordIcon}>🎙️</Text>
          <Text>Tap to Record</Text>
        </TouchableOpacity>
      ) : (
        <TouchableOpacity onPress={stopRecording} style={styles.stopButton}>
          <Text style={styles.stopIcon}>🛑</Text>
          <Text>Stop Recording</Text>
        </TouchableOpacity>
      )}
    </View>
  );
};
```

---

## Success Metrics

### Engagement Metrics
- **Active Groups**: Number of groups with at least 1 post/week
- **Post Rate**: Posts per farmer per month (target: 2+)
- **Reply Rate**: Replies per post (target: 5+)
- **Upvote Rate**: % of posts with 10+ upvotes (target: 30%)
- **Expert Verification Rate**: % of posts verified (target: 20%)

### Trust Metrics
- **Post Quality Score**: (Upvotes + Replies) / Views
- **Expert Response Time**: Time for expert to reply to questions (target: <24 hours)
- **Misinformation Correction Rate**: % of bad advice corrected (target: 100%)

### Community Health Metrics
- **Member Retention**: % of farmers active 30 days after joining (target: 60%)
- **Cross-Pollination**: % of farmers asking questions in other farmers' threads (target: 40%)
- **Showcase Participation**: % of farmers featured in weekly showcase (target: 10% per year)

### Impact Metrics
- **Adoption Rate**: % of farmers who try advice from feed (target: 40%)
- **Success Rate**: % of farmers who upvote after trying advice (target: 70%)
- **Knowledge Spread**: Average upvotes per verified post (target: 25+)

---

## Next Steps

1. **Integrate API into Mobile App** (Week 1-2)
   - Add group registration flow to onboarding
   - Build feed UI with filtering and sorting
   - Implement voice recording for posts
   - Add photo upload for problems/solutions

2. **Recruit Extension Officers** (Week 2-3)
   - Partner with Kenya Ministry of Agriculture
   - Train officers on verification process
   - Set up expert accounts with badges

3. **Pilot Program** (Week 4-8)
   - Launch in 3 regions (Bobasi, Nyamira, Kisii)
   - Target 500 farmers across 10 groups
   - Monitor engagement metrics
   - Collect feedback

4. **Iterate & Scale** (Week 9+)
   - Add more post templates based on usage
   - Improve trust signals (more badges, rankings)
   - Expand to more regions
   - Add marketplace integration (farmers sell to each other)

---

**🌾 Digital Village Groups: Turning Farmers into Teachers**

*Version 1.0 • October 2025*
