# Scoring System Test Plan

## Test Checklist

### ✅ Backend Tests

#### 1. API Endpoint Tests
- [ ] POST `/api/competitions/import_from_kaggle/` with scoring config
  - [ ] Returns 200 with valid data
  - [ ] Competition created with correct scoring fields
  - [ ] Defaults applied when parameters omitted

#### 2. Validation Tests
- [ ] Error when `metric_max_value <= metric_min_value`
- [ ] Error when `points_for_perfect_score <= 0`
- [ ] Error when parameters are non-numeric
- [ ] Success with valid parameters

#### 3. Score Calculation Tests
- [ ] Higher is better formula works correctly
- [ ] Lower is better formula works correctly
- [ ] Scores clamped between 0 and max points
- [ ] Edge cases (min score, max score, mid score)

### ✅ Frontend Tests

#### 1. UI Component Tests
- [ ] Scoring modal appears on import click
- [ ] All form fields render correctly
- [ ] Checkbox toggles higher/lower metric
- [ ] Number inputs accept valid values
- [ ] Formula preview updates in real-time
- [ ] Cancel button closes modal
- [ ] Import button submits with loading state

#### 2. Form Validation
- [ ] Can't submit with invalid numbers
- [ ] Proper error messages displayed
- [ ] Success message after import
- [ ] Modal closes on success

#### 3. Integration Tests
- [ ] Import flow from EventDetail page
- [ ] Import flow from CompetitionList page
- [ ] Scoring config sent to API correctly
- [ ] Competition appears in list after import

### ✅ End-to-End Tests

#### Test Case 1: Accuracy-based Competition (Higher is Better)
```
Configuration:
- Competition: Titanic (or similar)
- higher_is_better: true
- metric_min_value: 0.0
- metric_max_value: 1.0
- points_for_perfect_score: 100.0

Steps:
1. Search for "titanic" competition
2. Click Import
3. Set configuration as above
4. Click Import Competition
5. Navigate to competition detail page
6. Click Sync Leaderboard
7. Verify leaderboard loads

Expected Results:
- Top score (e.g., 0.95) → ~95 points
- Mid score (e.g., 0.75) → ~75 points
- Low score (e.g., 0.50) → ~50 points
- Scores are between 0 and 100
- Rankings match Kaggle rankings
```

#### Test Case 2: Error-based Competition (Lower is Better)
```
Configuration:
- Competition: House Prices (or similar)
- higher_is_better: false
- metric_min_value: 0.0
- metric_max_value: 1.0 (or estimated max RMSE)
- points_for_perfect_score: 100.0

Steps:
1. Search for "house-prices" competition
2. Click Import
3. Set configuration as above
4. Click Import Competition
5. Navigate to competition detail page
6. Click Sync Leaderboard
7. Verify leaderboard loads

Expected Results:
- Best score (lowest error, e.g., 0.10) → ~90 points
- Mid score (e.g., 0.50) → ~50 points
- Worst score (e.g., 1.00) → ~0 points
- Scores are inverted (lower Kaggle score = higher points)
- Rankings correct
```

#### Test Case 3: Custom Point Scale
```
Configuration:
- Any competition
- higher_is_better: true
- metric_min_value: 0.0
- metric_max_value: 100.0
- points_for_perfect_score: 500.0

Steps:
1. Import competition with config
2. Sync leaderboard
3. Verify scores

Expected Results:
- Perfect score (100) → 500 points
- Half score (50) → 250 points
- Zero score (0) → 0 points
- Scores scale proportionally
```

### ✅ Database Tests

#### 1. Migration
- [x] Migration `0003_competition_higher_is_better_and_more` applied
- [ ] All fields created with correct types
- [ ] Default values applied to existing competitions
- [ ] No data loss

#### 2. Model Tests
- [ ] Competition model saves scoring config
- [ ] Fields serialized correctly in API
- [ ] Query performance not degraded

### ✅ Score Calculation Verification

#### Manual Test Cases

**Higher is Better (min=0, max=1, points=100):**
| Raw Score | Expected Points | Formula |
|-----------|----------------|---------|
| 1.0       | 100.0          | (1.0-0)/(1-0)×100 = 100 |
| 0.95      | 95.0           | (0.95-0)/(1-0)×100 = 95 |
| 0.75      | 75.0           | (0.75-0)/(1-0)×100 = 75 |
| 0.50      | 50.0           | (0.50-0)/(1-0)×100 = 50 |
| 0.0       | 0.0            | (0-0)/(1-0)×100 = 0 |
| -0.1      | 0.0 (clamped)  | Negative → clamped to 0 |
| 1.1       | 100.0 (clamped)| Over max → clamped to 100 |

**Lower is Better (min=0, max=10, points=100):**
| Raw Score | Expected Points | Formula |
|-----------|----------------|---------|
| 0.0       | 100.0          | (10-0)/(10-0)×100 = 100 |
| 1.0       | 90.0           | (10-1)/(10-0)×100 = 90 |
| 5.0       | 50.0           | (10-5)/(10-0)×100 = 50 |
| 9.0       | 10.0           | (10-9)/(10-0)×100 = 10 |
| 10.0      | 0.0            | (10-10)/(10-0)×100 = 0 |
| 11.0      | 0.0 (clamped)  | Over max → clamped to 0 |

### ✅ Edge Cases

#### 1. Boundary Conditions
- [ ] Min value equals max value (should error)
- [ ] Zero points for perfect score (should error)
- [ ] Negative points (should error)
- [ ] Very large numbers (1e10)
- [ ] Very small numbers (1e-10)
- [ ] Exact min/max values

#### 2. Data Type Tests
- [ ] String inputs for numbers (should error)
- [ ] Null/undefined values (should use defaults)
- [ ] Float vs integer inputs
- [ ] Scientific notation

#### 3. Concurrent Operations
- [ ] Multiple imports at same time
- [ ] Import during sync
- [ ] Re-sync same competition

### ✅ User Experience Tests

#### 1. Admin Workflow
- [ ] Clear instructions in form
- [ ] Help text is helpful
- [ ] Formula preview is accurate
- [ ] Success/error messages clear
- [ ] Can cancel without side effects

#### 2. Performance
- [ ] Form loads quickly
- [ ] Import completes in <5 seconds
- [ ] Sync with scoring calc <30 seconds
- [ ] No browser freezing

#### 3. Responsive Design
- [ ] Form works on mobile
- [ ] All fields accessible
- [ ] Buttons tap-friendly
- [ ] Formula preview readable

## Test Data

### Sample Competitions for Testing

1. **Titanic** (accuracy, 0-1 scale, higher better)
2. **House Prices** (RMSE, error metric, lower better)
3. **Digit Recognizer** (accuracy, 0-1, higher better)
4. **Any completed competition** (to test with historical data)

## Automated Test Script

```bash
# Run backend tests
cd backend
python manage.py test apps.competitions.tests

# Check for errors
python manage.py check

# Validate migrations
python manage.py makemigrations --check

# Run frontend tests (if added)
cd ../frontend
npm test
```

## Manual Testing Procedure

### Phase 1: Basic Functionality (15 mins)
1. Start backend server
2. Start frontend server
3. Login as admin
4. Navigate to Events page
5. Search for a Kaggle competition
6. Click Import on one result
7. Verify scoring form appears
8. Fill in scoring parameters
9. Click Import Competition
10. Verify success message
11. Navigate to competition detail
12. Click Sync Leaderboard
13. Verify scores appear

### Phase 2: Score Verification (10 mins)
1. Pick 3-5 entries from leaderboard
2. Note their raw scores from Kaggle
3. Calculate expected normalized scores manually
4. Compare with displayed scores
5. Verify they match (±0.01 tolerance)

### Phase 3: Edge Cases (10 mins)
1. Try importing with invalid config (max < min)
2. Verify error message
3. Import with extreme values (1000000)
4. Verify no crashes
5. Toggle higher/lower checkbox
6. Verify formula preview updates

### Phase 4: Integration (10 mins)
1. Import multiple competitions
2. Verify each has correct config
3. Sync all leaderboards
4. Check database has correct scores
5. Test from CompetitionList page
6. Test from EventDetail page

## Success Criteria

✅ All test cases pass
✅ No console errors
✅ No server errors
✅ Scores calculated correctly
✅ UI is responsive and clear
✅ Import workflow is smooth
✅ Documentation is accurate

## Known Issues / Limitations

1. Cannot edit scoring config after import (need to use Django admin)
2. No bulk score recalculation if config changes
3. No historical tracking of score changes
4. Formula limited to linear normalization

## Future Test Cases

- [ ] Score history tracking
- [ ] Config edit feature
- [ ] Bulk recalculation
- [ ] Multiple scoring formulas
- [ ] Weighted scoring across competitions
- [ ] Export scores to CSV

---

**Testing Status:** Ready for testing
**Last Updated:** November 1, 2025
**Tester:** [Your Name]
**Results:** [To be filled]
