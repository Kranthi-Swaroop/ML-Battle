# Admin-Only Event System Implementation - Complete

## Summary of Changes

This document outlines the complete restructuring of the MLBattle platform to an **event-based system** where:
- ✅ Only **ADMIN** can create events and import Kaggle competitions
- ✅ **Normal users** can VIEW events, VIEW competitions, and PARTICIPATE
- ✅ **Competitions page removed** - everything is event-based now
- ✅ Home page shows **Featured Events** instead of competitions

---

## 1. Backend Changes

### A. Permissions & Authorization

#### `backend/apps/users/serializers.py`
**Added admin flags to UserSerializer:**
```python
fields = [
    'id', 'username', 'email', 'elo_rating', 'highest_rating',
    'competitions_participated', 'kaggle_username', 'bio',
    'avatar_url', 'rating_tier', 'is_staff', 'is_superuser',  # ← ADDED
    'created_at', 'updated_at'
]
```
- Frontend can now check if user is admin via `user.is_staff` or `user.is_superuser`

#### `backend/apps/competitions/views.py`
**Updated CompetitionEventViewSet permissions:**
```python
def get_permissions(self):
    # Only admins can create, update, or delete events
    # Normal users can only view events
    if self.action in ['create', 'update', 'partial_update', 'destroy']:
        return [IsAdminUser()]
    return super().get_permissions()
```

**Updated import_from_kaggle action:**
```python
@action(detail=False, methods=['post'], permission_classes=[IsAdminUser])  # ← ADDED
def import_from_kaggle(self, request):
```

**Result:**
- ✅ Only admin users can create/edit/delete events
- ✅ Only admin users can import Kaggle competitions
- ✅ All users can view events and competitions
- ✅ Backend enforces permissions with 403 Forbidden for unauthorized actions

---

## 2. Frontend Changes

### A. Authentication Enhancement

#### `frontend/src/hooks/useAuth.js`
**Added isAdmin helper function:**
```javascript
const isAdmin = () => {
  return user && (user.is_staff || user.is_superuser);
};

const value = {
  user,
  isAuthenticated,
  loading,
  login,
  register,
  logout,
  updateUser,
  isAdmin,  // ← ADDED
};
```

**Usage:**
```javascript
const { isAdmin } = useAuth();

{isAdmin() && (
  <button>Admin Only Feature</button>
)}
```

---

### B. Events Page (Admin Controls Hidden)

#### `frontend/src/pages/EventsPage.jsx`
**Changes:**
1. Imported `useAuth` hook
2. Wrapped "Create Event" button with `isAdmin()` check

**Before:**
```javascript
<button 
  className="btn btn-primary"
  onClick={() => setShowCreateModal(true)}
>
  + Create Event
</button>
```

**After:**
```javascript
{isAdmin() && (
  <button 
    className="btn btn-primary"
    onClick={() => setShowCreateModal(true)}
  >
    + Create Event
  </button>
)}
```

**Result:**
- ✅ Normal users see events grid but no create button
- ✅ Admin users see events grid AND create button

---

### C. Event Detail Page (Import Hidden)

#### `frontend/src/pages/EventDetail.jsx`
**Changes:**
1. Imported `useAuth` hook
2. Wrapped "Import Kaggle Competition" buttons with `isAdmin()` check
3. Updated empty state message for non-admins

**Header import button:**
```javascript
{isAdmin() && (
  <button 
    className="btn btn-primary"
    onClick={() => setShowKaggleSearch(true)}
  >
    + Import Kaggle Competition
  </button>
)}
```

**Empty state:**
```javascript
<p>{isAdmin() ? 'Import Kaggle competitions to add them to this event' : 'Check back later for competitions'}</p>
{isAdmin() && (
  <button 
    className="btn btn-primary"
    onClick={() => setShowKaggleSearch(true)}
  >
    Import First Competition
  </button>
)}
```

**Result:**
- ✅ Normal users see event details and competitions list
- ✅ Admin users see event details, competitions list, AND import button
- ✅ Empty state shows different message based on user role

---

### D. Navigation Restructuring

#### `frontend/src/components/Navbar.jsx`
**Removed "Competitions" link:**

**Before:**
```javascript
<Link to="/competitions">Competitions</Link>
```

**After:**
- ✅ Link removed completely
- ✅ Only "Home" and "Events" links remain

---

### E. Routing Changes

#### `frontend/src/App.jsx`
**Removed standalone competitions list route:**

**Before:**
```javascript
<Route path="/competitions" element={<CompetitionList />} />
<Route path="/competitions/:id" element={<CompetitionDetail />} />
```

**After:**
```javascript
// Removed: /competitions list route
<Route path="/competitions/:id" element={<CompetitionDetail />} />  // ← KEPT for viewing individual competitions
```

**Result:**
- ✅ `/competitions` route removed (no standalone list)
- ✅ `/competitions/:id` kept (individual competition details still accessible)
- ✅ Main navigation flows through `/events` → `/events/:slug` → competitions within event

---

### F. Home Page Redesign

#### `frontend/src/pages/Home.jsx`
**Replaced competitions with events:**

**Before:**
- Fetched ongoing competitions
- Showed competition cards
- Linked to `/competitions`

**After:**
```javascript
// Changed imports
import { competitionEventsAPI } from '../services/api';

// Changed state
const [featuredEvents, setFeaturedEvents] = useState([]);

// Changed fetch function
const fetchFeaturedEvents = async () => {
  const response = await competitionEventsAPI.getFeatured();
  setFeaturedEvents(response.data.results || response.data);
};

// Changed section title
<h2 className="section-title">Featured Events</h2>
<Link to="/events" className="view-all-link">View All →</Link>

// Changed cards to show events
{featuredEvents.slice(0, 3).map((event) => (
  <Link to={`/events/${event.slug}`}>
    <div className="event-card-home">
      <div className="event-card-banner">
        <img src={event.banner_image} alt={event.title} />
      </div>
      <div className="event-card-content">
        <h3>{event.title}</h3>
        <p>{event.description}</p>
        <div className="event-card-meta">
          <span>🏆 {event.total_prize_pool}</span>
          <span>📊 {event.competition_count} competitions</span>
        </div>
        <span className={`event-status-badge status-${event.status}`}>
          {event.status}
        </span>
      </div>
    </div>
  </Link>
))}
```

**Changed hero buttons:**
```javascript
// "Browse Competitions" → "Browse Events"
<Link to="/events">Browse Events</Link>

// "View Competitions" → "View Events"
<Link to="/events">View Events</Link>
```

#### `frontend/src/pages/Home.css`
**Added event card styles:**
```css
.event-card-link { /* hover effects */ }
.event-card-home { /* card container */ }
.event-card-banner { /* banner image */ }
.event-card-content { /* content area */ }
.event-card-desc { /* description */ }
.event-card-meta { /* prize, competition count */ }
.event-status-badge { /* status badge */ }
.status-upcoming, .status-active, .status-ended { /* status colors */ }
```

**Result:**
- ✅ Home page shows up to 3 featured events
- ✅ Events displayed with banner, title, description, prize, competition count
- ✅ "View All" links to `/events` page
- ✅ Hero buttons link to `/events` instead of `/competitions`

---

## 3. User Flow Comparison

### OLD FLOW (Competition-Centric):
```
Home → Competitions List → Competition Detail
                ↓
            Participate
```

### NEW FLOW (Event-Centric):
```
Home → Events List → Event Detail → Competition Detail
                                          ↓
                                     Participate

Admin Flow:
Home → Events List → [Create Event] → Event Detail → [Import Kaggle Competition] → Search → Import
```

---

## 4. Access Control Matrix

| Action | Admin | Normal User |
|--------|-------|-------------|
| View Events List | ✅ Yes | ✅ Yes |
| View Event Detail | ✅ Yes | ✅ Yes |
| Create Event | ✅ Yes | ❌ No (403 Forbidden) |
| Edit Event | ✅ Yes | ❌ No (403 Forbidden) |
| Delete Event | ✅ Yes | ❌ No (403 Forbidden) |
| View Competitions in Event | ✅ Yes | ✅ Yes |
| Import Kaggle Competition | ✅ Yes | ❌ No (403 Forbidden) |
| View Competition Detail | ✅ Yes | ✅ Yes |
| Participate in Competition | ✅ Yes | ✅ Yes |
| Submit to Competition | ✅ Yes | ✅ Yes |

---

## 5. UI Visibility Matrix

| UI Element | Admin | Normal User |
|------------|-------|-------------|
| "Create Event" button (Events page) | ✅ Visible | ❌ Hidden |
| "Import Kaggle Competition" button (Event Detail) | ✅ Visible | ❌ Hidden |
| Events grid | ✅ Visible | ✅ Visible |
| Event detail page | ✅ Visible | ✅ Visible |
| Competitions list in event | ✅ Visible | ✅ Visible |
| Kaggle search modal | ✅ Visible | ❌ Hidden |
| "Competitions" nav link | ❌ Removed | ❌ Removed |
| "Events" nav link | ✅ Visible | ✅ Visible |

---

## 6. Testing Checklist

### Backend Testing:
- [ ] Login as non-admin user
- [ ] Try POST /api/competitions/events/ → Should return 403
- [ ] Try POST /api/competitions/import_from_kaggle/ → Should return 403
- [ ] Try GET /api/competitions/events/ → Should return 200
- [ ] Login as admin user
- [ ] Try POST /api/competitions/events/ → Should return 201
- [ ] Try POST /api/competitions/import_from_kaggle/ → Should return 200

### Frontend Testing:
- [ ] Login as normal user (e.g., "samridha")
- [ ] Visit /events → Should see events, NO create button
- [ ] Visit /events/:slug → Should see event detail, NO import button
- [ ] Verify "Competitions" link NOT in navbar
- [ ] Verify Home page shows Featured Events
- [ ] Login as admin (username: "admin", password: "admin123")
- [ ] Visit /events → Should see "Create Event" button
- [ ] Click "Create Event" → Modal opens, can create event
- [ ] Visit /events/:slug → Should see "Import Kaggle Competition" button
- [ ] Click import → Modal opens, can search and import

---

## 7. Files Modified

### Backend Files:
1. `backend/apps/users/serializers.py` - Added is_staff, is_superuser fields
2. `backend/apps/competitions/views.py` - Added IsAdminUser permissions

### Frontend Files:
1. `frontend/src/hooks/useAuth.js` - Added isAdmin() helper
2. `frontend/src/pages/EventsPage.jsx` - Hidden create button for non-admins
3. `frontend/src/pages/EventDetail.jsx` - Hidden import button for non-admins
4. `frontend/src/components/Navbar.jsx` - Removed "Competitions" link
5. `frontend/src/App.jsx` - Removed /competitions route
6. `frontend/src/pages/Home.jsx` - Changed to show featured events
7. `frontend/src/pages/Home.css` - Added event card styles

---

## 8. Admin Account

**Admin credentials for testing:**
- Username: `admin`
- Password: `admin123`

**To create additional admin users:**
```bash
cd backend
venv\Scripts\python.exe manage.py createsuperuser
```

---

## 9. API Endpoints

### Public (All Users):
- `GET /api/competitions/events/` - List all events
- `GET /api/competitions/events/:slug/` - Event detail
- `GET /api/competitions/events/featured/` - Featured events
- `GET /api/competitions/events/:slug/competitions/` - Competitions in event
- `GET /api/competitions/:id/` - Competition detail

### Admin Only:
- `POST /api/competitions/events/` - Create event
- `PUT /api/competitions/events/:slug/` - Update event
- `DELETE /api/competitions/events/:slug/` - Delete event
- `POST /api/competitions/import_from_kaggle/` - Import competition

---

## 10. Key Design Decisions

1. **Why keep `/competitions/:id` route?**
   - Users need to view individual competition details and submit
   - Competition cards in event detail page link here
   - Maintains existing competition detail functionality

2. **Why use `is_staff` OR `is_superuser`?**
   - `is_superuser` = Full admin (created via createsuperuser)
   - `is_staff` = Can be regular user promoted to event manager
   - Flexibility for future: distinguish between super admins and event organizers

3. **Why hide UI elements instead of just disabling?**
   - Better UX - users don't see features they can't use
   - Cleaner interface for normal users
   - Backend still enforces permissions (defense in depth)

4. **Why remove CompetitionList page entirely?**
   - Aligns with your requirement: "structure is like a event, and in that event competitions are there"
   - Prevents confusion - single source of truth (events)
   - Admin workflow: Create event → Import competitions
   - User workflow: Browse events → See competitions

---

## ✅ Implementation Complete

**Status: FULLY IMPLEMENTED AND READY FOR TESTING**

All requirements met:
- ✅ Admin-only event creation
- ✅ Admin-only Kaggle import
- ✅ Normal users can view and participate
- ✅ Competitions page removed
- ✅ Event-based structure enforced
- ✅ Backend permissions secured
- ✅ Frontend UI conditionally rendered
- ✅ Home page shows featured events

**Next Steps:**
1. Restart backend server (changes auto-reload with Daphne)
2. Refresh frontend
3. Test with admin account
4. Test with normal user account
5. Create your first event (e.g., "Neural Night")
6. Import Kaggle competitions into the event
