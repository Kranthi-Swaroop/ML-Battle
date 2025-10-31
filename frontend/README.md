# MLBattle Frontend

Frontend application for MLBattle - A Machine Learning Competition Platform with Kaggle Integration.

## Technology Stack

- **React 18.2** - UI library
- **React Router v6** - Client-side routing
- **Axios** - HTTP client
- **Chart.js + react-chartjs-2** - Data visualization
- **CSS3** - Styling

## Prerequisites

- Node.js 16 or higher
- npm or yarn
- Backend server running (see backend/README.md)

## Setup Instructions

### 1. Install Dependencies

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### 2. Configure Environment Variables

Create a `.env` file in the frontend directory:

```powershell
# Copy the example environment file
cp .env.example .env
```

The `.env` file should contain:

```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/ws
```

### 3. Start Development Server

```powershell
npm start
```

The application will open at `http://localhost:3000`

### 4. Build for Production

```powershell
npm run build
```

The optimized production build will be in the `build/` directory.

## Project Structure

```
frontend/
├── public/
│   ├── index.html              # HTML template
│   ├── favicon.ico
│   └── manifest.json
├── src/
│   ├── components/             # Reusable components
│   │   ├── Navbar.jsx
│   │   ├── Navbar.css
│   │   ├── Footer.jsx
│   │   ├── Footer.css
│   │   ├── CompetitionCard.jsx
│   │   ├── CompetitionCard.css
│   │   ├── Leaderboard.jsx
│   │   ├── Leaderboard.css
│   │   ├── RatingChart.jsx
│   │   ├── RatingChart.css
│   │   ├── SubmissionHistory.jsx
│   │   └── SubmissionHistory.css
│   ├── pages/                  # Page components
│   │   ├── Home.jsx
│   │   ├── Home.css
│   │   ├── CompetitionList.jsx
│   │   ├── CompetitionList.css
│   │   ├── CompetitionDetail.jsx
│   │   ├── CompetitionDetail.css
│   │   ├── Profile.jsx
│   │   ├── Profile.css
│   │   ├── Login.jsx
│   │   ├── Login.css
│   │   ├── Register.jsx
│   │   └── Register.css
│   ├── services/               # API and services
│   │   ├── api.js              # ✅ Axios HTTP client
│   │   ├── websocket.js        # ✅ WebSocket manager
│   │   └── auth.js             # ✅ Auth utilities
│   ├── hooks/                  # Custom React hooks
│   │   ├── useWebSocket.js     # ✅ WebSocket hook
│   │   ├── useAuth.js          # ✅ Auth hook
│   │   └── useLeaderboard.js   # ✅ Leaderboard hook
│   ├── utils/                  # Utility functions
│   │   ├── constants.js        # ✅ App constants
│   │   └── helpers.js          # ✅ Helper functions
│   ├── App.jsx                 # Main App component
│   ├── App.css
│   ├── index.js                # Entry point
│   └── index.css
├── package.json
├── .env                        # Environment variables
├── .env.example               # Example environment file
├── .gitignore
└── README.md
```

## Components to Create

The services, hooks, and utilities are already created (✅). You need to create the following components and pages:

### Components (src/components/)

1. **Navbar.jsx** - Navigation bar with links and user menu
2. **Footer.jsx** - Footer with links and copyright
3. **CompetitionCard.jsx** - Competition preview card
4. **Leaderboard.jsx** - Live leaderboard table with WebSocket
5. **RatingChart.jsx** - User rating graph over time
6. **SubmissionHistory.jsx** - User's past submissions

### Pages (src/pages/)

1. **Home.jsx** - Landing page with featured competitions
2. **CompetitionList.jsx** - All competitions with filters
3. **CompetitionDetail.jsx** - Single competition view + leaderboard
4. **Profile.jsx** - User profile and statistics
5. **Login.jsx** - Authentication page
6. **Register.jsx** - User registration

### Main App Files

1. **App.jsx** - Main component with routing
2. **index.js** - Entry point with AuthProvider

## Example Component Structure

### App.jsx

```jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import CompetitionList from './pages/CompetitionList';
import CompetitionDetail from './pages/CompetitionDetail';
import Profile from './pages/Profile';
import Login from './pages/Login';
import Register from './pages/Register';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Navbar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/competitions" element={<CompetitionList />} />
              <Route path="/competitions/:id" element={<CompetitionDetail />} />
              <Route path="/profile/:id" element={<Profile />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
```

### Example Leaderboard Component

```jsx
import React from 'react';
import useLeaderboard from '../hooks/useLeaderboard';
import './Leaderboard.css';

const Leaderboard = ({ competitionId }) => {
  const { leaderboard, loading, isConnected } = useLeaderboard(competitionId);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="leaderboard">
      <div className="leaderboard-header">
        <h2>Leaderboard</h2>
        {isConnected && <span className="live-indicator">● LIVE</span>}
      </div>
      <table className="leaderboard-table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Username</th>
            <th>Rating</th>
            <th>Score</th>
            <th>Submissions</th>
          </tr>
        </thead>
        <tbody>
          {leaderboard.map((entry) => (
            <tr key={entry.id}>
              <td>{entry.rank}</td>
              <td>{entry.username}</td>
              <td>{entry.elo_rating}</td>
              <td>{entry.best_score}</td>
              <td>{entry.submissions_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Leaderboard;
```

## Available Services

### API Service (services/api.js)

```javascript
import { authAPI, usersAPI, competitionsAPI, submissionsAPI, leaderboardAPI, ratingsAPI } from './services/api';

// Example usage:
const competitions = await competitionsAPI.getAll();
const user = await usersAPI.getById(userId);
const leaderboard = await leaderboardAPI.getByCompetition(compId);
```

### WebSocket Service (services/websocket.js)

```javascript
import wsManager from './services/websocket';

// Connect to WebSocket
wsManager.connect('leaderboard/1', {
  onMessage: (data) => console.log(data),
  onOpen: () => console.log('Connected'),
});
```

### Custom Hooks

```javascript
import useAuth from './hooks/useAuth';
import useWebSocket from './hooks/useWebSocket';
import useLeaderboard from './hooks/useLeaderboard';

// In component:
const { user, login, logout } = useAuth();
const { leaderboard, isConnected } = useLeaderboard(competitionId);
```

## Features to Implement

1. **Authentication** - Login, register, logout with JWT
2. **Competition Listing** - Browse and filter competitions
3. **Competition Details** - View competition info and leaderboard
4. **Live Leaderboard** - Real-time updates via WebSocket
5. **User Profile** - View stats, rating history, submissions
6. **Rating Graph** - Visualize rating changes with Chart.js
7. **Responsive Design** - Mobile-friendly layout

## Testing

```powershell
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage
```

## Deployment

### Build for Production

```powershell
npm run build
```

### Serve Static Build

```powershell
# Install serve globally
npm install -g serve

# Serve the build
serve -s build -l 3000
```

## Common Issues

### Issue: API calls fail with CORS error
**Solution:** Ensure backend CORS settings include `http://localhost:3000`

### Issue: WebSocket connection fails
**Solution:** Check that Django Channels is running and WebSocket URL is correct

### Issue: Authentication redirects not working
**Solution:** Verify JWT tokens are being stored and sent correctly

## Next Steps

1. Create remaining components and pages
2. Implement styling for all components
3. Add loading states and error handling
4. Implement form validation
5. Add responsive design
6. Test WebSocket connections
7. Add Chart.js for rating graphs
8. Implement competition filters
9. Add pagination for lists
10. Deploy frontend application

## License

MIT License
