# 🔄 MongoDB Migration Guide

This document explains the database change from PostgreSQL to MongoDB and how it affects the MLBattle project.

---

## 📋 What Changed

### Database Engine
- **From:** PostgreSQL 14+ with psycopg2-binary
- **To:** MongoDB 6.0+ with djongo

### Why djongo?
Djongo is a Django-MongoDB connector that translates Django ORM queries to MongoDB queries. This means:
- ✅ All existing Django models work without changes
- ✅ Django admin panel continues to function
- ✅ No need to rewrite queries or views
- ✅ Migrations work as expected

---

## 🔧 Files Changed

### 1. **backend/requirements.txt**
**Removed:**
```txt
psycopg2-binary==2.9.9
dj-database-url==2.1.0
```

**Added:**
```txt
djongo==1.3.6
pymongo==3.12.3
sqlparse==0.2.4
```

### 2. **backend/.env.example**
**Removed:**
```env
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
```

**Added:**
```env
MONGO_HOST=localhost
MONGO_PORT=27017
# MONGO_USER=your-mongo-username  # Optional
# MONGO_PASSWORD=your-mongo-password  # Optional
```

### 3. **backend/config/settings/base.py**
**Old Database Configuration:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='mlbattle'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
```

**New Database Configuration:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': config('DB_NAME', default='mlbattle'),
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': config('MONGO_HOST', default='localhost'),
            'port': int(config('MONGO_PORT', default=27017)),
            'username': config('MONGO_USER', default=None),
            'password': config('MONGO_PASSWORD', default=None),
        }
    }
}
```

### 4. **backend/config/settings/production.py**
**Removed:**
```python
import dj_database_url
DATABASES['default'] = dj_database_url.config(conn_max_age=600)
```

**Updated:**
```python
# Database configuration inherited from base.py
# Override if needed for production
```

---

## 📦 Installation Steps

### For Development (Windows)

#### 1. Install MongoDB
```powershell
# Download MongoDB Community Server from:
# https://www.mongodb.com/try/download/community

# Or using Chocolatey:
choco install mongodb

# Or using Windows Package Manager:
winget install MongoDB.Server
```

#### 2. Start MongoDB
```powershell
# If installed as Windows Service:
net start MongoDB

# Or manually:
mongod --dbpath "C:\data\db"
```

#### 3. Update Backend Dependencies
```powershell
cd d:\MLBattle\backend
.\venv\Scripts\activate

# Uninstall old packages (optional)
pip uninstall psycopg2-binary dj-database-url -y

# Install new packages
pip install -r requirements.txt
```

#### 4. Update Environment Variables
```powershell
# Edit .env file
notepad .env
```

Replace PostgreSQL variables with MongoDB:
```env
DB_NAME=mlbattle
MONGO_HOST=localhost
MONGO_PORT=27017
# MONGO_USER=  # Leave empty for development
# MONGO_PASSWORD=  # Leave empty for development
```

#### 5. Run Migrations
```powershell
python manage.py migrate
python manage.py createsuperuser
```

### For Production (Ubuntu)

#### 1. Install MongoDB
```bash
# Import MongoDB GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Update and install
sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB
sudo systemctl enable mongod
sudo systemctl start mongod
```

#### 2. Configure MongoDB (Production Security)
```bash
mongosh

use mlbattle
db.createUser({
  user: "mlbattle_user",
  pwd: "your_secure_password",
  roles: [{role: "readWrite", db: "mlbattle"}]
})
exit
```

#### 3. Update Backend
```bash
cd /var/www/mlbattle/backend
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Update .env
nano .env
```

Update environment variables:
```env
DB_NAME=mlbattle
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_USER=mlbattle_user
MONGO_PASSWORD=your_secure_password
```

#### 4. Run Migrations
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

#### 5. Restart Services
```bash
sudo systemctl restart mlbattle
sudo systemctl restart mlbattle-celery
sudo systemctl restart mlbattle-daphne
```

---

## ✅ Model Compatibility

### Good News: No Model Changes Needed!

Djongo supports all standard Django field types used in MLBattle:

| Django Field | MongoDB Support | Notes |
|--------------|-----------------|-------|
| CharField | ✅ Works | Stored as string |
| TextField | ✅ Works | Stored as string |
| EmailField | ✅ Works | Stored as string |
| IntegerField | ✅ Works | Stored as number |
| FloatField | ✅ Works | Stored as number |
| DateTimeField | ✅ Works | Stored as ISODate |
| BooleanField | ✅ Works | Stored as boolean |
| ForeignKey | ✅ Works | Stored as ObjectId reference |
| JSONField | ✅ Works | Native MongoDB support |

### Models That Work Without Changes:
- ✅ `User` model (with ForeignKey relationships)
- ✅ `Competition` model
- ✅ `Submission` model
- ✅ `LeaderboardEntry` model
- ✅ `RatingHistory` model

---

## 🧪 Testing the Migration

### 1. Verify MongoDB Connection
```powershell
# Windows
mongosh --host localhost --port 27017

# Should connect successfully
```

### 2. Test Django Connection
```powershell
cd d:\MLBattle\backend
.\venv\Scripts\activate
python manage.py shell
```

In Django shell:
```python
from django.db import connection
connection.ensure_connection()
print("Connected to:", connection.settings_dict['NAME'])
# Should print: Connected to: mlbattle
```

### 3. Run Migrations
```powershell
python manage.py migrate
```

Expected output:
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying users.0001_initial... OK
  Applying competitions.0001_initial... OK
  ...
```

### 4. Test CRUD Operations
```python
# In Django shell
from apps.users.models import User

# Create
user = User.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='testpass123'
)

# Read
users = User.objects.all()
print(users)

# Update
user.kaggle_username = 'test_kaggle'
user.save()

# Delete
# user.delete()
```

### 5. Test Admin Panel
```powershell
python manage.py runserver
```

Visit: http://localhost:8000/admin
- Login with superuser credentials
- Try creating/editing competitions
- Verify all models load correctly

---

## 🔍 Checking MongoDB Data

### Using MongoDB Shell (mongosh)
```javascript
// Connect to MongoDB
mongosh

// Switch to database
use mlbattle

// List all collections
show collections

// View users
db.users_user.find().pretty()

// View competitions
db.competitions_competition.find().pretty()

// Count documents
db.users_user.countDocuments()
```

### Using MongoDB Compass (GUI)
1. Download MongoDB Compass: https://www.mongodb.com/products/compass
2. Connect to: `mongodb://localhost:27017`
3. Select `mlbattle` database
4. Browse collections visually

---

## ⚡ Performance Considerations

### Indexes
Django migrations will automatically create indexes for:
- Primary keys (_id in MongoDB)
- Foreign keys
- Fields with `db_index=True`

### Additional Indexes (Optional)
```python
# In Django shell or management command
from apps.competitions.models import Competition
from pymongo import ASCENDING, DESCENDING

# Get MongoDB collection
collection = Competition._meta.get_field('id').model._meta.db_table

# Create compound index for better query performance
from django.db import connection
db = connection.get_database()
db[collection].create_index([
    ('status', ASCENDING),
    ('start_date', DESCENDING)
])
```

---

## 🐛 Troubleshooting

### Issue: "djongo is not installed"
```powershell
pip install djongo==1.3.6 pymongo==3.12.3 sqlparse==0.2.4
```

### Issue: "MongoDB connection refused"
```powershell
# Check if MongoDB is running
Get-Service MongoDB  # Windows
sudo systemctl status mongod  # Linux

# Start if not running
net start MongoDB  # Windows
sudo systemctl start mongod  # Linux
```

### Issue: "No module named 'bson'"
```powershell
pip install pymongo==3.12.3
```

### Issue: Migrations fail
```powershell
# Clear migration history (only in development!)
python manage.py migrate --fake

# Or delete MongoDB database and start fresh
mongosh
use mlbattle
db.dropDatabase()
exit

# Then run migrations again
python manage.py migrate
```

### Issue: "ENFORCE_SCHEMA" errors
This is normal. `ENFORCE_SCHEMA=False` allows Django to work flexibly with MongoDB.

---

## 📊 Comparison: PostgreSQL vs MongoDB

| Feature | PostgreSQL | MongoDB | Impact on MLBattle |
|---------|------------|---------|-------------------|
| Schema | Rigid | Flexible | No impact with djongo |
| Queries | SQL | NoSQL | Handled by djongo |
| Transactions | ACID | Partial ACID | Works for our use case |
| Joins | Full support | Limited | Works via ForeignKey |
| Performance | Fast for complex queries | Fast for simple queries | Similar performance |
| Scalability | Vertical | Horizontal | MongoDB scales easier |
| Admin Tools | pgAdmin | Compass | Both have good tools |

---

## 🎯 Key Takeaways

1. ✅ **No code changes required** - djongo handles everything
2. ✅ **All models work** - ForeignKey, JSONField, etc. all supported
3. ✅ **Django admin works** - Full admin functionality preserved
4. ✅ **Migrations work** - Use `python manage.py migrate` as usual
5. ✅ **Easy to install** - MongoDB has simple installers for all platforms

---

## 📚 Additional Resources

- **djongo Documentation:** https://www.djongomapper.com/
- **MongoDB Documentation:** https://www.mongodb.com/docs/
- **MongoDB Compass:** https://www.mongodb.com/products/compass
- **MongoDB Installation:** https://www.mongodb.com/docs/manual/installation/

---

## 🆘 Need Help?

If you encounter issues:
1. Check MongoDB is running: `mongosh`
2. Verify .env configuration
3. Check logs: `python manage.py runserver` output
4. Test connection in Django shell
5. Review this guide's troubleshooting section

---

**Migration Complete!** 🎉

Your MLBattle project now uses MongoDB instead of PostgreSQL, with full Django ORM compatibility maintained through djongo.
