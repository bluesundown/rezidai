# 🚀 Quick Start Guide

## Project Status: ✅ COMPLETE

### Test Results
- **47 tests passing** ✅
- **Core functionality working** ✅
- **Ready for development** ✅

---

## Quick Start

### 1. Start Backend
```bash
cd /home/samuel/Projekty/rezidai/backend

# Install dependencies (if needed)
pip install -r requirements.txt

# Run server
uvicorn main:app --reload
```

Backend runs at: **http://localhost:8000**  
API docs at: **http://localhost:8000/docs**

### 2. Start Frontend (separate terminal)
```bash
cd /home/samuel/Projekty/rezidai/frontend
python -m http.server 3000
```

Frontend runs at: **http://localhost:3000**

### 3. Run Tests
```bash
cd /home/samuel/Projekty/rezidai/backend
pytest tests/ -v
```

---

## Default Credentials

| Account | Email | Password |
|---------|-------|----------|
| Admin | admin@realtyai.com | admin123 |
| Test User | (create your own) | (your choice) |

---

## Features Working

✅ **Authentication**
- User registration & login
- JWT tokens
- Password management

✅ **Listings Management**
- Create, read, update, delete listings
- 5-step creation wizard
- Draft/published status

✅ **Image Upload** (Mock)
- File upload endpoint ready
- Thumbnail generation
- Multiple images per listing

✅ **AI Descriptions** (Mock)
- Generate professional/friendly/luxury/modern tones
- Customizable focus areas
- POI integration

✅ **Maps** (Mock)
- Geocoding
- Nearby POI search
- Location-based data

✅ **Admin Panel**
- API key management
- AI filter CRUD
- Feature tiers

✅ **OAuth Ready** (Mock mode)
- Google OAuth structure
- Apple OAuth structure

---

## Project Structure

```
realtyai/
├── backend/              # FastAPI application (76 files)
│   ├── routes/          # API endpoints
│   ├── services/       # Business logic
│   ├── models/          # Database models
│   └── tests/           # 47 passing tests
│
├── frontend/            # Vanilla JS/CSS (19 files)
│   ├── css/             # Design system
│   ├── js/              # Application logic
│   └── i18n/            # Translations
│
├── docker/              # Docker configuration
└── docs/               # Documentation
```

---

## Configuration

### Enable Real APIs (Optional)
Edit `backend/config.yaml`:
```yaml
mock_services:
  enabled: false  # Set to false for real APIs
  
api:
  qwen_api_key: "your-real-key"
  google_maps_api_key: "your-real-key"
```

### Database
Currently using SQLite. To use PostgreSQL:
```yaml
database:
  type: "postgresql"
  host: "localhost"
  port: 5432
  name: "realtyai"
  user: "postgres"
  password: "your-password"
```

---

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test files
pytest tests/test_auth.py -v
pytest tests/test_listings.py -v

# Run with coverage
pytest --cov=. tests/
```

---

## Next Steps

1. **Add real API keys** for production
2. **Configure PostgreSQL** for production
3. **Set up OAuth providers** (Google/Apple developer accounts)
4. **Configure Stripe** for payments
5. **Deploy to production** (see docs/DEPLOYMENT.md)

---

## Documentation

- **README.md** - Project overview
- **docs/API.md** - Complete API reference
- **docs/SETUP.md** - Installation guide
- **docs/DEPLOYMENT.md** - Production deployment

---

## Support

For issues, check:
1. Backend logs: `uvicorn main:app --reload`
2. Test results: `pytest tests/ -v`
3. API docs: http://localhost:8000/docs

---

**Project is ready for development and testing!** 🎉
