# Quick Start: Using the Scoring System

## For Admins - How to Import a Competition with Scoring

### Step 1: Start Import Process
1. Go to **Competitions** or **Events** page
2. Click **"+ Import Kaggle Competition"** button
3. Search for your competition (e.g., "titanic", "house-prices")
4. Click **Search**

### Step 2: Configure Scoring
When you click **"Import"** on a competition, you'll see a scoring configuration form:

```
┌─────────────────────────────────────────────────────────┐
│  Configure Scoring for [Competition Name]          ✕   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Set up how scores from Kaggle will be normalized...   │
│                                                         │
│  ☑ Higher is Better                                    │
│    ✓ Higher scores = better performance                │
│                                                         │
│  Minimum Metric Value:  [0.0          ]                │
│    Worst possible score in the competition              │
│                                                         │
│  Maximum Metric Value:  [1.0          ]                │
│    Best possible score in the competition               │
│                                                         │
│  Points for Perfect Score: [100.0     ]                │
│    Maximum points a participant can earn                │
│                                                         │
│  Formula Preview:                                       │
│  points = (value - 0.0) / (1.0 - 0.0) × 100.0          │
│                                                         │
│  [Cancel]               [Import Competition]            │
└─────────────────────────────────────────────────────────┘
```

### Step 3: Choose Metric Direction

**Check "Higher is Better" if:**
- ✅ Accuracy (0.0 to 1.0)
- ✅ F1-Score (0.0 to 1.0)
- ✅ AUC Score (0.0 to 1.0)
- ✅ Precision/Recall (0.0 to 1.0)

**Uncheck "Higher is Better" if:**
- ❌ Error/Loss (lower is better)
- ❌ RMSE (Root Mean Squared Error)
- ❌ MAE (Mean Absolute Error)
- ❌ Log Loss

### Step 4: Set Min/Max Values

**Examples:**

#### Accuracy-based (0-1 scale)
```
Min: 0.0
Max: 1.0
Points: 100
```
→ Score 0.95 = 95 points
→ Score 0.50 = 50 points

#### Error-based (RMSE, 0-10 range)
```
Higher is Better: ☐ (unchecked)
Min: 0.0
Max: 10.0
Points: 100
```
→ Score 0.0 (perfect!) = 100 points
→ Score 5.0 = 50 points
→ Score 10.0 = 0 points

#### Percentage-based (0-100 scale)
```
Min: 0
Max: 100
Points: 500
```
→ Score 100 = 500 points
→ Score 50 = 250 points

### Step 5: Import & Verify

1. Click **"Import Competition"**
2. Wait for success message
3. Navigate to the competition page
4. Click **"Sync Leaderboard"** button
5. Verify normalized scores appear correctly

## Common Scoring Configurations

### 1. Kaggle Titanic (Accuracy)
```
☑ Higher is Better
Min: 0.0
Max: 1.0
Points: 100
```

### 2. House Prices (RMSE - Error)
```
☐ Higher is Better
Min: 0.0
Max: 50000.0  (estimate worst error)
Points: 100
```

### 3. Image Classification (Accuracy %)
```
☑ Higher is Better
Min: 0.0
Max: 100.0
Points: 100
```

### 4. Regression with MAE
```
☐ Higher is Better
Min: 0.0
Max: [estimate max error from Kaggle description]
Points: 100
```

## Tips & Best Practices

### 1. Check Kaggle Competition Page
- Look at the evaluation metric description
- Note the score range
- Check if higher or lower is better
- Look at current leaderboard to estimate min/max

### 2. Estimate Min/Max Values
If exact values aren't specified:
- **Min (worst)**: Look at bottom of Kaggle leaderboard
- **Max (best)**: Look at top of Kaggle leaderboard
- Add some buffer (e.g., if best is 0.95, set max to 1.0)

### 3. Points for Perfect Score
- Default: **100** is good for most cases
- Use higher values (500, 1000) if you want more granularity
- Use lower values (50) for smaller competitions

### 4. Formula Verification
The preview shows exactly how scores will be calculated:
```
Higher is Better:
  points = (value - min) / (max - min) × PS

Lower is Better:
  points = (max - value) / (max - min) × PS
```

### 5. Testing
1. Import the competition
2. Sync leaderboard (gets real data)
3. Check a few entries manually:
   - Top performer should have high points
   - Bottom performer should have low points
   - Values should be between 0 and your max points

## Troubleshooting

### Scores are all 0 or 100
- Check if min/max values are correct
- Verify "Higher is Better" is set correctly
- Re-sync leaderboard after fixing

### Scores seem inverted
- Toggle "Higher is Better" checkbox
- Re-import the competition with correct settings

### Points are too high/low
- Adjust "Points for Perfect Score" value
- This is a multiplier, doesn't affect relative rankings

### Error: "max must be greater than min"
- Ensure Maximum > Minimum
- Both must be valid numbers

## After Import

### Updating Existing Competitions
Currently, scoring config is set during import. To change:
1. Access Django admin panel
2. Navigate to Competitions
3. Edit the competition
4. Update scoring fields
5. Re-sync leaderboard

### Monitoring Scores
- Check leaderboard page after sync
- Verify scores make sense
- Compare with Kaggle leaderboard for sanity check

---

**Need Help?** 
- Review the SCORING_SYSTEM.md for technical details
- Test with a small competition first
- Check the formula preview before importing
