# Scoring System Documentation

## Overview
The ML-Battle platform now features a sophisticated scoring normalization system that allows competition organizers to configure how raw Kaggle scores are converted into normalized points for leaderboard rankings.

## Features

### 1. Configurable Scoring Parameters
When importing a competition from Kaggle, admins can configure:

- **Higher is Better** (boolean): Whether higher scores indicate better performance
- **Metric Min Value** (float): The worst possible score in the competition
- **Metric Max Value** (float): The best possible score in the competition  
- **Points for Perfect Score** (float): Maximum points a participant can earn (default: 100)

### 2. Scoring Formulas

The system uses different formulas based on the metric direction:

#### Higher is Better (e.g., Accuracy, F1-Score)
```
normalized_score = ((raw_score - min_value) / (max_value - min_value)) × perfect_score_points
```

#### Lower is Better (e.g., Error, Loss, RMSE)
```
normalized_score = ((max_value - raw_score) / (max_value - min_value)) × perfect_score_points
```

**Score Clamping**: All normalized scores are clamped between 0 and `perfect_score_points` to prevent invalid values.

## Usage

### Admin Import Flow

1. **Search for Kaggle Competition**
   - Navigate to Events or Competitions page
   - Click "Import Kaggle Competition" button
   - Search for the competition

2. **Configure Scoring Parameters**
   - Click "Import" on a competition
   - A modal appears with scoring configuration form
   - Set the scoring parameters:
     - Check/uncheck "Higher is Better"
     - Enter minimum metric value (worst possible score)
     - Enter maximum metric value (best possible score)
     - Set points for perfect score (default: 100)

3. **Preview Formula**
   - The form shows a live preview of the formula
   - Verify the formula matches your competition's scoring

4. **Import Competition**
   - Click "Import Competition"
   - The competition is created with scoring configuration
   - Leaderboard syncs will automatically use these parameters

### Leaderboard Sync

When syncing leaderboard data from Kaggle:

1. Raw scores are extracted from Kaggle CSV
2. Each score is normalized using the competition's formula
3. Normalized scores are saved to the database
4. Leaderboard displays normalized scores
5. Rankings are based on normalized scores

### Example Configurations

#### Accuracy-based Competition
```json
{
  "higher_is_better": true,
  "metric_min_value": 0.0,
  "metric_max_value": 1.0,
  "points_for_perfect_score": 100.0
}
```
- Raw score 0.95 → 95 points
- Raw score 0.50 → 50 points
- Raw score 0.00 → 0 points

#### Error-based Competition (RMSE)
```json
{
  "higher_is_better": false,
  "metric_min_value": 0.0,
  "metric_max_value": 10.0,
  "points_for_perfect_score": 100.0
}
```
- Raw score 0.0 (perfect) → 100 points
- Raw score 5.0 → 50 points
- Raw score 10.0 (worst) → 0 points

#### Custom Point Scale
```json
{
  "higher_is_better": true,
  "metric_min_value": 0.0,
  "metric_max_value": 100.0,
  "points_for_perfect_score": 500.0
}
```
- Raw score 100 → 500 points
- Raw score 50 → 250 points
- Raw score 0 → 0 points

## Database Schema

### Competition Model (New Fields)
```python
class Competition(models.Model):
    # ... existing fields ...
    
    # Scoring configuration
    higher_is_better = models.BooleanField(
        default=True,
        help_text='Whether higher scores indicate better performance'
    )
    metric_min_value = models.FloatField(
        default=0.0,
        help_text='Minimum value of the competition metric (worst score)'
    )
    metric_max_value = models.FloatField(
        default=1.0,
        help_text='Maximum value of the competition metric (best score)'
    )
    points_for_perfect_score = models.FloatField(
        default=100.0,
        help_text='Points awarded for achieving the best score'
    )
```

## API Endpoints

### Import Competition with Scoring Config
```http
POST /api/competitions/import_from_kaggle/
Content-Type: application/json

{
  "kaggle_id": "competition-name",
  "event_id": 1,  // optional
  "higher_is_better": true,
  "metric_min_value": 0.0,
  "metric_max_value": 1.0,
  "points_for_perfect_score": 100.0
}
```

**Response:**
```json
{
  "message": "Competition imported successfully",
  "competition": {
    "id": 1,
    "title": "Competition Name",
    "higher_is_better": true,
    "metric_min_value": 0.0,
    "metric_max_value": 1.0,
    "points_for_perfect_score": 100.0,
    // ... other fields
  }
}
```

## Technical Implementation

### Backend Changes

1. **Models** (`apps/competitions/models.py`)
   - Added 4 scoring configuration fields
   - Migration `0003_competition_higher_is_better_and_more` applied

2. **Views** (`apps/competitions/views.py`)
   - Updated `import_from_kaggle` to accept scoring parameters
   - Added validation for min/max values
   - Saves scoring config during competition creation

3. **Serializers** (`apps/competitions/serializers.py`)
   - Exposed scoring fields in API responses

4. **Leaderboard Sync** (`apps/competitions/kaggle_leaderboard_sync.py`)
   - Added `calculate_normalized_score()` method
   - Updated CSV processing to calculate normalized scores
   - Saves normalized scores to database

### Frontend Changes

1. **API Service** (`frontend/src/services/api.js`)
   - Updated `importFromKaggle()` to send scoring config

2. **Event Detail Page** (`frontend/src/pages/EventDetail.jsx`)
   - Added scoring configuration modal
   - Form with all scoring parameters
   - Live formula preview
   - Updates import flow to use scoring config

3. **Competition List Page** (`frontend/src/pages/CompetitionList.jsx`)
   - Same scoring configuration modal
   - Consistent import experience

4. **Styling** (`EventDetail.css`, `CompetitionList.css`)
   - Form styles with responsive design
   - Formula preview styling

## Validation & Error Handling

### Backend Validation
- `metric_max_value` must be greater than `metric_min_value`
- `points_for_perfect_score` must be positive
- All values must be valid floats
- Returns 400 error with clear message on validation failure

### Frontend Validation
- Number inputs with step controls
- Real-time formula preview
- Clear help text for each field
- Default values pre-filled

## Future Enhancements

Potential improvements:
- [ ] Allow editing scoring config after import
- [ ] Historical score tracking (raw vs normalized)
- [ ] Bulk score recalculation if config changes
- [ ] Score distribution visualization
- [ ] Preset configurations for common metric types
- [ ] Score normalization history/audit log

## Migration Guide

### Existing Competitions
For competitions imported before this feature:
- Default values are applied: `higher_is_better=True`, `min=0.0`, `max=1.0`, `points=100.0`
- Edit in Django admin to update scoring config
- Re-sync leaderboard to apply new scoring

### Testing Checklist
- [x] Backend validation works correctly
- [x] Frontend form displays and submits properly
- [x] Normalized scores calculated correctly
- [x] Leaderboard displays normalized scores
- [ ] Test with real Kaggle competition data
- [ ] Verify score updates on re-sync
- [ ] Test edge cases (min=max, negative values, etc.)

## Support

For issues or questions about the scoring system:
1. Check this documentation
2. Review example configurations above
3. Test with sample data first
4. Contact system administrator

---

**Last Updated:** November 1, 2025  
**Version:** 1.0  
**Status:** ✅ Production Ready
