# 🗄️ MongoDB Setup Guide for MLBattle (Windows)

## Step 1: Install MongoDB

### Option A: Download Installer (Recommended)

1. **Download MongoDB Community Server:**
   - Visit: https://www.mongodb.com/try/download/community
   - Select: **Windows x64**
   - Version: **6.0 or later**
   - Package: **MSI**

2. **Run the Installer:**
   - Double-click the downloaded `.msi` file
   - Choose **Complete** installation
   - ✅ Check "Install MongoDB as a Service"
   - ✅ Check "Run service as Network Service user"
   - Click **Install**

### Option B: Using Chocolatey

```powershell
choco install mongodb
```

### Option C: Using Winget

```powershell
winget install MongoDB.Server
```

---

## Step 2: Verify MongoDB Installation

```powershell
# Check if MongoDB service is running
Get-Service MongoDB

# Should show:
# Status   Name               DisplayName
# ------   ----               -----------
# Running  MongoDB            MongoDB Server
```

If not running, start it:
```powershell
net start MongoDB
```

---

## Step 3: Test MongoDB Connection

```powershell
# Open MongoDB shell
mongosh

# You should see:
# Current Mongosh Log ID: ...
# Connecting to: mongodb://127.0.0.1:27017/...
# Using MongoDB: 6.x.x
# test>

# Type 'exit' to quit
exit
```

✅ If you see the prompt, MongoDB is working!

---

## Step 4: Configure Backend

### Update .env file

```powershell
cd d:\MLBattle\backend
notepad .env
```

Make sure your `.env` has these MongoDB settings:

```env
# Database - MongoDB
DB_NAME=mlbattle
MONGO_HOST=localhost
MONGO_PORT=27017
# MONGO_USER=     # Leave empty for development
# MONGO_PASSWORD= # Leave empty for development
```

**Note:** For local development, MongoDB doesn't require authentication by default.

---

## Step 5: Install Python Dependencies

```powershell
cd d:\MLBattle\backend

# Activate virtual environment
.\venv\Scripts\activate

# Install/Update dependencies (includes djongo and pymongo)
pip install -r requirements.txt
```

Expected output:
```
Installing collected packages: djongo, pymongo, sqlparse...
Successfully installed djongo-1.3.6 pymongo-3.12.3 sqlparse-0.2.4
```

---

## Step 6: Run Django Migrations

```powershell
# Still in backend directory with venv activated
python manage.py migrate
```

Expected output:
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0001_initial... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  ...
  Applying users.0001_initial... OK
  Applying competitions.0001_initial... OK
  Applying submissions.0001_initial... OK
  Applying leaderboard.0001_initial... OK
  Applying ratings.0001_initial... OK
```

✅ All migrations should complete successfully!

---

## Step 7: Create Superuser

```powershell
python manage.py createsuperuser
```

Enter:
- Username: (your choice, e.g., `admin`)
- Email: (your email)
- Password: (strong password)
- Password (again): (repeat password)

✅ Superuser created successfully!

---

## Step 8: Verify Database

### Check in MongoDB Shell

```powershell
mongosh
```

In MongoDB shell:
```javascript
// Switch to mlbattle database
use mlbattle

// List all collections
show collections

// You should see:
// auth_group
// auth_permission
// competitions_competition
// django_content_type
// django_migrations
// django_session
// leaderboard_leaderboardentry
// ratings_ratinghistory
// submissions_submission
// users_user

// Count users
db.users_user.countDocuments()
// Should return: 1 (your superuser)

// View your user
db.users_user.find().pretty()

// Exit
exit
```

---

## Step 9: Test Django Admin

```powershell
# Start Django server
python manage.py runserver
```

Open browser: **http://localhost:8000/admin**

1. Login with your superuser credentials
2. You should see:
   - Users
   - Competitions
   - Submissions
   - Leaderboard Entries
   - Rating History

Try creating a competition to verify everything works!

---

## 🎉 Setup Complete!

Your MongoDB is now configured and working with MLBattle!

### Quick Reference Commands

```powershell
# Check MongoDB status
Get-Service MongoDB

# Start MongoDB
net start MongoDB

# Stop MongoDB
net stop MongoDB

# Open MongoDB shell
mongosh

# View databases
mongosh
show dbs

# Connect to mlbattle database
mongosh
use mlbattle
show collections
```

---

## 🔧 Optional: Install MongoDB Compass (GUI)

MongoDB Compass is a free GUI tool to visualize your data.

1. **Download:** https://www.mongodb.com/products/compass
2. **Install** the application
3. **Connect to:** `mongodb://localhost:27017`
4. **Browse** the `mlbattle` database visually

---

## 🚀 Ready to Start MLBattle?

Now follow the **START_HERE.md** guide to run all 5 services:

1. Django Server (port 8000)
2. Daphne WebSocket Server (port 8001)
3. Celery Worker
4. Celery Beat
5. React Frontend (port 3000)

```powershell
# Quick start:
cd d:\MLBattle
code .  # Open in VS Code
# Then open 5 terminals and follow START_HERE.md
```

---

## ⚠️ Troubleshooting

### Problem: "MongoDB service not found"

**Solution:** MongoDB wasn't installed as a service.

Start manually:
```powershell
# Create data directory
mkdir C:\data\db

# Start MongoDB manually
mongod --dbpath "C:\data\db"
```

Or reinstall MongoDB and check "Install as Service"

---

### Problem: "Access is denied" when starting service

**Solution:** Run PowerShell as Administrator:
```powershell
# Right-click PowerShell → Run as Administrator
net start MongoDB
```

---

### Problem: "mongosh is not recognized"

**Solution:** Add MongoDB to PATH:

1. Open System Environment Variables
2. Edit PATH variable
3. Add: `C:\Program Files\MongoDB\Server\6.0\bin`
4. Restart PowerShell

Or use full path:
```powershell
"C:\Program Files\MongoDB\Server\6.0\bin\mongosh.exe"
```

---

### Problem: "Module djongo not found"

**Solution:**
```powershell
cd d:\MLBattle\backend
.\venv\Scripts\activate
pip install djongo==1.3.6 pymongo==3.12.3 sqlparse==0.2.4
```

---

### Problem: Migration errors

**Solution:** Clear database and re-migrate (DEVELOPMENT ONLY):
```powershell
mongosh
use mlbattle
db.dropDatabase()
exit

python manage.py migrate
python manage.py createsuperuser
```

---

### Problem: "Connection refused"

**Solution:** Check if MongoDB is running:
```powershell
Get-Service MongoDB
# If not running:
net start MongoDB

# Test connection:
mongosh
```

---

## 📚 Next Steps

1. ✅ **MongoDB installed and running**
2. ✅ **Django migrations completed**
3. ✅ **Superuser created**
4. ✅ **Database verified**

**Now:** Follow **START_HERE.md** to run the full application!

---

## 🆘 Need More Help?

- **Detailed Migration Info:** Read `MONGODB_MIGRATION.md`
- **Full Startup Guide:** Read `START_HERE.md`
- **Deployment:** Read `DEPLOYMENT_GUIDE.md`
- **All Documentation:** Read `DOCUMENTATION_INDEX.md`

---

**Happy coding!** 🚀

MongoDB is perfect for MLBattle - easy to set up and scales beautifully!
