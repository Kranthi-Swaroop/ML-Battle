# 🔍 Event Competitions Display - Debugging Guide

## ✅ Backend Status: WORKING CORRECTLY

The test confirms that:
- ✅ Competitions are properly linked to events in database
- ✅ `event.competitions.all()` returns correct results
- ✅ Serializers include event competitions
- ✅ API endpoint `/api/competitions/events/{slug}/competitions/` works

## 🎯 Issue Identified

The backend is **working perfectly**. The issue is likely:
1. Frontend not refreshing after import
2. Browser cache
3. API call timing
4. Frontend state management

## 🔧 Frontend Debugging Steps

### Step 1: Check Network Tab
1. Open browser DevTools (F12)
2. Go to Network tab
3. Navigate to an event detail page
4. Look for API calls:
   - `GET /api/competitions/events/{slug}/`
   - `GET /api/competitions/events/{slug}/competitions/`

**Check**:
- Do both calls happen?
- What's the response for `/competitions/`?
- Does it include the competitions array?

### Step 2: Check Console
1. Open browser Console tab
2. Look for errors related to:
   - API calls
   - State updates
   - Rendering

### Step 3: Test Backend Directly

```bash
# Test 1: Get event details
curl http://localhost:8000/api/competitions/events/test-event-slug/

# Should show: "competition_count": 3 (or whatever number)

# Test 2: Get event competitions
curl http://localhost:8000/api/competitions/events/test-event-slug/competitions/

# Should return array of competitions
```

### Step 4: Check EventDetail.jsx

The component fetches competitions like this:

```javascript
const [eventRes, competitionsRes] = await Promise.all([
  competitionEventsAPI.getById(slug),
  competitionEventsAPI.getCompetitions(slug)  // This call
]);
setEvent(eventRes.data);
setCompetitions(competitionsRes.data);  // This should set competitions
```

**Possible Issues**:
1. `competitionsRes.data` might be wrapped (e.g., `{results: []}`)
2. State not updating
3. Re-render not triggering

## 🛠️ Fixes to Try

### Fix 1: Force Refresh After Import

In `EventDetail.jsx`, the `importCompetition` function calls `fetchEventDetails()` after import. This should work, but try adding a small delay:

```javascript
const importCompetition = async (kaggleId) => {
  setImportingIds(prev => new Set(prev).add(kaggleId));
  try {
    await competitionsAPI.importFromKaggle(kaggleId, event.id);
    alert('Competition imported successfully to this event!');
    
    // Add delay before refresh
    setTimeout(() => {
      fetchEventDetails();
    }, 500);
    
    // ... rest of code
  }
};
```

### Fix 2: Check API Response Structure

Add logging in `EventDetail.jsx`:

```javascript
const fetchEventDetails = async () => {
  try {
    setLoading(true);
    const [eventRes, competitionsRes] = await Promise.all([
      competitionEventsAPI.getById(slug),
      competitionEventsAPI.getCompetitions(slug)
    ]);
    
    console.log('Event Response:', eventRes.data);
    console.log('Competitions Response:', competitionsRes.data);
    console.log('Competitions Count:', competitionsRes.data?.length);
    
    setEvent(eventRes.data);
    setCompetitions(competitionsRes.data);
    // ...
  }
};
```

### Fix 3: Clear Browser Cache

Sometimes the issue is cached API responses:
1. Open DevTools (F12)
2. Right-click refresh button
3. Select "Empty Cache and Hard Reload"

### Fix 4: Check if competitions is an object vs array

The API might return:
```json
{
  "results": [competitions],
  "count": 3
}
```

Instead of just:
```json
[competitions]
```

Update `EventDetail.jsx`:

```javascript
const [eventRes, competitionsRes] = await Promise.all([
  competitionEventsAPI.getById(slug),
  competitionEventsAPI.getCompetitions(slug)
]);

setEvent(eventRes.data);

// Handle both array and object responses
const comps = competitionsRes.data.results || competitionsRes.data;
setCompetitions(Array.isArray(comps) ? comps : []);
```

## 🧪 Quick Backend Test

Run this to verify your actual event has competitions:

```bash
cd backend
python manage.py shell
```

```python
from apps.competitions.models import CompetitionEvent, Competition

# Find your event
event = CompetitionEvent.objects.get(slug='your-event-slug')

# Check competitions
print(f"Event: {event.title}")
print(f"Competition count: {event.competitions.count()}")
print("\nCompetitions:")
for comp in event.competitions.all():
    print(f"  - {comp.title} (ID: {comp.id})")
```

## 🎯 Most Likely Issue

Based on the test results, the most likely issues are:

1. **Frontend not refreshing properly after import**
   - Solution: Add delay before fetchEventDetails()
   - Or: Force component re-mount

2. **API response structure mismatch**
   - Check if response is `{results: []}` vs `[]`
   - Update code to handle both

3. **Browser cache**
   - Hard refresh (Ctrl+Shift+R)
   - Clear cache

## 📝 Next Steps

1. Open the event detail page in browser
2. Open DevTools (F12)
3. Go to Network tab
4. Look at the `/competitions/` API call
5. Check the response - does it include competitions?
6. If YES → Frontend state issue
7. If NO → Backend filtering issue

## ✅ Confirmed Working

From our test:
- ✅ Backend properly stores event-competition relationship
- ✅ Serializers include competitions
- ✅ API endpoints return correct data
- ✅ Database queries work perfectly

The issue is definitely in the **frontend display or state management**, not the backend!

---

**Need More Help?**

Share:
1. Network tab screenshot of `/competitions/` API call response
2. Console errors
3. Event slug you're testing with
